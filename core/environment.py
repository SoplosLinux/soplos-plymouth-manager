"""
Environment detection module for Soplos Plymouth Manager.
Unified logic from Soplos Welcome for robust desktop environment,
display protocol identification, and initramfs system detection.
"""

import os
import subprocess
import configparser
from pathlib import Path
from typing import Dict, Optional, Tuple
from enum import Enum
from utils.logger import logger


class DesktopEnvironment(Enum):
    """Supported desktop environments."""
    GNOME = "gnome"
    KDE = "kde"
    XFCE = "xfce"
    UNKNOWN = "unknown"


class DisplayProtocol(Enum):
    """Display server protocols."""
    X11 = "x11"
    WAYLAND = "wayland"
    UNKNOWN = "unknown"


class ThemeType(Enum):
    """System theme types."""
    LIGHT = "light"
    DARK = "dark"
    UNKNOWN = "unknown"


class EnvironmentDetector:
    """
    Detects and analyzes the current desktop environment, display protocol,
    and system environment configuration.
    """
    
    def __init__(self):
        self._desktop_env = None
        self._display_protocol = None
        self._theme_type = None
        self._initramfs_system = None
        self._environment_info = {}
        
    def detect_all(self) -> Dict[str, str]:
        """
        Performs complete environment detection.
        
        Returns:
            Dictionary with all detected environment information
        """
        self._detect_desktop_environment()
        self._detect_display_protocol()
        self._detect_theme_type()
        self._detect_initramfs_system()
        self._detect_additional_info()
        
        return {
            'desktop_environment': self._desktop_env.value,
            'display_protocol': self._display_protocol.value,
            'theme_type': self._theme_type.value,
            'initramfs': self._initramfs_system,
            'environment_info': self._environment_info
        }
    
    def _detect_desktop_environment(self) -> DesktopEnvironment:
        """Detects the current desktop environment."""
        # Check XDG_CURRENT_DESKTOP first (most reliable)
        current_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        
        if 'gnome' in current_desktop:
            self._desktop_env = DesktopEnvironment.GNOME
        elif 'kde' in current_desktop or 'plasma' in current_desktop:
            self._desktop_env = DesktopEnvironment.KDE
        elif 'xfce' in current_desktop:
            self._desktop_env = DesktopEnvironment.XFCE
        else:
            # Fallback detection methods
            self._desktop_env = self._fallback_desktop_detection()
        
        logger.info(f"Detected desktop environment: {self._desktop_env.value}")
        return self._desktop_env
    
    def _fallback_desktop_detection(self) -> DesktopEnvironment:
        """Fallback method for desktop environment detection."""
        # Check for specific processes
        try:
            # Check for common processes without using pgrep input for compatibility
            processes = {
                'gnome-shell': DesktopEnvironment.GNOME,
                'kwin': DesktopEnvironment.KDE,
                'xfwm4': DesktopEnvironment.XFCE
            }
            
            for proc, env in processes.items():
                res = subprocess.run(['pgrep', '-x', proc], capture_output=True)
                if res.returncode == 0:
                    return env
        except Exception:
            pass
        
        # Check for environment variables
        if os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            return DesktopEnvironment.GNOME
        elif os.environ.get('KDE_SESSION_VERSION') or os.environ.get('KDE_FULL_SESSION'):
            return DesktopEnvironment.KDE
        elif os.environ.get('XFCE_PANEL_MIGRATE_DEFAULT'):
            return DesktopEnvironment.XFCE
        
        return DesktopEnvironment.UNKNOWN
    
    def _detect_display_protocol(self) -> DisplayProtocol:
        """Detects the display server protocol (X11 or Wayland)."""
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        
        if session_type == 'wayland' or os.environ.get('WAYLAND_DISPLAY'):
            self._display_protocol = DisplayProtocol.WAYLAND
        elif session_type == 'x11' or os.environ.get('DISPLAY'):
            self._display_protocol = DisplayProtocol.X11
        else:
            self._display_protocol = DisplayProtocol.UNKNOWN
            
        logger.info(f"Detected display protocol: {self._display_protocol.value}")
        return self._display_protocol
    
    def _detect_initramfs_system(self) -> str:
        """Detects the initramfs system."""
        if self._initramfs_system:
            return self._initramfs_system
            
        commands = ['update-initramfs', 'dracut', 'mkinitcpio']
        for cmd in commands:
            if subprocess.run(['which', cmd], capture_output=True).returncode == 0:
                self._initramfs_system = cmd
                logger.info(f"Detected initramfs system: {cmd}")
                return cmd
                
        self._initramfs_system = 'unknown'
        return self._initramfs_system
    
    def _detect_theme_type(self) -> ThemeType:
        """Detects system theme preference (dark/light)."""
        try:
            if self.desktop_environment == DesktopEnvironment.GNOME:
                self._theme_type = self._detect_gnome_theme()
            elif self.desktop_environment == DesktopEnvironment.KDE:
                self._theme_type = self._detect_kde_theme()
            elif self.desktop_environment == DesktopEnvironment.XFCE:
                self._theme_type = self._detect_xfce_theme()
            else:
                self._theme_type = ThemeType.UNKNOWN
        except Exception:
            self._theme_type = ThemeType.UNKNOWN
            
        return self._theme_type
    
    def _detect_gnome_theme(self) -> ThemeType:
        """Detects GNOME theme preference."""
        try:
            result = subprocess.run([
                'gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                if 'dark' in result.stdout.lower():
                    return ThemeType.DARK
                elif 'light' in result.stdout.lower():
                    return ThemeType.LIGHT
        except Exception:
            pass
        
        # Fallback: check GTK theme
        try:
            result = subprocess.run([
                'gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and 'dark' in result.stdout.lower():
                return ThemeType.DARK
        except Exception:
            pass
            
        return ThemeType.LIGHT
    
    def _detect_kde_theme(self) -> ThemeType:
        """Detects KDE theme preference."""
        try:
            kde_config = Path.home() / '.config' / 'kdeglobals'
            if kde_config.exists():
                config = configparser.ConfigParser(strict=False)
                with open(kde_config, 'r', encoding='utf-8', errors='ignore') as f:
                    config.read_file(f)

                if 'General' in config:
                    color_scheme = config['General'].get('ColorScheme', '').lower()
                    if 'dark' in color_scheme or 'black' in color_scheme:
                        return ThemeType.DARK

                if 'KDE' in config:
                    look_and_feel = config['KDE'].get('LookAndFeelPackage', '').lower()
                    if 'dark' in look_and_feel or 'black' in look_and_feel:
                        return ThemeType.DARK

                if 'Colors:Window' in config:
                    bg_color = config['Colors:Window'].get('BackgroundNormal', '')
                    if bg_color:
                        try:
                            # Format: R,G,B
                            r, g, b = map(int, bg_color.split(','))
                            if (r + g + b) / 3 < 128:
                                return ThemeType.DARK
                        except ValueError:
                            pass
        except Exception as e:
            logger.debug(f"Error parsing kdeglobals: {e}")

        # Fallback GTK detection (KDE often syncs this)
        try:
            gtk_config = Path.home() / '.config' / 'gtk-3.0' / 'settings.ini'
            if gtk_config.exists():
                config = configparser.ConfigParser(strict=False)
                config.read(gtk_config)
                if 'Settings' in config:
                    prefer_dark = config['Settings'].get('gtk-application-prefer-dark-theme', '').lower()
                    if prefer_dark in ['1', 'true', 'yes']:
                        return ThemeType.DARK
                    theme_name = config['Settings'].get('gtk-theme-name', '').lower()
                    if 'dark' in theme_name:
                        return ThemeType.DARK
        except Exception:
            pass
            
        return ThemeType.LIGHT

    def _detect_xfce_theme(self) -> ThemeType:
        """Detects XFCE theme preference."""
        try:
            result = subprocess.run([
                'xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and 'dark' in result.stdout.lower():
                return ThemeType.DARK
        except Exception:
            pass
        
        return ThemeType.LIGHT
    
    def _detect_additional_info(self):
        """Collects additional environment information."""
        self._environment_info = {
            'desktop_session': os.environ.get('DESKTOP_SESSION', ''),
            'gdm_session': os.environ.get('GDMSESSION', ''),
            'is_wayland': self.is_wayland,
            'is_dark': self.is_dark_theme
        }
    
    @property
    def desktop_environment(self) -> DesktopEnvironment:
        if self._desktop_env is None:
            self._detect_desktop_environment()
        return self._desktop_env
    
    @property
    def display_protocol(self) -> DisplayProtocol:
        if self._display_protocol is None:
            self._detect_display_protocol()
        return self._display_protocol
    
    @property
    def theme_type(self) -> ThemeType:
        if self._theme_type is None:
            self._detect_theme_type()
        return self._theme_type
    
    @property
    def is_wayland(self) -> bool:
        return self.display_protocol == DisplayProtocol.WAYLAND
    
    @property
    def is_dark_theme(self) -> bool:
        return self.theme_type == ThemeType.DARK
        
    def get_environment_info(self) -> dict:
        """Compatibility method for current UI footer."""
        return {
            'desktop': self.desktop_environment.value,
            'protocol': self.display_protocol.value,
            'initramfs': self._detect_initramfs_system(),
            'is_wayland': self.is_wayland,
            'is_dark': self.is_dark_theme
        }


# Global instance
_environment_detector = None

def get_environment_detector() -> EnvironmentDetector:
    global _environment_detector
    if _environment_detector is None:
        _environment_detector = EnvironmentDetector()
    return _environment_detector
