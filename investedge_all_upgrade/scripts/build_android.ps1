$ErrorActionPreference='Stop'
Set-Location (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
$url = $env:INVESTEDGE_BACKEND_URL
if ([string]::IsNullOrWhiteSpace($url)) { $url = 'ws://10.0.2.2:8000/ws/market' }
flutter build apk --release --dart-define=INVESTEDGE_BACKEND_URL=$url
