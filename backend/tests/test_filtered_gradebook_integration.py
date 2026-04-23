def test_filtered_gradebook_empty(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "filter_grade_admin@example.com",
            "full_name": "Filter Grade Admin",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "filter_grade_admin@example.com", "password": "secret123"},
    ).json()["access_token"]

    r = client.get(
        "/api/grading/gradebook?published_only=false",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert "rows" in r.json()
