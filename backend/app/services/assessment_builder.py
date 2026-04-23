from sqlalchemy.orm import Session

from app.models.assessment import Assessment, AssessmentWindow, AssessmentCandidate, AssessmentItem
from app.models.question import Question
from app.schemas.assessment import AssessmentCreate, AssessmentBlueprintCreate


def build_assessment(db: Session, payload: AssessmentCreate) -> Assessment:
    assessment = Assessment(
        title=payload.title,
        type=payload.type,
        section_id=payload.section_id,
        duration_minutes=payload.duration_minutes,
        shuffle_questions=payload.shuffle_questions,
        requires_seb=payload.requires_seb,
        allow_resume=payload.allow_resume,
        instructions_md=payload.instructions_md,
        status="published",
    )
    db.add(assessment)
    db.flush()

    window = AssessmentWindow(
        assessment_id=assessment.id,
        open_time=payload.open_time,
        close_time=payload.close_time,
    )
    db.add(window)

    for order_index, qid in enumerate(payload.question_ids, start=1):
        question = db.get(Question, qid)
        if not question:
            continue
        db.add(
            AssessmentItem(
                assessment_id=assessment.id,
                question_id=qid,
                order_index=order_index,
                frozen_question_version=question.version,
            )
        )

    for uid in payload.candidate_user_ids:
        db.add(AssessmentCandidate(assessment_id=assessment.id, user_id=uid))

    db.commit()
    db.refresh(assessment)
    return assessment


def build_assessment_from_blueprint(db: Session, payload: AssessmentBlueprintCreate) -> Assessment:
    selected_questions: list[Question] = []

    for rule in payload.rules:
        query = db.query(Question)

        if rule.question_type:
            query = query.filter(Question.type == rule.question_type)
        if rule.difficulty:
            query = query.filter(Question.difficulty == rule.difficulty)
        if rule.topic:
            query = query.filter(Question.topics_json.like(f'%"{rule.topic}"%'))

        rows = query.order_by(Question.id.asc()).limit(rule.count).all()

        if len(rows) < rule.count:
            raise ValueError(
                f"Not enough questions for rule: type={rule.question_type}, "
                f"difficulty={rule.difficulty}, topic={rule.topic}, needed={rule.count}"
            )

        selected_questions.extend(rows)

    create_payload = AssessmentCreate(
        title=payload.title,
        type=payload.type,
        section_id=payload.section_id,
        duration_minutes=payload.duration_minutes,
        shuffle_questions=payload.shuffle_questions,
        requires_seb=payload.requires_seb,
        allow_resume=payload.allow_resume,
        instructions_md=payload.instructions_md,
        question_ids=[q.id for q in selected_questions],
        open_time=payload.open_time,
        close_time=payload.close_time,
        candidate_user_ids=payload.candidate_user_ids,
    )
    return build_assessment(db, create_payload)
