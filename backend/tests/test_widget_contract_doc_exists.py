from pathlib import Path


def test_widget_contract_doc_exists():
    path = Path("docs/jupyterlite_mock_exam_widget_contract.md")
    assert path.exists()
