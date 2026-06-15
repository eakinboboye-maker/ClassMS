import { apiFetch } from "./imports-api";

export async function listCourses() {
  return apiFetch("/api/courses", { method: "GET" });
}

export async function createCourse(payload: {
  code: string;
  title: string;
  description?: string;
}) {
  return apiFetch("/api/courses", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function createSection(
  courseId: number | string,
  payload: {
    name: string;
    term: string;
    capacity?: number | null;
  }
) {
  return apiFetch(`/api/courses/sections`, {
    method: "POST",
    body: JSON.stringify({
      course_id: Number(courseId),
      ...payload,
    }),
  });
}
