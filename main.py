import time
import threading
import sys
from settings_manager import settings
from audio_recorder import AudioRecorder
from transcriber import Transcriber
from text_injector import injector
from hotkey_manager import HotkeyManager
from llm_processor import LLMProcessor
from tray_icon import TrayIcon
from overlay_ui import OverlayUI

class VoiceTyperApp:
    def __init__(self):
        self.overlay = OverlayUI()
        self.recorder = AudioRecorder(on_volume_update=self.overlay.update_volume)
        self.transcriber = Transcriber(settings)
        self.llm = LLMProcessor(settings)
        self.hotkey_manager = HotkeyManager(settings, self.toggle_recording)
        
        self.is_recording = False
        self.tray_icon = TrayIcon(self, self.quit_app)
        
        # Wire up injection failure notifications to the tray icon
        injector.set_notification_callback(self.tray_icon.notify_user)

    def toggle_recording(self):
        if self.is_recording:
            # Stop
            self.overlay.hide()
            self.is_recording = False
            self.tray_icon.set_status('transcribing')
            
            # Fetch audio file
            audio_file = self.recorder.stop_recording()
            if audio_file:
                # Transcribe
                text = self.transcriber.transcribe(audio_file)
                
                # Optional LLM processing
                if text:
                    text = self.llm.process(text)
                
                # Type it out
                injector.type_text(text)
                
            self.tray_icon.set_status('idle')
        else:
            # Start
            self.is_recording = True
            self.tray_icon.set_status('recording')
            self.overlay.show()
            self.recorder.start_recording()

    def run(self):
        print("Voice Typer App is starting...")
        print(f"Press {settings.get('hotkey')} to start/stop dictation.")
        self.tray_icon.run()

    def quit_app(self):
        print("Exiting Voice Typer...")
        self.overlay.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = VoiceTyperApp()
    app.run()

