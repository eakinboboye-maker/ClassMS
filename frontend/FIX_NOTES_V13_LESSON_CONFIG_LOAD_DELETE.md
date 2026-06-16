# V13 Lesson Config Load/Delete

This patch extends the Vercel teacher dashboard lesson config workflow.

## Frontend route

Open:

```text
/lesson-configs
```

The page now supports:

1. Listing existing lesson launch configs.
2. Loading a config from the table.
3. Loading a config by typing its `lesson_slug`.
4. Deleting the current config.
5. Deleting a config from the table.
6. Refreshing the list after create/update/delete.

## Changed frontend files

```text
frontend/teacher-dashboard/app/lesson-configs/page.tsx
frontend/teacher-dashboard/lib/jupyterlite-api.ts
frontend/teacher-dashboard/app/globals.css
```

## Backend routes needed

The frontend calls these routes:

```text
GET    /api/jupyterlite/lesson-configs
GET    /api/jupyterlite/lesson-config/{lesson_slug}
POST   /api/jupyterlite/lesson-config
PUT    /api/jupyterlite/lesson-config/{lesson_slug}
DELETE /api/jupyterlite/lesson-config/{lesson_slug}
```

Your backend already had GET-by-slug, POST, and PUT. If your backend does not yet have list/delete, add the snippet in:

```text
frontend/backend_patches/jupyterlite_portal_list_delete_lesson_config_snippet.py
```

## Delete behavior

Delete removes only the `lesson_launch_configs` row. It does not delete:

```text
courses
sections
enrollments
assessments
questions
attempts
responses
scores
notebook files
```

This is intentional so you can hide/remove a portal launch record without destroying assessment history.

## Build

```bash
cd frontend/teacher-dashboard
npm install
npm run build
```

Then redeploy on Vercel.
