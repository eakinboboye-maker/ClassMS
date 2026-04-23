# Production Deployment Checklist

## Backend
- Set a strong `SECRET_KEY`
- Use PostgreSQL, not SQLite
- Run Alembic migrations before app start
- Enable HTTPS at the reverse proxy
- Restrict CORS to known frontend origins
- Configure structured logging
- Back up the database regularly

## Auth
- Change default seeded passwords
- Use institution SSO if available
- Review token lifetime settings
- Rotate compromised credentials quickly

## AI Grading
- Keep human-in-the-loop for essay/theory grading
- Log AI proposal outputs for auditing
- Add provider-level timeout and retry handling
- Review privacy policy for student responses

## Formal Exams
- Require SEB config key validation
- Use managed devices where possible
- Keep approved config hashes per exam
- Monitor heartbeat failures and replay incidents
- Test resume-token flow before exam day

## Workers
- Run grading worker continuously
- Run expiry check on a schedule
- Capture worker logs
- Alert on repeated job failures

## Monitoring
- Use health endpoint
- Monitor database availability
- Track failed logins
- Track incident dashboard events

## Frontends
- Keep backend base URL configurable
- Never hardcode production tokens
- Show autosave status clearly to students
- Handle expired-session responses gracefully

## Operational Readiness
- Test full mock-exam flow
- Test full formal-exam flow
- Test grade publication flow
- Test incident export flow
- Test backup and restore
