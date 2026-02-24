import pystray
from PIL import Image, ImageDraw
import threading
from ui_settings import show_settings

def create_image(width, height, color1, color2):
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    d = ImageDraw.Draw(image)
    d.ellipse((width//4, height//4, width*3//4, height*3//4), fill=color1, outline=color2)
    return image

class TrayIcon:
    def __init__(self, main_app, on_quit):
        self.main_app = main_app
        self.on_quit = on_quit
        
        # Icons
        self.icon_idle = create_image(64, 64, '#3498db', 'white')     # Blue
        self.icon_recording = create_image(64, 64, '#e74c3c', 'white') # Red
        self.icon_transcribing = create_image(64, 64, '#f1c40f', 'white') # Yellow
        
        menu = pystray.Menu(
            pystray.MenuItem('Settings', self.open_settings),
            pystray.MenuItem('Quit', self.quit_app)
        )
        self.icon = pystray.Icon("Voice Typer", self.icon_idle, "Voice Typer", menu)

    def open_settings(self):
        # Run settings UI in a thread so pystray doesn't lock
        def _open():
            show_settings(on_save_callback=self.main_app.hotkey_manager.reload)
        threading.Thread(target=_open, daemon=True).start()

    def quit_app(self):
        self.icon.stop()
        self.on_quit()

    def set_status(self, status):
        if status == 'recording':
            self.icon.icon = self.icon_recording
            self.icon.title = "Voice Typer (Recording...)"
        elif status == 'transcribing':
            self.icon.icon = self.icon_transcribing
            self.icon.title = "Voice Typer (Transcribing...)"
        else:
            self.icon.icon = self.icon_idle
            self.icon.title = "Voice Typer (Idle)"

    def notify_user(self, title, message):
        """Show a system toast notification."""
        if self.icon and self.icon.HAS_NOTIFICATION:
            self.icon.notify(message, title)

    def run(self):
        self.icon.run()
