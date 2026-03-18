#!/usr/bin/env python3
"""
Main entry point for Soplos Plymouth Manager.
"""

import os
import sys
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from core import create_application, run_application
from utils.constants import APPLICATION_ID
from utils.logger import logger
from core.i18n_manager import _

def main():
    """
    Main application entry point.
    """
    # Disable client-side decorations (CSD)
    os.environ['GTK_CSD'] = '0'

    # Disable accessibility bridge messages
    os.environ['NO_AT_BRIDGE'] = '1'

    # Set application identifiers
    GLib.set_prgname(APPLICATION_ID)
    GLib.set_application_name("Soplos Plymouth Manager")

    try:
        # Create and run application
        return run_application()

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0

    except Exception as e:
        logger.critical(f"Fatal error starting application: {e}", exc_info=True)

        # Show error dialog as fallback
        try:
            from gi.repository import Gtk
            dialog = Gtk.MessageDialog(
                modal=True,
                destroy_with_parent=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=_("Failed to start application:\n{error}").format(error=e)
            )
            dialog.run()
            dialog.destroy()
        except Exception:
            pass

        return 1

if __name__ == "__main__":
    sys.exit(main())
