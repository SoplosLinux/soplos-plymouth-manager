"""
Plymouth theme management for Soplos Plymouth Manager.
Handles theme installation, removal, application, and preview generation.
"""

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from utils.constants import PLYMOUTH_THEME_DIRS, INITRAMFS_COMMANDS, PKEXEC_COMMAND
from utils.logger import logger
from core.environment import get_environment_detector, DesktopEnvironment, DisplayProtocol
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
                        config_files = list(item.glob("*.plymouth"))
                        if config_files:
                            theme_info = self._parse_theme_info(item, config_files[0])
                            if theme_info:
                                themes.append(theme_info)
            except (OSError, PermissionError) as e:
                logger.warning(f"Error scanning theme directory {theme_dir}: {e}")

        seen_names = set()
        unique_themes = []
        for theme in themes:
            if theme['name'] not in seen_names:
                seen_names.add(theme['name'])
                unique_themes.append(theme)

        unique_themes.sort(key=lambda x: x['name'].lower())

        logger.info(f"Found {len(unique_themes)} Plymouth themes")
        return unique_themes

    def _parse_theme_info(self, theme_path: Path, config_file: Path) -> Optional[Dict[str, str]]:
        """
        Parse theme information from .plymouth configuration file.
        """
        try:
            theme_info = {
                'name': theme_path.name,
                'path': str(theme_path),
                'config_path': str(config_file),
                'description': theme_path.name.replace('-', ' ').title(),
                'preview_path': self._find_preview_image(theme_path),
                'is_graphical': self._is_graphical_theme(theme_path)
            }

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
        """
        desc_file = theme_path / "plymouth.description"
        if desc_file.exists():
            try:
                with open(desc_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except (OSError, UnicodeDecodeError):
                pass

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
        """Dynamically detect if theme has graphical assets, scripts or visual modules."""
        config_files = list(theme_path.glob("*.plymouth"))
        if config_files:
            try:
                with open(config_files[0], 'r', encoding='utf-8') as f:
                    module = ""
                    for line in f:
                        if line.lower().startswith('modulename='):
                            module = line.split('=')[1].strip().lower()
                            break

                    if module in ['text', 'details']:
                        logger.info(f"Theme {theme_path.name} is a pure text/details theme")
                        return False

                    if module:
                        logger.info(f"Theme {theme_path.name} uses visual module '{module}'")
                        return True
            except Exception as e:
                logger.debug(f"Error parsing .plymouth for {theme_path.name}: {e}")

        assets = [p for p in theme_path.rglob("*.png") if p.name not in ["preview.png", "thumbnail.png"]] + \
                 list(theme_path.rglob("*.jpg")) + \
                 list(theme_path.rglob("*.jpeg")) + \
                 list(theme_path.rglob("plymouth.script"))

        return len(assets) > 0

    def _get_available_terminal(self) -> Optional[str]:
        """Find an available terminal emulator."""
        terminals = ['xfce4-terminal', 'gnome-terminal', 'konsole', 'kitty', 'lxterminal', 'xterm']
        for term in terminals:
            if subprocess.run(['which', term], capture_output=True).returncode == 0:
                return term
        return None

    def _get_screenshot_tool(self) -> Optional[Tuple[str, str]]:
        """Find an available screenshot tool and its output flag."""
        is_wayland = bool(os.environ.get('WAYLAND_DISPLAY'))

        if is_wayland:
            tools = [
                ('scrot', '-o'),
                ('import', ''),
                ('gnome-screenshot', '-f'),
                ('grim', '')
            ]
        else:
            tools = [
                ('scrot', '-o'),
                ('xfce4-screenshooter', '-s'),
                ('import', '')
            ]

        for tool, flag in tools:
            if subprocess.run(['which', tool], capture_output=True).returncode == 0:
                return tool, flag
        return None

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
PLYMOUTH_CONFIG=$(find "$TEMP_DIR" -maxdepth 4 -name "*.plymouth" | head -n 1)

if [ -z "$PLYMOUTH_CONFIG" ]; then
    echo "Error: No .plymouth config found in {theme_file}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "SOPLOS_PROGRESS:60"
PLYMOUTH_FILENAME=$(basename "$PLYMOUTH_CONFIG")
THEME_NAME="${{PLYMOUTH_FILENAME%.plymouth}}"
EXTRACTED_THEME_DIR=$(dirname "$PLYMOUTH_CONFIG")

if [ -z "$THEME_NAME" ] || [ "$THEME_NAME" == "." ]; then
    echo "Error: Invalid theme name detected"
    rm -rf "$TEMP_DIR"
    exit 1
fi

if [ -d "$THEME_DIR/$THEME_NAME" ]; then
    rm -rf "$THEME_DIR/$THEME_NAME"
fi

echo "SOPLOS_PROGRESS:80"
mkdir -p "$THEME_DIR/$THEME_NAME"
cp -r "$EXTRACTED_THEME_DIR"/* "$THEME_DIR/$THEME_NAME/"
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
        current = self.get_current_theme()
        if theme_name == current:
            logger.error(f"Cannot remove active theme: {theme_name}")
            return False

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
        """Generate a preview of the SELECTED theme using 5-way modular logic."""
        env = get_environment_detector()
        de = env.desktop_environment
        protocol = env.display_protocol

        logger.info(f"Generating modular preview: Theme={theme_name}, DE={de.value}, Protocol={protocol.value}")

        if de == DesktopEnvironment.XFCE:
            return self._preview_xfce_x11(theme_name)
        elif de == DesktopEnvironment.GNOME:
            if protocol == DisplayProtocol.WAYLAND:
                return self._preview_gnome_wayland(theme_name)
            else:
                return self._preview_gnome_x11(theme_name)
        elif de == DesktopEnvironment.KDE:
            if protocol == DisplayProtocol.WAYLAND:
                return self._preview_kde_wayland(theme_name)
            else:
                return self._preview_kde_x11(theme_name)
        else:
            return self._preview_xfce_x11(theme_name)

    def _preview_xfce_x11(self, theme_name: str) -> Optional[str]:
        """Logic for XFCE/X11: Proven stable atomic block with TTY support."""
        theme_path = self._get_theme_path(theme_name)
        if not theme_path: return None

        output_file = str(theme_path / "preview.png")
        display = os.environ.get('DISPLAY', ':0')
        xauth = os.environ.get('XAUTHORITY', os.path.expanduser('~/.Xauthority'))

        is_tty = False
        config_files = list(theme_path.glob("*.plymouth"))
        if config_files:
            try:
                with open(config_files[0], 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if 'modulename=tribar' in content or 'modulename=bgrt' in content:
                        is_tty = True
                        logger.info(f"Theme {theme_name} detected as TTY-based (Terminal required)")
            except: pass

        shot_tool = "scrot"
        if subprocess.run(['which', 'scrot'], capture_output=True).returncode != 0:
            shot_tool = "xfce4-screenshooter"

        terminal = self._get_available_terminal()
        is_wayland = bool(os.environ.get('WAYLAND_DISPLAY'))

        if is_tty and terminal and not is_wayland:
            term_args = ""
            if "xfce4-terminal" in terminal:
                term_args = "--fullscreen --hide-menubar --hide-borders --hide-toolbar --hide-scrollbar"
            elif "gnome-terminal" in terminal:
                term_args = "--full-screen"

            preview_cmd = f"{terminal} {term_args} -T \"Plymouth Preview\" -e \"bash -c '/usr/sbin/plymouthd --mode=boot --no-daemon; /usr/bin/plymouth --show-splash; sleep 3; /usr/bin/plymouth --quit'\" &"
        else:
            preview_cmd = "/usr/sbin/plymouthd --mode=boot --no-daemon --renderer=x11 >/dev/null 2>&1 &"

        script = f"""#!/bin/bash
export DISPLAY="{display}"
export XAUTHORITY="{xauth}"
killall -9 plymouthd 2>/dev/null || true
CUR_THEME=$(plymouth-set-default-theme)
plymouth-set-default-theme "{theme_name}"

{preview_cmd}
PLY_PID=$!
sleep 2
plymouth --show-splash 2>/dev/null || true
sleep 2

if [ "{shot_tool}" == "scrot" ]; then
    scrot -u -o "{output_file}" || scrot -o "{output_file}"
else
    xfce4-screenshooter -f -s "{output_file}"
fi

plymouth --quit 2>/dev/null || true
kill -9 $PLY_PID 2>/dev/null || true
plymouth-set-default-theme "$CUR_THEME"
"""
        return self._run_preview_script(script, output_file)

    def _preview_gnome_x11(self, theme_name: str) -> Optional[str]:
        """Logic for GNOME/X11: Similar to XFCE but separate for future tweaks."""
        return self._preview_xfce_x11(theme_name)

    def _preview_gnome_wayland(self, theme_name: str) -> Optional[str]:
        """
        Logic for GNOME/Wayland: Using Xephyr as a nested X server bridge.
        Unifies pkexec to avoid double passwords and uses -fullscreen for geometry.
        """
        theme_path = self._get_theme_path(theme_name)
        if not theme_path: return None

        output_file = str(theme_path / "preview.png")
        xdg_runtime = os.environ.get('XDG_RUNTIME_DIR')

        is_tty = False
        config_files = list(theme_path.glob("*.plymouth"))
        if config_files:
            try:
                with open(config_files[0], 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if 'modulename=tribar' in content or 'modulename=bgrt' in content:
                        is_tty = True
                        logger.info(f"Theme {theme_name} is TTY-based. Redirecting to validated TTY-Wayland strategy.")
            except: pass

        if is_tty:
            return self._preview_tty_wayland(theme_name)

        script = f"""#!/bin/bash
FREE_DISPLAY=$(for i in $(seq 1 200); do ! xlsclients -display :$i >/dev/null 2>&1 && echo $i && break; done)
[ -z "$FREE_DISPLAY" ] && FREE_DISPLAY=10

xhost +local:root >/dev/null 2>&1
Xephyr :$FREE_DISPLAY -fullscreen -no-host-grab >/dev/null 2>&1 &
XE_PID=$!
sleep 2

TMP_SHOT="/tmp/plymouth_preview_$$.png"
(sleep 15; DISPLAY=:$FREE_DISPLAY scrot "$TMP_SHOT") &

G_ORIG=$(gsettings get org.gnome.shell.extensions.dash-to-panel intellihide 2>/dev/null) || G_ORIG=""
[ -n "$G_ORIG" ] && gsettings set org.gnome.shell.extensions.dash-to-panel intellihide true

pkexec bash -c "export DISPLAY=:$FREE_DISPLAY XDG_RUNTIME_DIR={xdg_runtime}; \\
    killall -9 plymouthd 2>/dev/null; \\
    CUR_THEME=\\$(plymouth-set-default-theme); \\
    plymouth-set-default-theme \\"{theme_name}\\"; \\
    /usr/sbin/plymouthd --mode=boot --no-daemon --renderer=x11 </dev/null >/dev/null 2>&1 & \\
    P=\\$!; (sleep 30; kill -9 \\$P 2>/dev/null) & \\
    sleep 5; /usr/bin/plymouth --show-splash >/dev/null 2>&1; \\
    sleep 10; kill -9 \\$P 2>/dev/null; \\
    [ -f '$TMP_SHOT' ] && mv '$TMP_SHOT' '{output_file}' && chmod 644 '{output_file}'; \\
    plymouth-set-default-theme \\\"\\$CUR_THEME\\\"; stty sane"

xhost -local:root >/dev/null 2>&1
[ -n "$G_ORIG" ] && gsettings set org.gnome.shell.extensions.dash-to-panel intellihide "$G_ORIG"
kill $XE_PID 2>/dev/null
rm -f "$TMP_SHOT" 2>/dev/null
"""
        logger.info("Executing Unified GNOME Wayland preview (Xephyr Fullscreen)...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(script)
            script_path = f.name

        os.chmod(script_path, 0o755)
        subprocess.run(['bash', script_path])
        os.remove(script_path)

        if os.path.exists(output_file):
            return output_file
        return None

    def _preview_tty_wayland(self, theme_name: str) -> Optional[str]:
        """Validated TTY preview for Wayland: xterm + pkexec script, import as user outside."""
        theme_path = self._get_theme_path(theme_name)
        if not theme_path: return None

        output_file = str(theme_path / "preview.png")
        pid = os.getpid()
        tmp_shot = f"/tmp/plymouth_tty_preview_{pid}.png"
        tmp_xauth = f"/tmp/xauth_soplos_{pid}"
        root_script_path = f"/tmp/soplos_root_script_{pid}.sh"
        
        display = os.environ.get('DISPLAY', ':0')
        xdg_runtime = os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}')
        xauth_orig = os.environ.get('XAUTHORITY', os.path.expanduser('~/.Xauthority'))

        try:
            shutil.copy2(xauth_orig, tmp_xauth)
            os.chmod(tmp_xauth, 0o644)
        except Exception as e:
            logger.error(f"[TTY] Failed to copy XAUTHORITY: {e}")
            return None

        script_content = f'''#!/bin/bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export DISPLAY="{display}"
export XAUTHORITY="{tmp_xauth}"
export XDG_RUNTIME_DIR="{xdg_runtime}"

killall -9 plymouthd 2>/dev/null || true
CUR=$(/usr/sbin/plymouth-set-default-theme)
/usr/sbin/plymouth-set-default-theme "{theme_name}"

/usr/sbin/plymouthd --mode=boot --no-daemon --no-udev --renderer=x11 --tty="$1" </dev/null >/dev/null 2>&1 &
P=$!

sleep 2
/usr/bin/plymouth --show-splash >/dev/null 2>&1

for i in $(seq 1 15); do
  if [ -f "{tmp_shot}.done" ]; then
    mv "{tmp_shot}" "{output_file}" >/dev/null 2>&1
    chmod 644 "{output_file}" >/dev/null 2>&1
    rm -f "{tmp_shot}.done" >/dev/null 2>&1
    break
  fi
  sleep 1
done

kill -9 $P 2>/dev/null || true
/usr/sbin/plymouth-set-default-theme "$CUR"
'''
        try:
            with open(root_script_path, 'w') as f:
                f.write(script_content)
            os.chmod(root_script_path, 0o755)
        except Exception as e:
            logger.error(f"[TTY] Failed to create root script: {e}")
            return None

        env = {**os.environ, 'DISPLAY': display, 'XAUTHORITY': tmp_xauth}

        xterm_cmd = [
            'xterm',
            '-fa', 'Monospace', '-fs', '12',
            '-bg', 'black', '-fg', 'white',
            '+rv',
            '-xrm', 'xterm*vt100.scrollBar: false',
            '-xrm', 'xterm*vt100.visualBell: false',
            '-fullscreen',
            '-e', 'bash', '-c', f'T=$(tty); pkexec bash "{root_script_path}" "$T"'
        ]

        try:
            logger.info("[TTY] Launching xterm via Popen...")
            xterm_proc = subprocess.Popen(xterm_cmd, env=env)

            wid = None
            for i in range(15):
                time.sleep(1)
                result = subprocess.run(
                    ['xdotool', 'search', '--class', 'xterm'],
                    capture_output=True, text=True, env=env
                )
                lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
                wid = lines[-1] if lines else None
                logger.info(f"[TTY] Attempt {i+1} — WID={wid}")
                if wid:
                    break

            if not wid:
                logger.error("[TTY] xterm window not found")
                xterm_proc.terminate()
                return None

            logger.info(f"[TTY] WID={wid} — waiting 8s for plymouth to render...")
            time.sleep(8)

            capture = subprocess.run(
                ['import', '-window', wid, tmp_shot],
                env=env, capture_output=True
            )
            logger.info(f"[TTY] import returned: {capture.returncode}")

            if capture.returncode == 0 and os.path.exists(tmp_shot):
                with open(f"{tmp_shot}.done", 'w') as f: pass

            xterm_proc.wait(timeout=20)

        except Exception as e:
            logger.error(f"[TTY] Preview failed: {e}")
        finally:
            for clean_file in [tmp_xauth, tmp_shot, f"{tmp_shot}.done", root_script_path]:
                if os.path.exists(clean_file):
                    try: os.remove(clean_file)
                    except: pass

        return output_file if os.path.exists(output_file) else None

    def _preview_kde_x11(self, theme_name: str) -> Optional[str]:
        """Logic for KDE/X11: Atomic block."""
        return self._preview_xfce_x11(theme_name)

    def _preview_kde_wayland(self, theme_name: str) -> Optional[str]:
        """Logic for KDE/Wayland: XWayland bridge or native."""
        logger.warning("KDE Wayland preview function is being prepared...")
        return None

    def _run_preview_script(self, script: str, output_file: str) -> Optional[str]:
        """Internal helper for classical (XFCE) preview."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(script)
            script_path = f.name

        os.chmod(script_path, 0o755)
        subprocess.run(PKEXEC_COMMAND + ['bash', script_path])
        os.remove(script_path)

        if os.path.exists(output_file):
            return output_file
        return None

    def _exec_pkexec_script(self, script_content: str):
        """Execute a partial script as root via pkexec."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(script_content)
            script_path = f.name

        os.chmod(script_path, 0o755)
        subprocess.run(PKEXEC_COMMAND + ['bash', script_path], check=False)
        os.remove(script_path)

    def _get_theme_path(self, name: str) -> Optional[Path]:
        for d in PLYMOUTH_THEME_DIRS:
            p = Path(d) / name
            if p.exists(): return p
        return None

    def _extract_archive(self, archive_path: Path, dest_dir: Path) -> None:
        """
        Extract archive file to destination directory.
        """
        import tarfile
        import zipfile

        if archive_path.suffix in ['.gz', '.bz2', '.xz'] and archive_path.name.endswith('.tar'):
            with tarfile.open(archive_path, 'r:*') as tar:
                tar.extractall(dest_dir)
        elif archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(dest_dir)
        else:
            raise ValueError(f"Unsupported archive format: {archive_path}")

    def _update_initramfs(self) -> bool:
        """
        Update initramfs to apply theme changes.
        """
        if self.initramfs_cmd == 'unknown':
            logger.warning("Unknown initramfs system, cannot update")
            return False

        try:
            cmd = INITRAMFS_COMMANDS.get(self.initramfs_cmd, [])
            if not cmd:
                return False

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
        """
        path = Path(theme_path)

        if not path.exists():
            return False, "Theme directory does not exist"

        if not path.is_dir():
            return False, "Theme path is not a directory"

        config_files = list(path.glob("*.plymouth"))
        if not config_files:
            return False, "Missing .plymouth configuration file"

        script_file = path / "plymouth.script"
        if not script_file.exists():
            return False, "Missing plymouth.script file"

        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'Plymouth' not in content and 'plymouth' not in content.lower():
                    return False, "Invalid plymouth.script content"
        except (OSError, UnicodeDecodeError) as e:
            return False, f"Error reading script file: {e}"

        return True, "Theme is valid"