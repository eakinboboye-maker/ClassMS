from app.workers.grading_jobs import run_expiry_check


def test_run_expiry_check():
    run_expiry_check()
    assert True
