# Voice Typer

A local, offline-capable voice-to-text dictation application that types transcribed speech directly into your active window.

The application leverages [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for blazing fast, high-quality transcription locally on your CPU or GPU. It records your microphone when a global hotkey is held/toggled, and gracefully pasts the transcribed text into any window you currently have focused (Discord, Word, your IDE, your browser, etc).

## Features

- **Local & Offline**: All processing happens entirely on your machine. Your voice is never sent to the cloud.
- **Universal Typing**: Injects text seamlessly into any active window across the entire OS.
- **Floating UI Overlay**: Provides a sleek, transparent floating mic overlay with dynamic audio bars while you're recording.
- **Ollama Integration**: Optionally route transcriptions through a local LLM (like Llama 3 via Ollama) to automatically fix grammar or apply custom formatting prompts before pasting.
- **Custom Vocabulary**: Provide specific terms or technical jargon in the settings to improve the transcription accuracy.

---

## Installation

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Recommended, especially on Windows, for faster dependency resolution and caching pre-compiled wheels).

### Setup

1. Clone this repository:

```bash
git clone https://github.com/yourusername/voice-typer.git
cd voice-typer
```

2. Create a virtual environment and install the dependencies:

If using `uv` (Recommended):

```bash
uv venv -p 3.11 .venv
uv pip install -r requirements.txt --python .\.venv\Scripts\python.exe
```

If using standard `pip`:

```bash
python -m venv .venv
.\.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

> **Note on Windows C++ Build Tools**: If standard `pip` fails to install dependencies like `tokenizers` or `av`, make sure you have the [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) installed, or use **Python 3.11** with `uv` to pull down standard pre-compiled binaries effortlessly.

---

## Running the app

There are two ways to run Voice Typer. Use whichever fits your situation:

### Option A — Portable EXE (no Python required)

Pre-built for Windows. Ideal for just using the app on any machine without a Python environment.

1. Build it once (requires the venv set up above):

```
build\build.bat
```

2. The output is at `dist\VoiceTyper\VoiceTyper.exe`. Double-click it to launch.
3. Copy the entire `dist\VoiceTyper\` folder anywhere you like — another PC, a USB drive, etc. It is self-contained.

> **Whisper models are not bundled.** On first launch the app will download the selected model (~150 MB for `base`) to your HuggingFace cache (`%USERPROFILE%\.cache\huggingface`). This only happens once.

**Rebuilding after code changes:** just run `build\build.bat` again. PyInstaller reuses its cache so subsequent builds are faster.

---

### Option B — Run from Python (dev / power-user)

Use this when you are actively editing code, debugging, or want to see console output.

```bash
# Recommended (uv venv):
$env:HF_HOME="E:\hf_cache"; .\.venv311\Scripts\python.exe main.py

# Standard pip venv:
.\.venv\Scripts\python.exe main.py
```

---

### Which should I use?

| | EXE | Python |
|---|---|---|
| Just want to use the app | ✅ | works too |
| Editing / debugging code | ✗ | ✅ |
| Sharing with someone else | ✅ | requires Python setup |
| See `print()` output | ✗ (no console) | ✅ |
| Fastest iteration on changes | ✗ (rebuild needed) | ✅ |

---

Once the app is running:

1. Look in your system tray (bottom right on Windows) for the **blue circle icon**.
2. Set your cursor inside any text box in any program.
3. Press the global recording hotkey (`ctrl+space` by default). The transparent overlay will appear showing your voice level.
4. Speak your dictation.
5. Press `ctrl+space` again to stop. The tray icon turns yellow while transcribing.
6. A moment later the text is typed into your active window.

## Configuration & Settings

Right-click the Voice Typer icon in your system tray and select **Settings**.

Options include:

- **Global Hotkey:** Change the hotkey (e.g. `ctrl+space`, `alt+d`, `windows+m`).
- **Whisper Model:** Choose from `tiny`, `base`, `small`, `medium`, or `large-v3`. Larger models are more accurate but use more RAM and are slower to transcribe.
- **Device:** Force the model to load on `cpu` or `cuda` (if you have an Nvidia GPU installed with proper drivers in your environment).
- **Custom Vocabulary:** Provide comma-separated technical words if Whisper is struggling to recognize them naturally.
- **Enable Ollama Post-Processing:** Check this box if you have [Ollama](https://ollama.com/) running locally on port 11434. You can provide an LLM prompt (ex: "Fix grammar and spelling. Output strictly the fixed text and nothing else.") to filter your transcriptions before they type!

---

Enjoy fast, private, and seamless dictation anywhere you need it!
