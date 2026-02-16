"""
Módulo de configuração FFmpeg para animações Matplotlib
========================================================

Este módulo fornece funções para configurar e salvar animações
do Matplotlib usando FFmpeg de forma simples e reutilizável.

========================================================
"""

import logging
import platform
import re
import shutil
import subprocess
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Final, List, Optional, Set, Tuple

import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, FuncAnimation

# ============================================================================
# Configuração de Logging
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Constantes (usando Final para type safety)
# ============================================================================

# Timeouts
VALIDATION_TIMEOUT: Final[int] = 3
CODEC_QUERY_TIMEOUT: Final[int] = 5

# Cache
CODEC_CACHE_TTL: Final[int] = 3600  # 1 hora em segundos

# Logging
PROGRESS_LOG_INTERVAL: Final[int] = 10  # Log a cada N frames

# Qualidades válidas
VALID_QUALITIES: Final[Set[str]] = {"low", "medium", "high", "ultra"}

# Codecs comuns de fallback
COMMON_CODECS: Final[Set[str]] = {
    "libx264",
    "libx265",
    "mpeg4",
    "h264",
    "vp9",
    "h264_nvenc",
    "hevc_nvenc",
    "libvpx",
    "libvpx-vp9",
}

# Padrão regex para parsing de codecs (suporta hífens)
CODEC_PATTERN: Final[str] = r"^\s*([D.][E.][VAS][I.][L.][S.])\s+([\w-]+)"


# ============================================================================
# Enums
# ============================================================================


class Quality(Enum):
    """Enum para presets de qualidade."""

    LOW = ("low", 1500, 72)
    MEDIUM = ("medium", 3000, 100)
    HIGH = ("high", 5000, 150)
    ULTRA = ("ultra", 8000, 200)

    def __init__(self, name: str, bitrate: int, dpi: int):
        self.quality_name = name
        self.bitrate = bitrate
        self.dpi = dpi

    @classmethod
    def from_string(cls, quality: str) -> "Quality":
        """Converte string para enum."""
        for q in cls:
            if q.quality_name == quality:
                return q
        raise ValueError(f"Qualidade inválida: {quality}")


# ============================================================================
# Exceções Customizadas
# ============================================================================


class FFmpegError(Exception):
    """Exceção base para erros relacionados ao FFmpeg."""

    pass


class FFmpegNotFoundError(FFmpegError):
    """FFmpeg não foi encontrado no sistema."""

    pass


class FFmpegNotConfiguredError(FFmpegError):
    """FFmpeg não foi configurado antes de tentar usá-lo."""

    pass


class InvalidCodecError(FFmpegError):
    """Codec solicitado não está disponível no FFmpeg instalado."""

    pass


class InvalidQualityError(FFmpegError):
    """Preset de qualidade inválido."""

    pass


class InvalidFileExtensionError(FFmpegError):
    """Extensão de arquivo não suportada."""

    pass


class InsufficientDiskSpaceError(FFmpegError):
    """Espaço em disco insuficiente."""

    pass


class StrictModeError(FFmpegError):
    """Erro em modo strict (fallback não permitido)."""

    pass


# ============================================================================
# Classes de Dados
# ============================================================================


@dataclass
class CodecQueryResult:
    """Resultado de uma consulta de codecs."""

    codecs: Set[str]
    using_fallback: bool
    timestamp: float = field(default_factory=time.time)
    error_message: Optional[str] = None

    def is_expired(self, ttl: int = CODEC_CACHE_TTL) -> bool:
        """Verifica se o cache expirou."""
        return (time.time() - self.timestamp) > ttl


@dataclass
class ValidationResult:
    """Resultado de validação de FFmpeg."""

    is_valid: bool
    path: Optional[str] = None
    version: Optional[Tuple[int, int, int]] = None
    error_message: Optional[str] = None


@dataclass
class SaveOptions:
    """Opções para salvar animação."""

    fps: int = 20
    dpi: Optional[int] = None
    quality: str = "high"
    metadata: Optional[Dict[str, str]] = None
    verbose: bool = True
    progress_callback: Optional[Callable[[int, int], None]] = None
    codec: str = "libx264"
    bitrate: Optional[int] = None
    validate_codec: bool = True
    strict_validation: bool = False
    check_disk_space: bool = True

    def __post_init__(self):
        """Validação após inicialização."""
        if self.quality not in VALID_QUALITIES:
            raise InvalidQualityError(
                f"Qualidade '{self.quality}' inválida. "
                f"Use: {', '.join(sorted(VALID_QUALITIES))}"
            )


@dataclass
class DiskSpaceInfo:
    """Informações sobre espaço em disco."""

    available_mb: float
    required_mb: float
    has_space: bool
    warning_threshold_mb: float = 500.0  # Aviso se sobrar menos que isso


# ============================================================================
# Detector de FFmpeg
# ============================================================================


class FFmpegDetector:
    """
    Classe responsável por detectar FFmpeg no sistema.

    Separação de concerns: apenas detecção de executável.
    """

    @staticmethod
    def get_system_specific_paths() -> List[Path]:
        """
        Retorna caminhos específicos do sistema operacional.

        Returns:
            List[Path]: Lista de caminhos possíveis
        """
        system = platform.system()

        if system == "Windows":
            return [
                Path("C:/ffmpeg/bin/ffmpeg.exe"),
                Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
                Path("C:/Program Files (x86)/ffmpeg/bin/ffmpeg.exe"),
                Path.home() / "ffmpeg" / "ffmpeg" / "bin" / "ffmpeg.exe",
                Path.home() / "AppData" / "Local" / "ffmpeg" / "bin" / "ffmpeg.exe",
            ]
        elif system == "Darwin":  # macOS
            return [
                Path("/opt/homebrew/bin/ffmpeg"),  # Apple Silicon
                Path("/usr/local/bin/ffmpeg"),  # Intel
                Path("/usr/bin/ffmpeg"),
                Path("/opt/local/bin/ffmpeg"),  # MacPorts
            ]
        else:  # Linux
            return [
                Path("/usr/bin/ffmpeg"),
                Path("/usr/local/bin/ffmpeg"),
                Path("/snap/bin/ffmpeg"),  # Snap
                Path("/opt/ffmpeg/bin/ffmpeg"),
                Path.home() / "bin" / "ffmpeg",
                Path.home() / ".local" / "bin" / "ffmpeg",
            ]

    @staticmethod
    def resolve_path(path: str) -> Optional[str]:
        """
        Resolve caminho de forma consistente.

        Tenta múltiplas estratégias:
        1. shutil.which (se for nome de comando)
        2. Path absoluto/relativo
        3. which do nome base (se path incluir diretório)

        Args:
            path: Caminho ou nome do executável

        Returns:
            Optional[str]: Caminho resolvido ou None
        """
        # Estratégia 1: which direto
        resolved = shutil.which(path)
        if resolved:
            return resolved

        # Estratégia 2: path existe como está
        path_obj = Path(path).expanduser().resolve()
        if path_obj.exists():
            return str(path_obj)

        # Estratégia 3: tentar which com nome base
        if "/" in path or "\\" in path:
            base_name = path_obj.name
            resolved = shutil.which(base_name)
            if resolved:
                return resolved

        return None

    @classmethod
    def find_in_path(cls) -> Optional[str]:
        """
        Busca FFmpeg no PATH do sistema.

        Returns:
            Optional[str]: Caminho do FFmpeg ou None
        """
        return cls.resolve_path("ffmpeg")

    @classmethod
    def auto_detect(cls) -> Optional[str]:
        """
        Detecta automaticamente FFmpeg no sistema.

        Estratégia:
        1. Busca no PATH (mais comum)
        2. Busca em locais específicos do SO

        Returns:
            Optional[str]: Caminho do FFmpeg detectado ou None
        """
        # Prioridade 1: PATH
        ffmpeg_path = cls.find_in_path()
        if ffmpeg_path:
            logger.debug("FFmpeg encontrado no PATH: %s", ffmpeg_path)
            return ffmpeg_path

        # Prioridade 2: Caminhos específicos do SO
        for path in cls.get_system_specific_paths():
            if path.exists():
                logger.debug("FFmpeg encontrado em: %s", path)
                return str(path)

        logger.debug("FFmpeg não detectado automaticamente")
        return None


# ============================================================================
# Validador de FFmpeg
# ============================================================================


class FFmpegValidator:
    """
    Classe responsável por validar executáveis e codecs FFmpeg.

    Separação de concerns: apenas validação.
    """

    @staticmethod
    def parse_version(version_output: str) -> Optional[Tuple[int, int, int]]:
        """
        Extrai versão do FFmpeg da saída do comando.

        Args:
            version_output: Saída do comando 'ffmpeg -version'

        Returns:
            Optional[Tuple[int, int, int]]: (major, minor, patch) ou None
        """
        # Padrão: "ffmpeg version 4.4.2" ou "ffmpeg version N-12345-gabcdef"
        match = re.search(r"ffmpeg version (\d+)\.(\d+)\.(\d+)", version_output)
        if match:
            return (int(match.group(1)), int(match.group(2)), int(match.group(3)))

        # Versão git/snapshot
        match = re.search(r"ffmpeg version [Nn]-(\d+)", version_output)
        if match:
            return (99, 0, int(match.group(1)))  # Versão de desenvolvimento

        return None

    @classmethod
    def validate_executable(cls, path: str) -> ValidationResult:
        """
        Valida se o caminho aponta para um executável FFmpeg válido.

        Args:
            path: Caminho para validar

        Returns:
            ValidationResult: Resultado da validação
        """
        # Resolver caminho de forma consistente
        resolved_path = FFmpegDetector.resolve_path(path)

        if not resolved_path:
            return ValidationResult(
                is_valid=False, error_message=f"Executável não encontrado: {path}"
            )

        # Verificar se arquivo existe
        if not Path(resolved_path).exists():
            return ValidationResult(
                is_valid=False,
                error_message=f"FFmpeg não encontrado em: {resolved_path}",
            )

        # Testar se é executável válido
        try:
            result = subprocess.run(
                [resolved_path, "-version"],
                capture_output=True,
                timeout=VALIDATION_TIMEOUT,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Executável retornou erro: {result.returncode}",
                )

            # Verificar se é realmente FFmpeg
            if "ffmpeg version" not in result.stdout.lower():
                return ValidationResult(
                    is_valid=False, error_message="Executável não parece ser FFmpeg"
                )

            # Extrair versão
            version = cls.parse_version(result.stdout)

            return ValidationResult(is_valid=True, path=resolved_path, version=version)

        except subprocess.TimeoutExpired:
            return ValidationResult(
                is_valid=False,
                error_message=f"Timeout ao verificar FFmpeg ({VALIDATION_TIMEOUT}s)",
            )
        except FileNotFoundError:
            return ValidationResult(
                is_valid=False,
                error_message=f"Executável não encontrado: {resolved_path}",
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False, error_message=f"Erro ao validar FFmpeg: {e}"
            )

    @staticmethod
    def parse_codec_line(line: str) -> Optional[str]:
        """
        Faz parsing de uma linha de saída do comando 'ffmpeg -codecs'.

        Args:
            line: Linha de texto

        Returns:
            Optional[str]: Nome do codec se for codec de vídeo, None caso contrário
        """
        # Usar regex robusto (suporta hífens agora)
        match = re.match(CODEC_PATTERN, line)

        if not match:
            return None

        flags, codec_name = match.groups()

        # Verificar se é codec de vídeo (flag 'V' ou 'v')
        if "V" in flags.upper():
            # Limpar nome do codec
            codec_name = codec_name.strip("()")

            if codec_name and not codec_name.startswith("-"):
                return codec_name

        return None

    @classmethod
    def query_available_codecs(cls, ffmpeg_path: str) -> CodecQueryResult:
        """
        Consulta codecs disponíveis no FFmpeg instalado.

        Args:
            ffmpeg_path: Caminho do executável FFmpeg

        Returns:
            CodecQueryResult: Resultado da consulta com codecs e status
        """
        try:
            result = subprocess.run(
                [ffmpeg_path, "-codecs"],
                capture_output=True,
                timeout=CODEC_QUERY_TIMEOUT,
                text=True,
                check=False,
            )

            codecs = set()
            in_codec_section = False

            for line in result.stdout.split("\n"):
                line = line.strip()

                # Detectar início da seção de codecs
                if "-------" in line or "Codecs:" in line:
                    in_codec_section = True
                    continue

                if not in_codec_section or not line:
                    continue

                # Parse da linha
                codec_name = cls.parse_codec_line(line)
                if codec_name:
                    codecs.add(codec_name)

            # Verificar se encontrou codecs
            if codecs:
                logger.debug("Codecs detectados: %d encontrados", len(codecs))
                return CodecQueryResult(codecs=codecs, using_fallback=False)
            else:
                logger.warning(
                    "Nenhum codec detectado via parsing. "
                    "Usando fallback de codecs comuns."
                )
                return CodecQueryResult(
                    codecs=COMMON_CODECS.copy(),
                    using_fallback=True,
                    error_message="Parsing não encontrou codecs",
                )

        except subprocess.TimeoutExpired:
            logger.warning(
                "Timeout ao consultar codecs (%ds). Usando fallback.",
                CODEC_QUERY_TIMEOUT,
            )
            return CodecQueryResult(
                codecs=COMMON_CODECS.copy(),
                using_fallback=True,
                error_message="Timeout na consulta",
            )
        except Exception as e:
            logger.warning("Erro ao consultar codecs: %s. Usando fallback.", e)
            return CodecQueryResult(
                codecs=COMMON_CODECS.copy(), using_fallback=True, error_message=str(e)
            )


# ============================================================================
# Utilitários
# ============================================================================


class DiskSpaceValidator:
    """Validador de espaço em disco."""

    @staticmethod
    def get_available_space(path: Path) -> float:
        """
        Retorna espaço disponível em MB.

        Args:
            path: Caminho do arquivo ou diretório

        Returns:
            float: Espaço disponível em MB
        """
        try:
            stat = shutil.disk_usage(path.parent if path.is_file() else path)
            return stat.free / (1024 * 1024)  # Bytes para MB
        except Exception as e:
            logger.warning("Erro ao verificar espaço em disco: %s", e)
            return float("inf")  # Assumir espaço ilimitado em caso de erro

    @staticmethod
    def estimate_video_size(
        duration: float,
        fps: int,
        quality: Quality,
        resolution: Optional[Tuple[int, int]] = None,
    ) -> float:
        """
        Estima tamanho do vídeo em MB.

        Fórmula simplificada:
        tamanho ≈ (bitrate * duration) / 8 / 1024

        Com fator de correção baseado na resolução.

        Args:
            duration: Duração em segundos
            fps: Frames por segundo
            quality: Preset de qualidade
            resolution: (width, height) opcional

        Returns:
            float: Tamanho estimado em MB
        """
        bitrate_kbps = quality.bitrate

        # Fator de correção para resolução
        resolution_factor = 1.0
        if resolution:
            width, height = resolution
            pixels = width * height
            # Normalizar para 1920x1080 (Full HD)
            reference_pixels = 1920 * 1080
            resolution_factor = pixels / reference_pixels

        # Cálculo: (kbps * segundos) / 8 / 1024 = MB
        size_mb = (bitrate_kbps * duration * resolution_factor) / 8 / 1024

        # Adicionar overhead de container (aproximadamente 5%)
        size_mb *= 1.05

        return size_mb

    @classmethod
    def check_space(
        cls, output_path: Path, estimated_size: float, safety_margin: float = 1.2
    ) -> DiskSpaceInfo:
        """
        Verifica se há espaço suficiente em disco.

        Args:
            output_path: Caminho do arquivo de saída
            estimated_size: Tamanho estimado em MB
            safety_margin: Margem de segurança (multiplicador)

        Returns:
            DiskSpaceInfo: Informações sobre espaço
        """
        available = cls.get_available_space(output_path)
        required = estimated_size * safety_margin

        has_space = available >= required

        return DiskSpaceInfo(
            available_mb=available, required_mb=required, has_space=has_space
        )


# ============================================================================
# Classe Principal de Configuração
# ============================================================================


class FFmpegConfig:
    """
    Classe para configurar e gerenciar o FFmpeg em animações Matplotlib.

    Usa dependency injection para detector e validator, permitindo
    melhor testabilidade e separação de concerns.

    Attributes:
        ffmpeg_path (str): Caminho para o executável do FFmpeg
        configured (bool): Indica se o FFmpeg foi configurado com sucesso
        version (Tuple[int, int, int]): Versão do FFmpeg
    """

    def __init__(
        self,
        ffmpeg_path: Optional[str] = None,
        auto_detect: bool = True,
        strict_mode: bool = False,
        detector: Optional[FFmpegDetector] = None,
        validator: Optional[FFmpegValidator] = None,
    ) -> None:
        """
        Inicializa a configuração do FFmpeg.

        Args:
            ffmpeg_path: Caminho manual para o FFmpeg
            auto_detect: Se True, tenta detectar FFmpeg no sistema
            strict_mode: Se True, não permite fallbacks
            detector: Instância customizada do detector (para testes)
            validator: Instância customizada do validator (para testes)
        """
        self._ffmpeg_path: Optional[str] = None
        self._ffmpeg_version: Optional[Tuple[int, int, int]] = None
        self._codec_cache: Optional[CodecQueryResult] = None
        self._strict_mode: bool = strict_mode
        self._lock: threading.RLock = threading.RLock()  # Lock reentrant

        # Dependency injection
        self.detector = detector or FFmpegDetector()
        self.validator = validator or FFmpegValidator()

        if ffmpeg_path:
            self.set_ffmpeg_path(ffmpeg_path)
        elif auto_detect:
            self.auto_detect_ffmpeg()

    @property
    def configured(self) -> bool:
        """
        Indica se FFmpeg está configurado.

        Returns:
            bool: True se ffmpeg_path está definido e válido
        """
        return self._ffmpeg_path is not None

    @property
    def ffmpeg_path(self) -> Optional[str]:
        """Retorna o caminho do FFmpeg configurado."""
        return self._ffmpeg_path

    @property
    def version(self) -> Optional[Tuple[int, int, int]]:
        """Retorna a versão do FFmpeg."""
        return self._ffmpeg_version

    @property
    def version_string(self) -> str:
        """Retorna versão como string."""
        if self._ffmpeg_version:
            return f"{self._ffmpeg_version[0]}.{self._ffmpeg_version[1]}.{self._ffmpeg_version[2]}"
        return "Desconhecida"

    @property
    def using_fallback_codecs(self) -> bool:
        """
        Indica se está usando fallback de codecs.

        Returns:
            bool: True se usando codecs de fallback
        """
        return self._codec_cache is not None and self._codec_cache.using_fallback

    @property
    def strict_mode(self) -> bool:
        """Indica se modo strict está ativo."""
        return self._strict_mode

    def auto_detect_ffmpeg(self) -> bool:
        """
        Detecta automaticamente o FFmpeg no sistema.

        Returns:
            bool: True se FFmpeg foi detectado e configurado com sucesso
        """
        detected_path = self.detector.auto_detect()

        if not detected_path:
            logger.warning("⚠ FFmpeg não detectado automaticamente.")
            logger.warning("  Use set_ffmpeg_path() para configurar manualmente.")
            return False

        try:
            self.set_ffmpeg_path(detected_path)
            logger.info("✓ FFmpeg detectado e configurado: %s", detected_path)
            if self._ffmpeg_version:
                logger.info("  Versão: %s", self.version_string)
            return True
        except (FFmpegNotFoundError, ValueError) as e:
            logger.error("Erro ao configurar FFmpeg detectado: %s", e)
            return False

    def set_ffmpeg_path(self, path: str) -> None:
        """
        Define o caminho do FFmpeg com validação.

        Args:
            path: Caminho para o executável do FFmpeg

        Raises:
            FFmpegNotFoundError: Se o FFmpeg não for encontrado
            ValueError: Se o caminho não for válido
        """
        with self._lock:
            # Validar antes de configurar
            validation = self.validator.validate_executable(path)

            if not validation.is_valid:
                raise FFmpegNotFoundError(
                    validation.error_message or f"FFmpeg inválido: {path}"
                )

            # Usar caminho resolvido
            resolved_path = validation.path or path

            self._ffmpeg_path = resolved_path
            self._ffmpeg_version = validation.version
            self._codec_cache = None  # Limpar cache de codecs
            plt.rcParams["animation.ffmpeg_path"] = resolved_path
            logger.debug("FFmpeg configurado: %s", resolved_path)

    def refresh_codec_cache(self) -> None:
        """
        Força atualização do cache de codecs.

        Útil quando FFmpeg é atualizado durante execução.
        """
        with self._lock:
            self._codec_cache = None
            if self.configured:
                self._get_available_codecs()
                logger.debug("Cache de codecs atualizado")

    def _get_available_codecs(self) -> CodecQueryResult:
        """
        Obtém lista de codecs disponíveis (com cache e TTL).

        Returns:
            CodecQueryResult: Resultado com codecs disponíveis

        Raises:
            FFmpegNotConfiguredError: Se FFmpeg não estiver configurado
            StrictModeError: Se em modo strict e usando fallback
        """
        if not self.configured:
            raise FFmpegNotConfiguredError(
                "FFmpeg não configurado. Configure antes de verificar codecs."
            )

        with self._lock:
            # Verificar cache válido
            if self._codec_cache is not None and not self._codec_cache.is_expired():
                return self._codec_cache

            # Consultar codecs
            self._codec_cache = self.validator.query_available_codecs(self._ffmpeg_path)

            # Verificar modo strict
            if self._strict_mode and self._codec_cache.using_fallback:
                raise StrictModeError(
                    "Modo strict ativo: não é permitido usar fallback de codecs. "
                    f"Razão: {self._codec_cache.error_message}"
                )

            # Alertar se usando fallback
            if self._codec_cache.using_fallback:
                logger.warning(
                    "⚠ Usando lista de fallback de codecs comuns. "
                    "Validação de codec pode não ser confiável."
                )
                if self._codec_cache.error_message:
                    logger.warning("  Razão: %s", self._codec_cache.error_message)

            return self._codec_cache

    def get_available_codecs(self) -> Set[str]:
        """
        Retorna conjunto de codecs disponíveis (API pública).

        Returns:
            Set[str]: Conjunto de nomes de codecs
        """
        return self._get_available_codecs().codecs.copy()

    def validate_codec(self, codec: str, strict: bool = True) -> bool:
        """
        Valida se um codec está disponível.

        Args:
            codec: Nome do codec a validar
            strict: Se True, lança exceção se codec inválido

        Returns:
            bool: True se codec está disponível

        Raises:
            InvalidCodecError: Se codec não disponível (apenas se strict=True)
        """
        codec_result = self._get_available_codecs()
        available_codecs = codec_result.codecs

        if codec not in available_codecs:
            # Mostrar exemplos de codecs disponíveis
            examples = ", ".join(sorted(list(available_codecs)[:10]))

            error_msg = (
                f"Codec '{codec}' não está disponível. "
                f"Codecs disponíveis: {examples}"
            )

            # Adicionar aviso se usando fallback
            if codec_result.using_fallback:
                error_msg += (
                    " (AVISO: Usando lista de fallback, "
                    "codec pode existir mas não foi detectado)"
                )

            if strict:
                raise InvalidCodecError(error_msg)
            else:
                logger.debug(error_msg)
                return False

        return True

    def create_writer(
        self,
        fps: int = 20,
        bitrate: Optional[int] = None,
        codec: str = "libx264",
        quality: str = "high",
        metadata: Optional[Dict[str, str]] = None,
        validate_codec: bool = True,
        strict_validation: bool = False,
    ) -> FFMpegWriter:
        """
        Cria um writer FFmpeg configurado.

        Args:
            fps: Frames por segundo (padrão: 20)
            bitrate: Taxa de bits em kbps (padrão: automático por qualidade)
            codec: Codec de vídeo (padrão: 'libx264')
            quality: Preset de qualidade - 'low', 'medium', 'high', 'ultra'
            metadata: Metadados do vídeo
            validate_codec: Se True, valida se codec está disponível
            strict_validation: Se True, lança exceção se codec inválido

        Returns:
            FFMpegWriter: Writer configurado

        Raises:
            FFmpegNotConfiguredError: Se FFmpeg não estiver configurado
            InvalidQualityError: Se qualidade for inválida
            InvalidCodecError: Se codec inválido (apenas se strict_validation=True)
        """
        if not self.configured:
            raise FFmpegNotConfiguredError(
                "FFmpeg não configurado. Use set_ffmpeg_path() ou "
                "auto_detect_ffmpeg() primeiro."
            )

        # Usar enum para qualidade
        try:
            quality_enum = Quality.from_string(quality)
        except ValueError:
            raise InvalidQualityError(
                f"Qualidade '{quality}' inválida. "
                f"Use: {', '.join(sorted(VALID_QUALITIES))}"
            )

        # Validar codec se solicitado
        if validate_codec:
            self.validate_codec(codec, strict=strict_validation)

        # Usar bitrate do preset se não especificado
        if bitrate is None:
            bitrate = quality_enum.bitrate

        if metadata is None:
            metadata = {"artist": "Matplotlib Animation"}

        return FFMpegWriter(fps=fps, metadata=metadata, bitrate=bitrate, codec=codec)

    def _create_verbose_callback(
        self, user_callback: Optional[Callable[[int, int], None]] = None
    ) -> Callable[[int, int], None]:
        """
        Cria callback de progresso com logging.

        Separa concerns: logging verbose não mistura com callback do usuário.

        Args:
            user_callback: Callback opcional do usuário

        Returns:
            Callable: Callback combinado
        """

        def combined_callback(current_frame: int, total_frames: int) -> None:
            # Logging a cada N frames
            if current_frame % PROGRESS_LOG_INTERVAL == 0:
                progress = (current_frame / total_frames) * 100
                logger.info(
                    "  Progresso: %.1f%% (%d/%d)", progress, current_frame, total_frames
                )

            # Chamar callback do usuário se fornecido
            if user_callback is not None:
                user_callback(current_frame, total_frames)

        return combined_callback

    def save_animation(
        self,
        animation: FuncAnimation,
        filename: str,
        options: Optional[SaveOptions] = None,
        **kwargs,
    ) -> str:
        """
        Salva uma animação em arquivo de vídeo.

        Args:
            animation: Objeto FuncAnimation do Matplotlib
            filename: Nome do arquivo de saída
            options: SaveOptions ou None (usa kwargs se None)
            **kwargs: Argumentos alternativos (apenas se options=None)

        Returns:
            str: Caminho completo do arquivo salvo

        Raises:
            FFmpegNotConfiguredError: Se FFmpeg não estiver configurado
            InvalidQualityError: Se qualidade for inválida
            InsufficientDiskSpaceError: Se não houver espaço em disco
        """
        if not self.configured:
            raise FFmpegNotConfiguredError("FFmpeg não configurado.")

        # Criar SaveOptions se não fornecido
        if options is None:
            options = SaveOptions(**kwargs)

        # Usar enum para qualidade
        quality_enum = Quality.from_string(options.quality)

        # Aplicar DPI do preset se não especificado
        dpi = options.dpi if options.dpi is not None else quality_enum.dpi
        logger.debug("DPI: %d (qualidade: %s)", dpi, options.quality)

        # Validar e normalizar nome do arquivo
        file_path = Path(filename)
        if file_path.suffix == "":
            file_path = file_path.with_suffix(".mp4")
            logger.debug("Extensão .mp4 adicionada automaticamente")

        # Criar diretório se necessário
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Verificar espaço em disco
        if options.check_disk_space:
            # Estimar tamanho (assumir duração baseada em frames)
            try:
                total_frames = (
                    len(animation._func_handles)
                    if hasattr(animation, "_func_handles")
                    else 100
                )
                duration = total_frames / options.fps

                fig = animation._fig if hasattr(animation, "_fig") else None
                resolution = None
                if fig:
                    resolution = (
                        int(fig.get_figwidth() * dpi),
                        int(fig.get_figheight() * dpi),
                    )

                estimated_size = DiskSpaceValidator.estimate_video_size(
                    duration, options.fps, quality_enum, resolution
                )

                disk_info = DiskSpaceValidator.check_space(file_path, estimated_size)

                if not disk_info.has_space:
                    raise InsufficientDiskSpaceError(
                        f"Espaço em disco insuficiente. "
                        f"Disponível: {disk_info.available_mb:.1f} MB, "
                        f"Necessário: {disk_info.required_mb:.1f} MB"
                    )

                if (
                    disk_info.available_mb - disk_info.required_mb
                    < disk_info.warning_threshold_mb
                ):
                    logger.warning(
                        "⚠ Espaço em disco baixo após salvamento. "
                        "Sobrará aproximadamente %.1f MB",
                        disk_info.available_mb - disk_info.required_mb,
                    )
            except Exception as e:
                logger.debug("Não foi possível verificar espaço em disco: %s", e)

        # Criar writer
        writer = self.create_writer(
            fps=options.fps,
            bitrate=options.bitrate,
            codec=options.codec,
            quality=options.quality,
            metadata=options.metadata,
            validate_codec=options.validate_codec,
            strict_validation=options.strict_validation,
        )

        # Log inicial se verbose
        if options.verbose:
            logger.info("\n" + "=" * 60)
            logger.info("Salvando animação: %s", file_path.name)
            logger.info("=" * 60)
            logger.info("Configurações:")
            logger.info("  • FPS: %d", options.fps)
            logger.info("  • DPI: %d", dpi)
            logger.info("  • Qualidade: %s", options.quality)
            logger.info("  • Codec: %s", writer.codec)
            logger.info("  • Bitrate: %d kbps", writer.bitrate)
            if self._ffmpeg_version:
                logger.info("  • FFmpeg: %s", self.version_string)
            logger.info("=" * 60)
            logger.info("Processando frames...")

        # Preparar argumentos para save
        save_kwargs: Dict[str, Any] = {"writer": writer, "dpi": dpi}

        # Configurar callback de progresso
        if options.verbose or options.progress_callback is not None:
            callback = self._create_verbose_callback(options.progress_callback)
            save_kwargs["progress_callback"] = callback

        # Salvar animação
        try:
            animation.save(str(file_path), **save_kwargs)
        except TypeError as e:
            # Fallback para versões antigas sem progress_callback
            if "progress_callback" in str(e):
                logger.warning(
                    "Versão do Matplotlib não suporta progress_callback, "
                    "salvando sem callback..."
                )
                save_kwargs.pop("progress_callback", None)
                animation.save(str(file_path), **save_kwargs)
            else:
                raise
        except Exception as e:
            logger.error("Erro ao salvar animação: %s", e)
            raise

        # Verificar resultado
        if not file_path.exists():
            raise RuntimeError(f"Arquivo não foi criado: {file_path}")

        file_size = file_path.stat().st_size / (1024 * 1024)  # MB

        if options.verbose:
            logger.info("=" * 60)
            logger.info("✓ Vídeo salvo com sucesso!")
            logger.info("=" * 60)
            logger.info("Arquivo: %s", file_path.name)
            logger.info("Caminho completo: %s", file_path.absolute())
            logger.info("Tamanho: %.2f MB", file_size)
            logger.info("=" * 60 + "\n")

        return str(file_path.absolute())

    @contextmanager
    def temporary_config(
        self, ffmpeg_path: Optional[str] = None, strict_mode: Optional[bool] = None
    ):
        """
        Context manager para configurações temporárias (thread-safe).

        Args:
            ffmpeg_path: Caminho temporário do FFmpeg
            strict_mode: Modo strict temporário

        Example:
            >>> with config.temporary_config(ffmpeg_path='/tmp/ffmpeg'):
            ...     config.save_animation(ani, 'video.mp4')
        """
        with self._lock:
            # Guardar estado atual
            old_path = self._ffmpeg_path
            old_version = self._ffmpeg_version
            old_cache = self._codec_cache
            old_strict = self._strict_mode

            try:
                if ffmpeg_path is not None:
                    self.set_ffmpeg_path(ffmpeg_path)
                if strict_mode is not None:
                    self._strict_mode = strict_mode
                yield self
            finally:
                # Restaurar estado
                self._ffmpeg_path = old_path
                self._ffmpeg_version = old_version
                self._codec_cache = old_cache
                self._strict_mode = old_strict
                if old_path:
                    plt.rcParams["animation.ffmpeg_path"] = old_path


# ============================================================================
# Singleton Thread-Safe
# ============================================================================


class FFmpegConfigSingleton:
    """
    Singleton thread-safe para configuração global.

    Usado para evitar problemas com estado global em ambientes
    multi-thread ou testes paralelos.
    """

    _instance: Optional[FFmpegConfig] = None
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def get_instance(cls, **kwargs) -> FFmpegConfig:
        """
        Retorna instância singleton (thread-safe).

        Args:
            **kwargs: Argumentos para FFmpegConfig (apenas na primeira criação)

        Returns:
            FFmpegConfig: Instância única
        """
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = FFmpegConfig(**kwargs)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reseta a instância singleton.

        Útil para testes.
        """
        with cls._lock:
            cls._instance = None


# ============================================================================
# Funções de Conveniência
# ============================================================================


def configurar_ffmpeg(caminho: Optional[str] = None, strict_mode: bool = False) -> bool:
    """
    Configura o FFmpeg (usando singleton thread-safe).

    Args:
        caminho: Caminho para o FFmpeg (None = auto-detectar)
        strict_mode: Se True, não permite fallbacks

    Returns:
        bool: True se configurado com sucesso

    Example:
        >>> configurar_ffmpeg()  # Auto-detecta
        >>> configurar_ffmpeg('/usr/bin/ffmpeg')  # Caminho manual
    """
    config = FFmpegConfigSingleton.get_instance(strict_mode=strict_mode)

    if caminho:
        try:
            config.set_ffmpeg_path(caminho)
            return True
        except (FFmpegNotFoundError, ValueError) as e:
            logger.error("Erro ao configurar FFmpeg: %s", e)
            return False
    else:
        return config.auto_detect_ffmpeg()


def criar_writer(fps: int = 20, quality: str = "high", **kwargs) -> FFMpegWriter:
    """
    Cria um writer FFmpeg (usando singleton).

    Args:
        fps: Frames por segundo
        quality: Qualidade ('low', 'medium', 'high', 'ultra')
        **kwargs: Argumentos adicionais para create_writer

    Returns:
        FFMpegWriter: Writer configurado

    Example:
        >>> writer = criar_writer(fps=30, quality='ultra')
    """
    config = FFmpegConfigSingleton.get_instance()
    return config.create_writer(fps=fps, quality=quality, **kwargs)


def salvar_animacao(animation: FuncAnimation, filename: str, **kwargs) -> str:
    """
    Salva uma animação (usando singleton).

    Args:
        animation: Objeto FuncAnimation
        filename: Nome do arquivo
        **kwargs: Argumentos adicionais (SaveOptions ou direto)

    Returns:
        str: Caminho do arquivo salvo

    Example:
        >>> caminho = salvar_animacao(ani, 'video.mp4', fps=30, quality='high')
    """
    config = FFmpegConfigSingleton.get_instance()
    return config.save_animation(animation, filename, **kwargs)


def obter_config_global() -> FFmpegConfig:
    """
    Retorna a instância de configuração singleton.

    Returns:
        FFmpegConfig: Instância de configuração
    """
    return FFmpegConfigSingleton.get_instance()


# ============================================================================
# Exemplo de Uso
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Módulo FFmpeg Config para Matplotlib")
    print("=" * 70)
    print("\n" + "=" * 70)
    print("EXEMPLO DE USO:")
    print("=" * 70)

    exemplo_uso = """
# 1. Configuração básica com modo strict
from ffmpeg_config_improved import FFmpegConfig, SaveOptions

config = FFmpegConfig(strict_mode=True)  # Fail-fast, sem fallbacks

# 2. Verificar versão
print(f"FFmpeg versão: {config.version_string}")

# 3. Listar codecs disponíveis
codecs = config.get_available_codecs()
print(f"Codecs: {len(codecs)}")

# 4. Refresh manual do cache
config.refresh_codec_cache()

# 5. Usar SaveOptions (melhor API)
options = SaveOptions(
    fps=30,
    quality='ultra',
    verbose=True,
    check_disk_space=True,
    strict_validation=True
)

caminho = config.save_animation(animacao, 'video.mp4', options=options)

# 6. Estimativa de tamanho
from ffmpeg_config_improved import DiskSpaceValidator, Quality

size = DiskSpaceValidator.estimate_video_size(
    duration=60,  # segundos
    fps=30,
    quality=Quality.HIGH,
    resolution=(1920, 1080)
)
print(f"Tamanho estimado: {size:.1f} MB")

# 7. Context manager thread-safe
with config.temporary_config(strict_mode=False):
    config.save_animation(ani, 'temp.mp4')

# 8. Funções de conveniência (singleton único)
from ffmpeg_config_improved import configurar_ffmpeg, salvar_animacao

configurar_ffmpeg(strict_mode=True)
salvar_animacao(ani, 'video.mp4', quality='ultra', check_disk_space=True)
"""

    print(exemplo_uso)

    # Teste de detecção
    print("\n" + "=" * 70)
    print("TESTANDO DETECÇÃO AUTOMÁTICA...")
    print("=" * 70)

    try:
        config = FFmpegConfig()

        if config.configured:
            print("\n✓ FFmpeg configurado com sucesso!")
            print(f"  Caminho: {config.ffmpeg_path}")
            print(f"  Versão: {config.version_string}")

            # Testar consulta de codecs
            try:
                codecs = config.get_available_codecs()
                print(f"\n✓ Codecs detectados: {len(codecs)}")
                print(f"  Usando fallback: {config.using_fallback_codecs}")

                exemplos = list(sorted(codecs))[:8]
                print(f"  Exemplos: {', '.join(exemplos)}")

            except Exception as e:
                print(f"\n✗ Erro ao consultar codecs: {e}")
        else:
            print("\n✗ FFmpeg não encontrado.")
            print("  Use: config.set_ffmpeg_path('/caminho/para/ffmpeg')")

    except Exception as e:
        print(f"\n✗ Erro: {e}")

    print("\n" + "=" * 70)
    print("Módulo pronto para uso!")
    print("=" * 70)
