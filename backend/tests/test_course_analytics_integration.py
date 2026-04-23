def test_course_analytics_empty(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "analytics_admin@example.com",
            "full_name": "Analytics Admin",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "analytics_admin@example.com", "password": "secret123"},
    ).json()["access_token"]

    r = client.get(
        "/api/grading/analytics/course/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert "rows" in r.json()
