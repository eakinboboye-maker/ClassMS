# Deploy with the least server work

## Backend on Render
1. Push this repo to GitHub.
2. In Render, create a new Blueprint from the repo root and select `render.yaml`.
3. Let Render create: 
   - managed Postgres
   - `classlite-backend` web service
   - `classlite-worker` background worker
   - `classlite-expiry` cron job
4. In the Render dashboard, set these environment variables on the backend service:
   - `CORS_ORIGINS` = your two Vercel frontend URLs separated by commas
   - `OPENAI_API_KEY` if using live AI grading
   - optionally `AI_PROVIDER=openai`
5. After first deploy, run a one-off job or shell command: `python seed_demo_data.py`.

## Frontends on Vercel
Create **two** separate Vercel projects from the same repo.

### Teacher dashboard
- Root Directory: `frontend/teacher-dashboard`
- Framework preset: Next.js
- Environment variable: `NEXT_PUBLIC_API_BASE_URL=https://<your-render-backend>.onrender.com`

### Exam client
- Root Directory: `frontend/exam-client`
- Framework preset: Next.js
- Environment variable: `NEXT_PUBLIC_API_BASE_URL=https://<your-render-backend>.onrender.com`

Redeploy both after setting env vars.

## Minimum production settings
- Replace demo passwords after first login
- Keep `AI_GRADING_REVIEW_REQUIRED=true`
- Keep `SEB_REQUIRED_FOR_FORMAL_EXAMS=true`
- Register a real SEB config hash for each formal exam
