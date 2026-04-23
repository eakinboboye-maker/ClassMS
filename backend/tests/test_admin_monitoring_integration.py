from datetime import datetime, timedelta


def test_admin_attempt_monitoring(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "admin_monitor@example.com",
            "full_name": "Admin Monitor",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "admin_monitor@example.com", "password": "secret123"},
    ).json()["access_token"]

    course = client.post(
        "/api/courses/",
        json={"code": "EEE356", "title": "Digital Systems", "description": "desc"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    section = client.post(
        "/api/courses/sections",
        json={
            "course_id": course["id"],
            "name": "B",
            "term": "2026/2027",
            "instructor_id": None,
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    q = client.post(
        "/api/questions/",
        json={
            "type": "mcq_single",
            "prompt_md": "Choose one",
            "marks": 1,
            "options": [
                {"option_key": "a", "text": "A", "is_correct": True},
                {"option_key": "b", "text": "B", "is_correct": False},
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    now = datetime.utcnow()
    exam = client.post(
        "/api/mock-exams/",
        json={
            "title": "Mock Exam",
            "type": "mock",
            "section_id": section["id"],
            "duration_minutes": 30,
            "shuffle_questions": False,
            "requires_seb": False,
            "allow_resume": True,
            "question_ids": [q["id"]],
            "open_time": now.isoformat(),
            "close_time": (now + timedelta(hours=1)).isoformat(),
            "candidate_user_ids": [],
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    attempts = client.get(
        f"/api/admin/assessments/{exam['id']}/attempts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert attempts.status_code == 200
    assert isinstance(attempts.json(), list)
