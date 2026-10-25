@echo off
setlocal
set "ROOT=C:\AI Projects\InvestEdge_Packages\InvestEdge_Combined_Workspace"
if exist "%ROOT%\mobile_app\pubspec.yaml" (
  cd /d "%ROOT%\mobile_app"
  echo Starting existing Flutter app in Chrome...
  flutter run -d chrome
  pause
  exit /b
)
echo Could not find a Flutter project at:
echo %ROOT%\mobile_app
echo.
echo No files were changed. Open your existing project terminal and run the Flutter command you used previously.
pause
