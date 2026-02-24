import keyboard
import time
import pyautogui

class TextInjector:
    def __init__(self):
        self.notification_callback = None

    def set_notification_callback(self, cb):
        self.notification_callback = cb

    def type_text(self, text):
        if not text:
            return
            
        text = text.strip()
        if not text:
            return
            
        print(f"Injecting text: {text}")
        
        # A tiny delay to ensure the hotkey is fully released before typing
        time.sleep(0.1)
        
        out_text = text + " "
        try:
            # First try the normal keyboard write
            keyboard.write(out_text, delay=0.005)
        except Exception as e:
            print(f"keyboard.write failed: {e}")
            try:
                # Fallback to pyautogui just in case it works
                pyautogui.typewrite(out_text, interval=0.005)
            except Exception as e2:
                print(f"pyautogui also failed: {e2}")
                if self.notification_callback:
                    self.notification_callback("Text Injection Failed", 
                        "The current app is blocking text input (it may be running as administrator or incompatible).")

injector = TextInjector()
