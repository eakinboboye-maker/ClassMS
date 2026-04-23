from datetime import datetime, timedelta


def test_mock_exam_full_flow(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "mock_admin@example.com",
            "full_name": "Mock Admin",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "mock_admin@example.com", "password": "secret123"},
    ).json()["access_token"]

    course = client.post(
        "/api/courses/",
        json={"code": "EEE500", "title": "Mock Course", "description": "desc"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    section = client.post(
        "/api/courses/sections",
        json={
            "course_id": course["id"],
            "name": "M1",
            "term": "2026/2027",
            "instructor_id": None,
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    q = client.post(
        "/api/questions/",
        json={
            "type": "mcq_single",
            "prompt_md": "2 + 2 = ?",
            "marks": 1,
            "options": [
                {"option_key": "a", "text": "4", "is_correct": True},
                {"option_key": "b", "text": "5", "is_correct": False},
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    now = datetime.utcnow()
    exam = client.post(
        "/api/mock-exams/",
        json={
            "title": "Mock Arithmetic",
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

    start = client.post(
        f"/api/mock-exams/{exam['id']}/start",
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    autosave = client.post(
        f"/api/mock-exams/attempts/{start['attempt_id']}/autosave",
        json={
            "responses": [
                {"question_id": q["id"], "response": {"selected_option": "a"}}
            ]
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert autosave.status_code == 200

    submit = client.post(
        f"/api/mock-exams/attempts/{start['attempt_id']}/submit",
        json={"submitted_payload": {"done": True}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert submit.status_code == 200

    scores = client.get(
        f"/api/mock-exams/attempts/{start['attempt_id']}/scores",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert scores.status_code == 200
    assert scores.json()["total_awarded"] == 1.0
