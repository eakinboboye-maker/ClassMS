from datetime import datetime
from sqlalchemy.orm import Session

from app.models.assessment import Attempt
from app.models.response import Response
from app.models.question import Question
from app.models.grading import Score
from app.services.autosave_service import finalize_attempt
from app.services.objective_grader import grade_mcq_single, grade_mcq_multi
from app.services.fillgap_grader import grade_fill_gap
import json


def auto_submit_expired_attempts(db: Session, assessment_type: str | None = None) -> list[int]:
    now = datetime.utcnow()

    query = db.query(Attempt).filter(
        Attempt.status == "in_progress",
        Attempt.expires_at.is_not(None),
        Attempt.expires_at <= now,
    )

    if assessment_type:
        from app.models.assessment import Assessment
        query = query.join(Assessment, Assessment.id == Attempt.assessment_id).filter(Assessment.type == assessment_type)

    attempts = query.all()
    submitted_attempt_ids: list[int] = []

    for attempt in attempts:
        responses = db.query(Response).filter(Response.attempt_id == attempt.id).all()

        for resp in responses:
            question = db.get(Question, resp.question_id)
            if not question:
                continue

            response_payload = json.loads(resp.response_json)

            if question.type == "mcq_single":
                awarded, _ = grade_mcq_single(db, question.id, response_payload, question.marks)
            elif question.type == "mcq_multi":
                awarded, _ = grade_mcq_multi(db, question.id, response_payload, question.marks)
            elif question.type == "fill_gap":
                awarded, _ = grade_fill_gap(db, question.id, response_payload)
            else:
                continue

            existing = db.query(Score).filter(
                Score.attempt_id == attempt.id,
                Score.question_id == question.id,
            ).first()
            if not existing:
                db.add(
                    Score(
                        attempt_id=attempt.id,
                        question_id=question.id,
                        awarded_marks=awarded,
                        max_marks=question.marks,
                        grading_method=question.type,
                        is_final=True,
                    )
                )

        attempt.is_auto_submitted = True
        finalize_attempt(db, attempt, {"auto_submitted": True})
        submitted_attempt_ids.append(attempt.id)

    return submitted_attempt_ids
