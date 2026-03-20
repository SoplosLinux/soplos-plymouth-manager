"""
Main window and UI components for Soplos Plymouth Manager.
Provides the graphical interface for Plymouth theme management.
Strict Soplos Welcome style: Header + Content + Progress Revealer + Footer.
"""

import gi
import os
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf, Gdk, Gio, Pango

from core.i18n_manager import (
    _, set_language, get_current_language, get_available_languages
)
from core.plymouth_manager import PlymouthManager
from config.settings import Config
from utils.constants import (
    APPLICATION_NAME, APPLICATION_ID, APPLICATION_VERSION,
    WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT,
    PREVIEW_WINDOW_WIDTH, PREVIEW_WINDOW_HEIGHT, PREVIEW_DURATION
)
from utils.logger import logger

class ThemeCard(Gtk.Button):
    """Visual card for a Plymouth theme."""
    def __init__(self, theme_info: Dict[str, Any]):
        super().__init__()
        self.theme_info = theme_info
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.get_style_context().add_class('theme-card')
        self.connect('clicked', self._on_clicked)
        
        # Minimalist thumbnails with responsive base size
        self.set_size_request(160, 130)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.add(vbox)

        # Image box - Previsualización (Centrado Premium)
        img_box = Gtk.Box()
        img_box.set_halign(Gtk.Align.CENTER)
        img_box.set_valign(Gtk.Align.CENTER)
        img_box.get_style_context().add_class('theme-preview-box')
        img_box.set_size_request(150, 90)
        vbox.pack_start(img_box, True, True, 0)

        # Thumbnail loading logic
        if theme_info.get('preview_path'):
            try:
                # Scaled to a larger base size for responsiveness
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    theme_info['preview_path'], 150, 90, True
                )
                image = Gtk.Image.new_from_pixbuf(pixbuf)
                image.set_halign(Gtk.Align.CENTER)
                image.set_valign(Gtk.Align.CENTER)
                img_box.add(image)
            except Exception:
                image = Gtk.Image.new_from_icon_name('image-missing', Gtk.IconSize.DIALOG)
                img_box.add(image)
        else:
            image = Gtk.Image.new_from_icon_name('preferences-desktop-theme', Gtk.IconSize.DIALOG)
            img_box.add(image)

        # Name label
        label = Gtk.Label(label=theme_info['name'])
        label.get_style_context().add_class('theme-card-label')
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_max_width_chars(15)
        label.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(label, False, False, 0)

        self.show_all()

    def _on_clicked(self, btn):
        """Proxy click to parent FlowBoxChild for proper selection."""
        parent = self.get_parent()
        if isinstance(parent, Gtk.FlowBoxChild):
            flowbox = parent.get_parent()
            flowbox.select_child(parent)
            flowbox.emit('child-activated', parent)

    def set_selected(self, selected: bool):
        """Toggle selected visual state."""
        context = self.get_style_context()
        if selected:
            context.add_class('theme-card-selected')
        else:
            context.remove_class('theme-card-selected')

class PlymouthThemeManager(Gtk.ApplicationWindow):
    """
    Main window for Plymouth theme management.
    Matches the official Soplos v2.0 widget hierarchy.
    """

    def __init__(self, application, plymouth_manager: PlymouthManager, config: Config):
        super().__init__(application=application)
        self.plymouth_manager = plymouth_manager
        self.config = config
        self.application = application
        self.selected_card = None

        # Window properties
        self.set_title(_(APPLICATION_NAME))
        # Use fixed default size to ensure compactness
        self.set_default_size(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(True)

        # Apply CSS classes matching Welcome apps
        self.get_style_context().add_class('soplos-window')
        self.get_style_context().add_class('soplos-welcome-window')
        self.set_resizable(True)
        self.set_name('main-window')

        # Create HeaderBar
        self._create_header_bar()

        # Build UI Structure
        self._setup_ui()

        # Keyboard shortcuts
        self._setup_shortcuts()

        # Load themes initially
        self._load_themes_async()
        
        # Persistence disabled to ensure compactness

        self.show_all()

    def _create_header_bar(self):
        """
        Match Soplos Standard: SSD for XFCE/KDE, CSD for GNOME.
        XFCE mode (SSD) must have a COMPLETELY CLEAN title bar.
        """
        # Detect environment safely
        env_detector = self.application.get_theme_detector()
        info = env_detector.get_environment_info()
        desktop_env = info.get('desktop', 'unknown').lower()
            
        logger.info(f"HeaderBar check: Detected Desktop = {desktop_env}")

        # XFCE and KDE/Plasma work best with native window decorations (SSD)
        if desktop_env in ['xfce', 'kde', 'plasma']:
            logger.info("Using native window decorations (SSD) - Clean Titlebar")
            self.header = None
            return

        # For GNOME and others, use Client-Side Decorations (CSD)
        # But we keep it clean too, moving controls inside per Soplos 2.0 style
        logger.info("Creating Client-Side Decorations (CSD)")
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title(_(APPLICATION_NAME))
        header.set_decoration_layout("menu:minimize,maximize,close")
        header.get_style_context().add_class('titlebar')
        
        self.set_titlebar(header)
        self.header = header

    def _setup_shortcuts(self):
        """Standard Soplos shortcuts."""
        accel_group = Gtk.AccelGroup()
        self.add_accel_group(accel_group)

        # Helper to connect shortcuts safely
        def add_shortcut(key, mask, callback):
            keyval, mod = Gtk.accelerator_parse(f"<{mask}>{key}") if mask else Gtk.accelerator_parse(key)
            accel_group.connect(keyval, mod, Gtk.AccelFlags.VISIBLE, lambda *a: callback(None))

        # Quit
        add_shortcut('q', 'Control', lambda x: self.application.quit())
        
        # Refresh
        add_shortcut('r', 'Control', lambda x: self._load_themes_async())
        add_shortcut('F5', None, lambda x: self._load_themes_async())

        # Action: Apply
        add_shortcut('a', 'Control', self._on_apply_theme)
        
        # Action: Preview
        add_shortcut('p', 'Control', self._on_preview_theme)
        
        # Action: Install
        add_shortcut('i', 'Control', self._on_install_theme)
        
        # Action: Remove
        add_shortcut('Delete', None, self._on_remove_theme)

        # F1 — About dialog
        add_shortcut('F1', None, self._show_about)

    def _setup_ui(self):
        """Hierarchy: VBox -> Content -> Actions Area -> ProgressRevealer -> Footer"""
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # 1. Main Gallery Area (Directly, no Notebook)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.get_style_context().add_class('soplos-content')
        main_vbox.pack_start(scrolled, True, True, 0)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        # Responsive: No hard limit on children per line
        self.flowbox.set_max_children_per_line(20) 
        self.flowbox.set_min_children_per_line(1)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.flowbox.set_homogeneous(True)
        self.flowbox.set_row_spacing(25)
        self.flowbox.set_column_spacing(25)
        self.flowbox.set_margin_top(25)
        self.flowbox.set_margin_bottom(25)
        self.flowbox.set_margin_start(25)
        self.flowbox.set_margin_end(25)
        self.flowbox.connect('child-activated', self._on_card_activated)
        scrolled.add(self.flowbox)

        # 2. Setup Actions Area (Buttons)
        self._setup_actions_area(main_vbox)

        # 3. Progress Revealer (Hidden at bottom, above footer)
        # This is where the progress bar lives, following Soplos standard.
        self.progress_revealer = Gtk.Revealer()
        self.progress_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        revealer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        revealer_box.set_margin_start(25)
        revealer_box.set_margin_end(25)
        revealer_box.set_margin_bottom(10)
        
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        revealer_box.pack_start(self.progress_bar, False, False, 0)
        
        self.progress_label = Gtk.Label(label=_("Ready"))
        self.progress_label.get_style_context().add_class('dim-label')
        revealer_box.pack_start(self.progress_label, False, False, 0)
        
        self.progress_revealer.add(revealer_box)
        main_vbox.pack_start(self.progress_revealer, False, False, 0)

        # 4. Footer (Status Bar)
        self._create_footer(main_vbox)

    def _setup_actions_area(self, main_vbox):
        """Create actions area."""
        # 2. Main Actions Area
        actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        actions_box.set_halign(Gtk.Align.CENTER)
        actions_box.set_margin_top(15)
        actions_box.set_margin_bottom(10)
        main_vbox.pack_start(actions_box, False, False, 0)

        # Unified button helper for actions with Soplos Card style
        def add_action_btn(label, icon, callback, extra_class='soplos-button-secondary'):
            btn = Gtk.Button()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            box.set_margin_start(5)
            box.set_margin_end(5)
            box.pack_start(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON), False, False, 0)
            box.pack_start(Gtk.Label(label=label), False, False, 0)
            btn.add(box)
            btn.get_style_context().add_class(extra_class)
            btn.connect('clicked', callback)
            actions_box.pack_start(btn, False, False, 0)

        add_action_btn(_("Apply Theme"), "preferences-desktop-theme", self._on_apply_theme, 'suggested-action')
        add_action_btn(_("Preview"), "view-preview", self._on_preview_theme)
        add_action_btn(_("Install"), "document-open", self._on_install_theme)
        add_action_btn(_("Remove"), "edit-delete", self._on_remove_theme)
        add_action_btn(_("Refresh"), "view-refresh", lambda w: self._load_themes_async())

    # _create_settings_row and _on_lang_combo_changed removed as per user request
    # App now strictly follows system locale

    def _create_footer(self, parent):
        """Consistent Soplos Footer."""
        footer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        footer_box.set_margin_start(15)
        footer_box.set_margin_end(15)
        footer_box.set_margin_top(8)
        footer_box.set_margin_bottom(8)
        parent.pack_end(footer_box, False, False, 0)

        # Left: System details
        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.get_style_context().add_class('dim-label')
        footer_box.pack_start(self.status_label, False, False, 0)

        # Right: Version
        version_label = Gtk.Label(label=f"v{APPLICATION_VERSION}")
        version_label.get_style_context().add_class('dim-label')
        footer_box.pack_end(version_label, False, False, 0)

        # Initial status update
        self._update_footer_info()

    def _update_footer_info(self):
        """Update footer matching GRUB Editor style: 'Running on XFCE (X11)'"""
        env_detector = self.application.get_theme_detector()
        info = env_detector.get_environment_info()
        desktop = info.get('desktop', 'unknown').upper()
        protocol = info.get('protocol', 'unknown').upper()
        self.status_label.set_text(_("Running on {} ({})").format(desktop, protocol))

    # --- Backend Threaded Jobs ---

    def _load_themes_async(self):
        self._set_ui_state(_("Loading themes…"), pulse=True)
        def thread_target():
            themes = self.plymouth_manager.get_available_themes()
            GLib.idle_add(self._fill_gallery, themes)
        threading.Thread(target=thread_target, daemon=True).start()

    def _fill_gallery(self, themes):
        for child in self.flowbox.get_children():
            self.flowbox.remove(child)
        for theme in themes:
            self.flowbox.add(ThemeCard(theme))
        self.flowbox.show_all()
        msg = _("{num} themes loaded").format(num=len(themes))
        self._set_ui_state(msg, show_revealer=False)

    # --- UI Event Handlers ---

    def _on_selection_changed(self, flowbox):
        # We handle selection mainly in _on_card_activated for Gtk.Button children
        pass

    def _on_card_activated(self, flowbox, child):
        # Force FlowBox selection
        flowbox.select_child(child)
        
        # Deselect old card visual state
        if self.selected_card:
            self.selected_card.set_selected(False)
        
        # Select new card visual state
        self.selected_card = child.get_child()
        self.selected_card.set_selected(True)
        
        logger.info(f"Theme selected: {self.selected_card.theme_info['name']}")

    def _on_apply_theme(self, btn):
        if not self.selected_card: return
        theme = self.selected_card.theme_info
        self._set_ui_state(_("Applying {name}…").format(name=theme['name']), pulse=True)
        def progress_cb(fraction):
            GLib.idle_add(self.progress_bar.set_fraction, fraction)
        def worker():
            success = self.plymouth_manager.set_theme(theme['name'], progress_callback=progress_cb)
            GLib.idle_add(self._on_apply_finished, success)
        threading.Thread(target=worker, daemon=True).start()

    def _on_apply_finished(self, success):
        self._set_ui_state(_("Success") if success else _("Error"), show_revealer=False)

    def _on_preview_theme(self, btn):
        if not self.selected_card: return
        theme = self.selected_card.theme_info
        
        if not theme.get('is_graphical', True):
            self._set_ui_state(_("Theme is text-only"), show_revealer=False)
            dialog = Gtk.MessageDialog(
                parent=self, modal=True, message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK, text=_("Text-only Theme")
            )
            dialog.format_secondary_text(_("This theme handles text only and cannot be previewed in a window."))
            dialog.run()
            dialog.destroy()
            return

        self._set_ui_state(_("Generating Preview for {name}…").format(name=theme['name']), pulse=True)
        def worker():
            path = self.plymouth_manager.generate_preview(theme['name'])
            GLib.idle_add(self._on_preview_finished, path)
        threading.Thread(target=worker, daemon=True).start()

    def _on_preview_finished(self, path):
        if path:
            self._set_ui_state(_("Preview generated"), show_revealer=False)
            self._load_themes_async() # Refresh to show new thumbnail
        else:
            self._set_ui_state(_("Error generating preview"), show_revealer=False)

    def _on_install_theme(self, btn):
        dialog = Gtk.FileChooserDialog(
            title=_("Select Theme Bundle"), parent=self, action=Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        if dialog.run() == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            dialog.destroy()
            self._set_ui_state(_("Installing…"), pulse=True)
            def progress_cb(fraction):
                GLib.idle_add(self.progress_bar.set_fraction, fraction)
            def worker():
                success, msg = self.plymouth_manager.install_theme(path, progress_callback=progress_cb)
                GLib.idle_add(self._on_install_finished, success, msg)
            threading.Thread(target=worker, daemon=True).start()
        else:
            dialog.destroy()

    def _on_install_finished(self, success, msg):
        self._set_ui_state(msg, show_revealer=True)
        # Always hide after delay, and refresh
        GLib.timeout_add_seconds(4, lambda: self._set_ui_state("", show_revealer=False))
        self._load_themes_async()

    def _on_remove_theme(self, btn):
        if not self.selected_card: return
        name = self.selected_card.theme_info['name']
        self._set_ui_state(_("Removing {name}…").format(name=name), pulse=True)
        def worker():
            self.plymouth_manager.remove_theme(name)
            GLib.idle_add(lambda: self._load_themes_async())
        threading.Thread(target=worker, daemon=True).start()

    # --- Utility Methods ---

    def _set_ui_state(self, message: str, pulse=False, fraction=0.0, show_revealer=True):
        self.progress_label.set_text(message)
        if pulse: self.progress_bar.pulse()
        else: self.progress_bar.set_fraction(fraction)
        self.progress_revealer.set_reveal_child(show_revealer)

    def _create_language_menu(self):
        menu = Gtk.Menu()
        for code, name in get_available_languages().items():
            item = Gtk.CheckMenuItem(label=f"{name} ({code.upper()})")
            item.set_active(code == get_current_language())
            item.connect('activate', lambda i, c: set_language(c) if i.get_active() else None, code)
            menu.append(item)
        menu.show_all()
        return menu

    def _on_theme_toggle_demo(self, btn):
        logger.info("Theme toggle clicked")

    def _show_about(self, *args):
        dialog = Gtk.AboutDialog()
        dialog.set_transient_for(self)
        dialog.set_modal(True)
        dialog.set_program_name(_(APPLICATION_NAME))
        dialog.set_version(APPLICATION_VERSION)
        dialog.set_comments(_("Plymouth boot splash theme manager for Soplos Linux."))
        dialog.set_website("https://soplos.org")
        dialog.set_website_label("soplos.org")
        dialog.set_authors(["Sergi Perich <info@soploslinux.com>"])
        dialog.set_license_type(Gtk.License.GPL_3_0)
        icon_path = Path(__file__).parent.parent / 'assets' / 'icons' / '64x64' / 'org.soplos.plymouthmanager.png'
        if icon_path.exists():
            dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file_at_scale(str(icon_path), 48, 48, True))
        _about_css = Gtk.CssProvider()
        _about_css.load_from_data(b"""
            dialog, messagedialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            dialog .background, messagedialog .background {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            dialog > box, messagedialog > box {
                background-color: #2b2b2b;
            }
            dialog label, messagedialog label {
                color: #ffffff;
            }
            dialog button, messagedialog button {
                background-image: none;
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 6px 14px;
                box-shadow: none;
            }
            dialog button:hover, messagedialog button:hover {
                background-color: #444444;
                border-color: #ff8800;
            }
            dialog stackswitcher button {
                border-radius: 100px;
                background-color: #2b2b2b;
                background-image: none;
                border: 1px solid #3c3c3c;
                font-weight: normal;
                padding: 4px 16px;
                box-shadow: none;
                color: #ffffff;
            }
            dialog stackswitcher button:hover {
                background-color: #444444;
                border-color: #ff8800;
            }
            dialog stackswitcher button:checked {
                background-color: #444444;
                color: #ffffff;
            }
            dialog scrolledwindow,
            dialog scrolledwindow viewport {
                background-color: #2b2b2b;
            }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), _about_css,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        dialog.run()
        dialog.destroy()

    def _on_configure_event(self, widget, event):
        self.config.set('window_width', event.width)
        self.config.set('window_height', event.height)