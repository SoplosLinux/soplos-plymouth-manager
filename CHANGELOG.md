# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-03-16

### 🎉 Added
- Complete modular architecture (core/, ui/, utils/, config/, locale/, assets/)
- Advanced support for Wayland, GNOME, Plasma, and XFCE
- Intelligent detection of desktop environments and protocols (X11/Wayland)
- Responsive Gallery: Dynamically adapts to window size without rigid column limits
- Standard Soplos keyboard shortcuts (Ctrl+Q, F5, Ctrl+A, Ctrl+P, Ctrl+I, Delete)
- **Eliminated hardcoded theme names and modules for full dynamic detection**
- **Robust theme installer with deep recursive search for compressed archives**

### 🔄 Changed
- App ID changed to `org.soplos.plymouthmanager`
- Total visual renewal following Soplos v2.0 design standards
- Relocation of progress bar to a dynamic `Revealer` above the footer
- Premium centering and scaling of thumbnails in the gallery
- **Dynamic protection of active and critical system themes**

### 🛠️ Improved
- Native support for Dracut-based systems (Soplos Linux standard)
- Unified privilege management via `pkexec`
- Complete internationalization with native support for 8 languages via gettext
- **Enhanced progress reporting with smooth updates during initramfs generation**

### 🐛 Fixed
- Removed duplicated footer
- Corrected asymmetric preview centering
- Fixed CSS syntax errors for GTK 3 compatibility
- **Fixed progress bar stuck at 20% during long operations**
- **Fixed installation issues with nested folder structures in theme bundles**

## [1.0.4] - 2025-07-27

### 🎨 Changed
- Program icon changed.
- Developer updated to Sergi Perich.

## [1.0.3] - 2025-07-18

### 🛠️ Improved - Metainfo and AppStream/DEP-11 compatibility
- Metainfo update for AppStream/DEP-11 compliance.
- Renamed screenshots to screenshot1.png, screenshot2.png, etc.
- Minor documentation and metadata improvements.
- No functional changes.

## [1.0.0] - 2025-05-08

### 🎉 Initial Release
- Graphical interface for managing Plymouth themes.
- Preview, install, and apply themes.
- Advanced configuration.
- Multi-language support (8 languages).
- Compatible with Soplos Linux and derivatives.

---

## Types of Changes

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for features to be removed soon
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities

## Contribute

To report bugs or request features:
- **Issues**: https://github.com/SoplosLinux/soplos-plymouth-manager/issues
- **Email**: info@soploslinux.com

## Support

- **Documentation**: https://soploslinux.com
- **Community**: https://soploslinux.com/community
- **Support**: info@soploslinux.com
