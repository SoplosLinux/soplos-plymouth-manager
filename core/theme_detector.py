"""
Environment detection bridge for Soplos Plymouth Manager.
Uses the unified EnvironmentDetector from core.environment.
"""

from core.environment import get_environment_detector, DesktopEnvironment, DisplayProtocol
from utils.logger import logger

class ThemeDetector:
    """
    Compatibility bridge for the new EnvironmentDetector.
    """

    def __init__(self):
        """Initialize the theme detector."""
        self._detector = get_environment_detector()

    def detect_desktop_environment(self) -> DesktopEnvironment:
        return self._detector.desktop_environment

    def detect_display_protocol(self) -> DisplayProtocol:
        return self._detector.display_protocol

    def detect_initramfs_system(self) -> str:
        return self._detector._detect_initramfs_system()

    def can_preview_theme(self) -> bool:
        """
        Check if theme preview is supported in current environment.
        Now more flexible for Wayland + GNOME if certain tools are present.
        """
        desktop = self.detect_desktop_environment()
        protocol = self.detect_display_protocol()

        if protocol == DisplayProtocol.WAYLAND:
            # We will handle Wayland+GNOME/KDE better in the next step
            # For now, we allow it if we detect it's not a generic unknown
            if desktop != DesktopEnvironment.UNKNOWN:
                return True
            return False
        return protocol == DisplayProtocol.X11

    def get_preview_method(self) -> str:
        """Get the recommended preview method for current environment."""
        protocol = self.detect_display_protocol()
        if protocol == DisplayProtocol.WAYLAND:
            return 'plymouthd' # We'll adapt this later
        return 'plymouthd'

    def is_privileged_execution_available(self) -> bool:
        import subprocess
        try:
            result = subprocess.run(['which', 'pkexec'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def is_dark_theme(self) -> bool:
        return self._detector.is_dark_theme

    def get_environment_info(self) -> dict:
        info = self._detector.get_environment_info()
        info.update({
            'can_preview': self.can_preview_theme(),
            'preview_method': self.get_preview_method(),
            'privileged_exec': self.is_privileged_execution_available()
        })
        return info

# Global detector instance
_detector = None

def get_theme_detector() -> ThemeDetector:
    global _detector
    if _detector is None:
        _detector = ThemeDetector()
    return _detector

def detect_environment() -> dict:
    return get_theme_detector().get_environment_info()