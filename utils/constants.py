"""
Constants and configuration values for Soplos Plymouth Manager.
"""

import os
from pathlib import Path

# Application information
APPLICATION_ID = "org.soplos.plymouthmanager"
APPLICATION_NAME = "Soplos Plymouth Manager"
APPLICATION_VERSION = "2.0.0"
APPLICATION_AUTHOR = "Sergi Perich"
APPLICATION_EMAIL = "info@soploslinux.com"

# Directory paths
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
SCREENSHOTS_DIR = ASSETS_DIR / "screenshots"
LOCALE_DIR = PROJECT_ROOT / "locale"

# Asset files
APP_ICON = "org.soplos.plymouthmanager"
DESKTOP_FILE = ASSETS_DIR / "org.soplos.plymouthmanager.desktop"

# Plymouth theme directories
PLYMOUTH_THEME_DIRS = [
    "/usr/share/plymouth/themes",
    "/lib/plymouth/themes",
    "/usr/local/share/plymouth/themes"
]

# Initramfs commands for different systems
INITRAMFS_COMMANDS = {
    'update-initramfs': ['update-initramfs', '-u'],
    'dracut': ['dracut', '--regenerate-all', '--force'],
    'mkinitcpio': ['mkinitcpio', '-P']
}

# Privileged command execution
PKEXEC_COMMAND = ['pkexec']

# Logging
LOG_DIR = Path.home() / ".cache" / "soplos-plymouth-manager"
LOG_FILE = LOG_DIR / "plymouth-manager.log"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

# UI constants
WINDOW_DEFAULT_WIDTH = 900
WINDOW_DEFAULT_HEIGHT = 500
PREVIEW_WINDOW_WIDTH = 640
PREVIEW_WINDOW_HEIGHT = 480

# Theme preview settings
PREVIEW_DURATION = 5  # seconds
PREVIEW_FPS = 30

# Supported desktop environments
SUPPORTED_DESKTOPS = ['xfce', 'gnome', 'kde', 'plasma', 'cinnamon', 'mate', 'lxde']

# Display protocols
DISPLAY_PROTOCOLS = ['x11', 'wayland']

# File extensions
THEME_EXTENSIONS = ['.plymouth', '.tar.gz', '.tar.bz2', '.tar.xz']
