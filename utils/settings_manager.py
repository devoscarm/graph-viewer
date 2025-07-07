import os
import json

from utils.logger import get_logger

logger = get_logger(__name__)

CONFIG_PATH = os.path.expanduser("~/.config/graphviewer/config.json")

DEFAULT_SETTINGS = {
    "theme": "System",
    "plotting_directory": os.path.expanduser("~"),
}


class SettingsManager:
    def __init__(self):
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    file_data = json.load(f)
                    logger.info(f"Loading settings from disk > {file_data}")
                    self.settings = {**DEFAULT_SETTINGS, **file_data}
            except Exception as e:
                logger.error(f"Failed to load settings > {e}")
                self.setting = DEFAULT_SETTINGS.copy()
        else:
            self.setting = DEFAULT_SETTINGS.copy()
            logger.info(f"Config file not found. Creating with default settings > {self.settings}")
            self.save_settings()

    def save_settings(self):
        logger.debug(f"Saving settings to disk > {self.settings}")
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.settings, f, indent=4, sort_keys=True)
        logger.info(f"Saved setting > {self.settings}")

    def update_setting(self, key, value):
        """Aggiorna una singola chiave e salva."""
        logger.info(f"Updating setting '{key}' = {value}")
        self.settings[key] = value
        self.save_settings()

    def get_theme(self):
        return self.settings.get("theme", "Sistema")

    def set_theme(self, theme):
        self.update_setting("theme", theme)

    def get_plotting_directory(self):
        return self.settings.get("plotting_directory", os.path.expanduser("~"))
    
    def set_plotting_directory(self, folder_path):
        logger.info(f"Setting plotting directory to > {folder_path}")
        self.settings["plotting_directory"] = folder_path
        self.save_settings()