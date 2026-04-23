import pytest
from datetime import datetime, timedelta
from app.schemas.assessment import AssessmentCreate


def test_assessment_create_valid():
    now = datetime.utcnow()
    payload = AssessmentCreate(
        title="Mock 1",
        type="mock",
        section_id=1,
        duration_minutes=60,
        question_ids=[1, 2],
        open_time=now,
        close_time=now + timedelta(hours=1),
    )
    assert payload.type == "mock"


def test_assessment_duration_positive():
    now = datetime.utcnow()
    with pytest.raises(Exception):
        AssessmentCreate(
            title="Bad",
            type="mock",
            section_id=1,
            duration_minutes=0,
            question_ids=[1],
            open_time=now,
            close_time=now + timedelta(hours=1),
        )
