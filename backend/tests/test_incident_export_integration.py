def test_incident_export_endpoints(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "export_admin@example.com",
            "full_name": "Export Admin",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "export_admin@example.com", "password": "secret123"},
    ).json()["access_token"]

    json_resp = client.get(
        "/api/admin/incidents/export.json",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert json_resp.status_code == 200
    assert "rows" in json_resp.json()

    csv_resp = client.get(
        "/api/admin/incidents/export.csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert csv_resp.status_code == 200
    assert "incident_id" in csv_resp.text
