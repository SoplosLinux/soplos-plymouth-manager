"""
Core module for Soplos Plymouth Manager.
Contains the main application logic, plymouth management, and system integration.
"""

__version__ = "2.0.0"
__author__ = "Sergi Perich"
__email__ = "info@soploslinux.com"
__license__ = "GPL-3.0+"

# Core module exports
from .application import PlymouthApp, create_application, run_application
from .plymouth_manager import PlymouthManager
from .i18n_manager import I18nManager, get_i18n_manager, initialize_i18n, _, ngettext

__all__ = [
    # Application
    'PlymouthApp',
    'create_application',
    'run_application',

    # Plymouth Management
    'PlymouthManager',

    # Internationalization
    'I18nManager',
    'get_i18n_manager',
    'initialize_i18n',
    '_',
    'ngettext'
]