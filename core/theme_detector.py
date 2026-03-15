"""
Environment detection for Soplos Plymouth Manager.
Detects desktop environments, display protocols, and system capabilities.
"""

import os
import subprocess
from enum import Enum
from typing import Optional, Tuple
from utils.logger import logger

class DesktopEnvironment(Enum):
    """Supported desktop environments."""
    XFCE = "xfce"
    GNOME = "gnome"
    KDE = "kde"
    PLASMA = "plasma"
    CINNAMON = "cinnamon"
    MATE = "mate"
    LXDE = "lxde"
    UNKNOWN = "unknown"

class DisplayProtocol(Enum):
    """Display protocols."""
    X11 = "x11"
    WAYLAND = "wayland"
    UNKNOWN = "unknown"

class ThemeDetector:
    """
    Detects the current desktop environment and display protocol.
    Provides methods to determine system capabilities for Plymouth theme previews.
    """

    def __init__(self):
        """Initialize the theme detector."""
        self._desktop_env = None
        self._display_protocol = None
        self._initramfs_system = None

    def detect_desktop_environment(self) -> DesktopEnvironment:
        """
        Detect the current desktop environment.

        Returns:
            DesktopEnvironment enum value
        """
        if self._desktop_env is not None:
            return self._desktop_env

        # Check environment variables
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        session = os.environ.get('DESKTOP_SESSION', '').lower()

        # Check for specific desktop environments
        if 'xfce' in desktop or 'xfce' in session:
            self._desktop_env = DesktopEnvironment.XFCE
        elif 'gnome' in desktop or 'gnome' in session:
            self._desktop_env = DesktopEnvironment.GNOME
        elif 'kde' in desktop or 'plasma' in session:
            self._desktop_env = DesktopEnvironment.PLASMA
        elif 'cinnamon' in desktop or 'cinnamon' in session:
            self._desktop_env = DesktopEnvironment.CINNAMON
        elif 'mate' in desktop or 'mate' in session:
            self._desktop_env = DesktopEnvironment.MATE
        elif 'lxde' in desktop or 'lxde' in session:
            self._desktop_env = DesktopEnvironment.LXDE
        else:
            # Fallback detection
            if os.environ.get('KDE_FULL_SESSION'):
                self._desktop_env = DesktopEnvironment.PLASMA
            elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                self._desktop_env = DesktopEnvironment.GNOME
            else:
                self._desktop_env = DesktopEnvironment.UNKNOWN

        logger.info(f"Detected desktop environment: {self._desktop_env.value}")
        return self._desktop_env

    def detect_display_protocol(self) -> DisplayProtocol:
        """
        Detect the current display protocol.

        Returns:
            DisplayProtocol enum value
        """
        if self._display_protocol is not None:
            return self._display_protocol

        # Check WAYLAND_DISPLAY environment variable
        if os.environ.get('WAYLAND_DISPLAY'):
            self._display_protocol = DisplayProtocol.WAYLAND
        # Check DISPLAY for X11
        elif os.environ.get('DISPLAY'):
            self._display_protocol = DisplayProtocol.X11
        else:
            self._display_protocol = DisplayProtocol.UNKNOWN

        logger.info(f"Detected display protocol: {self._display_protocol.value}")
        return self._display_protocol

    def detect_initramfs_system(self) -> str:
        """
        Detect the initramfs system used by the distribution.

        Returns:
            Initramfs system name ('update-initramfs', 'dracut', 'mkinitcpio', or 'unknown')
        """
        if self._initramfs_system is not None:
            return self._initramfs_system

        # Check for available commands
        commands = ['update-initramfs', 'dracut', 'mkinitcpio']

        for cmd in commands:
            try:
                result = subprocess.run(['which', cmd],
                                      capture_output=True,
                                      text=True,
                                      timeout=5)
                if result.returncode == 0:
                    self._initramfs_system = cmd
                    logger.info(f"Detected initramfs system: {cmd}")
                    return cmd
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                continue

        self._initramfs_system = 'unknown'
        logger.warning("Could not detect initramfs system")
        return self._initramfs_system

    def can_preview_theme(self) -> bool:
        """
        Check if theme preview is supported in current environment.

        Returns:
            True if preview is supported, False otherwise
        """
        desktop = self.detect_desktop_environment()
        protocol = self.detect_display_protocol()

        # Preview limitations:
        # - Wayland + GNOME: Limited support
        # - Wayland + KDE/Plasma: Better support but may need adjustments
        # - X11: Generally good support

        if protocol == DisplayProtocol.WAYLAND:
            if desktop in [DesktopEnvironment.GNOME, DesktopEnvironment.UNKNOWN]:
                logger.warning("Theme preview may not work properly on Wayland + GNOME")
                return False
            elif desktop == DesktopEnvironment.PLASMA:
                logger.info("Theme preview supported on Wayland + Plasma (with limitations)")
                return True
            else:
                return True
        elif protocol == DisplayProtocol.X11:
            return True
        else:
            return False

    def get_preview_method(self) -> str:
        """
        Get the recommended preview method for current environment.

        Returns:
            Preview method ('plymouthd', 'direct', 'fallback')
        """
        desktop = self.detect_desktop_environment()
        protocol = self.detect_display_protocol()

        if protocol == DisplayProtocol.WAYLAND:
            if desktop == DesktopEnvironment.PLASMA:
                return 'plymouthd'
            else:
                return 'fallback'
        else:
            return 'plymouthd'

    def is_privileged_execution_available(self) -> bool:
        """
        Check if privileged command execution is available.

        Returns:
            True if pkexec or similar is available
        """
        try:
            result = subprocess.run(['which', 'pkexec'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def is_dark_theme(self) -> bool:
        """
        Check if the current system theme is dark.

        Returns:
            True if dark theme is detected, False otherwise
        """
        # 1. Check environment variable (forced by user)
        if os.environ.get('SOPLOS_DARK_MODE') == '1':
            return True
            
        # 2. Check for 'dark' in GTK_THEME env var
        gtk_theme = os.environ.get('GTK_THEME', '').lower()
        if 'dark' in gtk_theme:
            return True

        # 3. Check desktop-specific settings
        desktop = self.detect_desktop_environment()
        
        try:
            if desktop == DesktopEnvironment.GNOME:
                # GNOME color-scheme (modern)
                cmd = ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                if 'prefer-dark' in result.stdout.lower():
                    return True
                
                # Legacy GTK theme name check
                cmd = ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                if 'dark' in result.stdout.lower():
                    return True

            elif desktop == DesktopEnvironment.PLASMA:
                # KDE Plasma look-and-feel check
                cmd = ['kreadconfig5', '--group', 'General', '--key', 'ColorScheme']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                if 'dark' in result.stdout.lower() or 'breeze-dark' in result.stdout.lower():
                    return True

            elif desktop == DesktopEnvironment.XFCE:
                # XFCE theme check
                cmd = ['xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                if 'dark' in result.stdout.lower():
                    return True
        except Exception as e:
            logger.debug(f"Error detecting dark theme via settings: {e}")

        # Default fallback: assume light
        return False

    def get_environment_info(self) -> dict:
        """
        Get comprehensive environment information.

        Returns:
            Dictionary with environment details
        """
        return {
            'desktop': self.detect_desktop_environment().value,
            'protocol': self.detect_display_protocol().value,
            'initramfs': self.detect_initramfs_system(),
            'can_preview': self.can_preview_theme(),
            'preview_method': self.get_preview_method(),
            'privileged_exec': self.is_privileged_execution_available()
        }

# Global detector instance
_detector = None

def get_theme_detector() -> ThemeDetector:
    """Get global theme detector instance."""
    global _detector
    if _detector is None:
        _detector = ThemeDetector()
    return _detector

def detect_environment() -> dict:
    """
    Convenience function to detect current environment.

    Returns:
        Environment information dictionary
    """
    detector = get_theme_detector()
    return detector.get_environment_info()