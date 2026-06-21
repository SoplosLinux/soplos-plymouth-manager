# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0-7] - 2026-06-21

### Fixed
- Polkit dependency updated to `polkitd`, the correct package name in current Debian. Removed obsolete `policykit-1-gnome`, `polkit` and `policykit-1` alternatives.

---

## [2.0.0-6] - 2026-06-11

### 💄 Changed
- Refined theme card selection style: 1px border, no glow effect, fixed FlowBoxChild orange background on selection.

---

## [2.0.0-5] - 2026-05-22

### 📝 Docs
- Added comprehensive historical documentation for Legacy 1.x branches (Tyron and Tyson) in CHANGELOG and README.
- Cleaned up obsolete AppStream metadata elements in metainfo.xml.

---

## [2.0.0-4] - 2026-05-18

### 📝 Docs
- Documentation-only release: version history corrected across the release page, CHANGELOG, README and metainfo. All timestamps updated to match the forensic audit of the official package archive.

---

## [2.0.0-3] - 2026-05-16

### 💄 Changed
- Simplified the footer UI text to match the modern Soplos standard layout (`XFCE · X11`).

---

## [2.0.0-2] - 2026-04-21

### 🐛 Fixed
- About dialog credits panel on KDE: the credits area now displays with an opaque dark background instead of being transparent (caused by global `scrolledwindow { background-color: transparent }` CSS rule).
- About dialog app icon standardized to 48×48 pixels.

---

## [2.0.0-1] - 2026-03-20

### ✨ Added
- **F1 — About dialog**: Opens the About dialog with version, author, license and website.

### 🐛 Fixed
- **HeaderBar CSS**: Global `button {}` rule no longer overrides CSD window controls (close/minimize/maximize) on GNOME.

### 🧹 Removed
- Version subtitle from the HeaderBar.

---

## [2.0.0] - 2026-03-18

### 🎉 Added
- Complete modular architecture (core/, ui/, utils/, config/, locale/, assets/)
- Advanced support for Wayland, GNOME, Plasma, and XFCE
- **Unified environment detection (core/environment.py) for DE, protocol, and system theme**
- **Advanced KDE dark theme detection (Colors:Window parsing & LookAndFeelPackage)**
- **Advanced GNOME & KDE previews with Xephyr bridge for Wayland and xterm for TTY-based themes**
- **Robust single-password prompt mechanism for text/TTY themes across all Wayland sessions**
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
- **Standard-compliant logging at ~/.cache/soplos-plymouth-manager/**
- **Minimized password prompts via unified pkexec logic for preview generation**
- Unified privilege management via `pkexec`
- Complete internationalization with native support for 8 languages via gettext
- **Enhanced progress reporting with smooth updates during initramfs generation**

### 🐛 Fixed
- Removed duplicated footer
- Corrected asymmetric preview centering
- Fixed CSS syntax errors for GTK 3 compatibility
- **Fixed progress bar stuck at 20% during long operations**
- **Fixed installation issues with nested folder structures in theme bundles**

---

## Legacy 1.x — Prior to Unification

Before version 2.0.0, the project existed as two separate branches:

- **Tyron** (XFCE + X11): versions 1.0.0 – 1.0.6, released April–May 2025
- **Tyson** (Plasma 6 + Wayland): versions 1.0.0 – 1.0.5, released May–July 2025

Both branches were merged and unified into version 2.0.0 (March 2026).

---

### Tyron branch

#### [1.0.6] - 2025-05-08

##### 🐛 Fixed
- Stability and compatibility: additional fixes and improvements for the Tyron environment.

#### [1.0.5] - 2025-05-08

##### 🐛 Fixed
- Internal cleanup and minor corrections for the Tyron build.

#### [1.0.4] - 2025-05-07

##### 🎨 Changed
- Program icon changed.
- Developer updated to Sergi Perich.

#### [1.0.3] - 2025-05-06

##### 🛠️ Improved
- Metainfo update for AppStream/DEP-11 compliance.
- Renamed screenshots to screenshot1.png, screenshot2.png, etc.
- Minor documentation and metadata improvements. No functional changes.

#### [1.0.2] - 2025-05-02

##### 🔧 Changed
- Packaging format updated to standard `_all.deb` structure.

#### [1.0.1] - 2025-05-02

##### 🌟 Improved
- Screenshots and app icons added (48×48, 64×64, 128×128).
- AppStream metainfo added.

#### [1.0.0] - 2025-04-13

##### 🎉 Initial Tyron Release
- Graphical interface for managing Plymouth themes.
- Preview, install, and apply themes with one click.
- Advanced configuration.
- Multi-language support (8 languages).
- Compatible with Soplos Linux and derivatives.

---

### Tyson branch

#### [1.0.5] - 2025-07-18

##### 🌟 Improved
- **Metainfo finalized** for AppStream/DEP-11 compliance.
- **Program icons** added in 48×48, 64×64 and 128×128 for software center compatibility.
- Program icon updated.

#### [1.0.4] - 2025-07-15

##### 🌟 Improved
- **Metainfo finalized** for AppStream/DEP-11 compliance.
- **Program icons** added in 48×48, 64×64 and 128×128 for software center compatibility.
- Minor structure and tag improvements.

#### [1.0.3] - 2025-07-15

##### 🐛 Fixed
- **Metainfo corrections:** Final fixes to ensure full visibility in software centers.
- Validated across Plasma Discover, GNOME Software and other AppStream-compatible centers.

#### [1.0.2] - 2025-06-18

##### ✨ Added
- **Dynamic translation system** with on-demand loading.
- **8 languages fully supported:** ES, EN, FR, PT, DE, IT, RU, RO.
- **Automatic language detection** based on `$LANG` with English fallback.

#### [1.0.1] - 2025-06-15

##### 🌟 Improved
- **System theme detection:** Automatic dark/light theme detection.
- **Wayland improvements:** Better compatibility with Plasma 6 Wayland sessions.

#### [1.0.0] - 2025-05-09

##### 🎉 Initial Tyson Release
- Complete graphical Plymouth theme manager with intuitive GTK3 interface.
- Preview, install, and apply themes with one click.
- Advanced configuration, automatic OS detection, automatic backup system.
- Secure `update-initramfs` integration with minimum privileges.
- Keyboard shortcuts and configuration validation.

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

- **Documentation**: https://soplos.org/wiki
- **Community**: https://soplos.org/
- **Support**: info@soploslinux.com
