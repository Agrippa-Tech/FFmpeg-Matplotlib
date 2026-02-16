# Módulo FFmpeg para Matplotlib

Módulo Python reutilizável para configuração e salvamento automático de animações Matplotlib usando FFmpeg, com detecção inteligente de sistema, presets de qualidade, validações robustas e funcionalidades avançadas.

##  Sobre

Este projeto oferece uma solução simplificada e profissional para salvar animações do Matplotlib em formato de vídeo. O módulo elimina a necessidade de configuração manual repetitiva do FFmpeg, fornecendo detecção automática do sistema, presets de qualidade, feedback visual durante o processo de renderização e validações inteligentes.

##  Implementações Recentes
# ffmpeg-matplotlib

[![Testes](https://img.shields.io/badge/testes-11%20passando-brightgreen)](https://github.com/seu-usuario/matplotlib-ffmpeg)
[![Cobertura](https://img.shields.io/badge/cobertura-42%25-yellow)](https://github.com/seu-usuario/matplotlib-ffmpeg)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/)
[![Licença](https://img.shields.io/badge/licença-MIT-green)](LICENSE)

Integração simplificada do FFmpeg para animações Matplotlib com detecção automática, presets de qualidade e validação robusta.

---

## Início Rápido

```python
from matplotlib.animation import FuncAnimation
from ffmpeg_matplotlib import configurar_ffmpeg, salvar_animacao

# Configurar uma vez
configurar_ffmpeg()

# Criar animação
ani = FuncAnimation(fig, update, frames=100)

# Salvar vídeo
salvar_animacao(ani, 'saida.mp4')
```

---

## Instalação

```bash
pip install ffmpeg-matplotlib
```

**Requisitos:**
- Python 3.8+
- Matplotlib ≥ 3.1.0
- NumPy ≥ 1.18.0
- FFmpeg instalado no sistema

---

## Funcionalidades

### Principais
- **Detecção automática**: Encontra FFmpeg automaticamente em Windows, macOS e Linux
- **Presets de qualidade**: `low`, `medium`, `high`, `ultra` com bitrate/DPI otimizados
- **Type-safe**: Type hints completos com marcador `py.typed`
- **Thread-safe**: Padrão singleton com locks apropriados
- **Zero configuração**: Funciona imediatamente

### Avançadas
- **Validação de codec**: Verifica disponibilidade antes de renderizar
- **Verificação de espaço**: Previne falhas por armazenamento insuficiente
- **Callbacks de progresso**: Acompanha progresso de renderização
- **Modo strict**: Fail-fast sem fallbacks para produção
- **Context managers**: Configurações temporárias com restauração automática
- **Gerenciamento de cache**: Cache de codecs com TTL e refresh manual

---

## API

### Uso Básico

```python
from ffmpeg_matplotlib import configurar_ffmpeg, salvar_animacao

# Auto-detectar FFmpeg
configurar_ffmpeg()

# Salvar com padrões (alta qualidade, 20 fps)
salvar_animacao(ani, 'video.mp4')

# Customizar qualidade e fps
salvar_animacao(ani, 'video.mp4', quality='ultra', fps=30)
```

### Configuração Avançada

```python
from ffmpeg_matplotlib import FFmpegConfig
from ffmpeg_matplotlib.config import SaveOptions

config = FFmpegConfig(strict_mode=True)

options = SaveOptions(
    fps=30,
    quality='ultra',
    codec='libx264',
    verbose=True,
    check_disk_space=True,
    validate_codec=True,
    strict_validation=True
)

config.save_animation(ani, 'video.mp4', options=options)
```

### Seleção de Codec

```python
config = FFmpegConfig()

# Verificar codecs disponíveis
codecs = config.get_available_codecs()

# Validar codec específico
if config.validate_codec('h264_nvenc', strict=False):
    codec = 'h264_nvenc'  # Aceleração GPU
else:
    codec = 'libx264'     # Fallback CPU

salvar_animacao(ani, 'video.mp4', codec=codec)
```

### Estimativa de Espaço em Disco

```python
from ffmpeg_matplotlib.config import DiskSpaceValidator, Quality

tamanho_mb = DiskSpaceValidator.estimate_video_size(
    duration=60,
    fps=30,
    quality=Quality.HIGH,
    resolution=(1920, 1080)
)

print(f"Tamanho estimado: {tamanho_mb:.1f} MB")
```

### Acompanhamento de Progresso

```python
def progresso(frame_atual: int, total_frames: int):
    percentual = (frame_atual / total_frames) * 100
    print(f"Renderizando: {percentual:.1f}%")

salvar_animacao(ani, 'video.mp4', progress_callback=progresso)
```

---

## Presets de Qualidade

| Qualidade | Bitrate | DPI | Caso de Uso |
|-----------|---------|-----|-------------|
| `low` | 1500 kbps | 72 | Previews rápidos |
| `medium` | 3000 kbps | 100 | Compartilhamento web |
| `high` | 5000 kbps | 150 | Alta qualidade (padrão) |
| `ultra` | 8000 kbps | 200 | Máxima qualidade |

---

## Arquitetura

### Hierarquia de Classes

```
FFmpegConfig
├── FFmpegDetector      # Detecção de caminhos específicos do sistema
├── FFmpegValidator     # Validação de executável e codecs
└── DiskSpaceValidator  # Verificação de disponibilidade de armazenamento
```

### Classes Principais

**FFmpegConfig**
- `auto_detect_ffmpeg()`: Detectar FFmpeg no sistema
- `set_ffmpeg_path()`: Configuração manual de caminho
- `save_animation()`: Salvar com pipeline completo de validação
- `get_available_codecs()`: Consultar codecs suportados
- `validate_codec()`: Verificar disponibilidade de codec
- `temporary_config()`: Context manager para configurações temporárias

**SaveOptions** (dataclass)
- Container de configuração type-safe
- Validação automática na inicialização
- Suporta todos os parâmetros do FFmpegWriter

**Quality** (enum)
- Presets de qualidade type-safe
- Encapsula combinações bitrate/DPI

### Hierarquia de Erros

```
FFmpegError
├── FFmpegNotFoundError
├── FFmpegNotConfiguredError
├── InvalidCodecError
├── InvalidQualityError
├── InsufficientDiskSpaceError
└── StrictModeError
```

---

## Exemplos

### Modo Strict (Produção)

```python
from ffmpeg_matplotlib import configurar_ffmpeg, salvar_animacao

# Fail-fast, sem fallbacks
configurar_ffmpeg(strict_mode=True)

salvar_animacao(
    ani,
    'video.mp4',
    quality='high',
    validate_codec=True,
    strict_validation=True,
    check_disk_space=True
)
```

### Context Manager

```python
from ffmpeg_matplotlib import FFmpegConfig

config = FFmpegConfig()

# Configuração temporária (thread-safe)
with config.temporary_config(strict_mode=False):
    config.save_animation(ani, 'teste.mp4')
# Configurações originais restauradas
```

### Aceleração por GPU

```python
from ffmpeg_matplotlib import FFmpegConfig

config = FFmpegConfig()
codecs = config.get_available_codecs()

if 'h264_nvenc' in codecs:
    print("✓ Codificação NVIDIA GPU disponível")
    codec = 'h264_nvenc'
    bitrate = 8000
else:
    print("⚠ Voltando para codificação CPU")
    codec = 'libx264'
    bitrate = 5000

salvar_animacao(ani, 'video.mp4', codec=codec, bitrate=bitrate)
```

---

## Desenvolvimento

### Configuração

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/matplotlib-ffmpeg.git
cd matplotlib-ffmpeg

# Instalar em modo desenvolvimento
pip install -e ".[dev]"

# Executar testes
pytest

# Verificar cobertura
pytest --cov=ffmpeg_matplotlib --cov-report=html
```

### Testes

```bash
# Executar todos os testes
pytest

# Saída detalhada
pytest -v

# Com cobertura
pytest --cov

# Arquivo de teste específico
pytest tests/test_config.py
```

### Qualidade de Código

```bash
# Formatar código
black src/ tests/
isort src/ tests/

# Linting
flake8 src/ tests/ --max-line-length=100

# Verificação de tipos
mypy src/
```

### Build

```bash
# Instalar ferramentas de build
pip install build twine

# Criar distribuição
python -m build

# Upload para PyPI (teste)
twine upload --repository testpypi dist/*

# Upload para PyPI (produção)
twine upload dist/*
```

---

## Solução de Problemas

### FFmpeg não encontrado

```python
# Configuração manual
from ffmpeg_matplotlib import configurar_ffmpeg

configurar_ffmpeg('/caminho/para/ffmpeg')
```

### Codec não disponível

```python
# Listar codecs disponíveis
from ffmpeg_matplotlib import FFmpegConfig

config = FFmpegConfig()
print(sorted(config.get_available_codecs()))

# Usar fallback
salvar_animacao(ani, 'video.mp4', codec='libx264')
```

### Espaço em disco insuficiente

```python
# Desabilitar verificação (não recomendado)
salvar_animacao(ani, 'video.mp4', check_disk_space=False)

# Ou reduzir qualidade
salvar_animacao(ani, 'video.mp4', quality='low', fps=15)
```

### Problemas de reprodução em dispositivos móveis

Alguns arquivos MP4 podem não reproduzir em dispositivos móveis devido ao posicionamento de metadados. Corrija com:

```bash
ffmpeg -i entrada.mp4 -c copy -movflags +faststart saida.mp4
```

---

## Detalhes Técnicos

### Thread Safety

- Padrão singleton com `threading.RLock`
- Context managers para configurações temporárias
- Cache protegido com locks

### Detecção de Codecs

- Analisa saída de `ffmpeg -codecs`
- Regex suporta hífens (`h264-nvenc`, `hevc-nvenc`)
- Cache com TTL (1 hora padrão)
- Fallback para lista de codecs comuns

### Resolução de Caminhos

- `shutil.which()` para comandos
- Suporte a caminhos absolutos/relativos
- Expansão de til (`~`)
- Caminhos de busca específicos do sistema

---

## Limitações

- Requer FFmpeg instalado no sistema
- Callback de progresso requer Matplotlib ≥ 3.4
- Estimativa de espaço em disco é aproximada
- Cache de codecs expira após 1 hora
- Singleton pode causar problemas em testes paralelos (use `reset_instance()`)

---

## Roadmap

- [ ] Suporte automático a `-movflags +faststart`
- [ ] Presets de qualidade adicionais (4K, 8K, mobile)
- [ ] Suporte a codecs VP9, AV1, HEVC
- [ ] Exportação GIF
- [ ] Processamento em lote
- [ ] Ferramenta de configuração GUI
- [ ] Integração Plotly/Bokeh
- [ ] Presets específicos de plataforma (YouTube, Instagram)

---

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie uma branch de feature
3. Escreva testes para nova funcionalidade
4. Garanta que todos os testes passem (`pytest`)
5. Formate o código (`black`, `isort`)
6. Submeta um pull request

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

---

## Licença

Licença MIT - veja [LICENSE](LICENSE) para detalhes.

Copyright (c) 2026 Seu Nome


---


**Status do Projeto:** Desenvolvimento ativo | Pronto para produção

**Versão:** 2.1.0 | **Python:** 3.8+ | **Matplotlib:** 3.1+ | **FFmpeg:** 3.4+
* **Modo Strict**: Fail-fast sem fallbacks para ambientes de produção
* **Cache de Codecs**: Consulta otimizada com TTL (1 hora) e refresh manual
* **Validação de Versão**: Detecção automática da versão do FFmpeg
* **Estimativa de Tamanho**: Cálculo prévio do tamanho do vídeo
* **Validação de Espaço**: Verificação automática de espaço em disco
* **SaveOptions Dataclass**: API melhorada e type-safe
* **Quality Enum**: Presets tipados com segurança
* **Thread-Safe**: Singleton e locks para ambientes concorrentes
* **Context Manager**: Configurações temporárias com `temporary_config()`
* **Path Resolution**: Sistema robusto de detecção de caminhos
* **Regex Corrigido**: Suporte a codecs com hífens (h264_nvenc, hevc_nvenc)

##  Funcionalidades

### Recursos Básicos
* **Detecção Automática**: Identifica e configura o FFmpeg automaticamente no sistema
* **Multiplataforma**: Funciona em Windows, macOS e Linux
* **Presets de Qualidade**: Configurações predefinidas (low, medium, high, ultra)
* **Feedback Visual**: Mensagens informativas sobre o progresso da renderização
* **Interface Simples**: Apenas 3 linhas de código para salvar uma animação
* **Tratamento de Erros**: Validações robustas e mensagens claras
* **Flexibilidade**: Uso funcional ou orientado a objetos
* **Metadados**: Suporte a informações personalizadas do vídeo

### Recursos Avançados
* **Validação de Codec**: Verifica se codec está disponível no FFmpeg instalado
* **Fallback Inteligente**: Lista de codecs comuns quando detecção falha
* **Progress Callback**: Callback customizável para tracking de progresso
* **Disk Space Check**: Validação de espaço disponível antes de renderizar
* **Extensão Automática**: Adiciona `.mp4` automaticamente se necessário
* **Criação de Diretórios**: Cria estrutura de pastas automaticamente
* **Cache Expirado**: TTL de 1 hora para cache de codecs
* **Logging Configurável**: Sistema de logs detalhado com níveis ajustáveis

##  Estrutura do Módulo

O módulo oferece:

1. **Classe FFmpegConfig**: Gerenciamento completo da configuração
2. **Funções de Conveniência**: Atalhos para uso rápido
3. **Detecção Inteligente**: Busca automática em locais comuns do sistema
4. **Presets Otimizados**: Configurações balanceadas para cada caso de uso
5. **Documentação Inline**: Docstrings detalhadas em todos os métodos
6. **Enums e Dataclasses**: API moderna e type-safe
7. **Validadores Separados**: Separação de concerns (Detector, Validator)
8. **Exceções Customizadas**: Hierarquia clara de erros

##  Requisitos

* Python 3.8 ou superior
* Matplotlib ≥ 3.1.0 - `pip install matplotlib`
* NumPy ≥ 1.18.0 - `pip install numpy`
* FFmpeg instalado no sistema

##  Instalação

### 1. Instalar FFmpeg

#### Windows
```bash
# Baixe em: https://www.gyan.dev/ffmpeg/builds/
# Extraia para C:\ffmpeg
# Adicione C:\ffmpeg\bin ao PATH (opcional)
```

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### 2. Instalar o Pacote

#### Via pip (quando publicado)
```bash
pip install matplotlib-ffmpeg
```

#### Via desenvolvimento
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/matplotlib-ffmpeg.git
cd matplotlib-ffmpeg

# Instale em modo desenvolvimento
pip install -e .
```

### 3. Instalar Dependências de Desenvolvimento

```bash
pip install -e ".[dev]"
```

##  Como Utilizar

### Modo Básico (Recomendado)

```python
from matplotlib.animation import FuncAnimation
from ffmpeg_matplotlib import configurar_ffmpeg, salvar_animacao

# 1. Configurar FFmpeg (uma vez no início)
configurar_ffmpeg()

# 2. Criar sua animação
ani = FuncAnimation(fig, update, frames=200, interval=50)

# 3. Salvar o vídeo
salvar_animacao(ani, 'minha_animacao.mp4')
```

### Modo com SaveOptions (Recomendado para Configurações Avançadas)

```python
from ffmpeg_matplotlib import FFmpegConfig, SaveOptions

# Configurar
config = FFmpegConfig()

# Criar opções de salvamento
options = SaveOptions(
    fps=30,
    quality='ultra',
    codec='libx264',
    verbose=True,
    check_disk_space=True,
    validate_codec=True,
    strict_validation=False  # True = falha se codec inválido
)

# Salvar com opções
caminho = config.save_animation(ani, 'video.mp4', options=options)
print(f"Salvo em: {caminho}")
```

### Modo Strict (Produção)

```python
from ffmpeg_matplotlib import configurar_ffmpeg, salvar_animacao

# Modo strict: sem fallbacks, fail-fast
configurar_ffmpeg(strict_mode=True)

# SaveOptions com validação estrita
salvar_animacao(
    ani, 
    'video.mp4',
    quality='high',
    validate_codec=True,
    strict_validation=True,  # Falha se codec não disponível
    check_disk_space=True    # Falha se espaço insuficiente
)
```

### Modo Avançado com Context Manager

```python
from ffmpeg_matplotlib import FFmpegConfig

config = FFmpegConfig()

# Configuração temporária (thread-safe)
with config.temporary_config(ffmpeg_path='/tmp/ffmpeg', strict_mode=True):
    config.save_animation(ani, 'video_temp.mp4')
# Configuração anterior é restaurada automaticamente
```

### Estimativa de Tamanho de Arquivo

```python
from ffmpeg_matplotlib.config import DiskSpaceValidator, Quality

# Estimar tamanho antes de renderizar
tamanho_mb = DiskSpaceValidator.estimate_video_size(
    duration=60,  # segundos
    fps=30,
    quality=Quality.HIGH,
    resolution=(1920, 1080)
)

print(f"Tamanho estimado: {tamanho_mb:.1f} MB")

# Verificar espaço disponível
from pathlib import Path
disk_info = DiskSpaceValidator.check_space(
    Path('video.mp4'),
    estimated_size=tamanho_mb
)

if disk_info.has_space:
    print(f"✓ Espaço suficiente: {disk_info.available_mb:.1f} MB disponíveis")
else:
    print(f"✗ Espaço insuficiente! Necessário: {disk_info.required_mb:.1f} MB")
```

### Gerenciamento de Cache de Codecs

```python
from ffmpeg_matplotlib import FFmpegConfig

config = FFmpegConfig()

# Obter codecs disponíveis (usa cache)
codecs = config.get_available_codecs()
print(f"Codecs detectados: {len(codecs)}")

# Verificar se usando fallback
if config.using_fallback_codecs:
    print("⚠ Usando lista de fallback - detecção falhou")

# Forçar refresh do cache (útil após atualizar FFmpeg)
config.refresh_codec_cache()
```

### Progress Callback Customizado

```python
def meu_progresso(current_frame: int, total_frames: int):
    progresso = (current_frame / total_frames) * 100
    print(f"Renderizando: {progresso:.1f}% completo")

salvar_animacao(
    ani,
    'video.mp4',
    progress_callback=meu_progresso,
    verbose=True  # Combina com logging interno
)
```

### Validação Manual de Codec

```python
from ffmpeg_matplotlib import FFmpegConfig

config = FFmpegConfig()

# Verificar codec sem lançar exceção
if config.validate_codec('h264_nvenc', strict=False):
    print("✓ Codec NVENC disponível (GPU)")
    codec = 'h264_nvenc'
else:
    print("✗ NVENC não disponível, usando CPU")
    codec = 'libx264'

# Salvar com codec validado
salvar_animacao(ani, 'video.mp4', codec=codec)
```

##  Parâmetros e Opções

### SaveOptions - Todos os Parâmetros

```python
from ffmpeg_matplotlib.config import SaveOptions

options = SaveOptions(
    fps=20,                      # Frames por segundo (int)
    dpi=None,                    # DPI (None = automático por qualidade)
    quality='high',              # Qualidade: 'low', 'medium', 'high', 'ultra'
    metadata=None,               # Dict de metadados (opcional)
    verbose=True,                # Logging detalhado (bool)
    progress_callback=None,      # Função callback (frame, total) -> None
    codec='libx264',             # Codec de vídeo (str)
    bitrate=None,                # Bitrate em kbps (None = automático)
    validate_codec=True,         # Validar se codec existe (bool)
    strict_validation=False,     # Falhar se codec inválido (bool)
    check_disk_space=True        # Validar espaço em disco (bool)
)
```

### Comandos e Opções da API Funcional

* **configurar_ffmpeg()**: Detecta FFmpeg automaticamente
* **configurar_ffmpeg(caminho)**: Define caminho manual
* **configurar_ffmpeg(strict_mode=True)**: Modo strict sem fallbacks
* **salvar_animacao()**: Salva vídeo com configurações padrão
* **quality**: 'low', 'medium', 'high', 'ultra'
* **fps**: Taxa de quadros (15, 20, 24, 30, 60)
* **dpi**: Resolução da renderização (72, 100, 150, 200, 300)
* **codec**: 'libx264', 'libx265', 'h264_nvenc', 'mpeg4', etc.

##  Presets de Qualidade

O módulo oferece 4 presets otimizados:

```
┌──────────┬─────────┬─────┬────────────────────────┐
│ Qualidade│ Bitrate │ DPI │ Uso Recomendado        │
├──────────┼─────────┼─────┼────────────────────────┤
│ low      │ 1500    │ 72  │ Previews rápidos       │
│ medium   │ 3000    │ 100 │ Compartilhamento web   │
│ high     │ 5000    │ 150 │ Alta qualidade (padrão)│
│ ultra    │ 8000    │ 200 │ Máxima qualidade       │
└──────────┴─────────┴─────┴────────────────────────┘
```

**Observação:** Os valores de DPI são aplicados automaticamente quando `dpi=None` em SaveOptions.

## 🔍 Tipos de Configuração Suportadas

O sistema aceita diferentes formas de configuração:

* Detecção automática do sistema
* Caminho manual do executável
* FFmpeg no PATH do sistema
* Configuração por variável de ambiente
* Path resolution robusto (suporta `~`, caminhos relativos, etc.)

##  Características Técnicas

### Classe `FFmpegConfig`

**Métodos Principais:**

* `auto_detect_ffmpeg()`: Detecta FFmpeg em locais comuns
* `set_ffmpeg_path()`: Define caminho manualmente (com validação)
* `create_writer()`: Cria writer com configurações personalizadas
* `save_animation()`: Salva animação com feedback visual
* `get_available_codecs()`: Retorna conjunto de codecs disponíveis
* `validate_codec()`: Valida se codec está disponível
* `refresh_codec_cache()`: Atualiza cache de codecs manualmente
* `temporary_config()`: Context manager para configurações temporárias

**Propriedades:**

* `configured`: bool - Se FFmpeg está configurado
* `ffmpeg_path`: Optional[str] - Caminho do executável
* `version`: Optional[Tuple[int, int, int]] - Versão do FFmpeg
* `version_string`: str - Versão formatada (ex: "4.4.2")
* `using_fallback_codecs`: bool - Se está usando fallback de codecs
* `strict_mode`: bool - Se modo strict está ativo

**Configurações Padrão:**

* Codec padrão: H.264 (libx264)
* FPS padrão: 20 quadros/segundo
* Bitrate padrão: 5000 kbps (quality='high')
* DPI padrão: 150 (quality='high')
* Formato padrão: MP4

### Classes Auxiliares

**FFmpegDetector:**
* `auto_detect()`: Detecta FFmpeg no sistema
* `find_in_path()`: Busca no PATH
* `get_system_specific_paths()`: Caminhos por SO
* `resolve_path()`: Resolução robusta de caminhos

**FFmpegValidator:**
* `validate_executable()`: Valida executável FFmpeg
* `query_available_codecs()`: Consulta codecs disponíveis
* `parse_version()`: Extrai versão do FFmpeg
* `parse_codec_line()`: Parse de linha de codec (suporta hífens)

**DiskSpaceValidator:**
* `get_available_space()`: Espaço disponível em MB
* `estimate_video_size()`: Estima tamanho do vídeo
* `check_space()`: Verifica se há espaço suficiente

### Enums

**Quality:**
* `Quality.LOW`: 1500 kbps, 72 DPI
* `Quality.MEDIUM`: 3000 kbps, 100 DPI
* `Quality.HIGH`: 5000 kbps, 150 DPI
* `Quality.ULTRA`: 8000 kbps, 200 DPI

### Exceções Customizadas

* `FFmpegError`: Base para erros do módulo
* `FFmpegNotFoundError`: FFmpeg não encontrado
* `FFmpegNotConfiguredError`: FFmpeg não configurado antes do uso
* `InvalidCodecError`: Codec não disponível
* `InvalidQualityError`: Preset de qualidade inválido
* `InvalidFileExtensionError`: Extensão não suportada
* `InsufficientDiskSpaceError`: Espaço em disco insuficiente
* `StrictModeError`: Erro em modo strict (fallback não permitido)

##  Exemplo de Uso Completo

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from ffmpeg_matplotlib import (
    configurar_ffmpeg, 
    salvar_animacao
)
from ffmpeg_matplotlib.config import (
    SaveOptions,
    DiskSpaceValidator,
    Quality
)

# 1. Configurar FFmpeg com modo strict
configurar_ffmpeg(strict_mode=True)

# 2. Criar figura
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(-1.5, 1.5)
ax.set_title('Animação de Onda Senoidal', fontsize=14, fontweight='bold')
ax.set_xlabel('x')
ax.set_ylabel('sin(x + t)')
ax.grid(True, alpha=0.3)
line, = ax.plot([], [], 'b-', linewidth=2)

# 3. Funções de animação
def init():
    line.set_data([], [])
    return line,

def update(frame):
    x = np.linspace(0, 2*np.pi, 200)
    y = np.sin(x + frame/10)
    line.set_data(x, y)
    return line,

# 4. Criar animação
ani = FuncAnimation(
    fig, 
    update, 
    init_func=init,
    frames=100, 
    interval=50, 
    blit=True
)

# 5. Estimar tamanho antes de salvar
tamanho_estimado = DiskSpaceValidator.estimate_video_size(
    duration=100/20,  # frames/fps = segundos
    fps=20,
    quality=Quality.HIGH,
    resolution=(1000, 600)
)
print(f"Tamanho estimado: {tamanho_estimado:.1f} MB")

# 6. Configurar opções de salvamento
options = SaveOptions(
    fps=20,
    quality='high',
    verbose=True,
    check_disk_space=True,
    validate_codec=True,
    metadata={'title': 'Onda Senoidal', 'artist': 'Meu Projeto'}
)

# 7. Salvar com diferentes qualidades
print("\n" + "="*60)
print("Gerando vídeos em diferentes qualidades...")
print("="*60)

# Preview rápido
salvar_animacao(ani, 'onda_preview.mp4', quality='low', verbose=False)
print("✓ Preview salvo (low quality)")

# Qualidade média para web
salvar_animacao(ani, 'onda_web.mp4', quality='medium', fps=24)
print("✓ Versão web salva (medium quality)")

# Alta qualidade com opções customizadas
caminho_final = salvar_animacao(ani, 'onda_final.mp4', options=options)
print(f"✓ Vídeo final salvo em: {caminho_final}")

# Ultra qualidade com callback de progresso
def progresso_callback(frame, total):
    if frame % 20 == 0:
        print(f"  → Renderizando: {frame}/{total} frames")

salvar_animacao(
    ani, 
    'onda_ultra.mp4',
    quality='ultra',
    fps=60,
    progress_callback=progresso_callback
)
print("✓ Versão ultra salva (ultra quality, 60 fps)")

print("\n" + "="*60)
print("✓ Todos os vídeos salvos com sucesso!")
print("="*60)
```

##  Exemplo Avançado: Validação de Codec com Fallback

```python
from ffmpeg_matplotlib import FFmpegConfig
from ffmpeg_matplotlib.config import SaveOptions

config = FFmpegConfig()

# Tentar usar codec de GPU (NVENC)
codecs_disponiveis = config.get_available_codecs()

if 'h264_nvenc' in codecs_disponiveis:
    print("✓ GPU NVENC disponível - usando aceleração de hardware")
    codec_escolhido = 'h264_nvenc'
    bitrate = 8000  # Pode usar bitrate maior com GPU
elif 'hevc_nvenc' in codecs_disponiveis:
    print("✓ GPU HEVC disponível - usando aceleração de hardware")
    codec_escolhido = 'hevc_nvenc'
    bitrate = 6000
else:
    print("⚠ GPU não disponível - usando codec de CPU")
    codec_escolhido = 'libx264'
    bitrate = 5000

# Salvar com codec otimizado
options = SaveOptions(
    fps=30,
    quality='ultra',
    codec=codec_escolhido,
    bitrate=bitrate,
    validate_codec=False  # Já validamos manualmente
)

config.save_animation(ani, 'video_otimizado.mp4', options=options)
```

##  Comparação: Antes vs Depois

### Código Tradicional (Repetitivo)

```python
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter

# Repetir em cada projeto
plt.rcParams['animation.ffmpeg_path'] = r'C:\Users\...\ffmpeg.exe'
writer = FFMpegWriter(fps=20, metadata=dict(artist='X'), 
                      bitrate=5000, codec='libx264')
ani.save('video.mp4', writer=writer, dpi=150)
# Sem feedback, sem tratamento de erros, sem validações
```

### Com Módulo FFmpeg Básico

```python
from ffmpeg_matplotlib import configurar_ffmpeg, salvar_animacao

configurar_ffmpeg()  # Uma vez
salvar_animacao(ani, 'video.mp4')  # Sempre
# ✓ Automático ✓ Feedback ✓ Validações
```

### Com Módulo FFmpeg Avançado

```python
from ffmpeg_matplotlib import configurar_ffmpeg, salvar_animacao
from ffmpeg_matplotlib.config import SaveOptions

configurar_ffmpeg(strict_mode=True)

options = SaveOptions(
    quality='ultra',
    check_disk_space=True,
    validate_codec=True,
    strict_validation=True
)

salvar_animacao(ani, 'video.mp4', options=options)
# ✓ Type-safe ✓ Validações robustas ✓ Fail-fast ✓ Thread-safe
```

**Redução de código: ~70% + Type Safety + Validações inteligentes**

##  Tratamento de Erros

O sistema possui validações para:

* FFmpeg não instalado ou não encontrado (`FFmpegNotFoundError`)
* Caminho inválido do executável (validação em `set_ffmpeg_path()`)
* Codec não disponível (`InvalidCodecError`)
* Qualidade inválida (`InvalidQualityError`)
* Espaço em disco insuficiente (`InsufficientDiskSpaceError`)
* FFmpeg não configurado antes do uso (`FFmpegNotConfiguredError`)
* Modo strict sem fallback (`StrictModeError`)
* Falha na renderização de frames (propagada do Matplotlib)
* Erro na gravação do arquivo (IO errors)
* Timeout em validações (configurável)
* Falta de permissões de escrita (OS errors)

### Exemplo de Tratamento

```python
from ffmpeg_matplotlib import FFmpegConfig
from ffmpeg_matplotlib.config import (
    FFmpegNotFoundError,
    InvalidCodecError,
    InsufficientDiskSpaceError
)

try:
    config = FFmpegConfig()
    config.save_animation(ani, 'video.mp4', codec='h264_nvenc')
    
except FFmpegNotFoundError as e:
    print(f"Erro: FFmpeg não encontrado - {e}")
    print("Instale o FFmpeg: https://ffmpeg.org/download.html")
    
except InvalidCodecError as e:
    print(f"Erro: Codec não disponível - {e}")
    print("Tente com codec='libx264' (padrão)")
    
except InsufficientDiskSpaceError as e:
    print(f"Erro: Espaço insuficiente - {e}")
    print("Libere espaço ou reduza a qualidade")
    
except Exception as e:
    print(f"Erro inesperado: {e}")
```

##  Limitações Conhecidas

* Requer FFmpeg instalado no sistema
* Não funciona com animações 3D complexas sem configuração adicional
* Tempo de renderização proporcional à quantidade de frames e qualidade
* Arquivos em qualidade 'ultra' podem ser muito grandes (use estimativa)
* Alguns codecs específicos requerem compilações especiais do FFmpeg
* Cache de codecs expira após 1 hora (configurável via `CODEC_CACHE_TTL`)
* Progress callback não funciona em versões antigas do Matplotlib (< 3.4)
* Validação de espaço em disco é estimativa (overhead pode variar)
* Thread-safety: singleton global pode causar race conditions em testes paralelos

##  Fluxo de Trabalho Recomendado

1. **Configuração Inicial**: Configure FFmpeg uma vez no início do projeto
2. **Desenvolvimento**: Teste sua animação com `plt.show()`
3. **Preview Rápido**: Salve com `quality='low'` para verificar resultado
4. **Estimativa**: Use `DiskSpaceValidator.estimate_video_size()` para planejar
5. **Ajustes**: Modifique parâmetros conforme necessário
6. **Validação**: Use `validate_codec()` para verificar disponibilidade
7. **Renderização Final**: Salve com `quality='high'` ou `'ultra'`
8. **Compartilhamento**: Use `quality='medium'` para arquivos menores
9. **Produção**: Use `strict_mode=True` e `check_disk_space=True`

##  Estrutura de Arquivos do Projeto

```
ffmpeg-matplotlib/
│
├── src/
│   └── ffmpeg_matplotlib/
│       ├── __init__.py          # Exports principais
│       ├── config.py            # Módulo principal
│       └── py.typed             # Marker para type hints
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures compartilhadas
│   ├── test_config.py           # Testes de configuração
│   └── test_detector.py         # Testes de detecção
│
├── examples/
│   ├── basic_usage.py           # Exemplo básico
│   └── heliocentric_system.py   # Exemplo avançado
│
├── .github/
│   └── workflows/
│       └── tests.yml            # CI/CD GitHub Actions
│
├── pyproject.toml               # Configuração do projeto
├── setup.py                     # Setup script
├── README.md                    # Este arquivo
├── LICENSE                      # Licença MIT
└── .gitignore                   # Arquivos ignorados
```

##  Solução de Problemas Comuns

### Erro: "FFmpeg não detectado"

```python
# Verifique se está instalado
import subprocess
subprocess.run(['ffmpeg', '-version'])

# Se não funcionar, configure manualmente
from ffmpeg_matplotlib import configurar_ffmpeg
configurar_ffmpeg(r'C:\caminho\completo\para\ffmpeg.exe')
```

### Erro: "RuntimeError: FFmpeg não configurado"

```python
# Sempre chame configurar_ffmpeg() antes de salvar
from ffmpeg_matplotlib import configurar_ffmpeg
configurar_ffmpeg()  # ← Não esqueça desta linha
salvar_animacao(ani, 'video.mp4')
```

### Erro: "InvalidCodecError: Codec não disponível"

```python
# Verifique codecs disponíveis
from ffmpeg_matplotlib import obter_config_global
config = obter_config_global()
codecs = config.get_available_codecs()
print(f"Codecs disponíveis: {sorted(codecs)}")

# Use codec genérico
salvar_animacao(ani, 'video.mp4', codec='libx264')  # Sempre funciona
```

### Erro: "InsufficientDiskSpaceError: Espaço insuficiente"

```python
# Desabilitar verificação (não recomendado)
salvar_animacao(ani, 'video.mp4', check_disk_space=False)

# Ou reduzir qualidade/fps
salvar_animacao(ani, 'video.mp4', quality='low', fps=15)
```

### Aviso: "Usando lista de fallback de codecs comuns"

```python
# Cache de codecs expirou ou detecção falhou
# Forçar refresh
from ffmpeg_matplotlib import obter_config_global
config = obter_config_global()
config.refresh_codec_cache()

# Ou usar modo strict (falha ao invés de fallback)
from ffmpeg_matplotlib import configurar_ffmpeg
configurar_ffmpeg(strict_mode=True)
```

### Vídeo muito grande

```python
# Use qualidade menor ou reduza parâmetros
salvar_animacao(ani, 'video.mp4', quality='medium', fps=15, dpi=100)

# Ou estime antes
from ffmpeg_matplotlib.config import DiskSpaceValidator, Quality
tamanho = DiskSpaceValidator.estimate_video_size(60, 30, Quality.LOW)
print(f"Low: {tamanho:.1f} MB")
```

### Renderização muito lenta

```python
# Reduza número de frames ou use preview
ani = FuncAnimation(..., frames=100)  # Menos frames
salvar_animacao(ani, 'preview.mp4', quality='low')  # Preview rápido

# Ou desabilite verbose
salvar_animacao(ani, 'video.mp4', verbose=False)
```

### Codec de GPU não funciona

```python
# Verifique se sua GPU/drivers suportam
from ffmpeg_matplotlib import FFmpegConfig
config = FFmpegConfig()

if config.validate_codec('h264_nvenc', strict=False):
    print("✓ NVENC disponível")
else:
    print("✗ NVENC não disponível - use libx264")
    # Fallback para CPU
    salvar_animacao(ani, 'video.mp4', codec='libx264')
```

##  Troubleshooting: Problema de Reprodução 

###  Vídeos MP4 que não reproduzem ou crasham

**Sintoma:**
- Vídeo faz upload no Google Drive com sucesso
- Reproduz no navegador (web player)
- **NÃO funciona** em dispositivos móveis ou players locais
- Trava após alguns segundos
- Erro de "arquivo corrompido"

**Causa:** Localização do "moov atom"

O FFmpeg, por padrão, coloca metadados estruturais no final do arquivo, causando problemas em dispositivos que não carregam o arquivo inteiro na memória.

**Solução 1: Corrigir arquivo já gerado (sem reencodar)**

```bash
ffmpeg -i video_problematico.mp4 -c copy -movflags +faststart video_corrigido.mp4
```

**Solução 2: Gerar arquivo correto desde o início**

```bash
ffmpeg -i entrada.mp4 -c:v libx264 -c:a aac -movflags +faststart saida.mp4
```

**Solução 3: Usar editor de vídeo online**

1. Faça upload do vídeo para um editor online
2. Faça edição mínima (ex: cortar 1 segundo)
3. Exporte o vídeo
4. Editor reescreverá a estrutura automaticamente

**Nota:** O módulo atual não adiciona `-movflags +faststart` automaticamente. Para adicionar esse suporte, seria necessário estender a classe `FFMpegWriter` ou usar `extra_args` no writer (se suportado pela versão do Matplotlib).

##  Informações Adicionais

### Formatos de Vídeo Suportados

* **MP4** (padrão, melhor compatibilidade)
* **AVI** (sem compressão, arquivos grandes)
* **MOV** (QuickTime)
* **MKV** (Matroska)
* **WebM** (requer codec VP9)

### Requisitos de Sistema

* **RAM**: Mínimo 2GB (recomendado 4GB+ para alta qualidade)
* **Disco**: Espaço livre para vídeos (use estimativa)
* **CPU**: Quanto mais rápida, menor o tempo de renderização
* **GPU**: Opcional (para codecs NVENC/QSV)

### Codecs Comuns

* **libx264**: H.264 (CPU) - padrão, melhor compatibilidade
* **libx265**: H.265/HEVC (CPU) - melhor compressão, mais lento
* **h264_nvenc**: H.264 (GPU NVIDIA) - rápido, requer GPU
* **hevc_nvenc**: H.265 (GPU NVIDIA) - rápido, melhor compressão
* **mpeg4**: MPEG-4 (CPU) - compatibilidade com players antigos
* **vp9**: VP9 (CPU) - para WebM

### Thread-Safety e Testes

O módulo é thread-safe, mas tenha cuidado ao:

* Usar singleton em testes paralelos (use `reset_instance()`)
* Modificar configuração global em threads concorrentes
* Cache de codecs compartilhado entre threads (protegido por lock)

```python
# Em testes, limpar singleton
from ffmpeg_matplotlib.config import FFmpegConfigSingleton
FFmpegConfigSingleton.reset_instance()

# Ou usar instância isolada
from ffmpeg_matplotlib import FFmpegConfig
config = FFmpegConfig()  # Instância própria, não singleton
```

##  Contribuições

Sugestões de melhorias e contribuições são bem-vindas! Áreas de interesse:

* Suporte a `-movflags +faststart` automático
* Mais presets de qualidade (4K, 8K, mobile)
* Suporte a outros codecs (VP9, AV1, HEVC)
* Exportação em formatos adicionais (GIF animado, WebM, AVI)
* Interface gráfica (GUI) para configuração
* Processamento em lote de múltiplas animações
* Compressão adaptativa baseada em conteúdo
* Integração com outras bibliotecas (Plotly, Bokeh, Seaborn)
* Presets específicos por plataforma (YouTube, Instagram, TikTok)
* Pipeline de pós-processamento (filters, watermarks)
* Suporte a áudio sincronizado

##  Casos de Uso

* **Cientistas de Dados**: Visualizações animadas de análises temporais
* **Pesquisadores**: Animações de simulações científicas
* **Educadores**: Material didático com animações explicativas
* **Desenvolvedores**: Demonstrações visuais de algoritmos
* **Artistas Digitais**: Criações generativas em movimento
* **Engenheiros**: Visualização de dados de sensores em tempo real
* **Analistas Financeiros**: Animações de mercados e tendências
* **Meteorologistas**: Visualização de previsões e modelos climáticos

## Objetivo

Simplificar o processo de salvamento de animações Matplotlib através da automação da configuração do FFmpeg, permitindo que desenvolvedores e pesquisadores foquem na criação de visualizações ao invés de configurações técnicas repetitivas, com validações robustas, type-safety e recursos avançados para ambientes de produção.

##  Licença

Este módulo é dedicado à comunidade open source, aos meus estudos pessoais e a todos que desejam criar visualizações animadas de forma simples e eficiente. Sinta-se livre para utilizar, estudar, modificar e contribuir com este material.

---

**Versão:** 2.1.0  
**Data:** 2026  
**Compatibilidade:** Python 3.8+, Matplotlib 3.1+, FFmpeg 3.4+