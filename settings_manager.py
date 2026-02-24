import json
import os
import sys

def _resolve_config_path(filename):
    """Return an absolute path for config next to the EXE (frozen) or script (dev)."""
    if not os.path.isabs(filename):
        base = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) \
               else os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, filename)
    return filename

class SettingsManager:
    def __init__(self, config_file="config.json"):
        config_file = _resolve_config_path(config_file)
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
        val = self.settings.get(key, self.default_settings.get(key))
        if key == "hotkey" and isinstance(val, str):
            # Translate pynput style keys to keyboard library style
            val = val.replace("<ctrl>", "ctrl").replace("<shift>", "shift")
            val = val.replace("<alt>", "alt").replace("<cmd>", "windows")
            val = val.replace("<space>", "space").replace("<esc>", "esc").replace("<tab>", "tab")
            val = val.replace("<enter>", "enter").replace("<backspace>", "backspace")
        return val

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

settings = SettingsManager()
