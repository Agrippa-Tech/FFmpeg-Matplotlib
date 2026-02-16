# matplotlib-ffmpeg

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

## Citação

Se você usar este pacote em pesquisa, por favor cite:

```bibtex
@software{matplotlib_ffmpeg,
  author = {Seu Nome},
  title = {matplotlib-ffmpeg: Integração simplificada do FFmpeg para Matplotlib},
  year = {2026},
  version = {2.1.0},
  url = {https://github.com/seu-usuario/matplotlib-ffmpeg}
}
```

---

## Agradecimentos

Construído para simplificar workflows de animação Matplotlib para a comunidade Python científica.

**Status do Projeto:** Desenvolvimento ativo | Pronto para produção

**Versão:** 2.1.0 | **Python:** 3.8+ | **Matplotlib:** 3.1+ | **FFmpeg:** 3.4+