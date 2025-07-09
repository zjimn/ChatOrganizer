#define MyAppName "AI对话管理"
#define MyAppEnName "ChatOrganizer"
#define MyAppVersion "1.0"
#define MyAppExeName "ChatOrganizer.exe"
#define MyAppAssocName MyAppEnName + " File"
#define MyAppAssocExt ".myp"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
AppId={{C872537F-8106-47C1-B136-3CD8536A6369}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\ChatOrganizer
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
DisableProgramGroupPage=yes
LicenseFile=res\doc\license.txt
InfoBeforeFile=res\doc\info_before_install.txt
InfoAfterFile=res\doc\info_after_install.txt
OutputDir=release
OutputBaseFilename=AI对话管理安装包
SetupIconFile=res\icon\app_logo.ico
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
AppPublisher=Jim
AppCopyright=© 2025 Jim. All rights reserved.
VersionInfoVersion=1.0.0.0


[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\res\*"; DestDir: "{app}\res"; Flags: ignoreversion recursesubdirs createallsubdirs

[Registry]
Root: HKA; Subkey: "Software\{#MyAppEnName}\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\{#MyAppEnName}\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\{#MyAppEnName}\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\{#MyAppEnName}\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\{#MyAppEnName}\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".myp"; ValueData: ""



[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent


[Code]
function InitializeSetup(): Boolean;
begin
  if RegKeyExists(HKEY_AUTO, 'Software\{#MyAppEnName}\{#MyAppAssocExt}\OpenWithProgids') and
            RegValueExists(HKEY_AUTO, 'Software\{#MyAppEnName}\{#MyAppAssocExt}\OpenWithProgids', '{#MyAppAssocKey}') then
  begin
    MsgBox('检测到应用程序已安装，请先卸载现有版本后再进行安装', mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

function KDetectSoft(strExeName: String): Boolean;
var ErrorCode: Integer;
var bRes: Boolean;
var strFileContent: AnsiString;
var strTmpPath: String;
var strTmpFile: String;
var strCmdFind: String;
var strCmdKill: String;
begin
  strTmpPath := GetTempDir();
  strTmpFile := Format('%sfindSoftRes.txt', [strTmpPath]);
  strCmdFind := Format('/c tasklist /nh|find /c /i "%s" > "%s"', [strExeName, strTmpFile]);
  strCmdKill := Format('/c taskkill /f /t /im %s', [strExeName]);
  bRes := ShellExec('open', ExpandConstant('{cmd}'), strCmdFind, '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
  if bRes then begin
      bRes := LoadStringFromFile(strTmpFile, strFileContent);
      strFileContent := Trim(strFileContent);
      if bRes then begin
         if StrToInt(strFileContent) > 0 then begin
            if MsgBox(ExpandConstant('软件正在运行，点击“确定”将自动关闭软件并继续卸载'), mbConfirmation, MB_OKCANCEL) = IDOK then begin
             ShellExec('open', ExpandConstant('{cmd}'), strCmdKill, '', SW_HIDE, ewNoWait, ErrorCode);
             Result:= true;
            end else begin
             Result:= false;
             Exit;
            end;
         end else begin
            Result:= true;
            Exit;
         end;
      end;
  end;
  Result :=true;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  if 1=CurPageID then begin
      Result := KDetectSoft('ChatOrganizer.exe');
      Exit;
  end; 
  Result:= true;
end;

function InitializeUninstall(): Boolean;
begin
  Result := KDetectSoft('ChatOrganizer.exe');
end;
