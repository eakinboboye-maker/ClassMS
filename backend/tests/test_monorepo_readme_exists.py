from pathlib import Path


def test_monorepo_readme_exists():
    path = Path("../README.md")
    assert path.exists()
