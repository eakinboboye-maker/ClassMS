
---

# `README.md`

Create this monorepo root README.

```md
# ClassLite Monorepo

This repository contains:

- `backend/` — FastAPI backend for courses, question banks, mock exams, formal exams, grading, attendance, and admin tools
- `frontend/teacher-dashboard/` — minimal Next.js teacher dashboard scaffold
- `frontend/exam-client/` — minimal Next.js formal exam client scaffold
- `frontend/shared/` — shared frontend API client and JupyterLite widget examples

## High-level architecture

### Teaching and mock exams
- JupyterLite for lessons, in-class quizzes, and mock exams
- backend stores authoritative submissions and grades
- essay/theory in mock exams can be AI-assisted with human review

### Formal exams
- dedicated exam client
- backend enforces candidate eligibility, exam-session tokens, resume tokens, and incident tracking
- SEB is required for the secure exam shell

## Quick start

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python seed_demo_data.py
uvicorn app.main:app --reload

### Teacher dashboard

cd frontend/teacher-dashboard
npm install
npm run dev

### Exam client

cd frontend/exam-client
npm install
npm run dev


