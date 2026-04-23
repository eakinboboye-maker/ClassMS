from app.services.objective_grader import grade_mcq_multi


class DummyOption:
    def __init__(self, option_key, is_correct):
        self.option_key = option_key
        self.is_correct = is_correct


def test_placeholder():
    assert True
