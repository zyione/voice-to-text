@echo off
setlocal

:: ── Voice Typer  —  PyInstaller build script ──────────────────────
:: Produces  dist\VoiceTyper\VoiceTyper.exe  (folder mode).
:: Run from the repo root:   build\build.bat
:: Requires the .venv to be set up first (see README).
:: ──────────────────────────────────────────────────────────────────

set "ROOT=%~dp0.."
set "VENV=%ROOT%\.venv"

:: Prefer the venv Python; fall back to the one on PATH
if exist "%VENV%\Scripts\python.exe" (
    set "PY=%VENV%\Scripts\python.exe"
) else (
    set "PY=python"
)

echo.
echo ══════════════════════════════════════════════
echo   Building Voice Typer with PyInstaller
echo ══════════════════════════════════════════════
echo   Python : %PY%
echo   Root   : %ROOT%
echo.

:: Make sure PyInstaller is available
"%PY%" -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyInstaller...
    "%PY%" -m pip install pyinstaller
)

:: Run PyInstaller
"%PY%" -m PyInstaller ^
    --name "VoiceTyper" ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --icon "NUL" ^
    --add-data "%ROOT%\config.json;." ^
    --distpath "%ROOT%\dist" ^
    --workpath "%ROOT%\build\temp" ^
    --specpath "%ROOT%\build" ^
    "%ROOT%\main.py"

if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo ══════════════════════════════════════════════
echo   Build complete!
echo   Output : %ROOT%\dist\VoiceTyper\VoiceTyper.exe
echo ══════════════════════════════════════════════
echo.
pause
