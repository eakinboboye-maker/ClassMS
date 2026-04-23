import re
from sqlalchemy.orm import Session

from app.models.question import QuestionGap, AcceptedAnswer


def normalize_answer(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = " ".join(text.split())
    return text


def grade_fill_gap(db: Session, question_id: int, response: dict) -> tuple[float, dict]:
    gaps_payload = response.get("gaps", {})
    gaps = db.query(QuestionGap).filter(QuestionGap.question_id == question_id).all()

    total = 0.0
    details = []

    for gap in gaps:
        accepted_rows = db.query(AcceptedAnswer).filter(AcceptedAnswer.gap_id == gap.id).all()
        accepted = {row.normalized_text for row in accepted_rows}
        student_raw = gaps_payload.get(gap.gap_key, "")
        student_norm = normalize_answer(student_raw)

        ok = student_norm in accepted
        awarded = float(gap.marks if ok else 0.0)
        total += awarded

        details.append(
            {
                "gap_key": gap.gap_key,
                "student": student_raw,
                "normalized": student_norm,
                "accepted": sorted(accepted),
                "awarded": awarded,
                "max_marks": gap.marks,
            }
        )

    return total, {"gaps": details}
