from pathlib import Path


def test_frontend_api_client_exists():
    path = Path("../frontend/shared/frontend_api_client.ts")
    assert path.exists()
