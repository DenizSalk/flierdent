; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "FlierDent"
#define MyAppVersion "0.2"
#define MyAppPublisher "FlierDent"
#define MyAppURL "https://www.denizsalk.com/"
#define MyAppExeName "main.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{18037B4A-B7E6-4179-BB94-D47EF944BC17}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableDirPage=yes
DisableProgramGroupPage=yes
LicenseFile=C:\Users\deniz\OneDrive\Masa�st�\flierdent\output\main\license.txt
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputDir=C:\Users\deniz\OneDrive\Masa�st�\setup
OutputBaseFilename=FliderDent_v0.2_Setup
SetupIconFile=C:\Users\deniz\OneDrive\Masa�st�\flierdent\static\medical_9345306.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\deniz\OneDrive\Masa�st�\flierdent\output\main\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\deniz\OneDrive\Masa�st�\flierdent\data\*"; DestDir: "{app}/data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\deniz\OneDrive\Masa�st�\flierdent\output\main\_internal\*"; DestDir: "{app}/_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
