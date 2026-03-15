"""
Configuration management for Soplos Plymouth Manager.
Handles application settings persistence using JSON.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from utils.constants import PROJECT_ROOT
from utils.logger import logger

class Config:
    """
    Manages application configuration settings.
    Settings are stored in JSON format in the user's config directory.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_file: Path to config file (optional)
        """
        if config_file:
            self.config_file = Path(config_file)
        else:
            # Default config location
            config_dir = Path.home() / ".config" / "soplos-plymouth-manager"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_file = config_dir / "settings.json"

        self._settings = {}
        self.load()

    def load(self) -> None:
        """Load settings from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._settings = json.load(f)
                logger.debug(f"Loaded settings from {self.config_file}")
            else:
                logger.debug(f"Config file does not exist, using defaults")
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Error loading config: {e}")
            self._settings = {}

    def save(self) -> None:
        """Save settings to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved settings to {self.config_file}")
        except OSError as e:
            logger.error(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value.

        Args:
            key: Setting key
            value: Setting value
        """
        self._settings[key] = value
        self.save()

    def delete(self, key: str) -> None:
        """
        Delete a setting.

        Args:
            key: Setting key to delete
        """
        if key in self._settings:
            del self._settings[key]
            self.save()

    def get_all(self) -> Dict[str, Any]:
        """Get all settings."""
        return self._settings.copy()

    def reset(self) -> None:
        """Reset all settings to defaults."""
        self._settings = {}
        self.save()

# Global config instance
_config = None

def get_config() -> Config:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config