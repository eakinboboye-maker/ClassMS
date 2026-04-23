from pathlib import Path


def test_openai_stub_doc_exists():
    path = Path("docs/openai_integration_stub.md")
    assert path.exists()
