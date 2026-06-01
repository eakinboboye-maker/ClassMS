# Corrected ClassLite JupyterLite App

This corrected version includes:
- root portal page copied into `dist/index.html`
- portal assets copied into `dist/assets`
- portal mock exam page
- portal stylesheet
- stricter `copy_portal.py`
- build script that prints `dist` contents for debugging

## Local run
```bash
npm run build
npm run serve
```

Open:
- http://localhost:9000/
- http://localhost:9000/lab/index.html

For a stricter local server with browser-isolation headers:
```bash
npm run serve_headers
```

## Vercel
Use:
- Framework: Other
- Install: `python -m pip install --break-system-packages -r requirements.txt`
- Build: `npm run build`
- Output: `dist`
