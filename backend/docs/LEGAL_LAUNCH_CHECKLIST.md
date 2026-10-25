INVESTEDGE — LEGAL / STORE LAUNCH CHECKLIST
============================================

Engineering
-----------
[ ] Production database (PostgreSQL or managed equivalent)
[ ] HTTPS everywhere
[ ] Password hashing (Argon2id or equivalent)
[ ] OTP provider with expiry, attempt limits and abuse/rate controls
[ ] Secure sessions/JWT + refresh-token rotation
[ ] Secrets stored outside source control
[ ] Audit/security logging
[ ] Per-user data isolation and authorization checks
[ ] Account deletion and data deletion flows
[ ] Backups + restore test
[ ] Monitoring and incident response

Identity / product
------------------
[ ] Full name, username, email/phone verification flow
[ ] Unique username and verified contact
[ ] Forgot-password / account recovery
[ ] Device/session management
[ ] Terms acceptance with version tracking
[ ] Privacy consent where required
[ ] Age / eligibility policy reviewed by counsel

India financial-regulatory review
----------------------------------
[ ] Define exactly what InvestEdge does: information, research, recommendations, personalized advice, execution, or a combination
[ ] Obtain professional legal/compliance review of the business model
[ ] Determine whether SEBI Investment Adviser and/or Research Analyst requirements apply
[ ] Complete applicable SEBI registration/enlistment before offering regulated services
[ ] Implement required disclosures, records, grievance handling and other obligations applicable to the final model
[ ] Review advertising/marketing claims and AI-generated recommendations

Google Play / Apple
-------------------
[ ] Privacy policy URL
[ ] Terms URL
[ ] In-app account deletion
[ ] External web account-deletion path
[ ] Data Safety disclosure (Google Play)
[ ] App privacy disclosures (Apple)
[ ] Store reviewer/demo credentials and any OTP bypass procedure required for review
[ ] Production support/contact details
[ ] Current target SDK / platform requirements checked before submission

Launch rule
-----------
Do not enable a regulated advisory mode simply because the app technically supports it. Keep APP_COMPLIANCE_MODE=RESEARCH_ONLY until the legal/compliance work for the exact service is complete.
