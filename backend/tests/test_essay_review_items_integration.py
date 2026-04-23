def test_pending_essay_review_items_empty(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "essay_admin@example.com",
            "full_name": "Essay Admin",
            "password": "secret123",
            "role": "admin",
        },
    )
    token = client.post(
        "/api/auth/login",
        json={"email": "essay_admin@example.com", "password": "secret123"},
    ).json()["access_token"]

    r = client.get(
        "/api/grading/reviews/essay-items",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert "items" in r.json()
