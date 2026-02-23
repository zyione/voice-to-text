from faster_whisper import WhisperModel
import os
import sys

class Transcriber:
    def __init__(self, settings_manager):
        self.settings = settings_manager
        self.model = None
        self.current_model_size = None
        self.load_model()

    def load_model(self):
        model_size = self.settings.get("model_size")
        device = self.settings.get("device")
        compute_type = self.settings.get("compute_type")
        
        # default fallbacks
        if device == "auto" or not device:
            device = "auto"
        if compute_type == "default" or not compute_type:
            compute_type = "default"

        if self.model is None or self.current_model_size != model_size:
            print(f"Loading Whisper model '{model_size}' on {device} ({compute_type})...")
            try:
                self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
                self.current_model_size = model_size
                print("Model loaded successfully.")
            except Exception as e:
                print(f"Failed to load model: {e}")
                print("Falling back to CPU / int8...")
                try:
                    self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
                    self.current_model_size = model_size
                except Exception as e2:
                    print(f"Fatal error loading model: {e2}")

    def transcribe(self, audio_file):
        if not self.model:
            self.load_model()
            
        if not audio_file or not os.path.exists(audio_file):
            return ""

        vocab = self.settings.get("custom_vocabulary")
        initial_prompt = vocab if vocab else None

        print(f"Transcribing {audio_file}...")
        try:
            segments, info = self.model.transcribe(audio_file, beam_size=5, initial_prompt=initial_prompt)
            
            # segments is a generator, so we need to iterate it
            text = "".join([segment.text for segment in segments])
            print(f"Transcription complete: {text}")
        except Exception as e:
            print(f"Transcription error: {e}")
            text = ""
            
        # Cleanup temp file
        try:
            os.remove(audio_file)
        except Exception as e:
            print(f"Cleanup error: {e}")
            
        return text
