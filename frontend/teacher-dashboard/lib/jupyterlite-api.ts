import { apiFetch } from "./imports-api";

export type LessonConfigPayload = {
  lesson_slug: string;
  course_code: string;
  title: string;
  assessment_id?: number | null;
  attendance_session_id?: number | null;
  question_keys: Record<string, unknown>;
  notebook_path: string;
  attendance_open_at?: string | null;
  attendance_close_at?: string | null;
  show_on_portal: boolean;
  allow_portal_mock_exam: boolean;
  is_active: boolean;
};

export async function createLessonConfig(payload: LessonConfigPayload) {
  return apiFetch("/api/jupyterlite/lesson-config", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateLessonConfig(lessonSlug: string, payload: Partial<LessonConfigPayload>) {
  return apiFetch(`/api/jupyterlite/lesson-config/${encodeURIComponent(lessonSlug)}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function getLessonConfig(lessonSlug: string) {
  return apiFetch(`/api/jupyterlite/lesson-config/${encodeURIComponent(lessonSlug)}`, {
    method: "GET",
  });
}

export async function createOrUpdateLessonConfig(payload: LessonConfigPayload) {
  try {
    return await createLessonConfig(payload);
  } catch (err: any) {
    const message = String(err?.message || err || "");
    if (message.includes("lesson_slug already exists") || message.includes("400")) {
      return updateLessonConfig(payload.lesson_slug, payload);
    }
    throw err;
  }
}
