# JupyterLite Mock Exam Widget Contract

This document defines the contract between a JupyterLite notebook widget layer and the backend.

---

## 1. Purpose

The JupyterLite mock-exam widget is responsible for:

- rendering question prompts inside a notebook
- collecting answers for:
  - mcq_single
  - mcq_multi
  - fill_gap
  - short_answer
  - essay
- autosaving answers to the backend
- submitting the final mock exam attempt

The backend remains the source of truth.

---

## 2. Required Backend Endpoints

### Start Mock Exam
`POST /api/mock-exams/{assessment_id}/start`

### Get Mock Exam Paper
`GET /api/mock-exams/{assessment_id}/paper`

### Autosave
`POST /api/mock-exams/attempts/{attempt_id}/autosave`

### Submit
`POST /api/mock-exams/attempts/{attempt_id}/submit`

### Score Summary
`GET /api/mock-exams/attempts/{attempt_id}/scores`

---

## 3. Suggested Widget State Model

```json id="40079"
{
  "attempt_id": 11,
  "assessment_id": 5,
  "responses": {
    "1": {"selected_option": "a"},
    "2": {"gaps": {"GAP1": "created", "GAP2": "destroyed"}},
    "3": {"answer_text": "A Moore machine depends only on state."}
  }
}

## 4. Autosave Payload

{
  "responses": [
    {
      "question_id": 1,
      "response": {"selected_option": "a"}
    },
    {
      "question_id": 2,
      "response": {"gaps": {"GAP1": "created", "GAP2": "destroyed"}}
    },
    {
      "question_id": 3,
      "response": {"answer_text": "A Moore machine depends only on state."}
    }
  ]
}

## 5. Submission Payload
{
  "submitted_payload": {
    "widget_version": "v1",
    "submitted_from": "jupyterlite",
    "done": true
  }
}
