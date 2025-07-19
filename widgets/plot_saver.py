import os
from pathlib import Path # Metodo più moderno di "os" consigliato da chatgpt per python > 3.6
from gi.repository import Gtk, Pango

from widgets.folder_selector import FolderSelector
from utils.logger import get_logger

logger = get_logger(__name__)

# Supported formats
FORMATS = [".png", ".jpg", ".svg"]


class PlotSaver(Gtk.Box):
    def __init__(self, 
                window_context, 
                settings_manager = None,
        ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.window = window_context.window # For the folder selector
        self.plot_manager = window_context.plot_manager # For saving the plot
        self.settings_manager = settings_manager # For saving the saving directory on file

        self.saving_dir = self.get_saving_directory()
        # Last opened file read from config file
        self.file_path = self.get_opened_file_path()
        # Extracting the stem (file name without suffix and parents)
        self.file_name = self.file_path.stem if self.file_path else None

        logger.debug(f"saving dir > {self.saving_dir}")
        logger.debug(f"file_name (stem) > {self.file_name}")

# Widget "plot saver"
        self.widget = Gtk.Box(
            orientation = Gtk.Orientation.VERTICAL,
            spacing = 6    
        )
        self.append(self.widget)
        # self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

# Widget title
        self.widget_title = Gtk.Label()
        self.widget_title.set_markup("<b>Save the plot</b>")
        self.widget.append(self.widget_title)
        
# Directory selector line
        self.dir_selector = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL, 
            spacing = 6
        )
        self.widget.append(self.dir_selector)

        self.folder_selector = FolderSelector(
            parent_window=self.window,
            on_folder_selected_callback=self.set_saving_directory
        )
        self.dir_selector.append(self.folder_selector)
        self.dir_label = Gtk.Label()
        self.dir_label.set_label(str(self.saving_dir) if self.saving_dir else "Chose a folder")
        self.dir_label.set_xalign(1.08)
        self.dir_label.set_ellipsize(Pango.EllipsizeMode.START)
        self.dir_selector.append(self.dir_label)

# File name line
        self.name_entry = Gtk.Entry(
            placeholder_text = self.file_name if self.file_name else "File name"
        )
        self.widget.append(self.name_entry)


# Buttons save line
        self.buttons_line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.widget.append(self.buttons_line)

        # Supported formats
        # self.formats = [".png", ".jpg", ".svg"]

        for fmt in FORMATS:
            button = Gtk.Button(label=fmt.upper().replace('.', ''))  # PNG, JPG, SVG
            button.connect("clicked", self.on_save_clicked_factory(fmt))
            self.buttons_line.append(button)

        


    def on_save_clicked_factory(self, suffix):
        """
            Function connected to the button, returned as callback 
            connected to the widget that emitted the signal.
        """

        # Gtk pass that button so we need it even if not accessed
        def handler(button):
            """
                Closure: internal function returned from the external 
                environment. She remembers locals variable defined in 
                the external environment
                This enclosure system is required by the use of the 
                loop, by the "recycling of the button"
            """

            # Title entered by the user (if any)
            file_stem = self.name_entry.get_text()
            # Wins the user entry, otherwise last file opened
            self.base_name = file_stem if file_stem else self.file_name

            # Fallback if can't find a fucking name
            if not self.base_name:
                self.base_name = 'plot'

            filename = Path(self.base_name).with_suffix(suffix)
            full_path = self.saving_dir / filename

            count = 1
            while full_path.exists():
                logger.info(f"File {filename} already present in {self.saving_dir}")
                filename = Path(f"{self.base_name}_{count}").with_suffix(suffix)
                logger.info(f"Trying with filename > {filename}")
                full_path = self.saving_dir / filename
                count += 1

            try:
                figure = self.plot_manager.figure
                figure.savefig(full_path, dpi=300, bbox_inches='tight')
                logger.info(f"Plot saved in: {full_path}")
                self.plot_manager.canvas.draw()
            except Exception as e:
                logger.error(f"Failed saving file: {e}")

        return handler


    def get_opened_file_path(self) -> Path | None:
        """
            Use the settings manager for reading the last opened file path
        """

        try:
            opened_file = self.settings_manager.read_last_file_opened()
            opened_file_path = Path(opened_file) if opened_file else None
            return opened_file_path
        except Exception as e:
            logger.error(f"Reading last opened file path > {e}")
            return None


    def get_saving_directory(self) -> Path | None:
        """
            Use the settings manager for reading the default 
            saving directory frome the config file
        """

        try:
            saving_dir = self.settings_manager.read_saving_directory()
            saving_dir_path = Path(saving_dir) if saving_dir else None
            return saving_dir_path
        except Exception as e:
            logger.error(f"Reading saving directory > {e}")
            return None


    def set_saving_directory(self, folder_path):
        """
            Callback function for saving the saving directory on file
            with the settings manager
        """
        
        logger.debug(f"Questa è la funzione di callback! (save_plotting_directory di PlotSaver)")
        self.saving_dir = folder_path
        self.dir_label.set_label(folder_path)

        try:
            self.settings_manager.save_saving_directory(folder_path)
        except Exception as e:
            logger.error(f"Saving saving directory > {e} ")
    