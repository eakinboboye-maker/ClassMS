from datetime import datetime, timedelta

from app.models.question import Question
from app.services.assessment_builder import build_assessment_from_blueprint
from app.schemas.assessment import AssessmentBlueprintCreate


def test_build_assessment_from_blueprint(db_session):
    q1 = Question(
        type="mcq_single",
        prompt_md="Q1",
        marks=1,
        difficulty="easy",
        topics_json='["logic"]',
        version=1,
    )
    q2 = Question(
        type="mcq_single",
        prompt_md="Q2",
        marks=1,
        difficulty="easy",
        topics_json='["logic"]',
        version=1,
    )
    db_session.add_all([q1, q2])
    db_session.commit()

    now = datetime.utcnow()
    payload = AssessmentBlueprintCreate(
        title="Blueprint Test",
        type="mock",
        section_id=1,
        rules=[
            {"question_type": "mcq_single", "difficulty": "easy", "topic": "logic", "count": 2}
        ],
        open_time=now,
        close_time=now + timedelta(hours=1),
    )

    assessment = build_assessment_from_blueprint(db_session, payload)
    assert assessment.id is not None
    assert assessment.title == "Blueprint Test"
