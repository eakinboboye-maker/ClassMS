Required portal-oriented backend endpoints:

Auth:
- POST /api/auth/login
- GET /api/auth/me

Portal:
- GET /api/jupyterlite/portal/home
- POST /api/jupyterlite/portal/launch/{lesson_slug}
- GET /api/jupyterlite/portal/performance

Attendance:
- GET /api/jupyterlite/attendance-window/{lesson_slug}
- POST /api/jupyterlite/attendance/{lesson_slug}/mark

Portal mock exam:
- POST /api/jupyterlite/portal/mock-exams/{lesson_slug}/start
- GET /api/jupyterlite/portal/mock-exams/{attempt_id}/paper
- POST /api/jupyterlite/portal/mock-exams/{attempt_id}/autosave
- POST /api/jupyterlite/portal/mock-exams/{attempt_id}/submit
- GET /api/jupyterlite/portal/mock-exams/{attempt_id}/results

Notebook quiz:
- POST /api/mock-exams/{assessment_id}/start
- GET /api/mock-exams/{assessment_id}/paper
- POST /api/mock-exams/attempts/{attempt_id}/autosave
- POST /api/mock-exams/attempts/{attempt_id}/submit
- GET /api/mock-exams/attempts/{attempt_id}/results
