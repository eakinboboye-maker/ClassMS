# ClassLite JupyterLite Portal Fix v4

## What v4 fixes

The notebook previously called:

```text
POST /api/mock-exams/{assessment_id}/start
```

That produced a bare `HTTPError: 400` inside JupyterLite. The frontend portal already uses lesson-slug based portal endpoints, so v4 makes the notebook use the same route family first:

```text
POST /api/jupyterlite/portal/mock-exams/{lesson_slug}/start
GET  /api/jupyterlite/portal/mock-exams/{attempt_id}/paper
POST /api/jupyterlite/portal/mock-exams/{attempt_id}/autosave
POST /api/jupyterlite/portal/mock-exams/{attempt_id}/submit
GET  /api/jupyterlite/portal/mock-exams/{attempt_id}/results
```

The older assessment-id routes remain as fallback only if the portal route is missing.

## Other retained fixes

- `/` redirects to `/portal/index.html` without breaking JupyterLite config loading.
- Lab opens from the portal with `../lab/index.html?path=...`.
- Attendance marking remains disabled in the frontend.
- Backend errors now include the response body in the notebook exception.
