def test_parse_csv_roster_endpoint(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "parse_admin@example.com",
            "full_name": "Parse Admin",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "parse_admin@example.com", "password": "secret123"},
    ).json()["access_token"]

    csv_content = "email,full_name,matric_no\ns1@example.com,Student One,S001\ns2@example.com,Student Two,S002\n"

    r = client.post(
        "/api/users/parse-csv",
        json={"csv_content": csv_content},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["parsed_count"] == 2
    assert len(data["rows"]) == 2
