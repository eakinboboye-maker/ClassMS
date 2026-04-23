def test_question_bank_import_export(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "bank_admin@example.com",
            "full_name": "Bank Admin",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "bank_admin@example.com", "password": "secret123"},
    ).json()["access_token"]

    import_payload = {
        "questions": [
            {
                "type": "mcq_single",
                "prompt_md": "Sun rises in the?",
                "marks": 1,
                "topics": ["geography"],
                "options": [
                    {"option_key": "a", "text": "East", "is_correct": True},
                    {"option_key": "b", "text": "West", "is_correct": False},
                ],
            }
        ]
    }

    r = client.post(
        "/api/questions/import",
        json=import_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["count"] == 1

    exported = client.get(
        "/api/questions/export",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert exported.status_code == 200
    assert len(exported.json()["questions"]) >= 1
