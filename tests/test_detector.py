"""
Testes para FFmpegDetector
"""

from unittest.mock import patch

from ffmpeg_matplotlib.config import FFmpegDetector


class TestResolveP:
    """Testes de resolução de caminho"""

    def test_resolve_path_with_which(self):
        """Testa resolução usando shutil.which"""
        with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
            result = FFmpegDetector.resolve_path("ffmpeg")
            assert result == "/usr/bin/ffmpeg"

    def test_resolve_path_not_found(self):
        """Testa quando caminho não é encontrado"""
        with patch("shutil.which", return_value=None):
            with patch("pathlib.Path.exists", return_value=False):
                result = FFmpegDetector.resolve_path("/nonexistent/ffmpeg")
                assert result is None


class TestFindInPath:
    """Testes de busca no PATH"""

    def test_find_in_path_success(self):
        """Testa busca bem-sucedida no PATH"""
        with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
            result = FFmpegDetector.find_in_path()
            assert result == "/usr/bin/ffmpeg"

    def test_find_in_path_not_found(self):
        """Testa busca sem sucesso no PATH"""
        with patch("shutil.which", return_value=None):
            result = FFmpegDetector.find_in_path()
            assert result is None


class TestAutoDetect:
    """Testes de auto-detecção"""

    def test_auto_detect_finds_in_path(self):
        """Testa detecção via PATH"""
        with patch.object(
            FFmpegDetector, "find_in_path", return_value="/usr/bin/ffmpeg"
        ):
            result = FFmpegDetector.auto_detect()
            assert result == "/usr/bin/ffmpeg"

    def test_auto_detect_not_found(self):
        """Testa quando não encontra FFmpeg"""
        with patch.object(FFmpegDetector, "find_in_path", return_value=None):
            with patch.object(
                FFmpegDetector, "get_system_specific_paths", return_value=[]
            ):
                result = FFmpegDetector.auto_detect()
                assert result is None
