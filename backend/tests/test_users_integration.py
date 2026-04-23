def test_register_and_list_users(client):
    register_payload = {
        "email": "student1@example.com",
        "full_name": "Student One",
        "password": "secret123",
        "matric_no": "MAT001",
        "role": "admin",
    }

    r = client.post("/api/auth/register", json=register_payload)
    assert r.status_code == 200
    token = client.post(
        "/api/auth/login",
        json={"email": "student1@example.com", "password": "secret123"},
    ).json()["access_token"]

    r = client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1
