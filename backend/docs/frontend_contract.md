# Frontend Contract

This document defines the payloads the frontend can rely on for:

- Teacher dashboard
- Student mock-exam client
- Student formal-exam client
- Essay review UI
- Incident monitoring UI

---

## 1. Auth

### Login
`POST /api/auth/login`

Request:
```json id="i3i6gy"
{
  "email": "admin@example.com",
  "password": "secret123"
}

Response:
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}

Use the token in:

Authorization: Bearer JWT_TOKEN
