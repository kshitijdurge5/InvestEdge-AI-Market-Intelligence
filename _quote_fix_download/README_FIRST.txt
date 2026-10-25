INVESTEDGE SAFE QUOTE PATCH

This package is an automated patch for the existing Flutter main.dart.
It creates a timestamped backup outside lib before applying changes and restores the backup if validation/analyzer fails.

HOW TO USE
1. Extract this ZIP.
2. Copy Install-InvestEdgeQuoteFix.ps1 into:
   C:\AI Projects\InvestEdge_Packages\InvestEdge_Combined_Workspace
3. In File Explorer, open that workspace folder.
4. Click the address bar, type powershell, and press Enter.
5. Run:
   powershell -ExecutionPolicy Bypass -File .\Install-InvestEdgeQuoteFix.ps1

The script expects mobile_app\lib\main.dart at the workspace root.
Do not run it from another folder.

IMPORTANT LIMITATION
This script is a best-effort patch based on the code supplied in chat. It checks source markers, creates a backup, and tries to run flutter analyze. Because the exact source file was not uploaded as an attachment, it cannot guarantee that every UI section has been fully corrected. If the script reports failure, it restores the original file. Do not ignore analyzer errors.
