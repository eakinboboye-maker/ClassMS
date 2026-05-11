from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
src = root / "portal"
dst = root / "dist" / "portal"

if not src.exists():
    raise FileNotFoundError(f"Portal source folder not found: {src}")

if dst.exists():
    shutil.rmtree(dst)

shutil.copytree(src, dst)
print(f"Copied portal -> {dst}")
