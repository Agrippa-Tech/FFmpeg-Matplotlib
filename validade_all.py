"""
Script de validação completo
"""

import subprocess
import sys


def run_command(cmd, description):
    """Executa comando e mostra resultado"""
    print(f"\n{'='*70}")
    print(f"🔍 {description}")
    print(f"{'='*70}")
    print(f"Comando: {cmd}")
    print()

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print("✓ SUCESSO")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print("✗ FALHOU")
        if result.stderr:
            print(result.stderr)
        return False


print("=" * 70)
print("VALIDAÇÃO COMPLETA DO PROJETO")
print("=" * 70)

results = {}

# 1. Importação
results["import"] = run_command(
    'python -c "import ffmpeg_matplotlib; print(ffmpeg_matplotlib.__version__)"',
    "Teste de Importação",
)

# 2. Testes
results["pytest"] = run_command("pytest -v", "Executar Testes (pytest)")

# 3. Cobertura
results["coverage"] = run_command(
    "pytest --cov=ffmpeg_matplotlib --cov-report=term", "Cobertura de Código"
)

# 4. Black (formatação)
results["black"] = run_command("black --check tests/", "Verificar Formatação (black)")

# 5. isort (imports)
results["isort"] = run_command("isort --check-only tests/", "Verificar Imports (isort)")

# 6. Build
results["build"] = run_command("python -m build", "Build do Pacote")

# Resumo
print("\n" + "=" * 70)
print("RESUMO DOS TESTES")
print("=" * 70)

for test, passed in results.items():
    status = "✓ PASSOU" if passed else "✗ FALHOU"
    print(f"{test:15} : {status}")

total = len(results)
passed = sum(results.values())

print(f"\nTotal: {passed}/{total} testes passaram")

if passed == total:
    print("\n🎉 TODOS OS TESTES PASSARAM! PROJETO OK!")
    sys.exit(0)
else:
    print(f"\n⚠ {total - passed} teste(s) falharam")
    sys.exit(1)
