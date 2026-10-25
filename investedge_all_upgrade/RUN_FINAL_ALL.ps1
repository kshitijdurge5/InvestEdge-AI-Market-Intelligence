$ErrorActionPreference = 'Stop'
$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = 'C:\AI Projects\InvestEdge_Full_Upgrade'
if (-not (Test-Path (Join-Path $projectRoot 'pubspec.yaml'))) { throw "InvestEdge_Full_Upgrade was not found at $projectRoot" }
Set-Location $projectRoot
Write-Host "Starting InvestEdge final integrated stack..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList '-NoExit','-ExecutionPolicy','Bypass','-File',(Join-Path $projectRoot 'scripts\start_backend.ps1')
Start-Sleep -Seconds 3
Write-Host "Starting Flutter Chrome..." -ForegroundColor Green
flutter run -d chrome
