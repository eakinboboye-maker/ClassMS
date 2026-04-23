def test_parse_xlsx_rows_endpoint(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "xlsx_admin@example.com",
            "full_name": "XLSX Admin",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "xlsx_admin@example.com", "password": "secret123"},
    ).json()["access_token"]

    rows = [
        {"Email Address": "x1@example.com", "Names": "Student X1", "Reg No.": "X001"},
        {"Email Address": "x2@example.com", "Names": "Student X2", "Reg No.": "X002"},
    ]

    r = client.post(
        "/api/users/parse-xlsx-rows",
        json={"rows": rows},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["parsed_count"] == 2
