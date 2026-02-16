"""
Testes básicos para FFmpegConfig
"""

import warnings

import matplotlib.pyplot as plt
import pytest
from matplotlib.animation import FuncAnimation

from ffmpeg_matplotlib import __version__
from ffmpeg_matplotlib.config import (FFmpegConfig, FFmpegNotConfiguredError,
                                      configurar_ffmpeg)

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")


class TestFFmpegConfigInit:
    """Testes de inicialização"""

    def test_config_without_auto_detect(self):
        """Testa criação sem auto-detecção"""
        config = FFmpegConfig(auto_detect=False)
        assert not config.configured

    def test_config_has_version_property(self):
        """Testa que config tem propriedade version"""
        config = FFmpegConfig(auto_detect=False)
        assert hasattr(config, "version")
        assert hasattr(config, "version_string")


class TestFFmpegConfigProperties:
    """Testes de propriedades"""

    def test_configured_property(self):
        """Testa propriedade configured"""
        config = FFmpegConfig(auto_detect=False)
        assert isinstance(config.configured, bool)
        assert not config.configured

    def test_ffmpeg_path_property(self):
        """Testa propriedade ffmpeg_path"""
        config = FFmpegConfig(auto_detect=False)
        assert config.ffmpeg_path is None

    def test_version_string(self):
        """Testa version_string com FFmpeg não configurado"""
        config = FFmpegConfig(auto_detect=False)
        assert config.version_string == "Desconhecida"


class TestSaveAnimation:
    """Testes de salvamento de animação"""

    def test_save_animation_not_configured(self):
        """Testa que salvar sem configurar lança exceção"""
        config = FFmpegConfig(auto_detect=False)

        with pytest.raises(FFmpegNotConfiguredError):
            fig, ax = plt.subplots()
            (line,) = ax.plot([], [])

            def update(frame):
                return (line,)

            ani = FuncAnimation(fig, update, frames=10)
            try:
                config.save_animation(ani, "test.mp4")
            finally:
                plt.close(fig)
                del ani


class TestConvenienceFunctions:
    """Testes de funções de conveniência"""

    def test_configurar_ffmpeg_exists(self):
        """Testa que função configurar_ffmpeg existe"""
        assert callable(configurar_ffmpeg)

    def test_configurar_ffmpeg_returns_bool(self):
        """Testa que configurar_ffmpeg retorna bool"""
        result = configurar_ffmpeg()
        assert isinstance(result, bool)


class TestVersion:
    """Testes de versão do pacote"""

    def test_package_has_version(self):
        """Testa que pacote tem __version__"""
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_version_format(self):
        """Testa formato da versão"""
        version = __version__
        # Versão deve ser X.Y.Z
        parts = version.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)


# Teste simples para rodar primeiro
def test_import_works():
    """Testa que o pacote pode ser importado"""
    import ffmpeg_matplotlib

    assert ffmpeg_matplotlib is not None
