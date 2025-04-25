import os
import json


CONFIG_PATH = os.path.expanduser("~/.config/graphviewer/config.json")




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