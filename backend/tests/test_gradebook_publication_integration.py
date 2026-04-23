from datetime import datetime, timedelta


def test_grade_publication_and_lookup(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "grade_admin@example.com",
            "full_name": "Grade Admin",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "grade_admin@example.com", "password": "secret123"},
    ).json()["access_token"]

    course = client.post(
        "/api/courses/",
        json={"code": "EEE700", "title": "Gradebook Course", "description": "desc"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    section = client.post(
        "/api/courses/sections",
        json={
            "course_id": course["id"],
            "name": "G1",
            "term": "2026/2027",
            "instructor_id": None,
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    q = client.post(
        "/api/questions/",
        json={
            "type": "mcq_single",
            "prompt_md": "1+1?",
            "marks": 1,
            "options": [
                {"option_key": "a", "text": "2", "is_correct": True},
                {"option_key": "b", "text": "3", "is_correct": False},
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    now = datetime.utcnow()
    exam = client.post(
        "/api/mock-exams/",
        json={
            "title": "Grade Mock",
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

    client.post(
        f"/api/mock-exams/attempts/{start['attempt_id']}/autosave",
        json={"responses": [{"question_id": q["id"], "response": {"selected_option": "a"}}]},
        headers={"Authorization": f"Bearer {token}"},
    )

    client.post(
        f"/api/mock-exams/attempts/{start['attempt_id']}/submit",
        json={"submitted_payload": {"done": True}},
        headers={"Authorization": f"Bearer {token}"},
    )

    publish = client.post(
        f"/api/grading/assessments/{exam['id']}/publish",
        json={"note": "Released"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert publish.status_code == 200

    my_grade = client.get(
        f"/api/grading/my-grades/{exam['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert my_grade.status_code == 200
    assert my_grade.json()["total_awarded"] == 1.0
