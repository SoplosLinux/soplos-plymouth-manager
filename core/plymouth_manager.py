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
                'preview_path': self._find_preview_image(theme_path),
                'is_graphical': self._is_graphical_theme(theme_path)
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

    def _is_graphical_theme(self, theme_path: Path) -> bool:
        """Dynamically detect if theme has graphical assets or scripts."""
        has_images = any(theme_path.glob("*.png")) or \
                     any(theme_path.glob("*.jpg")) or \
                     any(theme_path.glob("*.jpeg"))
        has_script = (theme_path / "plymouth.script").exists()
        return has_images or has_script

    def get_current_theme(self) -> Optional[str]:
        """Get current theme name."""
        try:
            res = subprocess.run(['plymouth-set-default-theme'], capture_output=True, text=True, timeout=5)
            return res.stdout.strip() if res.returncode == 0 else None
        except: return None

    def set_theme(self, theme_name: str, progress_callback: Optional[callable] = None) -> bool:
        """Set the active Plymouth theme and update initramfs in one step."""
        try:
            initramfs_system = self.theme_detector.detect_initramfs_system()
            init_cmd_parts = INITRAMFS_COMMANDS.get(initramfs_system, [])
            init_cmd_str = " ".join(init_cmd_parts) if init_cmd_parts else ""

            script_content = f"""#!/bin/bash
echo "SOPLOS_PROGRESS:5"
plymouth-set-default-theme "{theme_name}"
echo "SOPLOS_PROGRESS:20"
if [ -n "{init_cmd_str}" ]; then
    echo "Updating initramfs..."
    {init_cmd_str} > /dev/null 2>&1 &
    PID=$!
    # Increment progress while waiting (max 90%)
    P=20
    while kill -0 $PID 2>/dev/null; do
        sleep 1
        if [ $P -lt 90 ]; then
            P=$((P + 2))
            echo "SOPLOS_PROGRESS:$P"
        fi
    done
    wait $PID
    echo "SOPLOS_PROGRESS:95"
fi
echo "SOPLOS_PROGRESS:100"
exit 0
"""
            return self._run_script_with_progress(script_content, progress_callback)
        except Exception as e:
            logger.error(f"Error in set_theme: {e}")
            return False

    def _run_script_with_progress(self, script_content: str, progress_callback: Optional[callable]) -> bool:
        """Helper to run a shell script with pkexec and track progress markers."""
        script_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as script_file:
                script_file.write(script_content)
                script_path = script_file.name
            
            os.chmod(script_path, 0o755)
            pkexec_cmd = PKEXEC_COMMAND + ['bash', script_path]
            process = subprocess.Popen(
                pkexec_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            while True:
                line = process.stdout.readline()
                if not line: break
                if "SOPLOS_PROGRESS:" in line and progress_callback:
                    try:
                        percent = int(line.split("SOPLOS_PROGRESS:")[1].strip())
                        progress_callback(percent / 100.0)
                    except: pass
            
            process.wait()
            return process.returncode == 0
        finally:
            if script_path and os.path.exists(script_path):
                try: os.remove(script_path)
                except: pass

    def install_theme(self, theme_file: str, progress_callback: Optional[callable] = None) -> Tuple[bool, str]:
        """Install a Plymouth theme from file (Recursive search v2.0)."""
        theme_path = Path(theme_file)
        if not theme_path.exists():
            return False, "Theme file does not exist"

        try:
            script_content = f"""#!/bin/bash
echo "SOPLOS_PROGRESS:5"
THEME_DIR="/usr/share/plymouth/themes"
TEMP_DIR=$(mktemp -d)

# Robust extraction (v2.1 logic)
EXTRACT_CMD=""
if [[ "{theme_file}" == *.tar.* ]] || [[ "{theme_file}" == *.tgz ]]; then
    EXTRACT_CMD="tar xf \\"{theme_file}\\" -C \\"$TEMP_DIR\\""
elif [[ "{theme_file}" == *.zip ]]; then
    EXTRACT_CMD="unzip -q \\"{theme_file}\\" -d \\"$TEMP_DIR\\""
elif [ -d "{theme_file}" ]; then
    EXTRACT_CMD="cp -r \\"{theme_file}\\"/* \\"$TEMP_DIR/\\""
fi

if [ -n "$EXTRACT_CMD" ]; then
    eval $EXTRACT_CMD || {{ echo "Error extracting archive"; rm -rf "$TEMP_DIR"; exit 1; }}
fi

echo "SOPLOS_PROGRESS:40"
# Recursive find to support nested gnome-look themes
PLYMOUTH_CONFIG=$(find "$TEMP_DIR" -maxdepth 4 -name "*.plymouth" | head -n 1)

if [ -z "$PLYMOUTH_CONFIG" ]; then
    echo "Error: No .plymouth config found in {theme_file}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "SOPLOS_PROGRESS:60"
EXTRACTED_THEME_DIR=$(dirname "$PLYMOUTH_CONFIG")
THEME_NAME=$(basename "$EXTRACTED_THEME_DIR")

# Install to system
if [ -z "$THEME_NAME" ] || [ "$THEME_NAME" == "." ]; then
    echo "Error: Invalid theme name detected"
    rm -rf "$TEMP_DIR"
    exit 1
fi

if [ -d "$THEME_DIR/$THEME_NAME" ]; then
    rm -rf "$THEME_DIR/$THEME_NAME"
fi

echo "SOPLOS_PROGRESS:80"
cp -r "$EXTRACTED_THEME_DIR" "$THEME_DIR/"
chmod -R 755 "$THEME_DIR/$THEME_NAME"
chown -R root:root "$THEME_DIR/$THEME_NAME"

rm -rf "$TEMP_DIR"
echo "SOPLOS_PROGRESS:100"
exit 0
"""
            if self._run_script_with_progress(script_content, progress_callback):
                return True, "Successfully installed theme"
            return False, "Installation failed"

        except Exception as e:
            logger.error(f"Error installing theme: {e}")
            return False, str(e)

    def remove_theme(self, theme_name: str) -> bool:
        """Remove a Plymouth theme (Dynamic protection v2.0)."""
        # Protect active theme instead of hardcoded list
        current = self.get_current_theme()
        if theme_name == current:
            logger.error(f"Cannot remove active theme: {theme_name}")
            return False

        # Basic safe list for critical system themes
        if theme_name in ['text', 'details', 'spinner', 'bgrt']:
            logger.error(f"Cannot remove critical system theme: {theme_name}")
            return False

        for theme_dir in PLYMOUTH_THEME_DIRS:
            theme_path = Path(theme_dir) / theme_name
            if theme_path.exists():
                try:
                    subprocess.run(PKEXEC_COMMAND + ['rm', '-rf', str(theme_path)], check=True)
                    logger.info(f"Successfully removed theme: {theme_name}")
                    return True
                except subprocess.CalledProcessError as e:
                    logger.error(f"Error removing theme {theme_name}: {e}")
                    return False
        return False

    def generate_preview(self, theme_name: str) -> Optional[str]:
        """Generate a preview of the SELECTED theme (v2.0 logic)."""
        theme_path = self._get_theme_path(theme_name)
        if not theme_path: return None
        
        output_file = str(theme_path / "preview.png")
        display = os.environ.get('DISPLAY', ':0')
        xauth = os.environ.get('XAUTHORITY', os.path.expanduser('~/.Xauthority'))

        script = f"""#!/bin/bash
export DISPLAY="{display}"
export XAUTHORITY="{xauth}"
killall -9 plymouthd 2>/dev/null || true

# Remember current theme
CUR_THEME=$(plymouth-set-default-theme)

# Temporarily switch to selected theme for preview
plymouth-set-default-theme "{theme_name}"

# Launch plymouth in windowed mode
/usr/sbin/plymouthd --mode=boot --no-daemon --debug --renderer=x11 &
PLY_PID=$!
sleep 1
plymouth --show-splash
sleep 2

# Capture
scrot -o "{output_file}"

# Cleanup
plymouth --quit
kill -9 $PLY_PID 2>/dev/null || true
plymouth-set-default-theme "$CUR_THEME"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        os.chmod(script_path, 0o755)
        subprocess.run(PKEXEC_COMMAND + ['bash', script_path])
        os.remove(script_path)
        
        return output_file if os.path.exists(output_file) else None

    def _get_theme_path(self, name: str) -> Optional[Path]:
        for d in PLYMOUTH_THEME_DIRS:
            p = Path(d) / name
            if p.exists(): return p
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

        # Check for plymouth.script
        script_file = path / "plymouth.script"
        if not script_file.exists():
            return False, "Missing plymouth.script file"

        # Check for basic script structure
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'Plymouth' not in content and 'plymouth' not in content.lower():
                    return False, "Invalid plymouth.script content"
        except (OSError, UnicodeDecodeError) as e:
            return False, f"Error reading script file: {e}"

        return True, "Theme is valid"