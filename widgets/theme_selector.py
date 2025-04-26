import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from utils.settings_manager import SettingsManager
from components.base import BoxBase


class ThemeSwitcher(BoxBase):
    def __init__(self):
        super().__init__()
        self.set_orientation(orientation=Gtk.Orientation.HORIZONTAL)
        self.settings_manager = SettingsManager()

        self.theme_model = Gtk.StringList.new(["System", "Light", "Dark"])
        self.theme_combo = Gtk.DropDown()
        self.theme_combo.set_model(self.theme_model)

        initial = self.settings_manager.get_theme()
        if initial in ["System", "Light", "Dark"]:
            self.theme_combo.set_selected(["System", "Light", "Dark"].index(initial))
        else:
            self.theme_combo.set_selected(0)

        self.theme_combo.connect("notify::selected", self.on_theme_change)
        # self.append(Gtk.Label(label="Tema: "))
        self.append(self.theme_combo)
        self.apply_theme(initial)

    def on_theme_change(self, combo, param):
        index = combo.get_selected()
        theme = ["System", "Light", "Dark"][index]
        self.settings_manager.set_theme(theme)
        self.apply_theme(theme)

    def apply_theme(self, theme):
        style_manager = Adw.StyleManager.get_default()
        if theme == "System":
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
        elif theme == "Light":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        elif theme == "Dark":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
