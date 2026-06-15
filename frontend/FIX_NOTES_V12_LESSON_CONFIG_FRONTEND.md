# ClassLite Frontend v12: Lesson Configs from Vercel Teacher Dashboard

This patch adds a Vercel/Next.js teacher-dashboard page for creating and updating JupyterLite lesson launch configs from the frontend.

## New route

```text
/lesson-configs
```

The route lets an admin/instructor:

1. Select an existing course.
2. Create or update a `lesson_launch_configs` row through the backend.
3. Set `lesson_slug`, `course_code`, `title`, `notebook_path`, `assessment_id`, optional attendance settings, and visibility flags.
4. Load an existing config by slug.
5. See the backend response for troubleshooting.

## Files changed

```text
teacher-dashboard/app/layout.tsx
teacher-dashboard/app/globals.css
```

## Files added

```text
teacher-dashboard/app/lesson-configs/page.tsx
teacher-dashboard/lib/jupyterlite-api.ts
```

## Backend routes used

```text
POST /api/jupyterlite/lesson-config
PUT  /api/jupyterlite/lesson-config/{lesson_slug}
GET  /api/jupyterlite/lesson-config/{lesson_slug}
GET  /api/courses
```

The teacher must be logged in on the dashboard home page first, because the page uses the existing `classlite_teacher_session` token in localStorage.

## Visibility rule reminder

Creating a lesson config does not by itself make the lesson visible to every student. With the enrollment guard patch, a student sees the lesson only if:

```text
lesson_launch_configs.course_code == courses.code
and the student has an active enrollment in a section under that course.
```

Also ensure:

```text
show_on_portal = true
is_active = true
```

If mock exam launch is enabled, also ensure:

```text
allow_portal_mock_exam = true
assessment_id points to a real published/open assessment
```
