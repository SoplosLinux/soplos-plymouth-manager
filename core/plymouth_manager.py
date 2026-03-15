"""
Plymouth theme management for Soplos Plymouth Manager.
Handles theme installation, removal, application, and preview generation.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from utils.constants import PLYMOUTH_THEME_DIRS, INITRAMFS_COMMANDS, PKEXEC_COMMAND
from utils.logger import logger
from core.theme_detector import get_theme_detector

class PlymouthManager:
    """
    Manages Plymouth themes: listing, installing, removing, applying, and previewing.
    Handles privileged operations and different initramfs systems.
    """

    def __init__(self):
        """Initialize the Plymouth manager."""
        self.theme_detector = get_theme_detector()
        self.initramfs_cmd = self.theme_detector.detect_initramfs_system()

    def get_available_themes(self) -> List[Dict[str, str]]:
        """
        Get list of available Plymouth themes.

        Returns:
            List of theme dictionaries with 'name', 'path', 'description'
        """
        themes = []

        for theme_dir in PLYMOUTH_THEME_DIRS:
            theme_path = Path(theme_dir)
            if not theme_path.exists():
                continue

            try:
                for item in theme_path.iterdir():
                    if item.is_dir():
                        # Check for .plymouth files in the directory
                        config_files = list(item.glob("*.plymouth"))
                        if config_files:
                            theme_info = self._parse_theme_info(item, config_files[0])
                            if theme_info:
                                themes.append(theme_info)
            except (OSError, PermissionError) as e:
                logger.warning(f"Error scanning theme directory {theme_dir}: {e}")

        # Remove duplicates (themes may appear in multiple directories)
        seen_names = set()
        unique_themes = []
        for theme in themes:
            if theme['name'] not in seen_names:
                seen_names.add(theme['name'])
                unique_themes.append(theme)

        logger.info(f"Found {len(unique_themes)} Plymouth themes")
        return unique_themes

    def _parse_theme_info(self, theme_path: Path, config_file: Path) -> Optional[Dict[str, str]]:
        """
        Parse theme information from .plymouth configuration file.
        """
        try:
            # Basic theme info
            theme_info = {
                'name': theme_path.name,
                'path': str(theme_path),
                'config_path': str(config_file),
                'description': theme_path.name.replace('-', ' ').title(),
                'preview_path': self._find_preview_image(theme_path)
            }

            # Try to read description from script or other files
            description = self._extract_description(theme_path)
            if description:
                theme_info['description'] = description

            return theme_info

        except Exception as e:
            logger.error(f"Error parsing theme {theme_path}: {e}")
            return None

    def _extract_description(self, theme_path: Path) -> Optional[str]:
        """
        Extract theme description from various sources.

        Args:
            theme_path: Theme directory path

        Returns:
            Description string or None
        """
        # Check for description file
        desc_file = theme_path / "plymouth.description"
        if desc_file.exists():
            try:
                with open(desc_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except (OSError, UnicodeDecodeError):
                pass

        # Check script file for comments
        script_file = theme_path / "plymouth.script"
        if script_file.exists():
            try:
                with open(script_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip().startswith('#') and 'description' in line.lower():
                            return line.strip()[1:].strip()
            except (OSError, UnicodeDecodeError):
                pass

    def _find_preview_image(self, theme_path: Path) -> Optional[str]:
        """Look for preview image in theme directory."""
        preview_names = ['preview.png', 'preview.jpg', 'preview.jpeg', 'screenshot.png', 'background.png']
        for name in preview_names:
            preview_file = theme_path / name
            if preview_file.exists():
                return str(preview_file)
        return None

    def get_current_theme(self) -> Optional[str]:
        """
        Get the currently active Plymouth theme.

        Returns:
            Current theme name or None
        """
        try:
            result = subprocess.run(['plymouth-set-default-theme'],
                                  capture_output=True,
                                  text=True,
                                  timeout=10)
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.error(f"Error getting current theme: {e}")

        return None

    def set_theme(self, theme_name: str) -> bool:
        """
        Set the active Plymouth theme.

        Args:
            theme_name: Name of the theme to set

        Returns:
            True if successful, False otherwise
        """
        try:
            # Use pkexec for privileged operation
            cmd = PKEXEC_COMMAND + ['plymouth-set-default-theme', theme_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.info(f"Successfully set Plymouth theme to: {theme_name}")
                self._update_initramfs()
                return True
            else:
                logger.error(f"Failed to set theme: {result.stderr}")
                return False

        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.error(f"Error setting theme {theme_name}: {e}")
            return False

    def install_theme(self, theme_file: str) -> bool:
        """
        Install a Plymouth theme from file.

        Args:
            theme_file: Path to theme archive or directory

        Returns:
            True if successful, False otherwise
        """
        theme_path = Path(theme_file)
        if not theme_path.exists():
            logger.error(f"Theme file does not exist: {theme_file}")
            return False

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                if theme_path.is_file():
                    # Extract archive
                    self._extract_archive(theme_path, temp_path)
                else:
                    # Copy directory
                    shutil.copytree(theme_path, temp_path / theme_path.name)

                # Find theme directory
                theme_dirs = list(temp_path.glob("*"))
                if not theme_dirs:
                    logger.error("No theme directory found in archive")
                    return False

                theme_dir = theme_dirs[0]
                if not (theme_dir / "plymouth.script").exists():
                    logger.error("Invalid Plymouth theme: missing plymouth.script")
                    return False

                # Install to system directory
                system_theme_dir = Path("/usr/share/plymouth/themes")
                system_theme_dir.mkdir(parents=True, exist_ok=True)

                dest_dir = system_theme_dir / theme_dir.name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)

                shutil.copytree(theme_dir, dest_dir)

                logger.info(f"Successfully installed theme: {theme_dir.name}")
                return True

        except Exception as e:
            logger.error(f"Error installing theme: {e}")
            return False

    def remove_theme(self, theme_name: str) -> bool:
        """
        Remove a Plymouth theme.

        Args:
            theme_name: Name of the theme to remove

        Returns:
            True if successful, False otherwise
        """
        # Don't allow removal of system themes
        system_themes = ['text', 'details', 'fade-in', 'glow', 'script', 'solar', 'spinfinity']

        if theme_name in system_themes:
            logger.error(f"Cannot remove system theme: {theme_name}")
            return False

        for theme_dir in PLYMOUTH_THEME_DIRS:
            theme_path = Path(theme_dir) / theme_name
            if theme_path.exists():
                try:
                    shutil.rmtree(theme_path)
                    logger.info(f"Successfully removed theme: {theme_name}")
                    return True
                except OSError as e:
                    logger.error(f"Error removing theme {theme_name}: {e}")
                    return False

        logger.error(f"Theme not found: {theme_name}")
        return False

    def generate_preview(self, theme_name: str, output_file: Optional[str] = None) -> Optional[str]:
        """
        Generate a preview image for a Plymouth theme.

        Args:
            theme_name: Name of the theme
            output_file: Output file path (optional)

        Returns:
            Path to preview image or None if failed
        """
        if not self.theme_detector.can_preview_theme():
            logger.warning("Theme preview not supported in current environment")
            return None

        try:
            # Create temporary output file if not specified
            if not output_file:
                import tempfile
                temp_fd, output_file = tempfile.mkstemp(suffix='.png')
                os.close(temp_fd)

            # Use plymouth to generate preview
            cmd = [
                'plymouth',
                '--show-splash',
                '--theme', theme_name,
                '--capture', output_file
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and Path(output_file).exists():
                logger.info(f"Generated preview for theme {theme_name}: {output_file}")
                return output_file
            else:
                logger.error(f"Failed to generate preview: {result.stderr}")
                return None

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
            logger.error(f"Error generating preview: {e}")
            return None

    def _extract_archive(self, archive_path: Path, dest_dir: Path) -> None:
        """
        Extract archive file to destination directory.

        Args:
            archive_path: Path to archive
            dest_dir: Destination directory
        """
        import tarfile
        import zipfile

        if archive_path.suffix in ['.gz', '.bz2', '.xz'] and archive_path.name.endswith('.tar'):
            # Tar archive
            with tarfile.open(archive_path, 'r:*') as tar:
                tar.extractall(dest_dir)
        elif archive_path.suffix == '.zip':
            # Zip archive
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(dest_dir)
        else:
            raise ValueError(f"Unsupported archive format: {archive_path}")

    def _update_initramfs(self) -> bool:
        """
        Update initramfs to apply theme changes.

        Returns:
            True if successful, False otherwise
        """
        if self.initramfs_cmd == 'unknown':
            logger.warning("Unknown initramfs system, cannot update")
            return False

        try:
            cmd = INITRAMFS_COMMANDS.get(self.initramfs_cmd, [])
            if not cmd:
                return False

            # Use pkexec for privileged operation
            full_cmd = PKEXEC_COMMAND + cmd
            result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                logger.info("Successfully updated initramfs")
                return True
            else:
                logger.error(f"Failed to update initramfs: {result.stderr}")
                return False

        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.error(f"Error updating initramfs: {e}")
            return False

    def validate_theme(self, theme_path: str) -> Tuple[bool, str]:
        """
        Validate a Plymouth theme.

        Args:
            theme_path: Path to theme directory

        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(theme_path)

        if not path.exists():
            return False, "Theme directory does not exist"

        if not path.is_dir():
            return False, "Theme path is not a directory"

        config_files = list(path.glob("*.plymouth"))
        if not config_files:
            return False, "Missing .plymouth configuration file"

        # Check for basic script structure
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'Plymouth' not in content and 'plymouth' not in content.lower():
                    return False, "Invalid plymouth.script content"
        except (OSError, UnicodeDecodeError) as e:
            return False, f"Error reading script file: {e}"

        return True, "Theme is valid"