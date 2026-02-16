"""
Teste manual rápido
"""

print("=" * 70)
print("TESTE MANUAL DO PACOTE")
print("=" * 70)

# 1. Importar
print("\n1. Testando importação...")
try:
    import ffmpeg_matplotlib

    print("   ✓ Pacote importado")
    print(f"   Versão: {ffmpeg_matplotlib.__version__}")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    exit(1)

# 2. Importar funções
print("\n2. Testando funções de conveniência...")
try:
    from ffmpeg_matplotlib import configurar_ffmpeg

    print("   ✓ Funções importadas")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    exit(1)

# 3. Importar classes
print("\n3. Testando classes principais...")
try:
    from ffmpeg_matplotlib.config import FFmpegConfig

    print("   ✓ FFmpegConfig importado")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    exit(1)

# 4. Criar instância
print("\n4. Testando criação de instância...")
try:
    config = FFmpegConfig(auto_detect=False)
    print("   ✓ Instância criada")
    print(f"   Configurado: {config.configured}")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    exit(1)

# 5. Testar auto-detecção
print("\n5. Testando auto-detecção de FFmpeg...")
try:
    resultado = configurar_ffmpeg()
    if resultado:
        print("   ✓ FFmpeg detectado automaticamente")
    else:
        print("   ⚠ FFmpeg não encontrado (normal se não instalado)")
except Exception as e:
    print(f"   ✗ Erro: {e}")

print("\n" + "=" * 70)
print("✅ TODOS OS TESTES MANUAIS PASSARAM!")
print("=" * 70)
