from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PORTAL_DIR = ROOT / "portal"
DIST_DIR = ROOT / "dist"
DIST_PORTAL_DIR = DIST_DIR / "portal"

DIST_DIR.mkdir(parents=True, exist_ok=True)
DIST_PORTAL_DIR.mkdir(parents=True, exist_ok=True)

# GitHub Pages must not ignore JupyterLite folders such as _output, _shared, etc.
(DIST_DIR / ".nojekyll").write_text("", encoding="utf-8")

# Copy the portal as a real /portal/ app.
assets_src = PORTAL_DIR / "assets"
assets_dst = DIST_PORTAL_DIR / "assets"
if assets_dst.exists():
    shutil.rmtree(assets_dst)
if assets_src.exists():
    shutil.copytree(assets_src, assets_dst)

for name in ["index.html", "mock-exam.html"]:
    src = PORTAL_DIR / name
    if src.exists():
        shutil.copy2(src, DIST_PORTAL_DIR / name)

# IMPORTANT:
# JupyterLite app pages fetch parent index.html files during config startup.
# Therefore root index.html must keep a valid jupyter-config-data script tag.
# Without it, /lab/index.html fails in config-utils.js with:
#   Cannot read properties of null (reading 'textContent')
# This page redirects humans from / to /portal/index.html, while still serving
# valid config JSON to JupyterLite's config-utils when Lab fetches /index.html.
(DIST_DIR / "index.html").write_text("""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>Redirecting to ClassLite Portal</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <script id=\"jupyter-config-data\" type=\"application/json\" data-jupyter-lite-root=\".\">{}</script>
  <meta http-equiv=\"refresh\" content=\"0; url=./portal/index.html\" />
  <script>
    // Human landing page: / -> /portal/index.html
    // JupyterLite config-utils can still fetch and parse this file safely.
    location.replace('./portal/index.html');
  </script>
</head>
<body>
  <p>Redirecting to <a href=\"./portal/index.html\">ClassLite Portal</a>...</p>
</body>
</html>
""", encoding="utf-8")

# Optional client-side guard: Lab should be launched after portal login.
# This is not a substitute for real server-side authorization, but it prevents
# casual direct entry to /lab/index.html when no portal session exists.
lab_index = DIST_DIR / "lab" / "index.html"
if lab_index.exists():
    html = lab_index.read_text(encoding="utf-8")
    guard_marker = "classlite-lab-login-guard"
    guard = """\n    <script id=\"classlite-lab-login-guard\">\n      (function () {\n        try {\n          var session = JSON.parse(localStorage.getItem('classlite_portal_session') || 'null');\n          if (!session || !session.token) {\n            var portal = new URL('../portal/index.html', location.href);\n            portal.searchParams.set('next', location.pathname + location.search + location.hash);\n            location.replace(portal.toString());\n          }\n        } catch (err) {\n          location.replace(new URL('../portal/index.html', location.href).toString());\n        }\n      }());\n    </script>\n"""
    if guard_marker not in html:
        # Insert after jupyter-config-data so config remains available, before config-utils starts.
        needle = "</script>\n    <script>\n      (async function () {"
        if needle in html:
            html = html.replace(needle, "</script>" + guard + "    <script>\n      (async function () {", 1)
        else:
            html = html.replace("</head>", guard + "</head>", 1)
        lab_index.write_text(html, encoding="utf-8")

print(f"✅ Portal copied to {DIST_PORTAL_DIR}")
print("✅ Root / redirects to /portal/index.html and still preserves jupyter-config-data")
print("✅ Lab startup config error fixed")
