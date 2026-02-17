# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Publicado]

## [2.1.0] - 2026-02-17

### Adicionado
- Estrutura de pacote Python profissional com layout `src/`
- Detecção automática de FFmpeg em Windows, macOS e Linux
- Sistema de presets de qualidade (`low`, `medium`, `high`, `ultra`)
- Validação de codecs disponíveis no FFmpeg instalado
- Verificação automática de espaço em disco antes da renderização
- Estimativa de tamanho de vídeo baseada em parâmetros
- Cache de codecs com TTL de 1 hora e refresh manual
- Modo strict para ambientes de produção (fail-fast sem fallbacks)
- Context manager para configurações temporárias thread-safe
- Sistema de exceções hierárquico e específico
- Progress callbacks customizáveis
- Dataclass `SaveOptions` para configuração type-safe
- Enum `Quality` para presets tipados
- Type hints completos com arquivo `py.typed`
- Thread-safety com singleton e locks
- 11 testes automatizados com pytest
- Cobertura de código de 42%
- Documentação completa em português
- Exemplos práticos de uso

### Características Técnicas
- Separação de concerns (Detector, Validator, Config)
- Path resolution robusto (suporta `~`, caminhos relativos, etc.)
- Regex melhorado para parsing de codecs (suporta hífens)
- Validação de versão do FFmpeg
- Logging configurável por níveis
- Fallback inteligente para codecs comuns
- Criação automática de diretórios
- Extensão `.mp4` automática se não especificada

### Compatibilidade
- Python 3.8+
- Matplotlib 3.1+
- NumPy 1.18+
- FFmpeg 3.4+
- Multiplataforma: Windows, macOS, Linux


[2.1.0]: https://github.com/Agrippa-Tech/FFmpeg-Matplotlib