# ClassLite JupyterLite Portal Upgrade

This upgrade moves these features from notebooks to the portal:
- login
- lesson access by teacher lesson config
- attendance marking
- attendance window enforcement
- student performance over time
- portal mock exam flow

Lesson quizzes remain inside notebooks.

## Important
The notebook still uses a small hidden portal-session bootstrap so it can reuse the portal session instead of asking students to log in again.
