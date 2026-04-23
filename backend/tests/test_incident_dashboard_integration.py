def test_incident_dashboard_empty(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "incident_admin@example.com",
            "full_name": "Incident Admin",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "incident_admin@example.com", "password": "secret123"},
    ).json()["access_token"]

    r = client.get(
        "/api/admin/incidents/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert "rows" in r.json()
