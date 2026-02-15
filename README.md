# Módulo FFmpeg para Matplotlib

Módulo Python reutilizável para configuração e salvamento automático de animações Matplotlib usando FFmpeg, com detecção inteligente de sistema e presets de qualidade.

## Sobre

Este projeto oferece uma solução simplificada e profissional para salvar animações do Matplotlib em formato de vídeo. O módulo elimina a necessidade de configuração manual repetitiva do FFmpeg, fornecendo detecção automática do sistema, presets de qualidade e feedback visual durante o processo de renderização.

## Funcionalidades

* **Detecção Automática**: Identifica e configura o FFmpeg automaticamente no sistema
* **Multiplataforma**: Funciona em Windows, macOS e Linux
* **Presets de Qualidade**: Configurações predefinidas (low, medium, high, ultra)
* **Feedback Visual**: Mensagens informativas sobre o progresso da renderização
* **Interface Simples**: Apenas 3 linhas de código para salvar uma animação
* **Tratamento de Erros**: Validações robustas e mensagens claras
* **Flexibilidade**: Uso funcional ou orientado a objetos
* **Metadados**: Suporte a informações personalizadas do vídeo

## Estrutura do Módulo

O módulo oferece:

1. **Classe FFmpegConfig**: Gerenciamento completo da configuração
2. **Funções de Conveniência**: Atalhos para uso rápido
3. **Detecção Inteligente**: Busca automática em locais comuns do sistema
4. **Presets Otimizados**: Configurações balanceadas para cada caso de uso
5. **Documentação Inline**: Docstrings detalhadas em todos os métodos

## Requisitos

* Python 3.8 ou superior
* Matplotlib - `pip install matplotlib`
* NumPy - `pip install numpy`
* FFmpeg instalado no sistema

## Instalação

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

### 2. Instalar Dependências Python

```bash
pip install matplotlib numpy
```

### 3. Adicionar o Módulo ao Projeto

```bash
# Copie o arquivo ffmpeg_config.py para seu projeto
# Ou adicione ao PYTHONPATH
```

## Como Utilizar

### Modo Básico (Recomendado)

```python
from matplotlib.animation import FuncAnimation
from ffmpeg_config import configurar_ffmpeg, salvar_animacao

# 1. Configurar FFmpeg (uma vez no início)
configurar_ffmpeg()

# 2. Criar sua animação
ani = FuncAnimation(fig, update, frames=200, interval=50)

# 3. Salvar o vídeo
salvar_animacao(ani, 'minha_animacao.mp4')
```

### Modo Avançado

```python
from ffmpeg_config import FFmpegConfig

# Criar configuração personalizada
config = FFmpegConfig(ffmpeg_path=r'C:\meu\caminho\ffmpeg.exe')

# Criar writer customizado
writer = config.create_writer(fps=30, quality='ultra')

# Salvar com configurações específicas
config.save_animation(ani, 'video_hd.mp4', dpi=200)
```

### Comandos e Opções

* **configurar_ffmpeg()**: Detecta FFmpeg automaticamente
* **configurar_ffmpeg(caminho)**: Define caminho manual
* **salvar_animacao()**: Salva vídeo com configurações padrão
* **quality**: 'low', 'medium', 'high', 'ultra'
* **fps**: Taxa de quadros (15, 20, 24, 30, 60)
* **dpi**: Resolução da renderização (72, 100, 150, 200, 300)

## Presets de Qualidade

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

## Tipos de Configuração Suportadas

O sistema aceita diferentes formas de configuração:

* Detecção automática do sistema
* Caminho manual do executável
* FFmpeg no PATH do sistema
* Configuração por variável de ambiente

## Características Técnicas

### Classe `FFmpegConfig`

**Métodos Principais:**

* `auto_detect_ffmpeg()`: Detecta FFmpeg em locais comuns
* `set_ffmpeg_path()`: Define caminho manualmente
* `create_writer()`: Cria writer com configurações personalizadas
* `save_animation()`: Salva animação com feedback visual

**Configurações:**

* Codec padrão: H.264 (libx264)
* FPS padrão: 20 quadros/segundo
* Bitrate padrão: 5000 kbps
* DPI padrão: 150
* Formato padrão: MP4

## Exemplo de Uso Completo Aplicado no Repositório

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from ffmpeg_config import configurar_ffmpeg, salvar_animacao

# Configurar FFmpeg
configurar_ffmpeg()

# Criar figura
fig, ax = plt.subplots()
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(-1, 1)
line, = ax.plot([], [])

# Funções de animação
def init():
    line.set_data([], [])
    return line,

def update(frame):
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x + frame/10)
    line.set_data(x, y)
    return line,

# Criar animação
ani = FuncAnimation(fig, update, init_func=init, 
                   frames=100, interval=50, blit=True)

# Salvar com diferentes qualidades
salvar_animacao(ani, 'onda_baixa.mp4', quality='low')
salvar_animacao(ani, 'onda_media.mp4', quality='medium')
salvar_animacao(ani, 'onda_alta.mp4', quality='high')
salvar_animacao(ani, 'onda_ultra.mp4', quality='ultra', fps=60)

print("✓ Todos os vídeos salvos com sucesso!")
```

## Tratamento de Erros

O sistema possui validações para:

* FFmpeg não instalado ou não encontrado
* Caminho inválido do executável
* Falha na renderização de frames
* Erro na gravação do arquivo
* Configurações incompatíveis
* Falta de permissões de escrita

## Limitações Conhecidas

* Requer FFmpeg instalado no sistema
* Não funciona com animações 3D complexas sem configuração adicional
* Tempo de renderização proporcional à quantidade de frames e qualidade
* Arquivos em qualidade 'ultra' podem ser muito grandes
* Alguns codecs específicos requerem compilações especiais do FFmpeg

## Fluxo de Trabalho Recomendado

1. **Desenvolvimento**: Teste sua animação com `plt.show()`
2. **Preview Rápido**: Salve com `quality='low'` para verificar resultado
3. **Ajustes**: Modifique parâmetros conforme necessário
4. **Renderização Final**: Salve com `quality='high'` ou `'ultra'`
5. **Compartilhamento**: Use `quality='medium'` para arquivos menores

## Estrutura de Arquivos

```
projeto-animacao/
│
├── ffmpeg_config.py              # Módulo principal
├── exemplo_uso_ffmpeg.py         # Exemplo de uso
├── README_FFMPEG.md              # Documentação completa
└── videos/                       # Diretório de saída (criado automaticamente)
    ├── animacao_low.mp4          # Preview de baixa qualidade
    ├── animacao_medium.mp4       # Qualidade média
    ├── animacao_high.mp4         # Alta qualidade
    └── animacao_ultra.mp4        # Máxima qualidade
```

## Contribuições

Sugestões de melhorias e contribuições são bem-vindas. Áreas de interesse:

* Suporte a outros codecs (VP9, AV1, HEVC)
* Exportação em formatos adicionais (GIF, WebM, AVI)
* Interface gráfica (GUI) para configuração
* Processamento em lote de múltiplas animações
* Compressão adaptativa baseada em conteúdo
* Integração com outras bibliotecas de visualização (Plotly, Bokeh)

## Comparação: Antes vs Depois

### Código Tradicional (Repetitivo)

```python
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter

# Repetir em cada projeto
plt.rcParams['animation.ffmpeg_path'] = r'C:\Users\...\ffmpeg.exe'
writer = FFMpegWriter(fps=20, metadata=dict(artist='X'), 
                      bitrate=5000, codec='libx264')
ani.save('video.mp4', writer=writer, dpi=150)
# Sem feedback, sem tratamento de erros
```

### Com Módulo FFmpeg (Simples)

```python
from ffmpeg_config import configurar_ffmpeg, salvar_animacao

configurar_ffmpeg()  # Uma vez
salvar_animacao(ani, 'video.mp4')  # Sempre
# ✓ Automático ✓ Feedback ✓ Validações
```

**Redução de código: ~70%**

## Objetivo

Simplificar o processo de salvamento de animações Matplotlib através da automação da configuração do FFmpeg, permitindo que desenvolvedores e pesquisadores foquem na criação de visualizações ao invés de configurações técnicas repetitivas.

## Casos de Uso

* **Cientistas de Dados**: Visualizações animadas de análises temporais
* **Pesquisadores**: Animações de simulações científicas
* **Educadores**: Material didático com animações explicativas
* **Desenvolvedores**: Demonstrações visuais de algoritmos
* **Artistas Digitais**: Criações generativas em movimento

## Solução de Problemas

### Erro: "FFmpeg não detectado"

```python
# Verifique se está instalado
import subprocess
subprocess.run(['ffmpeg', '-version'])

# Se não funcionar, configure manualmente
configurar_ffmpeg(r'C:\caminho\completo\para\ffmpeg.exe')
```

### Erro: "RuntimeError: FFmpeg não configurado"

```python
# Sempre chame configurar_ffmpeg() antes de salvar
configurar_ffmpeg()  # ← Não esqueça desta linha
salvar_animacao(ani, 'video.mp4')
```

### Vídeo muito grande

```python
# Use qualidade menor ou reduza parâmetros
salvar_animacao(ani, 'video.mp4', quality='medium', fps=15, dpi=100)
```

### Renderização muito lenta

```python
# Reduza número de frames ou use preview
ani = FuncAnimation(..., frames=100)  # Menos frames
salvar_animacao(ani, 'preview.mp4', quality='low')  # Preview rápido
```

## Informações Adicionais

### Formatos de Vídeo Suportados

* MP4 (padrão, melhor compatibilidade)
* AVI (sem compressão, arquivos grandes)
* MOV (QuickTime)
* MKV (Matroska)

### Requisitos de Sistema

* **RAM**: Mínimo 2GB (recomendado 4GB+)
* **Disco**: Espaço livre para vídeos (varia com qualidade)
* **CPU**: Quanto mais rápida, menor o tempo de renderização
* **GPU**: Não utilizada (renderização em CPU)

## Licença

Este módulo é dedicado à humanidade, aos meus estudos pessoais e a todos que desejam criar visualizações animadas de forma simples e eficiente. Sinta-se livre para utilizar, estudar, modificar e contribuir com este material.

---
