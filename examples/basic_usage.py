"""
Exemplo básico de uso do ffmpeg_matplotlib
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from ffmpeg_matplotlib import configurar_ffmpeg, salvar_animacao

# 1. Configurar FFmpeg (uma vez no início)
print("Configurando FFmpeg...")
if configurar_ffmpeg():
    print("✓ FFmpeg configurado com sucesso!")
else:
    print("✗ FFmpeg não encontrado. Instale o FFmpeg e tente novamente.")
    exit(1)

# 2. Criar animação simples
print("\nCriando animação...")

fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(0, 2 * np.pi)
ax.set_ylim(-1.5, 1.5)
ax.set_xlabel("x")
ax.set_ylabel("sin(x + t)")
ax.set_title("Animação de Onda Senoidal")
ax.grid(True, alpha=0.3)

(line,) = ax.plot([], [], "b-", linewidth=2, label="sin(x + t)")
ax.legend()


def init():
    """Inicializa a animação"""
    line.set_data([], [])
    return (line,)


def update(frame):
    """Atualiza cada frame"""
    x = np.linspace(0, 2 * np.pi, 200)
    y = np.sin(x + frame / 10)
    line.set_data(x, y)
    return (line,)


# Criar animação
ani = FuncAnimation(fig, update, init_func=init, frames=100, interval=50, blit=True)

# 3. Salvar vídeo
print("\nSalvando vídeo...")

# Opção simples (padrão)
salvar_animacao(ani, "onda_simples.mp4")

# Opção com qualidade customizada
salvar_animacao(ani, "onda_hd.mp4", fps=30, quality="high", verbose=True)

print("\n✓ Processo concluído!")
print("Vídeos salvos: onda_simples.mp4 e onda_hd.mp4")
