# ClassLite JupyterLite Portal Fix v5

This version addresses the error where the xeus kernel attempted to load:

```text
/api/mock-exams/3/paper
```

and failed with a browser-level `NetworkError`.

## Key changes

- Adds clearer network/CORS error reporting in `_request_json`.
- Adds `lesson.debug_state()` so the notebook can reveal the current `assessment_id`, `attempt_id`, API mode, and launch context.
- Makes `fetch_paper()` avoid confusing `assessment_id` and `attempt_id`:
  - Portal mode uses `/api/jupyterlite/portal/mock-exams/{attempt_id}/paper`.
  - Legacy mode first uses `/api/mock-exams/{assessment_id}/paper`.
  - It only falls back to alternate endpoints when an endpoint is missing/unavailable.

## Backend check still required

If the browser still shows a network-level failure, fix the FastAPI CORS middleware and verify that the backend has a working paper route.
