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
pip install -r requirements.txt # if fail
pip install --no-deps --no-cache-dir --upgrade -r requirements.txt
```

> **Note on Windows C++ Build Tools**: If standard `pip` fails to install dependencies like `tokenizers` or `av`, make sure you have the [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) installed, or use **Python 3.11** with `uv` to pull down standard pre-compiled binaries effortlessly.

---

## Running the App

### Option A — Windows Installer (recommended for end users)

If you already have `VoiceTyperSetup.exe` (built by a developer, see [Building & Updating the Installer](#building--updating-the-installer) below):

1. Double-click `VoiceTyperSetup.exe`.
2. Follow the setup wizard — choose an install location, tick shortcuts as desired, click **Install**.
3. Launch **Voice Typer** from the Start Menu or Desktop shortcut.

> **Whisper models are not bundled.** On first launch the app will download the selected model (~150 MB for `base`) to your HuggingFace cache (`%USERPROFILE%\.cache\huggingface`). This only happens once.

### Option B — Run from Python (dev / power-user)

Use this when you are actively editing code, debugging, or want to see console output.

```bash
# Recommended (uv venv):
$env:HF_HOME="E:\hf_cache"; .\.venv311\Scripts\python.exe main.py

# Standard pip venv:
.\.venv\Scripts\python.exe main.py
```

### Which should I use?

|                              | Installer          | Python                |
| ---------------------------- | ------------------ | --------------------- |
| Just want to use the app     | ✅                 | works too             |
| Editing / debugging code     | ✗                  | ✅                    |
| Sharing with someone else    | ✅ (one file)      | requires Python setup |
| See `print()` output         | ✗ (no console)     | ✅                    |
| Fastest iteration on changes | ✗ (rebuild needed) | ✅                    |

---

Once the app is running:

1. Look in your system tray (bottom right on Windows) for the **blue circle icon**.
2. Set your cursor inside any text box in any program.
3. Press the global recording hotkey (`ctrl+space` by default). The transparent overlay will appear showing your voice level.
4. Speak your dictation.
5. Press `ctrl+space` again to stop. The tray icon turns yellow while transcribing.
6. A moment later the text is typed into your active window.

---

## Building & Updating the Installer

This section is for **developers** who need to produce a fresh `VoiceTyperSetup.exe` after making code changes.

### One-time setup

You need two tools installed on the build machine (both are free):

1. **Python 3.11 + venv** — set up as described in the [Installation](#installation) section above.
2. **[Inno Setup 6](https://jrsoftware.org/isdl.php)** — download and install with default options. The build step below expects it at the default path `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`.

### Step 1 — Build the EXE bundle with PyInstaller

From the repo root, run:

```bash
build\build.bat
```

This will:

- Install PyInstaller into your venv if it's not already there.
- Bundle `main.py` and all dependencies into `dist\VoiceTyper\` (folder mode).
- The standalone EXE lives at `dist\VoiceTyper\VoiceTyper.exe`.

You can test the app by double-clicking `dist\VoiceTyper\VoiceTyper.exe` directly before proceeding.

### Step 2 — Package into an installer with Inno Setup

**Option A — GUI:** Open `build\installer.iss` in Inno Setup Compiler and click **Compile** (or press `Ctrl+F9`).

**Option B — Command line:**

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" build\installer.iss
```

This produces `dist\VoiceTyperSetup.exe` — a single installer file you can share with anyone.

The installer will:

- Copy files to `C:\Users\<user>\AppData\Local\Programs\Voice Typer\` (no admin required)
- Create a **Start Menu** shortcut
- Optionally create a **Desktop** shortcut
- Optionally register to **start on Windows login**
- Add an entry in **Add/Remove Programs** with a clean uninstaller

### Updating after code changes

Whenever you change the Python source code:

1. Run `build\build.bat` again (PyInstaller reuses its cache, so rebuilds are fast).
2. Run the Inno Setup compile again (Step 2 above).
3. Distribute the new `dist\VoiceTyperSetup.exe`.

That's it — two commands to go from code change to distributable installer.

### Bumping the version number

Edit the version in `build\installer.iss`:

```ini
#define MyAppVersion   "1.0.0"   ; ← change this
```

This controls what shows in Add/Remove Programs and the installer title bar.

---

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
