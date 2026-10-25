$ErrorActionPreference='Stop'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Start-Process powershell -ArgumentList '-NoExit','-ExecutionPolicy','Bypass','-File',(Join-Path $root 'scripts\start_backend.ps1')
Write-Host 'Backend starting in a separate PowerShell window.' -ForegroundColor Green
Write-Host 'Then use Antigravity Run -> Start Debugging -> Dart & Flutter -> Chrome.' -ForegroundColor Cyan
