from pathlib import Path


def test_deployment_checklist_exists():
    path = Path("docs/production_deployment_checklist.md")
    assert path.exists()
