; ── Voice Typer  —  Inno Setup installer script ─────────────────
; Produces  dist\VoiceTyperSetup.exe
;
; Prerequisites:
;   1. Run  build\build.bat  first to create  dist\VoiceTyper\
;   2. Install Inno Setup 6  (https://jrsoftware.org/isdl.php)
;   3. Open this file in Inno Setup and click Compile,
;      OR run from the command line:
;        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" build\installer.iss
; ─────────────────────────────────────────────────────────────────

#define MyAppName      "Voice Typer"
#define MyAppVersion   "1.0.0"
#define MyAppPublisher "Voice Typer"
#define MyAppExeName   "VoiceTyper.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=..\dist
OutputBaseFilename=VoiceTyperSetup
Compression=lzma2/ultra64
SolidCompression=yes
SetupIconFile=compiler:SetupClassicIcon.ico
WizardStyle=modern
PrivilegesRequired=lowest
AllowNoIcons=yes
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";  Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon";  Description: "Start Voice Typer when Windows starts"; GroupDescription: "Other:"

[Files]
; Bundle the entire PyInstaller output folder
Source: "..\dist\VoiceTyper\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}";       Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}";  Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}";  Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
