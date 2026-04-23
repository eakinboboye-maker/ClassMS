from sqlalchemy.orm import Session

from app.models.question import QuestionOption


def grade_mcq_single(db: Session, question_id: int, response: dict, max_marks: int) -> tuple[float, dict]:
    selected = response.get("selected_option")
    correct = db.query(QuestionOption).filter(
        QuestionOption.question_id == question_id,
        QuestionOption.is_correct.is_(True),
    ).first()

    awarded = float(max_marks if correct and selected == correct.option_key else 0)
    return awarded, {
        "policy": "exact_single",
        "selected": selected,
        "correct": correct.option_key if correct else None,
    }


def grade_mcq_multi(
    db: Session,
    question_id: int,
    response: dict,
    max_marks: int,
    policy: str = "exact",
) -> tuple[float, dict]:
    selected = set(response.get("selected_options", []))
    correct = {
        row.option_key
        for row in db.query(QuestionOption).filter(
            QuestionOption.question_id == question_id,
            QuestionOption.is_correct.is_(True),
        ).all()
    }

    if policy == "exact":
        awarded = float(max_marks if selected == correct else 0)

    elif policy == "partial":
        if not correct:
            awarded = 0.0
        else:
            hit = len(selected & correct)
            miss = len(selected - correct)
            raw = max(hit - miss, 0)
            awarded = float(max_marks * raw / len(correct))

    else:
        awarded = 0.0

    return awarded, {
        "policy": policy,
        "selected": sorted(selected),
        "correct": sorted(correct),
    }
