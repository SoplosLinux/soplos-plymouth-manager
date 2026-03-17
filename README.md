# Soplos Plymouth Manager

[![License: GPL-3.0+](https://img.shields.io/badge/License-GPL--3.0%2B-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)]()

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

### v2.0.0 (2026-03-16)
- Complete refactoring to modular architecture.
- Full dynamic theme detection (Eliminated hardcoded names/modules).
- Robust theme installer with deep search for nested archives.
- Enhanced progress bars and real-time feedback.
- Advanced support for Wayland and Plasma/GNOME environments.
- Responsive interface and standard Soplos keyboard shortcuts.
- Native Dracut support.

### v1.0.4 (2025-07-27)
- Program icon changed.

### v1.0.3 (2025-07-18)
- Metainfo update for AppStream/DEP-11 compliance.
- Renamed screenshots to screenshot1.png, screenshot2.png, etc.
- Minor documentation and metadata improvements.

### v1.0.0 (2025-05-08)
- Initial version
