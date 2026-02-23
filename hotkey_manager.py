import keyboard
import threading

class HotkeyManager:
    def __init__(self, settings_manager, on_toggle_callback):
        self.settings = settings_manager
        self.on_toggle_callback = on_toggle_callback
        self.hotkey_hook = None
        self.setup_hotkey()

    def setup_hotkey(self):
        hotkey = self.settings.get("hotkey")
        
        if self.hotkey_hook:
            keyboard.remove_hotkey(self.hotkey_hook)
            
        print(f"Registering hotkey: {hotkey}")
        try:
            # We use suppress=True so the hotkey doesn't reach the active window
            self.hotkey_hook = keyboard.add_hotkey(hotkey, self._on_activated, suppress=True)
        except Exception as e:
            print(f"Failed to set hotkey: {e}")

    def _on_activated(self):
        # run callback in a separate thread to prevent blocking the keyboard hook
        threading.Thread(target=self.on_toggle_callback, daemon=True).start()

    def reload(self):
        self.setup_hotkey()
