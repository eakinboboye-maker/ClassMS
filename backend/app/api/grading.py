from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role, get_current_user
from app.models.user import User
from app.models.assessment import Assessment, Attempt
from app.models.grading import AIGradingJob, GradingReview, Score, GradePublication
from app.models.response import Response
from app.models.question import Question
from app.schemas.grading import (
    AIGradingRequest,
    ReviewDecisionRequest,
    GradePublicationRequest,
)
from app.services.gradebook_service import get_gradebook_rows
from app.services.essay_review_service import get_pending_essay_reviews
from app.services.analytics_service import get_section_analytics, get_course_analytics

router = APIRouter()


@router.post("/queue")
def queue_ai_grading(
    payload: AIGradingRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    for response_id in payload.response_ids:
        db.add(AIGradingJob(response_id=response_id, status="queued"))
    db.commit()
    return {"status": "queued"}


@router.get("/reviews")
def pending_reviews(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    return db.query(GradingReview).filter(GradingReview.status == "pending").all()


@router.get("/reviews/essay-items")
def pending_essay_review_items(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    return {"items": get_pending_essay_reviews(db)}


@router.post("/reviews/{review_id}/resolve")
def resolve_review(
    review_id: int,
    payload: ReviewDecisionRequest,
    db: Session = Depends(get_db),
    reviewer: User = Depends(require_role("admin", "instructor")),
):
    review = db.get(GradingReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    response = db.get(Response, review.response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")

    question = db.get(Question, response.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    review.status = "approved" if payload.approved else "rejected"
    review.final_score = payload.final_score
    review.comment = payload.reviewer_comment
    review.reviewer_id = reviewer.id

    db.add(
        Score(
            attempt_id=response.attempt_id,
            question_id=response.question_id,
            awarded_marks=payload.final_score,
            max_marks=question.marks,
            grading_method="ai_human_review",
            is_final=True,
        )
    )
    db.commit()
    return {"status": review.status}


@router.post("/assessments/{assessment_id}/publish")
def publish_assessment_grades(
    assessment_id: int,
    payload: GradePublicationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "instructor")),
):
    assessment = db.get(Assessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    publication = GradePublication(
        assessment_id=assessment_id,
        published_by=current_user.id,
        note=payload.note,
    )
    db.add(publication)
    db.commit()
    db.refresh(publication)
    return {"status": "published", "publication_id": publication.id}


@router.get("/assessments/{assessment_id}/gradebook")
def get_assessment_gradebook(
    assessment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    assessment = db.get(Assessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    rows = get_gradebook_rows(db, assessment_id=assessment_id)
    return {"assessment_id": assessment_id, "rows": rows}


@router.get("/gradebook")
def get_filtered_gradebook(
    course_id: int | None = Query(default=None),
    section_id: int | None = Query(default=None),
    assessment_id: int | None = Query(default=None),
    published_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    rows = get_gradebook_rows(
        db,
        course_id=course_id,
        section_id=section_id,
        assessment_id=assessment_id,
        published_only=published_only,
    )
    return {"rows": rows}


@router.get("/analytics/section/{section_id}")
def section_analytics(
    section_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    return {"rows": get_section_analytics(db, section_id=section_id)}


@router.get("/analytics/course/{course_id}")
def course_analytics(
    course_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    return {"rows": get_course_analytics(db, course_id=course_id)}


@router.get("/my-grades/{assessment_id}")
def get_my_published_grade(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    publication = db.query(GradePublication).filter(GradePublication.assessment_id == assessment_id).first()
    if not publication:
        raise HTTPException(status_code=403, detail="Grades not yet published")

    attempt = (
        db.query(Attempt)
        .filter(Attempt.assessment_id == assessment_id, Attempt.user_id == current_user.id)
        .order_by(Attempt.id.desc())
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    scores = db.query(Score).filter(Score.attempt_id == attempt.id).all()
    return {
        "assessment_id": assessment_id,
        "attempt_id": attempt.id,
        "total_awarded": sum(s.awarded_marks for s in scores),
        "total_max": sum(s.max_marks for s in scores),
        "scores": [
            {
                "question_id": s.question_id,
                "awarded_marks": s.awarded_marks,
                "max_marks": s.max_marks,
                "grading_method": s.grading_method,
            }
            for s in scores
        ],
    }
