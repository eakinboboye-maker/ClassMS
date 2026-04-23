from app.core.security import hash_password, verify_password


def test_hash_and_verify():
    password = "secret123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False
