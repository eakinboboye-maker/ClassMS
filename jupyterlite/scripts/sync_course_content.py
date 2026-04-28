from pathlib import Path
import shutil

repo_root = Path(__file__).resolve().parents[1]
master_root = repo_root / "master-content" / "courses" / "EEE355"
publish_root = repo_root / "content" / "EEE355"

publish_root.mkdir(parents=True, exist_ok=True)

for src_dir in [master_root / "lessons", master_root / "mock-exams"]:
    if not src_dir.exists():
        continue
    for path in src_dir.glob("*.ipynb"):
        shutil.copy2(path, publish_root / path.name)
        print(f"Copied {path.name}")
