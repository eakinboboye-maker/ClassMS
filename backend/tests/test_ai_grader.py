from app.services.ai_grader import grade_essay_response


def test_ai_grader_returns_structure():
    result = grade_essay_response(
        question_prompt="Explain a Moore machine.",
        answer_key={"canonical_answer": "Outputs depend only on state."},
        rubric=[{"criterion": "States Moore depends on state", "points": 5}],
        student_answer="A Moore machine produces outputs based on current state.",
    )
    assert "proposed_score" in result
    assert "criteria" in result
    assert "flags" in result
