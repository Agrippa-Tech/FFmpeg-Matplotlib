"""Simplified FFmpeg integration for Matplotlib animations"""

from .config import (FFmpegConfig, configurar_ffmpeg, criar_writer,
                     salvar_animacao)

__version__ = "2.1.0"

__all__ = [
    "FFmpegConfig",
    "configurar_ffmpeg",
    "salvar_animacao",
    "criar_writer",
]
