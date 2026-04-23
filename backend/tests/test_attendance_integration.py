from datetime import datetime, timedelta


def test_attendance_session_and_marking(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "attendance_admin@example.com",
            "full_name": "Attendance Admin",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "attendance_admin@example.com", "password": "secret123"},
    ).json()["access_token"]

    course = client.post(
        "/api/courses/",
        json={"code": "EEE355", "title": "Computation Structures", "description": "desc"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    section = client.post(
        "/api/courses/sections",
        json={
            "course_id": course["id"],
            "name": "A",
            "term": "2026/2027",
            "instructor_id": None,
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    now = datetime.utcnow()
    session_payload = {
        "section_id": section["id"],
        "title": "Week 1 Attendance",
        "open_time": now.isoformat(),
        "close_time": (now + timedelta(minutes=30)).isoformat(),
        "mode": "checkpoint",
    }

    attendance_session = client.post(
        "/api/courses/attendance/sessions",
        json=session_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert attendance_session.status_code == 200
    attendance_session_id = attendance_session.json()["id"]

    mark_resp = client.post(
        "/api/courses/attendance/mark",
        json={"attendance_session_id": attendance_session_id, "status": "present"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert mark_resp.status_code == 200
    assert mark_resp.json()["status"] == "present"
