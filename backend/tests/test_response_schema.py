import pytest
from app.schemas.response import ResponseSave


def test_response_not_empty():
    with pytest.raises(Exception):
        ResponseSave(question_id=1, response={})
