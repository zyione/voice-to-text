import sys
import sounddevice as sd
import soundfile as sf
import tempfile
import queue
import threading
import os
import numpy as np

class AudioRecorder:
    def __init__(self, samplerate=16000, channels=1, on_volume_update=None):
        self.samplerate = samplerate
        self.channels = channels
        self.q = queue.Queue()
        self.recording = False
        self.thread = None
        self.filename = None
        self.on_volume_update = on_volume_update

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())
        
        if self.on_volume_update:
            # calculate volume (RMS)
            rms = np.sqrt(np.mean(indata**2))
            self.on_volume_update(rms)

    def start_recording(self):
        if self.recording:
            return
            
        print("Starting recording...")
        self.recording = True
        fd, self.filename = tempfile.mkstemp(suffix='.wav')
        os.close(fd) # Close it so soundfile can open it
        
        # clear queue
        while not self.q.empty():
            self.q.get()

        self.thread = threading.Thread(target=self._record_thread)
        self.thread.start()

    def _record_thread(self):
        try:
            with sf.SoundFile(self.filename, mode='w', samplerate=self.samplerate, channels=self.channels) as file:
                with sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=self.callback):
                    while self.recording:
                        item = self.q.get()
                        if item is None:
                            break
                        file.write(item)
        except Exception as e:
            print(f"Error during recording: {e}")

    def stop_recording(self):
        if not self.recording:
            return self.filename
            
        print("Stopping recording...")
        self.recording = False
        if self.thread and self.thread.is_alive():
            # To ensure the loop unblocks, put a dummy in queue
            self.q.put(None)
            self.thread.join()
        
        return self.filename
