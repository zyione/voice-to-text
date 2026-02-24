import tkinter as tk
from tkinter import ttk, messagebox
from settings_manager import settings

class SettingsWindow(tk.Toplevel):
    def __init__(self, master, on_save_callback=None):
        super().__init__(master)
        self.on_save_callback = on_save_callback
        self.title("Voice Typer Settings")
        self.geometry("450x520")
        self.resizable(False, False)

        # Make the window foreground
        self.attributes('-topmost', True)
        self.update()
        self.attributes('-topmost', False)

        self.init_ui()

        # Handle close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def init_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ── Hotkey ──
        ttk.Label(main_frame, text="Global Hotkey:").pack(anchor=tk.W)
        self.hotkey_var = tk.StringVar(value=settings.get("hotkey"))
        ttk.Entry(main_frame, textvariable=self.hotkey_var).pack(fill=tk.X, pady=(0, 10))

        # ── Model Size ──
        ttk.Label(main_frame, text="Whisper Model:").pack(anchor=tk.W)
        self.model_var = tk.StringVar(value=settings.get("model_size"))
        model_combo = ttk.Combobox(main_frame, textvariable=self.model_var,
                                   values=["tiny", "base", "small", "medium", "large-v3"],
                                   state="readonly")
        model_combo.pack(fill=tk.X, pady=(0, 10))

        # ── Device ──
        ttk.Label(main_frame, text="Device:").pack(anchor=tk.W)
        self.device_var = tk.StringVar(value=settings.get("device"))
        device_combo = ttk.Combobox(main_frame, textvariable=self.device_var,
                                    values=["auto", "cpu", "cuda"],
                                    state="readonly")
        device_combo.pack(fill=tk.X, pady=(0, 10))

        # ── Compute Type ──
        ttk.Label(main_frame, text="Compute Type:").pack(anchor=tk.W)
        self.compute_var = tk.StringVar(value=settings.get("compute_type"))
        compute_combo = ttk.Combobox(main_frame, textvariable=self.compute_var,
                                     values=["default", "int8", "float16", "float32"],
                                     state="readonly")
        compute_combo.pack(fill=tk.X, pady=(0, 10))

        # ── Custom Vocabulary ──
        ttk.Label(main_frame, text="Custom Vocabulary:").pack(anchor=tk.W)
        self.vocab_text = tk.Text(main_frame, height=3)
        self.vocab_text.pack(fill=tk.X, pady=(0, 10))
        self.vocab_text.insert(tk.END, settings.get("custom_vocabulary") or "")

        # ── Use LLM ──
        self.use_llm_var = tk.BooleanVar(value=settings.get("use_llm"))
        ttk.Checkbutton(main_frame, text="Enable Ollama Post-Processing (localhost:11434)",
                        variable=self.use_llm_var).pack(anchor=tk.W, pady=(0, 5))

        ttk.Label(main_frame, text="LLM Prompt:").pack(anchor=tk.W)
        self.llm_prompt_text = tk.Text(main_frame, height=3)
        self.llm_prompt_text.pack(fill=tk.X, pady=(0, 10))
        self.llm_prompt_text.insert(tk.END, settings.get("llm_prompt") or "")

        # ── Save History ──
        self.save_history_var = tk.BooleanVar(value=settings.get("save_history"))
        ttk.Checkbutton(main_frame, text="Save transcription history",
                        variable=self.save_history_var).pack(anchor=tk.W, pady=(0, 10))

        # ── Buttons ──
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="Save Settings", command=self.save_settings).pack(side=tk.RIGHT)

    def save_settings(self):
        settings.set("hotkey", self.hotkey_var.get())
        settings.set("model_size", self.model_var.get())
        settings.set("device", self.device_var.get())
        settings.set("compute_type", self.compute_var.get())
        settings.set("custom_vocabulary", self.vocab_text.get("1.0", tk.END).strip())
        settings.set("use_llm", self.use_llm_var.get())
        settings.set("llm_prompt", self.llm_prompt_text.get("1.0", tk.END).strip())
        settings.set("save_history", self.save_history_var.get())

        messagebox.showinfo("Success", "Settings saved! (Model/device change may require restart)")

        if self.on_save_callback:
            self.on_save_callback()

        self._on_close()

    def _on_close(self):
        self.destroy()
        self.master.destroy()


def show_settings(on_save_callback=None):
    """Open settings in a standalone hidden-root + Toplevel pattern to avoid
    creating multiple Tk() instances (which causes Tcl_AsyncDelete crashes)."""
    root = tk.Tk()
    root.withdraw()  # Hidden root
    win = SettingsWindow(root, on_save_callback)
    win.mainloop()


if __name__ == "__main__":
    show_settings()
