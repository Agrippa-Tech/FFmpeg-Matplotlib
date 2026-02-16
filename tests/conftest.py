"""
Fixtures compartilhadas para testes
"""

import shutil
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.animation import FuncAnimation


@pytest.fixture
def temp_dir():
    """Cria diretório temporário para testes"""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def simple_animation():
    """Cria animação simples para testes"""
    fig, ax = plt.subplots()
    ax.set_xlim(0, 2 * np.pi)
    ax.set_ylim(-1, 1)
    (line,) = ax.plot([], [])

    def init():
        line.set_data([], [])
        return (line,)

    def update(frame):
        x = np.linspace(0, 2 * np.pi, 100)
        y = np.sin(x + frame / 10)
        line.set_data(x, y)
        return (line,)

    ani = FuncAnimation(fig, update, init_func=init, frames=10)

    yield ani

    plt.close(fig)


@pytest.fixture
def mock_ffmpeg_path(temp_dir):
    """Cria executável FFmpeg fake para testes"""
    ffmpeg = temp_dir / "ffmpeg"
    ffmpeg.touch()
    ffmpeg.chmod(0o755)
    return str(ffmpeg)
