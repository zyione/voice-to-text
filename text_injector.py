import keyboard
import time

class TextInjector:
    def type_text(self, text):
        if not text:
            return
            
        text = text.strip()
        if not text:
            return
            
        print(f"Injecting text: {text}")
        
        # A tiny delay to ensure the hotkey is fully released before typing
        time.sleep(0.1)
        
        try:
            # Write characters. Add space at the end to prepare for next word.
            keyboard.write(text + " ", delay=0.005)
        except Exception as e:
            print(f"Error injecting text: {e}")

injector = TextInjector()
