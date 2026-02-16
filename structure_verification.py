#!/usr/bin/env python3
"""
Script de verificação da estrutura do pacote matplotlib-ffmpeg
"""

import sys
from pathlib import Path


def verificar_arquivo(caminho, obrigatorio=True):
    """Verifica se arquivo existe"""
    existe = Path(caminho).exists()
    simbolo = "✓" if existe else ("✗" if obrigatorio else "⚠")
    status = "OK" if existe else ("FALTANDO" if obrigatorio else "OPCIONAL")
    print(f"{simbolo} {caminho:<40} [{status}]")
    return existe


def verificar_estrutura():
    """Verifica estrutura completa do pacote"""
    print("\n" + "=" * 70)
    print("VERIFICAÇÃO DA ESTRUTURA DO PACOTE MATPLOTLIB-FFMPEG")
    print("=" * 70 + "\n")

    # Arquivos principais
    print("📄 ARQUIVOS DE CONFIGURAÇÃO:")
    print("-" * 70)
    config_ok = all(
        [
            verificar_arquivo("pyproject.toml"),
            verificar_arquivo("setup.py"),
            verificar_arquivo("README.md"),
            verificar_arquivo("LICENSE", obrigatorio=False),
            verificar_arquivo(".gitignore", obrigatorio=False),
            verificar_arquivo("MANIFEST.in", obrigatorio=False),
        ]
    )

    # Código fonte
    print("\n📦 CÓDIGO FONTE:")
    print("-" * 70)
    src_ok = all(
        [
            verificar_arquivo("src/ffmpeg_matplotlib/__init__.py"),
            verificar_arquivo("src/ffmpeg_matplotlib/config.py"),
            verificar_arquivo("src/ffmpeg_matplotlib/py.typed"),
        ]
    )

    # Testes
    print("\n🧪 TESTES:")
    print("-" * 70)
    verificar_arquivo("tests/__init__.py", obrigatorio=False)
    verificar_arquivo("tests/test_config.py", obrigatorio=False)
    verificar_arquivo("tests/conftest.py", obrigatorio=False)

    # Exemplos
    print("\n📚 EXEMPLOS:")
    print("-" * 70)
    verificar_arquivo("examples/basic_usage.py", obrigatorio=False)
    verificar_arquivo("examples/heliocentric_system.py", obrigatorio=False)

    # Documentação
    print("\n📖 DOCUMENTAÇÃO:")
    print("-" * 70)
    verificar_arquivo("docs/source/conf.py", obrigatorio=False)
    verificar_arquivo("CONTRIBUTING.md", obrigatorio=False)
    verificar_arquivo("CHANGELOG.md", obrigatorio=False)

    # CI/CD
    print("\n⚙️  CI/CD:")
    print("-" * 70)
    verificar_arquivo(".github/workflows/tests.yml", obrigatorio=False)
    verificar_arquivo(".github/workflows/lint.yml", obrigatorio=False)

    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO:")
    print("=" * 70)

    if config_ok and src_ok:
        print("✓ Estrutura mínima está OK!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("  1. Instalar em modo desenvolvimento: pip install -e .")
        print("  2. Testar importação: python -c 'import matplotlib_ffmpeg'")
        print("  3. Rodar testes: pytest")
        print("  4. Build: python -m build")
    else:
        print("✗ Estrutura incompleta. Verifique os arquivos faltando acima.")
        return False

    return True


if __name__ == "__main__":
    # Verificar se estamos no diretório correto
    if not Path("pyproject.toml").exists():
        print(
            "⚠️  Execute este script no diretório raiz do projeto (onde está pyproject.toml)"
        )
        sys.exit(1)

    sucesso = verificar_estrutura()
    sys.exit(0 if sucesso else 1)
