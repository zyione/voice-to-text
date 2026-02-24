import os
import sys
import site

# ─── Ensure NVIDIA CUDA DLLs are discoverable on Windows ───
def _setup_cuda_dll_paths():
    """Add nvidia package DLL dirs to PATH so cublas64_12.dll etc. are found."""
    try:
        sp = site.getsitepackages() if hasattr(site, "getsitepackages") else []
        sp.append(os.path.join(sys.prefix, "Lib", "site-packages"))  # venv fallback
        for p in sp:
            # Check the "nvidia" directory created by pip
            nvidia_dir = os.path.join(p, "nvidia")
            if os.path.isdir(nvidia_dir):
                for pkg in os.listdir(nvidia_dir):
                    pkg_dir = os.path.join(nvidia_dir, pkg)
                    if os.path.isdir(pkg_dir):
                        for sub in ("bin", "lib"):
                            target_dir = os.path.join(pkg_dir, sub)
                            if os.path.isdir(target_dir):
                                os.environ["PATH"] = target_dir + os.pathsep + os.environ.get("PATH", "")
                                if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
                                    os.add_dll_directory(target_dir)
            # Also check old direct package names just in case
            for pkg in ("nvidia_cublas_cu12", "nvidia_cudnn_cu12"):
                dll_dir = os.path.join(p, pkg, "bin")
                if os.path.isdir(dll_dir):
                    os.environ["PATH"] = dll_dir + os.pathsep + os.environ.get("PATH", "")
                    if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
                        os.add_dll_directory(dll_dir)
    except Exception as e:
        print(f"Warning: Could not setup CUDA DLL paths: {e}")

_setup_cuda_dll_paths()

from faster_whisper import WhisperModel

class Transcriber:
    def __init__(self, settings_manager):
        self.settings = settings_manager
        self.model = None
        self.current_model_size = None
        self.active_device = None
        self.active_compute = None
        self.load_model()

    def load_model(self):
        model_size = self.settings.get("model_size")
        device = self.settings.get("device")
        compute_type = self.settings.get("compute_type")

        # Resolve "auto" / "default" to concrete values
        if not device or device == "auto":
            device = "cuda"           # Try GPU first
        if not compute_type or compute_type == "default":
            compute_type = "float16"  # Optimal for RTX 3060

        if self.model is not None and self.current_model_size == model_size:
            return  # Already loaded, nothing to do

        print(f"Loading Whisper model '{model_size}' on {device} ({compute_type})...")
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
            self.current_model_size = model_size
            self.active_device = device
            self.active_compute = compute_type
            print(f"Model loaded successfully on {device}.")
        except Exception as e:
            print(f"Failed to load model on {device}: {e}")
            if device != "cpu":
                print("Falling back to CPU / int8...")
                try:
                    self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
                    self.current_model_size = model_size
                    self.active_device = "cpu"
                    self.active_compute = "int8"
                    print("Fallback to CPU successful.")
                except Exception as e2:
                    print(f"Fatal error loading model: {e2}")

    def _reload_on_cpu(self):
        """Force reload the model on CPU (used as a recovery path)."""
        model_size = self.settings.get("model_size")
        print("Reloading model on CPU / int8 for recovery...")
        try:
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            self.current_model_size = model_size
            self.active_device = "cpu"
            self.active_compute = "int8"
            print("CPU fallback model loaded.")
        except Exception as e:
            print(f"Fatal: could not load fallback model: {e}")
            self.model = None

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
            text = "".join([segment.text for segment in segments])
            print(f"Transcription complete: {text}")
        except Exception as e:
            err_msg = str(e).lower()
            # If CUDA / cuBLAS error during transcription, retry on CPU
            if any(kw in err_msg for kw in ("cublas", "cuda", "gpu", "cudnn")):
                print(f"CUDA error during transcription: {e}")
                self._reload_on_cpu()
                if self.model:
                    try:
                        segments, info = self.model.transcribe(audio_file, beam_size=5, initial_prompt=initial_prompt)
                        text = "".join([segment.text for segment in segments])
                        print(f"Transcription complete (CPU fallback): {text}")
                    except Exception as e2:
                        print(f"Transcription failed on CPU fallback: {e2}")
                        text = ""
                else:
                    text = ""
            else:
                print(f"Transcription error: {e}")
                text = ""

        # Cleanup temp file
        try:
            os.remove(audio_file)
        except Exception as e:
            print(f"Cleanup error: {e}")

        return text
