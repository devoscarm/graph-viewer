import os
from pathlib import Path # Metodo più moderno di "os" consigliato da chatgpt per python > 3.6
from gi.repository import Gtk, Pango

from widgets.folder_selector import FolderSelector
from utils.logger import get_logger

logger = get_logger(__name__)

class PlotSaver(Gtk.Box):
    def __init__(self, 
                window_context, 
                settings_manager = None,
        ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.window_context = window_context
        self.settings_manager = settings_manager # For saving the saving directory on file

        self.saving_dir = settings_manager.get_saving_directory()
        self.file_name = None

        self.widget = Gtk.Box(
            orientation = Gtk.Orientation.VERTICAL,
            spacing = 6    
        )
        self.append(self.widget)
        
# Directory selector line
        self.dir_selector = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL, 
            spacing = 6
        )
        self.widget.append(self.dir_selector)

        self.folder_selector = FolderSelector(
            parent_window=window_context.window,
            on_folder_selected_callback=self.save_saving_direcotory
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
        self.save_button = Gtk.Button(label="PNG")
        self.save_button.connect("clicked", self.on_save_clicked)
        self.widget.append(self.save_button)


    def on_save_clicked(self, button):
        plot_manager = self.window_context.plot_manager
        settings_manager = self.settings_manager

        figure = plot_manager.figure

        # Base name = nome del file caricato

        last_file_opened = Path(settings_manager.get_last_file_opened())
        self.saving_dir = Path(settings_manager.get_saving_directory())
        
        if self.name_entry.get_text():
            self.base_name = self.name_entry.get_text()
            logger.info(f"Saving file with user entry > {self.base_name}")
        elif settings_manager.get_last_file_opened():
            self.base_name = Path(settings_manager.get_last_file_opened()).stem
            logger.info(f"Saving file with last file opened name > {self.base_name}")
        else:
            self.base_name = "plot"
            logger.info(f"Saving file with temporary name > {self.base_name}")
        
        logger.debug(f"saving directory > {self.saving_dir}")
        logger.debug(f"last file opened > {last_file_opened}")


        self.suffix = ".png"
        filename = Path(self.base_name).with_suffix(self.suffix)
        full_path = self.saving_dir / filename
        #full_path = os.path.join(saving_dir, filename)

        # Evita sovrascrittura
        count = 1
        while full_path.exists():
            filename = Path(f"{self.base_name}_{count}").with_suffix(self.suffix)
            full_path = self.saving_dir / filename
            count += 1

        

        try:
            figure.savefig(full_path, dpi=300)
            print(f"[INFO] Grafico salvato in: {full_path}")
        except Exception as e:
            print(f"[ERRORE] Salvataggio fallito: {e}")




    def save_saving_direcotory(self, folder_path):
        """
            Callback function for saving the saving directory on file
        """
        
        logger.debug(f"Questa è la funzione di callback! (save_plotting_directory di PlotSaver)")
        self.saving_dir = folder_path
        self.dir_label.set_label(folder_path)

        try:
            self.settings_manager.set_saving_directory(folder_path)
        except Exception as e:
            logger.error(f"Saving saving directory > {e} ")
    