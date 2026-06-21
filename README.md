# Soplos Plymouth Manager

[![License: GPL-3.0+](https://img.shields.io/badge/License-GPL--3.0%2B-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-2.0.0--7-green.svg)]()

Graphical Plymouth theme manager for Soplos Linux compatible with XFCE, Plasma and GNOME.

## 📝 Description

A GTK3 graphical interface to manage Plymouth boot splash themes: preview, installation, application and advanced theme configuration, with complete internationalization support.

## ✨ Features

- 🎨 **Responsive Interface**: The gallery automatically adapts to the window width.
- ⌨️ **Keyboard Shortcuts**: Support for standard Soplos shortcuts (Ctrl+Q, F5, Ctrl+A, etc.).
- 🎨 Plymouth theme preview.
- 💾 Immediate theme installation and application.
- ⚙️ Advanced configuration.
- 🌍 Multi-language support (8 languages).
- 🖥️ Compatible with XFCE, Plasma and GNOME.
- 🌊 **Full support for Wayland and X11**.
- 🎨 **Automatic system theme detection** (No more hardcoded theme lists).
- 📦 **Robust installer** with deep recursive search for nested themes.
- ⏳ **Real-time progress reporting** for background system updates.

## 🛠️ Requirements

- Python 3.6+
- GTK 3.0
- Plymouth installed

## 📥 Installation

Available in the official Soplos Linux repositories:

```bash
sudo apt update
sudo apt install soplos-plymouth-manager
```

## 🚀 Usage

```bash
# Run the application
soplos-plymouth-manager
```

## 🌊 Wayland Compatibility

The application is **fully compatible with Wayland** and works perfectly on:

- **Xfce (X11)** (Soplos Linux Tyron)
- **Plasma 6 (Wayland/X11)** (Soplos Linux Tyson)
- **GNOME (Wayland/X11)** (Soplos Linux Boro)

### Wayland Specific Features:
- ✅ Automatic window protocol detection
- ✅ Automatic theme application (including dark theme on Plasma 6)
- ✅ Correct scaling on HiDPI monitors
- ✅ Native integration with the compositor

### Theme Troubleshooting:

If the application is not using the correct theme:

```bash
# Force Orchis Orange Dark Compact theme
GTK_THEME=Orchis-Orange-Dark-Compact soplos-plymouth-manager
```

## 📸 Screenshots

### Theme Gallery
![Theme Gallery](https://raw.githubusercontent.com/SoplosLinux/soplos-plymouth-manager/main/assets/screenshots/screenshot1.png)

### Preview Options
![Preview Options](https://raw.githubusercontent.com/SoplosLinux/soplos-plymouth-manager/main/assets/screenshots/screenshot2.png)

## 🌐 Supported Languages

- 🇪🇸 Spanish
- 🇺🇸 English
- 🇵🇹 Portuguese
- 🇫🇷 French
- 🇩🇪 German
- 🇮🇹 Italian
- 🇷🇴 Romanian
- 🇷🇺 Russian

## 🐧 Distribution Compatibility

- ✅ **Soplos Linux Tyron** (Xfce)
- ✅ **Soplos Linux Tyson** (Plasma 6)
- ✅ **Soplos Linux Boro** (GNOME)

## 📄 License

This project is licensed under [GPL-3.0+](https://www.gnu.org/licenses/gpl-3.0.html).

## 👥 Developers

Developed by Sergi Perich

## 🔗 Links

- [Website](https://soplos.org/)
- [Documentation](https://soplos.org/#docs)
- [Help / Wiki](https://soplos.org/wiki)
- [Report Issues](https://github.com/SoplosLinux/soplos-plymouth-manager/issues)
- [Contact](mailto:info@soploslinux.com)

## 📦 Versions

### v2.0.0-5 (2026-05-22)
- Added comprehensive historical documentation for Legacy 1.x branches (Tyron and Tyson) in CHANGELOG and README.
- Cleaned up obsolete AppStream metadata elements in metainfo.xml.

### v2.0.0-4 (2026-05-18)
- Documentation-only release: version history corrected across the release page, CHANGELOG, README and metainfo. All timestamps updated to match the forensic audit of the official package archive.

### v2.0.0-3 (2026-05-16)
- Simplified the footer UI text to match the modern Soplos standard layout (`XFCE · X11`).

### v2.0.0-2 (2026-04-21)
- Fixed: About dialog credits panel on KDE now displays with an opaque dark background instead of being transparent.
- About dialog app icon standardized to 48×48 pixels.

### v2.0.0-1 (2026-03-20)
- **F1 — About dialog**: Press F1 to open the About dialog with version, author, license and website.
- **HeaderBar fix**: CSD window controls no longer affected by the global button CSS rule on GNOME.
- Removed version subtitle from the HeaderBar.

### v2.0.0 (2026-03-18)
- Complete refactoring to modular architecture.
- **Unified environment detection (`core/environment.py`) for DE, protocol, and theme.**
- **Advanced GNOME and KDE previews with Xephyr bridge and xterm for TTY themes.**
- **Robust single-password prompt mechanism for text/TTY themes across all Wayland sessions.**
- **Advanced dark theme detection for KDE Plasma via background mathematical brightness analysis and LookAndFeelPackage checking.**
- **Standard-compliant logging at `~/.cache/soplos-plymouth-manager/`.**
- Full dynamic theme detection (Eliminated hardcoded names/modules).
- Robust theme installer with deep search for nested archives.
- Enhanced progress bars and real-time feedback.
- Advanced support for Wayland and Plasma/GNOME environments.
- Responsive interface and standard Soplos keyboard shortcuts.
- Native Dracut support.

---

## Legacy 1.x — Tyron branch (XFCE + X11)

### 🆕 New in version 1.0.6 (May 8, 2025)
- Stability and compatibility: additional fixes and improvements for the Tyron environment.

### 🆕 New in version 1.0.5 (May 8, 2025)
- Internal cleanup and minor corrections for the Tyron build.

### 🆕 New in version 1.0.4 (May 7, 2025)
- Program icon changed.
- Developer updated to Sergi Perich.

### 🆕 New in version 1.0.3 (May 6, 2025)
- Metainfo update for AppStream/DEP-11 compliance.
- Renamed screenshots to screenshot1.png, screenshot2.png, etc.
- Minor documentation and metadata improvements. No functional changes.

### 🆕 New in version 1.0.2 (May 2, 2025)
- Packaging format updated to standard `_all.deb` structure.

### 🆕 New in version 1.0.1 (May 2, 2025)
- Screenshots and app icons added (48×48, 64×64, 128×128).
- AppStream metainfo added.

### 🆕 New in version 1.0.0 (April 13, 2025)
- Initial Tyron release — complete GTK3 Plymouth theme manager.
- Preview, install, and apply themes.
- Advanced configuration, multi-language support (8 languages).

---

## Legacy 1.x — Tyson branch (Plasma 6 + Wayland)

### 🆕 New in version 1.0.5 (July 18, 2025)
- Metainfo finalized for AppStream/DEP-11 compliance.
- Program icons added in 48×48, 64×64 and 128×128 for software center compatibility.
- Program icon updated.

### 🆕 New in version 1.0.4 (July 15, 2025)
- Metainfo finalized for AppStream/DEP-11 compliance.
- Program icons added in 48×48, 64×64 and 128×128 for software center compatibility.
- Minor structure and tag improvements.

### 🆕 New in version 1.0.3 (July 15, 2025)
- Final metainfo corrections to ensure full visibility in software centers.
- Validated across Plasma Discover, GNOME Software and other AppStream-compatible centers.

### 🆕 New in version 1.0.2 (June 18, 2025)
- Dynamic translation system with on-demand loading.
- 8 languages fully supported (ES, EN, FR, PT, DE, IT, RU, RO) with automatic `$LANG` detection.

### 🆕 New in version 1.0.1 (June 15, 2025)
- System theme detection: automatic dark/light theme detection.
- Wayland improvements: better compatibility with Plasma 6 Wayland sessions.

### 🆕 New in version 1.0.0 (May 9, 2025)
- Initial Tyson release — complete GTK3 Plymouth theme manager.
- Preview, install, and apply themes.
- Secure `update-initramfs` integration, keyboard shortcuts and validation.
