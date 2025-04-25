# file: full_panel.py

import gi
import sys

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio


class SideBar(Gtk.Box):
    def __init__(self, position='left'):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_size_request(-1, 250)
        self.visible = True
        self.label = Gtk.Label(label=f"Barra {position}")
        self.append(self.label)

    def toggle_visibility(self):
        self.set_visible(not self.get_visible())


class TopBar(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.set_size_request(-1, 40)
        self.label = Gtk.Label(label="Barra Superiore")
        self.append(self.label)


class GraphDisplay(Gtk.Box):
    def __init__(self, name="Grafico"):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.label = Gtk.Label(label=f"[{name} qui]")
        self.append(self.label)


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
        if page == self.plus_tab:
            self.remove_page(page_num)
            self.add_graph_tab(f"Grafico {self.get_n_pages()}")
            self.add_plus_tab()


class GraphApp(Gtk.Application):
    def __init__(self):
        # super().__init__(application_id='com.osan.graphviewer', flags=Gio.ApplicationFlags.FLAGS_NONE)
        super().__init__(application_id="Diocane", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.window = Gtk.ApplicationWindow(application=app)
        self.window.set_default_size(1000, 700)
        self.window.set_title('Pannello Grafici')

        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.window.set_child(root_box)

        self.top_bar = TopBar()
        root_box.append(self.top_bar)

        self.graph_tabs = GraphTabContainer()
        root_box.append(self.graph_tabs)

        self.window.present()


if __name__ == '__main__':
    app = GraphApp()
    app.run(sys.argv)
