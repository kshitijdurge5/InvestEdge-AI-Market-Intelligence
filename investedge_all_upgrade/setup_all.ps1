$ErrorActionPreference = 'Stop'
Write-Host "InvestEdge - ALL-IN-ONE UPGRADE" -ForegroundColor Cyan
Write-Host "This applies WebSocket -> live state -> AI signals -> Watchlist -> Portfolio -> Security -> Production -> Android in one pass." -ForegroundColor Gray

$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = (Get-Location).Path
if (-not (Test-Path (Join-Path $projectRoot 'pubspec.yaml'))) {
    $fallback = 'C:\AI Projects\InvestEdge_Full_Upgrade'
    if (Test-Path (Join-Path $fallback 'pubspec.yaml')) { $projectRoot = $fallback }
}
if (-not (Test-Path (Join-Path $projectRoot 'pubspec.yaml'))) {
    throw "Could not find the Flutter project root (pubspec.yaml). Open the InvestEdge project folder and run this script there."
}

$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backup = Join-Path $projectRoot ".investedge_backups\$stamp"
New-Item -ItemType Directory -Force -Path $backup | Out-Null

function Backup-IfExists($relative) {
    $src = Join-Path $projectRoot $relative
    if (Test-Path $src) {
        $dst = Join-Path $backup $relative
        New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
        Copy-Item $src $dst -Force
    }
}

Backup-IfExists 'lib\main.dart'
Backup-IfExists 'pubspec.yaml'
Backup-IfExists 'backend\main.py'
Backup-IfExists 'backend\requirements.txt'
Backup-IfExists 'backend\.env'
Backup-IfExists 'config\production.env'

# Copy the complete upgrade payload.
Copy-Item (Join-Path $packageRoot 'lib\main.dart') (Join-Path $projectRoot 'lib\main.dart') -Force
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'backend') | Out-Null
Copy-Item (Join-Path $packageRoot 'backend\main.py') (Join-Path $projectRoot 'backend\main.py') -Force
Copy-Item (Join-Path $packageRoot 'backend\requirements.txt') (Join-Path $projectRoot 'backend\requirements.txt') -Force
Copy-Item (Join-Path $packageRoot 'backend\.env.example') (Join-Path $projectRoot 'backend\.env.example') -Force
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'config') | Out-Null
Copy-Item (Join-Path $packageRoot 'config\production.env.template') (Join-Path $projectRoot 'config\production.env.template') -Force


# Copy the complete operational scripts, docs and production assets into the project.
foreach ($rel in @('scripts\start_backend.ps1','scripts\run_all_dev.ps1','scripts\build_android.ps1','docs\ARCHITECTURE.md','backend\Dockerfile','docker-compose.yml','.gitignore.additions')) {
    $src = Join-Path $packageRoot $rel
    if (Test-Path $src) {
        $dst = Join-Path $projectRoot $rel
        New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
        Copy-Item $src $dst -Force
    }
}

# Add only the Flutter packages this unified client actually needs.
$pub = Get-Content (Join-Path $projectRoot 'pubspec.yaml') -Raw
if ($pub -notmatch '(?m)^\s*web_socket_channel\s*:') {
    $pub = [regex]::Replace($pub, '(?m)^(dependencies:\s*\r?\n)', ('$1' + [Environment]::NewLine + '  web_socket_channel: ^3.0.3' + [Environment]::NewLine), 1)
}
if ($pub -notmatch '(?m)^\s*shared_preferences\s*:') {
    $pub = [regex]::Replace($pub, '(?m)^(dependencies:\s*\r?\n)', ('$1' + [Environment]::NewLine + '  shared_preferences: ^2.5.3' + [Environment]::NewLine), 1)
}
Set-Content (Join-Path $projectRoot 'pubspec.yaml') $pub -Encoding UTF8

# Android internet access is required for the secure backend/WebSocket connection.
$manifest = Join-Path $projectRoot 'android\app\src\main\AndroidManifest.xml'
if (Test-Path $manifest) {
    $m = Get-Content $manifest -Raw
    if ($m -notmatch 'android.permission.INTERNET') {
        $m = [regex]::Replace($m, '(<manifest[^>]*>)', ('$1' + [Environment]::NewLine + '    <uses-permission android:name="android.permission.INTERNET" />'), 1)
        Set-Content $manifest $m -Encoding UTF8
    }
}

# Create local backend environment file without putting secrets into Flutter.
$envPath = Join-Path $projectRoot 'backend\.env'
if (-not (Test-Path $envPath)) {
    Copy-Item (Join-Path $packageRoot 'backend\.env.example') $envPath
}

Write-Host ""
Write-Host "Running flutter pub get..." -ForegroundColor Cyan
try { flutter pub get } catch { Write-Warning "flutter pub get could not be run automatically. Run it once from the Flutter project." }
Write-Host ""
Write-Host "BACKUP:" $backup -ForegroundColor Green
Write-Host "APPLIED TO:" $projectRoot -ForegroundColor Green
Write-Host "" 
Write-Host "Unified upgrade installed." -ForegroundColor Green
Write-Host "Flutter UI is preserved; it now connects to ws://127.0.0.1:8000/ws/market when available and otherwise uses DEMO data." -ForegroundColor Yellow
Write-Host "" 
Write-Host "Next run action: use the Antigravity Run menu to start Dart & Flutter on Chrome." -ForegroundColor Cyan
Write-Host "For the backend, use scripts\\start_backend.ps1 when you are ready; no broker secret is required for DEMO mode." -ForegroundColor Gray
