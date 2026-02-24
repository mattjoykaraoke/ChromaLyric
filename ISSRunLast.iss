; =========================================================
; ChromaLyric Installer (Inno Setup)
; - Optional .ass association
; - Optional context menu
; =========================================================

#define AppName "ChromaLyric"
#define AppPublisher "Matt Joy"
#define AppExeName "ChromaLyric.exe"
#define AppVersion "1.7.0"

[Setup]
AppId={{D1D77C0F-3AF1-4E73-9E1B-6C0F8D7B1F1B}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=release
OutputBaseFilename={#AppName}-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
ChangesAssociations=yes
SetupIconFile=assets\ChromaLyric.ico
UninstallDisplayIcon={app}\{#AppExeName}
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

; ---------------------------------------------------------
; INSTALLER CHECKBOX OPTIONS
; ---------------------------------------------------------
[Tasks]
Name: "fileassoc"; Description: "Associate .ass files with ChromaLyric"; GroupDescription: "File integration:"; Flags: unchecked
Name: "contextmenu"; Description: "Add right-click 'Open with ChromaLyric' menu"; GroupDescription: "File integration:"; Flags: unchecked

[Files]
Source: "dist\ChromaLyric\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

; ---------------------------------------------------------
; FILE ASSOCIATION (Only if user selects checkbox)
; ---------------------------------------------------------
[Registry]

; Default association
Root: HKCR; Subkey: ".ass"; ValueType: string; ValueName: ""; ValueData: "{#AppName}.AssFile"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCR; Subkey: "{#AppName}.AssFile"; ValueType: string; ValueName: ""; ValueData: "Advanced SubStation Alpha Subtitle"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCR; Subkey: "{#AppName}.AssFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#AppExeName},0"; Tasks: fileassoc
Root: HKCR; Subkey: "{#AppName}.AssFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; Tasks: fileassoc

; ---------------------------------------------------------
; CONTEXT MENU (Optional)
; ---------------------------------------------------------

Root: HKCR; Subkey: ".ass\shell\OpenWithChromaLyric"; ValueType: string; ValueName: ""; ValueData: "Open with {#AppName}"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCR; Subkey: ".ass\shell\OpenWithChromaLyric"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#AppExeName},0"; Tasks: contextmenu
Root: HKCR; Subkey: ".ass\shell\OpenWithChromaLyric\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; Tasks: contextmenu

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
