import json
from sqlalchemy.orm import Session

from app.models.question import Question, QuestionOption, QuestionGap, AcceptedAnswer
from app.schemas.question import QuestionCreate


def create_question_from_schema(db: Session, payload: QuestionCreate) -> Question:
    answer_key = payload.answer_key or {}
    if payload.rubric:
        answer_key["rubric"] = [r.model_dump() for r in payload.rubric]

    question = Question(
        type=payload.type,
        prompt_md=payload.prompt_md,
        marks=payload.marks,
        difficulty=payload.difficulty,
        topics_json=json.dumps(payload.topics),
        answer_key_json=json.dumps(answer_key) if answer_key else None,
        grading_mode=payload.grading_mode,
    )
    db.add(question)
    db.flush()

    for option in payload.options:
        db.add(
            QuestionOption(
                question_id=question.id,
                option_key=option.option_key,
                text=option.text,
                is_correct=option.is_correct,
            )
        )

    for gap in payload.gaps:
        gap_row = QuestionGap(
            question_id=question.id,
            gap_key=gap.gap_key,
            marks=gap.marks,
            position=gap.position,
        )
        db.add(gap_row)
        db.flush()

        for ans in gap.accepted_answers:
            db.add(
                AcceptedAnswer(
                    gap_id=gap_row.id,
                    text=ans,
                    normalized_text=" ".join(ans.strip().lower().split()),
                )
            )

    return question


def export_question_to_dict(db: Session, question: Question) -> dict:
    options = db.query(QuestionOption).filter(QuestionOption.question_id == question.id).all()
    gaps = db.query(QuestionGap).filter(QuestionGap.question_id == question.id).order_by(QuestionGap.position).all()

    gap_items = []
    for gap in gaps:
        answers = db.query(AcceptedAnswer).filter(AcceptedAnswer.gap_id == gap.id).all()
        gap_items.append(
            {
                "gap_key": gap.gap_key,
                "marks": gap.marks,
                "position": gap.position,
                "accepted_answers": [a.text for a in answers],
            }
        )

    return {
        "id": question.id,
        "type": question.type,
        "prompt_md": question.prompt_md,
        "marks": question.marks,
        "difficulty": question.difficulty,
        "topics": json.loads(question.topics_json) if question.topics_json else [],
        "grading_mode": question.grading_mode,
        "options": [
            {
                "option_key": o.option_key,
                "text": o.text,
                "is_correct": o.is_correct,
            }
            for o in options
        ],
        "gaps": gap_items,
        "answer_key": json.loads(question.answer_key_json) if question.answer_key_json else None,
    }
