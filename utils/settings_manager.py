import os
import json

from utils.logger import get_logger

logger = get_logger(__name__)

# CONFIG_FILE_NAME = "~/.config/graphviewer/config.json"

# CONFIG_PATH = os.path.expanduser(CONFIG_FILE_NAME)

# DEFAULT_SETTINGS = {
#     "theme": "System",
#     "plotting_directory": os.path.expanduser("~"),
#     "saving_directory": os.path.expanduser("~"),
#     "last_file_opened": None,
# }


class SettingsManager:
    def __init__(self):
        self.config_file = "~/.config/graphviewer/config.json"
        self.config_path = os.path.expanduser(self.config_file)

        self.default_settings = {
            "theme": "System",
            "plotting_directory": os.path.expanduser("~"),
            "saving_directory": os.path.expanduser("~"),
            "last_file_opened": None,
        }

        self.settings = {}
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    file_data = json.load(f)
                    logger.info(f"Loading settings from disk > {json.dumps(file_data, indent=4)}")
                    self.settings = {**self.default_settings, **file_data}
            except Exception as e:
                logger.error(f"Failed to load settings > {e}")
                self.setting = self.default_settings.copy()
        else:
            self.settings = self.default_settings.copy()
            logger.info(f"Config file not found. Creating with default settings > {self.settings}")
            self.save_settings()

# Not optimized to write all settings every time!
    def save_settings(self):
        # logger.debug(f"Saving settings to disk > {self.settings}")
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.settings, f, indent=4, sort_keys=True)
        logger.info(f"Saved settings > {json.dumps(self.settings, indent=4)}")

    def update_setting(self, key, value):
        """Aggiorna una singola chiave e salva."""
        logger.info(f"Updating setting '{key}' = {value}")
        self.settings[key] = value
        self.save_settings()

    def get_theme(self):
        return self.settings.get("theme", "Sistema")

    def set_theme(self, theme):
        self.update_setting("theme", theme)

    def read_plotting_directory(self):
        return self.settings.get("plotting_directory", os.path.expanduser("~"))
    
    def save_plotting_directory(self, folder_path):
        logger.info(f"Saving plotting directory {folder_path} on file {self.config_file}")
        self.settings["plotting_directory"] = folder_path
        self.save_settings()

    def read_saving_directory(self):
        return self.settings.get("saving_directory", os.path.expanduser("~"))

    def save_saving_directory(self, folder_path):
        logger.info(f"Saving saving directory {folder_path} on file {self.config_file} ")
        self.settings["saving_directory"] = folder_path
        self.save_settings()

    def read_last_file_opened(self):
        return self.settings.get("last_file_opened", None)

    def save_last_file_opened(self, file_name):
        logger.info(f"Saving last file opened {file_name} on file {self.config_file}")
        self.settings["last_file_opened"] = file_name
        self.save_settings()