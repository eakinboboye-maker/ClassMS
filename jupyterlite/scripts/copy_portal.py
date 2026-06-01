# scripts/copy_portal.py  (replace the whole file)
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
portal_dir = root / "portal"
dist_dir = root / "dist"

dist_dir.mkdir(parents=True, exist_ok=True)

# 1. Copy portal assets
src_assets = portal_dir / "assets"
dst_assets = dist_dir / "assets"
if dst_assets.exists():
    shutil.rmtree(dst_assets)
shutil.copytree(src_assets, dst_assets)
print(f"✅ Copied portal assets -> {dst_assets}")

# 2. Copy portal pages (but NOT as root index.html)
shutil.copy2(portal_dir / "index.html", dist_dir / "portal.html")
shutil.copy2(portal_dir / "mock-exam.html", dist_dir / "mock-exam.html")
print("✅ Copied portal.html and mock-exam.html")

# 3. Create a proper root index.html with choice
with open(dist_dir / "index.html", "w", encoding="utf-8") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>ClassLite - JupyterLite</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: system-ui, sans-serif; text-align: center; padding: 60px 20px; background: #f8fafc; }
        .card { max-width: 420px; margin: 30px auto; padding: 40px; background: white; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        h1 { color: #1e40af; }
        a { display: inline-block; margin: 12px; padding: 14px 28px; background: #1e40af; color: white; text-decoration: none; border-radius: 12px; font-weight: bold; }
        a:hover { background: #1e3a8a; }
    </style>
</head>
<body>
    <div class="card">
        <h1>ClassLite</h1>
        <p>Choose where to go:</p>
        <a href="./portal.html">🏠 Student Portal</a><br>
        <a href="./lab/index.html">🧪 JupyterLite Lab</a>
    </div>
</body>
</html>""")
print("✅ Created smart root index.html")
