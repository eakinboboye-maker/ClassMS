from pathlib import Path


def test_frontend_contract_exists():
    path = Path("docs/frontend_contract.md")
    assert path.exists()
