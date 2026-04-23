from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User
from app.models.question import Question
from app.schemas.question import (
    QuestionCreate,
    QuestionRead,
    QuestionBankImportRequest,
    QuestionBankExportResponse,
)
from app.services.question_bank_service import create_question_from_schema, export_question_to_dict

router = APIRouter()


@router.post("/", response_model=QuestionRead)
def create_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    question = create_question_from_schema(db, payload)
    db.commit()
    db.refresh(question)
    return question


@router.post("/import")
def import_question_bank(
    payload: QuestionBankImportRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    created_ids = []
    for item in payload.questions:
        q = create_question_from_schema(db, item)
        db.flush()
        created_ids.append(q.id)

    db.commit()
    return {"created_ids": created_ids, "count": len(created_ids)}


@router.get("/export", response_model=QuestionBankExportResponse)
def export_question_bank(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    questions = db.query(Question).order_by(Question.id.asc()).all()
    return QuestionBankExportResponse(
        questions=[export_question_to_dict(db, q) for q in questions]
    )


@router.get("/", response_model=list[QuestionRead])
def list_questions(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    return db.query(Question).all()


@router.get("/{question_id}", response_model=QuestionRead)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question
