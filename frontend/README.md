# ClassLite Frontend

This folder contains two Vercel-ready Next.js apps:

- `teacher-dashboard/` — teacher and admin interface
- `exam-client/` — formal exam interface

## Local development

Teacher dashboard:
```bash
cd teacher-dashboard
cp .env.local.example .env.local
npm install
npm run dev
```

Formal exam client:
```bash
cd exam-client
cp .env.local.example .env.local
npm install
npm run dev
```

## Environment variable

Set in both apps:

```bash
NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.onrender.com
```
