"""
Módulo de configuração FFmpeg para animações Matplotlib
========================================================

Este módulo fornece funções para configurar e salvar animações
do Matplotlib usando FFmpeg de forma simples e reutilizável.

========================================================
"""

import os
import platform
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from pathlib import Path


class FFmpegConfig:
    """
    Classe para configurar e gerenciar o FFmpeg em animações Matplotlib.
    
    Attributes:
        ffmpeg_path (str): Caminho para o executável do FFmpeg
        configured (bool): Indica se o FFmpeg foi configurado com sucesso
    """
    
    def __init__(self, ffmpeg_path=None, auto_detect=True):
        """
        Inicializa a configuração do FFmpeg.
        
        Args:
            ffmpeg_path (str, optional): Caminho manual para o FFmpeg.
                Se None, tenta detectar automaticamente.
            auto_detect (bool): Se True, tenta detectar FFmpeg no sistema.
        """
        self.ffmpeg_path = None
        self.configured = False
        
        if ffmpeg_path:
            self.set_ffmpeg_path(ffmpeg_path)
        elif auto_detect:
            self.auto_detect_ffmpeg()
    
    def auto_detect_ffmpeg(self):
        """
        Detecta automaticamente o FFmpeg no sistema.
        
        Procura em locais comuns dependendo do sistema operacional.
        """
        system = platform.system()
        possible_paths = []
        
        if system == 'Windows':
            # Caminhos comuns no Windows
            possible_paths = [
                r'C:\ffmpeg\bin\ffmpeg.exe',
                r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
                r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
                os.path.expanduser(r'~\ffmpeg\ffmpeg\bin\ffmpeg.exe'),
                os.path.expanduser(r'~\AppData\Local\ffmpeg\bin\ffmpeg.exe'),
            ]
        elif system == 'Darwin':  # macOS
            # Caminhos comuns no macOS
            possible_paths = [
                '/usr/local/bin/ffmpeg',
                '/opt/homebrew/bin/ffmpeg',
                '/usr/bin/ffmpeg',
            ]
        else:  # Linux
            # Caminhos comuns no Linux
            possible_paths = [
                '/usr/bin/ffmpeg',
                '/usr/local/bin/ffmpeg',
                os.path.expanduser('~/bin/ffmpeg'),
            ]
        
        # Tenta encontrar FFmpeg nos caminhos
        for path in possible_paths:
            if os.path.exists(path):
                self.set_ffmpeg_path(path)
                print(f"✓ FFmpeg detectado automaticamente: {path}")
                return True
        
        # Tenta usar FFmpeg do PATH do sistema
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                   capture_output=True, 
                                   timeout=2)
            if result.returncode == 0:
                self.set_ffmpeg_path('ffmpeg')
                print("✓ FFmpeg encontrado no PATH do sistema")
                return True
        except:
            pass
        
        print("⚠ FFmpeg não detectado automaticamente.")
        print("  Use set_ffmpeg_path() para configurar manualmente.")
        return False
    
    def set_ffmpeg_path(self, path):
        """
        Define o caminho do FFmpeg.
        
        Args:
            path (str): Caminho para o executável do FFmpeg
        """
        self.ffmpeg_path = path
        plt.rcParams['animation.ffmpeg_path'] = path
        self.configured = True
    
    def create_writer(self, fps=20, bitrate=5000, codec='libx264', 
                     quality='high', metadata=None):
        """
        Cria um writer FFmpeg configurado.
        
        Args:
            fps (int): Frames por segundo (padrão: 20)
            bitrate (int): Taxa de bits em kbps (padrão: 5000)
            codec (str): Codec de vídeo (padrão: 'libx264')
            quality (str): Preset de qualidade - 'low', 'medium', 'high', 'ultra'
            metadata (dict, optional): Metadados do vídeo
        
        Returns:
            FFMpegWriter: Writer configurado
        """
        if not self.configured:
            raise RuntimeError(
                "FFmpeg não configurado. Use set_ffmpeg_path() ou "
                "auto_detect_ffmpeg() primeiro."
            )
        
        # Configurações de qualidade predefinidas
        quality_presets = {
            'low': {'bitrate': 1500, 'dpi': 72},
            'medium': {'bitrate': 3000, 'dpi': 100},
            'high': {'bitrate': 5000, 'dpi': 150},
            'ultra': {'bitrate': 8000, 'dpi': 200}
        }
        
        if quality in quality_presets:
            preset = quality_presets[quality]
            bitrate = preset['bitrate']
        
        if metadata is None:
            metadata = {'artist': 'Matplotlib Animation'}
        
        return FFMpegWriter(
            fps=fps,
            metadata=metadata,
            bitrate=bitrate,
            codec=codec
        )
    
    def save_animation(self, animation, filename, fps=20, dpi=150, 
                      quality='high', metadata=None, verbose=True):
        """
        Salva uma animação em arquivo de vídeo.
        
        Args:
            animation: Objeto FuncAnimation do Matplotlib
            filename (str): Nome do arquivo de saída
            fps (int): Frames por segundo (padrão: 20)
            dpi (int): DPI da renderização (padrão: 150)
            quality (str): Preset de qualidade (padrão: 'high')
            metadata (dict, optional): Metadados do vídeo
            verbose (bool): Se True, exibe informações do progresso
        
        Returns:
            str: Caminho completo do arquivo salvo
        """
        if not self.configured:
            raise RuntimeError("FFmpeg não configurado.")
        
        # Adicionar extensão se não houver
        if not filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            filename += '.mp4'
        
        # Criar writer
        writer = self.create_writer(fps=fps, quality=quality, metadata=metadata)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Salvando animação: {filename}")
            print(f"{'='*60}")
            print(f"Configurações:")
            print(f"  • FPS: {fps}")
            print(f"  • DPI: {dpi}")
            print(f"  • Qualidade: {quality}")
            print(f"  • Codec: {writer.codec}")
            print(f"  • Bitrate: {writer.bitrate} kbps")
            print(f"{'='*60}")
            print("Processando frames... (isso pode levar alguns minutos)")
        
        # Salvar animação
        animation.save(filename, writer=writer, dpi=dpi)
        
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
        
        if verbose:
            print(f"{'='*60}")
            print(f"✓ Vídeo salvo com sucesso!")
            print(f"{'='*60}")
            print(f"Arquivo: {filename}")
            print(f"Tamanho: {file_size:.2f} MB")
            print(f"{'='*60}\n")
        
        return os.path.abspath(filename)


# Instância global para uso conveniente
_global_config = FFmpegConfig()


# Funções de conveniência para uso direto
def configurar_ffmpeg(caminho=None):
    """
    Configura o FFmpeg (atalho para a instância global).
    
    Args:
        caminho (str, optional): Caminho para o FFmpeg. Se None, detecta automaticamente.
    
    Returns:
        bool: True se configurado com sucesso
    """
    global _global_config
    
    if caminho:
        _global_config.set_ffmpeg_path(caminho)
        return True
    else:
        return _global_config.auto_detect_ffmpeg()


def criar_writer(fps=20, quality='high', **kwargs):
    """
    Cria um writer FFmpeg (atalho para a instância global).
    
    Args:
        fps (int): Frames por segundo
        quality (str): Qualidade ('low', 'medium', 'high', 'ultra')
        **kwargs: Argumentos adicionais para FFMpegWriter
    
    Returns:
        FFMpegWriter: Writer configurado
    """
    return _global_config.create_writer(fps=fps, quality=quality, **kwargs)


def salvar_animacao(animation, filename, **kwargs):
    """
    Salva uma animação (atalho para a instância global).
    
    Args:
        animation: Objeto FuncAnimation
        filename (str): Nome do arquivo
        **kwargs: Argumentos adicionais para save_animation
    
    Returns:
        str: Caminho do arquivo salvo
    """
    return _global_config.save_animation(animation, filename, **kwargs)


# Exemplo de uso
if __name__ == "__main__":
    print("Módulo FFmpeg Config para Matplotlib")
    print("=" * 60)
    print("\nExemplo de uso:")
    print("""
    # Opção 1: Uso simples com detecção automática
    from ffmpeg_config import configurar_ffmpeg, salvar_animacao
    
    configurar_ffmpeg()  # Detecta automaticamente
    salvar_animacao(ani, 'meu_video.mp4', fps=30, quality='high')
    
    
    # Opção 2: Caminho manual
    from ffmpeg_config import configurar_ffmpeg, salvar_animacao
    
    configurar_ffmpeg(r'C:\\ffmpeg\\bin\\ffmpeg.exe')
    salvar_animacao(ani, 'meu_video.mp4')
    
    
    # Opção 3: Uso orientado a objetos
    from ffmpeg_config import FFmpegConfig
    
    config = FFmpegConfig()
    writer = config.create_writer(fps=24, quality='ultra')
    config.save_animation(ani, 'video_hd.mp4', dpi=200)
    """)
    
    # Testar detecção
    print("\n" + "=" * 60)
    print("Testando detecção automática...")
    print("=" * 60)
    configurar_ffmpeg()