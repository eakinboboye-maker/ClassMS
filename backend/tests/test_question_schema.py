import pytest
from app.schemas.question import QuestionCreate


def test_mcq_single_requires_one_correct():
    with pytest.raises(Exception):
        QuestionCreate(
            type="mcq_single",
            prompt_md="Pick one",
            marks=1,
            options=[
                {"option_key": "a", "text": "A", "is_correct": False},
                {"option_key": "b", "text": "B", "is_correct": False},
            ],
        )


def test_fill_gap_requires_answers():
    with pytest.raises(Exception):
        QuestionCreate(
            type="fill_gap",
            prompt_md="Fill this",
            marks=2,
            gaps=[{"gap_key": "G1", "marks": 1, "position": 0, "accepted_answers": []}],
        )
