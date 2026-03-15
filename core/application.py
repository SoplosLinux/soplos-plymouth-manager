"""
Main application class for Soplos Plymouth Manager.
Handles GTK application lifecycle, window management, and core functionality.
"""

import gi
import os
import sys
from pathlib import Path

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Gio

from core.plymouth_manager import PlymouthManager
from core.theme_detector import get_theme_detector
from ui.main_window import PlymouthThemeManager
from config.settings import get_config
from utils.constants import APPLICATION_ID, APPLICATION_NAME, LOCALE_DIR
from utils.logger import logger
from core.i18n_manager import initialize_i18n

class PlymouthApp(Gtk.Application):
    """
    Main GTK application class for Soplos Plymouth Manager.
    Manages the application lifecycle and coordinates between components.
    """

    def __init__(self):
        """Initialize the Plymouth application."""
        super().__init__(
            application_id=APPLICATION_ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        self.plymouth_manager = None
        self.theme_detector = None
        self.config = None
        self.main_window = None

        # Connect signals
        self.connect('startup', self.on_startup)
        self.connect('activate', self.on_activate)
        self.connect('shutdown', self.on_shutdown)

    def on_startup(self, app):
        """Handle application startup."""
        logger.info("Starting Soplos Plymouth Manager")

        try:
            # Initialize internationalization
            initialize_i18n(str(LOCALE_DIR))

            # Cleanup __pycache__ on startup
            self._cleanup_garbage()

            # Initialize core components
            self.config = get_config()
            self.theme_detector = get_theme_detector()
            self.plymouth_manager = PlymouthManager()

            # Apply CSS themes
            self._apply_css()

            # Set default icon
            Gtk.Window.set_default_icon_name(APPLICATION_ID)

            # Log environment info
            env_info = self.theme_detector.get_environment_info()
            logger.info(f"Environment: {env_info}")

        except Exception as e:
            logger.critical(f"Error during startup: {e}", exc_info=True)
            self.quit()

    def _apply_css(self):
        """Apply CSS themes to the application."""
        css_provider = Gtk.CssProvider()
        
        # Load base CSS
        base_css = Path(__file__).parent.parent / "assets" / "themes" / "base.css"
        if base_css.exists():
            try:
                css_provider.load_from_path(str(base_css))
            except Exception as e:
                logger.error(f"Error loading base CSS: {e}")

        # Load theme-specific CSS (dark/light)
        is_dark = self.theme_detector.is_dark_theme()
        theme_file = "dark.css" if is_dark else "light.css"
        theme_path = Path(__file__).parent.parent / "assets" / "themes" / theme_file
        
        if theme_path.exists():
            try:
                theme_provider = Gtk.CssProvider()
                theme_provider.load_from_path(str(theme_path))
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    theme_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
            except Exception as e:
                logger.error(f"Error loading {theme_file}: {e}")

        # Add base provider
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_activate(self, app):
        """Handle application activation."""
        try:
            # Create main window if it doesn't exist
            if not self.main_window:
                self.main_window = PlymouthThemeManager(
                    application=self,
                    plymouth_manager=self.plymouth_manager,
                    config=self.config
                )

            # Present the window
            self.main_window.present()

        except Exception as e:
            logger.critical(f"Error activating application: {e}", exc_info=True)
            self.quit()

    def on_shutdown(self, app):
        """Handle application shutdown."""
        logger.info("Shutting down Soplos Plymouth Manager")

        # Save configuration
        if self.config:
            try:
                self.config.save()
            except Exception as e:
                logger.error(f"Error saving configuration: {e}")

        # Cleanup __pycache__ on shutdown
        self._cleanup_garbage()

    def _cleanup_garbage(self):
        """Remove __pycache__ and other temporary files."""
        try:
            import shutil
            root_path = Path(__file__).parent.parent
            logger.debug(f"Cleaning cache from: {root_path}")
            
            # Clean __pycache__
            for root, dirs, files in os.walk(root_path):
                if '__pycache__' in dirs:
                    pycache_path = os.path.join(root, '__pycache__')
                    try:
                        shutil.rmtree(pycache_path, ignore_errors=True)
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")

    def get_plymouth_manager(self) -> PlymouthManager:
        """Get the Plymouth manager instance."""
        return self.plymouth_manager

    def get_theme_detector(self):
        """Get the theme detector instance."""
        return self.theme_detector

    def get_config(self):
        """Get the configuration instance."""
        return self.config

def create_application() -> PlymouthApp:
    """
    Create and return a new PlymouthApp instance.

    Returns:
        PlymouthApp instance
    """
    return PlymouthApp()

def run_application() -> int:
    """
    Create and run the Plymouth application.

    Returns:
        Exit code
    """
    app = create_application()
    return app.run(sys.argv)
