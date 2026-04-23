def test_bulk_roster_import(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "admin_roster@example.com",
            "full_name": "Admin Roster",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "admin_roster@example.com", "password": "secret123"},
    ).json()["access_token"]

    payload = {
        "users": [
            {
                "email": "s1@example.com",
                "full_name": "Student 1",
                "matric_no": "S001",
                "role": "student",
            },
            {
                "email": "s2@example.com",
                "full_name": "Student 2",
                "matric_no": "S002",
                "role": "student",
            },
        ],
        "default_password": "welcome123",
        "skip_existing": True,
    }

    r = client.post(
        "/api/users/bulk-import",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["created_count"] == 2
    assert data["skipped_count"] == 0
