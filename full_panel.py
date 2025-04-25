# file: full_panel.py

import gi
import sys
import os
import json

CONFIG_PATH = os.path.expanduser("~/.config/graphviewer/config.json")


gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Adw, Gdk

Adw.init()


class SettingsManager:
    def __init__(self):
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_settings(self):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.settings, f)

    def get_theme(self):
        return self.settings.get("theme", "Sistema")

    def set_theme(self, theme):
        self.settings["theme"] = theme
        self.save_settings()


class ThemeSwitcher(Gtk.Box):
    def __init__(self, settings_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.settings_manager = settings_manager

        self.theme_model = Gtk.StringList.new(["Sistema", "Chiaro", "Scuro"])
        self.theme_combo = Gtk.DropDown()
        self.theme_combo.set_model(self.theme_model)

        initial = self.settings_manager.get_theme()
        if initial in ["Sistema", "Chiaro", "Scuro"]:
            self.theme_combo.set_selected(["Sistema", "Chiaro", "Scuro"].index(initial))
        else:
            self.theme_combo.set_selected(0)

        self.theme_combo.connect("notify::selected", self.on_theme_change)
        self.append(Gtk.Label(label="Tema: "))
        self.append(self.theme_combo)
        self.apply_theme(initial)

    def on_theme_change(self, combo, param):
        index = combo.get_selected()
        theme = ["Sistema", "Chiaro", "Scuro"][index]
        self.settings_manager.set_theme(theme)
        self.apply_theme(theme)

    def apply_theme(self, theme):
        style_manager = Adw.StyleManager.get_default()
        if theme == "Sistema":
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
        elif theme == "Chiaro":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        elif theme == "Scuro":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)


class SideBar(Gtk.Box):
    def __init__(self, position='left'):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_size_request(250, -1)
        self.visible = True
        self.label = Gtk.Label(label=f"Barra {position}")
        self.append(self.label)

    def toggle_visibility(self):
        self.set_visible(not self.get_visible())


class TopBar(Gtk.Box):
    def __init__(self, theme_switcher):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.set_size_request(-1, 40)
        self.label = Gtk.Label(label="Barra Superiore")
        self.append(self.label)
        self.append(theme_switcher)


class GraphDisplay(Gtk.Box):
    def __init__(self, name="Grafico"):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.label = Gtk.Label(label=f"[{name} qui]")
        self.append(self.label)
        self.update_background()

    def update_background(self):
        style_manager = Adw.StyleManager.get_default()
        scheme = style_manager.get_color_scheme()
        if scheme == Adw.ColorScheme.FORCE_DARK:
            color = Gdk.RGBA(red=0.15, green=0.15, blue=0.15, alpha=1.0)
        elif scheme == Adw.ColorScheme.FORCE_LIGHT:
            color = Gdk.RGBA(red=0.92, green=0.92, blue=0.92, alpha=1.0)
        else:
            color = Gdk.RGBA(red=0.85, green=0.85, blue=0.85, alpha=1.0)
        self.set_background_color(color)

    def set_background_color(self, rgba):
        css_provider = Gtk.CssProvider()
        css = f"background-color: rgba({int(rgba.red*255)}, {int(rgba.green*255)}, {int(rgba.blue*255)}, {rgba.alpha});"
        css_provider.load_from_data(f"#graph-bg {{ {css} }}".encode())
        self.set_name("graph-bg")
        style_context = self.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


class GraphTab(Gtk.Box):
    def __init__(self, name):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.left_sidebar = SideBar(position='left')
        self.right_sidebar = SideBar(position='right')
        self.graph_display = GraphDisplay(name=name)

        self.append(self.left_sidebar)
        self.append(self.graph_display)
        self.append(self.right_sidebar)


class GraphTabContainer(Gtk.Notebook):
    def __init__(self):
        super().__init__()
        self.set_tab_pos(Gtk.PositionType.TOP)
        self.plus_tab = Gtk.Box()
        self.connect('switch-page', self.on_tab_switch)
        self.add_graph_tab("Grafico 1")
        self.add_plus_tab()

    def add_graph_tab(self, name):
        tab_content = GraphTab(name)
        label = Gtk.Label(label=name)
        self.insert_page(tab_content, label, self.get_n_pages() - 1)
        self.set_current_page(self.get_n_pages() - 2)

    def add_plus_tab(self):
        self.plus_tab = Gtk.Box()
        label = Gtk.Label(label='+')
        self.append_page(self.plus_tab, label)

    def on_tab_switch(self, notebook, page, page_num):
        temp_plus = self.plus_tab
        if page == temp_plus:
            self.remove_page(page_num)
            self.add_graph_tab(f"Grafico {self.get_n_pages()}")
            self.add_plus_tab()
            self.set_current_page(self.get_n_pages() - 2)


class GraphApp(Gtk.Application):
    def __init__(self):
        unique_id = f"com.osan.graphviewer.instance_{os.getpid()}"
        super().__init__(application_id=unique_id, flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect('activate', self.on_activate)
        self.settings_manager = SettingsManager()

    def on_activate(self, app):
        self.window = Gtk.ApplicationWindow(application=app)
        self.window.set_default_size(1000, 700)
        self.window.set_title('Pannello Grafici')

        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.window.set_child(root_box)

        theme_switcher = ThemeSwitcher(self.settings_manager)
        self.top_bar = TopBar(theme_switcher)
        root_box.append(self.top_bar)

        self.graph_tabs = GraphTabContainer()
        root_box.append(self.graph_tabs)

        self.window.present()


if __name__ == '__main__':
    app = GraphApp()
    app.run(sys.argv)
