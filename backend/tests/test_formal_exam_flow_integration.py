from datetime import datetime, timedelta


def test_formal_exam_flow_requires_candidate_and_seb(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "formal_admin@example.com",
            "full_name": "Formal Admin",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "formal_admin@example.com", "password": "secret123"},
    ).json()["access_token"]

    course = client.post(
        "/api/courses/",
        json={"code": "EEE600", "title": "Formal Course", "description": "desc"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    section = client.post(
        "/api/courses/sections",
        json={
            "course_id": course["id"],
            "name": "F1",
            "term": "2026/2027",
            "instructor_id": None,
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    q = client.post(
        "/api/questions/",
        json={
            "type": "mcq_single",
            "prompt_md": "Capital of France?",
            "marks": 1,
            "options": [
                {"option_key": "a", "text": "Paris", "is_correct": True},
                {"option_key": "b", "text": "Rome", "is_correct": False},
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    now = datetime.utcnow()
    exam = client.post(
        "/api/formal-exams/",
        json={
            "title": "Formal Geography",
            "type": "formal",
            "section_id": section["id"],
            "duration_minutes": 30,
            "shuffle_questions": False,
            "requires_seb": True,
            "allow_resume": True,
            "question_ids": [q["id"]],
            "open_time": now.isoformat(),
            "close_time": (now + timedelta(hours=1)).isoformat(),
            "candidate_user_ids": [1],
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    client.post(
        f"/api/admin/seb-config-key/{exam['id']}",
        json={"config_key_hash": "valid-config-key"},
        headers={"Authorization": f"Bearer {token}"},
    )

    start = client.post(
        f"/api/formal-exams/{exam['id']}/start",
        headers={
            "Authorization": f"Bearer {token}",
            "X-SafeExamBrowser-ConfigKeyHash": "valid-config-key",
        },
    )
    assert start.status_code == 200
