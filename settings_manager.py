import json
import os

class SettingsManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_settings = {
            "hotkey": "<ctrl>+<space>",
            "model_size": "base",
            "device": "auto",
            "compute_type": "default",
            "custom_vocabulary": "",
            "llm_prompt": "Fix spelling and grammar of the following text, outputting ONLY the corrected text:",
            "use_llm": False,
            "save_history": False
        }
        self.settings = self.load_settings()

    def load_settings(self):
        if not os.path.exists(self.config_file):
            return self.default_settings.copy()
        
        try:
            with open(self.config_file, 'r') as f:
                settings = json.load(f)
                # merge with defaults
                merged = self.default_settings.copy()
                merged.update(settings)
                return merged
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_settings.copy()

    def save_settings(self, new_settings=None):
        if new_settings:
            self.settings.update(new_settings)
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key):
        return self.settings.get(key, self.default_settings.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

settings = SettingsManager()
