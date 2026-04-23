from app.services.fillgap_grader import normalize_answer


def test_normalize_answer():
    assert normalize_answer("  Created! ") == "created"
