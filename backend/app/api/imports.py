import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.core.security import hash_password
from app.models.user import User
from app.models.course import Course, Section, Enrollment
from app.models.question import Question, QuestionOption
from app.schemas.imports import (
    ParseQuestionTextRequest,
    ParseQuestionTextResponse,
    PublishParsedQuestionsRequest,
    PublishParsedQuestionsResponse,
    ParseEnrollmentRowsRequest,
    ParseEnrollmentRowsResponse,
    BulkEnrollmentRequest,
    BulkEnrollmentResponse,
)
from app.schemas.user import BulkRosterImportRequest, BulkRosterImportResult, ParsedRosterResponse
from app.services.question_import_service import (
    parse_quiz_text,
    parse_mixed_question_csv_text,
    parse_enrollment_rows,
)
from app.services.roster_import_service import parse_csv_roster, parse_xlsx_roster_rows

router = APIRouter()


@router.post("/questions/parse-text", response_model=ParseQuestionTextResponse)
def parse_question_text(
    payload: ParseQuestionTextRequest,
    _: User = Depends(require_role("admin", "instructor")),
):
    items, warnings = parse_quiz_text(payload.text)
    return ParseQuestionTextResponse(count=len(items), items=items, warnings=warnings)


@router.post("/questions/parse-csv", response_model=ParseQuestionTextResponse)
def parse_question_csv(
    payload: ParseQuestionTextRequest,
    _: User = Depends(require_role("admin", "instructor")),
):
    items, errors = parse_mixed_question_csv_text(payload.text)
    warnings = [f"row {err['row']}: {err['error']}" for err in errors]
    return ParseQuestionTextResponse(count=len(items), items=items, warnings=warnings)


@router.post("/questions/publish", response_model=PublishParsedQuestionsResponse)
def publish_parsed_questions(
    payload: PublishParsedQuestionsRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    created_ids: list[int] = []

    for item in payload.items:
        question = Question(
            type=item.type,
            prompt_md=item.prompt_md,
            marks=item.marks,
            topics_json=json.dumps(item.topics),
            difficulty=None,
            answer_key_json=json.dumps(item.answer_key or {}),
            grading_mode=item.grading_mode,
            explanation_md=item.explanation_md,
            show_explanation_after_submit=item.show_explanation_after_submit,
            version=1,
        )
        db.add(question)
        db.flush()

        for opt in item.options:
            db.add(
                QuestionOption(
                    question_id=question.id,
                    option_key=opt.option_key,
                    text=opt.text,
                    is_correct=opt.is_correct,
                )
            )

        created_ids.append(question.id)

    db.commit()
    return PublishParsedQuestionsResponse(created_count=len(created_ids), created_ids=created_ids)


@router.post("/users/parse-csv", response_model=ParsedRosterResponse)
def parse_users_csv(
    payload: ParseQuestionTextRequest,
    _: User = Depends(require_role("admin", "instructor")),
):
    rows, errors = parse_csv_roster(payload.text)
    return ParsedRosterResponse(parsed_count=len(rows), rows=rows, errors=errors)


@router.post("/users/parse-xlsx-rows", response_model=ParsedRosterResponse)
def parse_users_xlsx_rows(
    payload: ParseEnrollmentRowsRequest,
    _: User = Depends(require_role("admin", "instructor")),
):
    rows, errors = parse_xlsx_roster_rows(payload.rows)
    return ParsedRosterResponse(parsed_count=len(rows), rows=rows, errors=errors)


@router.post("/users/bulk-create", response_model=BulkRosterImportResult)
def bulk_create_users(
    payload: BulkRosterImportRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    created_users = []
    created_count = 0
    skipped_count = 0

    for item in payload.users:
        existing = db.query(User).filter(User.email == item.email).first()
        if existing:
            if payload.skip_existing:
                skipped_count += 1
                continue
            raise HTTPException(status_code=400, detail=f"User already exists: {item.email}")

        password = item.password or payload.default_password
        user = User(
            email=item.email,
            full_name=item.full_name,
            matric_no=item.matric_no,
            role=item.role,
            hashed_password=hash_password(password),
        )
        db.add(user)
        db.flush()
        created_users.append(user)
        created_count += 1

    db.commit()

    return BulkRosterImportResult(
        created_count=created_count,
        skipped_count=skipped_count,
        created_users=created_users,
    )


@router.post("/enrollment/parse", response_model=ParseEnrollmentRowsResponse)
def parse_enrollment(
    payload: ParseEnrollmentRowsRequest,
    _: User = Depends(require_role("admin", "instructor")),
):
    rows, errors = parse_enrollment_rows(payload.rows)
    return ParseEnrollmentRowsResponse(parsed_count=len(rows), rows=rows, errors=errors)


@router.post("/enrollment/publish", response_model=BulkEnrollmentResponse)
def publish_enrollment(
    payload: BulkEnrollmentRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    enrolled_count = 0
    skipped_count = 0
    details = []

    for row in payload.rows:
        user = db.query(User).filter(User.matric_no == row.reg_no).first()
        course = db.query(Course).filter(Course.code == row.course_code).first()
        if not user or not course:
            skipped_count += 1
            details.append({"reg_no": row.reg_no, "status": "skipped_missing_user_or_course"})
            continue

        section = db.query(Section).filter(
            Section.course_id == course.id,
            Section.name == row.section,
            Section.term == row.session,
        ).first()
        if not section:
            skipped_count += 1
            details.append({"reg_no": row.reg_no, "status": "skipped_missing_section"})
            continue

        existing = db.query(Enrollment).filter(
            Enrollment.user_id == user.id,
            Enrollment.section_id == section.id,
        ).first()
        if existing:
            skipped_count += 1
            details.append({"reg_no": row.reg_no, "status": "skipped_existing_enrollment"})
            continue

        db.add(Enrollment(user_id=user.id, section_id=section.id, status="active"))
        enrolled_count += 1
        details.append({"reg_no": row.reg_no, "status": "enrolled"})

    db.commit()
    return BulkEnrollmentResponse(
        enrolled_count=enrolled_count,
        skipped_count=skipped_count,
        details=details,
    )
