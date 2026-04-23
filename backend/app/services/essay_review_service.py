import json
from sqlalchemy.orm import Session

from app.models.grading import GradingReview, AIGradingJob, AIGradingResult
from app.models.response import Response
from app.models.question import Question
from app.models.assessment import Attempt


def build_essay_review_item(db: Session, review: GradingReview) -> dict | None:
    response = db.get(Response, review.response_id)
    if not response:
        return None

    question = db.get(Question, response.question_id)
    if not question:
        return None

    attempt = db.get(Attempt, response.attempt_id)
    if not attempt:
        return None

    job = (
        db.query(AIGradingJob)
        .filter(AIGradingJob.response_id == response.id)
        .order_by(AIGradingJob.id.desc())
        .first()
    )
    result = None
    if job:
        result = (
            db.query(AIGradingResult)
            .filter(AIGradingResult.job_id == job.id)
            .order_by(AIGradingResult.id.desc())
            .first()
        )

    response_payload = json.loads(response.response_json)
    student_answer = response_payload.get("answer_text", "")

    return {
        "review_id": review.id,
        "response_id": response.id,
        "question_id": question.id,
        "attempt_id": attempt.id,
        "user_id": attempt.user_id,
        "prompt_md": question.prompt_md,
        "student_answer": student_answer,
        "proposed_score": result.proposed_score if result else None,
        "confidence": result.confidence if result else None,
        "criteria": json.loads(result.criteria_json) if result and result.criteria_json else [],
        "flags": json.loads(result.flags_json) if result and result.flags_json else [],
        "rationale": json.loads(result.rationale_json) if result and result.rationale_json else None,
        "max_marks": float(question.marks),
    }


def get_pending_essay_reviews(db: Session) -> list[dict]:
    reviews = db.query(GradingReview).filter(GradingReview.status == "pending").all()
    items = []
    for review in reviews:
        item = build_essay_review_item(db, review)
        if item:
            items.append(item)
    return items
