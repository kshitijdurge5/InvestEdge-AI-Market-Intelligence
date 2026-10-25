INVESTEDGE WEBSITE UPGRADE — LOCAL PREVIEW

This is a safe add-on package. It does NOT replace your existing Flutter app or backend.

EXTRACT TO:
C:\AI Projects\InvestEdge_Packages\InvestEdge_Combined_Workspace

After extraction, open:
C:\AI Projects\InvestEdge_Packages\InvestEdge_Combined_Workspace\InvestEdge_Website_Upgrade

RUN THE WEBSITE:
Double-click RUN_WEBSITE.bat
It starts a local Python web server and opens the site in your browser at http://localhost:8091

RUN YOUR EXISTING FLUTTER APP:
Double-click RUN_EXISTING_FLUTTER_APP.bat. It attempts to run the existing Flutter app from:
C:\AI Projects\InvestEdge_Packages\InvestEdge_Combined_Workspace\mobile_app
If the active Flutter project is in a different subfolder, use the existing terminal and current working command you already use. This launcher does not modify app files.

WHAT'S INCLUDED:
- Responsive InvestEdge website/dashboard preview
- Navigation previews for stocks, mutual funds, SIP planner, bonds, ETFs, crypto, IPOs, portfolio, market news and AI research
- Sample index values, top movers, illustrative allocation chart and research demo
- Local launch scripts

IMPORTANT:
- All prices, market indicators and portfolio values in this preview are illustrative sample data, NOT live market prices.
- This is a frontend preview, not yet a public internet website and not connected to a live market provider, authentication backend or real AI service.
- Do not enter passwords, financial account details, API keys or other sensitive data into this demo.
- Before a public launch, connect verified data providers and backend APIs, implement real authentication, privacy/security controls, and obtain professional compliance advice for any regulated financial services.

The Flutter release build can be created with `flutter build web` once the existing Flutter project is ready and its web target is configured. Official Flutter guide:
https://docs.flutter.dev/deployment/web
