"use client";

import { useEffect, useMemo, useState } from "react";
import { loadTeacherSession } from "../../lib/auth";
import { listCourses } from "../../lib/courses-api";
import {
  createLessonConfig,
  createOrUpdateLessonConfig,
  getLessonConfig,
  type LessonConfigPayload,
  updateLessonConfig,
} from "../../lib/jupyterlite-api";

type CourseRow = {
  id: number | string;
  code?: string;
  title?: string;
  description?: string;
  sections?: any[];
};

const defaultQuestionKeys = "{}";

function normalizeSlug(value: string) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

function toApiDateTime(value: string) {
  if (!value.trim()) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toISOString();
}

function fromApiDateTime(value: string | null | undefined) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function parseOptionalNumber(value: string, label: string) {
  const trimmed = value.trim();
  if (!trimmed) return null;
  const parsed = Number(trimmed);
  if (!Number.isFinite(parsed)) throw new Error(`${label} must be a number or blank.`);
  return parsed;
}

export default function LessonConfigsPage() {
  const [status, setStatus] = useState("");
  const [courses, setCourses] = useState<CourseRow[]>([]);
  const [loadingCourses, setLoadingCourses] = useState(false);
  const [saving, setSaving] = useState(false);

  const [lessonSlug, setLessonSlug] = useState("week01_intro");
  const [courseCode, setCourseCode] = useState("EEE355");
  const [title, setTitle] = useState("Week 01: Introduction to Computation");
  const [notebookPath, setNotebookPath] = useState("EEE355/week01_class_note.ipynb");
  const [assessmentId, setAssessmentId] = useState("1");
  const [attendanceSessionId, setAttendanceSessionId] = useState("");
  const [questionKeysJson, setQuestionKeysJson] = useState(defaultQuestionKeys);
  const [attendanceOpenAt, setAttendanceOpenAt] = useState("");
  const [attendanceCloseAt, setAttendanceCloseAt] = useState("");
  const [showOnPortal, setShowOnPortal] = useState(true);
  const [allowPortalMockExam, setAllowPortalMockExam] = useState(true);
  const [isActive, setIsActive] = useState(true);
  const [lastResponse, setLastResponse] = useState<any>(null);

  useEffect(() => {
    const session = loadTeacherSession();
    if (!session?.token) {
      setStatus("No teacher session found. Please sign in on the Home page.");
      return;
    }
    refreshCourses();
  }, []);

  const selectedCourse = useMemo(
    () => courses.find((course) => course.code === courseCode),
    [courses, courseCode]
  );

  async function refreshCourses() {
    try {
      setLoadingCourses(true);
      const payload = await listCourses();
      const rows = Array.isArray(payload) ? payload : payload.items || payload.courses || [];
      setCourses(rows);
      setStatus(`Loaded ${rows.length} course(s).`);
      if (rows.length && !courseCode) {
        const firstCode = rows[0]?.code || "";
        setCourseCode(firstCode);
      }
    } catch (err: any) {
      setStatus(err.message || "Failed to load courses");
    } finally {
      setLoadingCourses(false);
    }
  }

  function buildPayload(): LessonConfigPayload {
    const slug = normalizeSlug(lessonSlug);
    if (!slug) throw new Error("Lesson slug is required.");
    if (!courseCode.trim()) throw new Error("Course code is required.");
    if (!title.trim()) throw new Error("Lesson title is required.");
    if (!notebookPath.trim()) throw new Error("Notebook path is required.");

    let parsedQuestionKeys: Record<string, unknown>;
    try {
      const parsed = JSON.parse(questionKeysJson || "{}");
      if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") {
        throw new Error("Question keys must be a JSON object.");
      }
      parsedQuestionKeys = parsed;
    } catch (err: any) {
      throw new Error(`Invalid question_keys JSON: ${err.message || err}`);
    }

    const parsedAssessmentId = parseOptionalNumber(assessmentId, "Assessment ID");
    if (allowPortalMockExam && parsedAssessmentId === null) {
      throw new Error("Assessment ID is required when portal mock exam is enabled.");
    }

    return {
      lesson_slug: slug,
      course_code: courseCode.trim().toUpperCase(),
      title: title.trim(),
      assessment_id: parsedAssessmentId,
      attendance_session_id: parseOptionalNumber(attendanceSessionId, "Attendance session ID"),
      question_keys: parsedQuestionKeys,
      notebook_path: notebookPath.trim(),
      attendance_open_at: toApiDateTime(attendanceOpenAt),
      attendance_close_at: toApiDateTime(attendanceCloseAt),
      show_on_portal: showOnPortal,
      allow_portal_mock_exam: allowPortalMockExam,
      is_active: isActive,
    };
  }

  async function handleCreate() {
    try {
      setSaving(true);
      const payload = buildPayload();
      const response = await createLessonConfig(payload);
      setLastResponse(response);
      setLessonSlug(payload.lesson_slug);
      setStatus(`Created lesson config: ${payload.lesson_slug}`);
    } catch (err: any) {
      setStatus(err.message || "Failed to create lesson config");
    } finally {
      setSaving(false);
    }
  }

  async function handleUpdate() {
    try {
      setSaving(true);
      const payload = buildPayload();
      const response = await updateLessonConfig(payload.lesson_slug, payload);
      setLastResponse(response);
      setLessonSlug(payload.lesson_slug);
      setStatus(`Updated lesson config: ${payload.lesson_slug}`);
    } catch (err: any) {
      setStatus(err.message || "Failed to update lesson config");
    } finally {
      setSaving(false);
    }
  }

  async function handleCreateOrUpdate() {
    try {
      setSaving(true);
      const payload = buildPayload();
      const response = await createOrUpdateLessonConfig(payload);
      setLastResponse(response);
      setLessonSlug(payload.lesson_slug);
      setStatus(`Saved lesson config: ${payload.lesson_slug}`);
    } catch (err: any) {
      setStatus(err.message || "Failed to save lesson config");
    } finally {
      setSaving(false);
    }
  }

  async function handleLoadBySlug() {
    try {
      if (!lessonSlug.trim()) throw new Error("Enter a lesson slug first.");
      setSaving(true);
      const row = await getLessonConfig(normalizeSlug(lessonSlug));
      setLastResponse(row);
      setLessonSlug(row.lesson_slug || lessonSlug);
      setCourseCode(row.course_code || "");
      setTitle(row.title || "");
      setAssessmentId(row.assessment_id == null ? "" : String(row.assessment_id));
      setAttendanceSessionId(row.attendance_session_id == null ? "" : String(row.attendance_session_id));
      setQuestionKeysJson(JSON.stringify(row.question_keys || {}, null, 2));
      setNotebookPath(row.notebook_path || "");
      setAttendanceOpenAt(fromApiDateTime(row.attendance_open_at));
      setAttendanceCloseAt(fromApiDateTime(row.attendance_close_at));
      setShowOnPortal(Boolean(row.show_on_portal));
      setAllowPortalMockExam(Boolean(row.allow_portal_mock_exam));
      setIsActive(Boolean(row.is_active));
      setStatus(`Loaded lesson config: ${row.lesson_slug}`);
    } catch (err: any) {
      setStatus(err.message || "Failed to load lesson config");
    } finally {
      setSaving(false);
    }
  }

  function useSelectedCourseTemplate() {
    if (!courseCode.trim()) return;
    const code = courseCode.trim().toUpperCase();
    const slug = normalizeSlug(`${code}_week01_intro`);
    setLessonSlug(slug);
    setTitle(`${code} Week 01: Introduction`);
    setNotebookPath(`${code}/week01_intro.ipynb`);
  }

  return (
    <main>
      <h1 className="page-title">JupyterLite Lesson Configs</h1>
      <p className="page-subtitle">
        Create the portal launch record that makes a notebook lesson visible to enrolled students.
      </p>

      <section className="card card-accent">
        <h2 className="card-title">Teacher Session</h2>
        <div className="notice notice-info">
          {status || "Signed-in admin/instructor token will be used automatically."}
        </div>
      </section>

      <div className="grid-2">
        <section className="card">
          <h2 className="card-title">1. Choose Course</h2>
          <label className="label">Course Code</label>
          <select className="select" value={courseCode} onChange={(e) => setCourseCode(e.target.value)}>
            <option value="">Select a course</option>
            {courses.map((course) => (
              <option key={String(course.id)} value={course.code || ""}>
                {(course.code || "COURSE")} — {course.title || "Untitled"}
              </option>
            ))}
          </select>
          <div className="button-row">
            <button className="btn btn-secondary" onClick={refreshCourses} disabled={loadingCourses}>
              Refresh Courses
            </button>
            <button className="btn btn-secondary" onClick={useSelectedCourseTemplate} disabled={!courseCode}>
              Fill Week 01 Template
            </button>
          </div>
          <div className="notice notice-info">
            {selectedCourse ? (
              <>
                Selected: <strong>{selectedCourse.code}</strong> — {selectedCourse.title || "Untitled"}
              </>
            ) : (
              "Create the course and section first if it is not listed here."
            )}
          </div>
        </section>

        <section className="card">
          <h2 className="card-title">Visibility Rules</h2>
          <ul className="list compact-list">
            <li><strong>show_on_portal</strong> must be enabled.</li>
            <li><strong>is_active</strong> must be enabled.</li>
            <li>The student must be enrolled in this course code.</li>
            <li>If mock exam is enabled, the assessment must exist and be open.</li>
          </ul>
          <div className="notice notice-info">
            The portal will not show this lesson to a student unless the backend enrollment guard finds an active enrollment for the same course code.
          </div>
        </section>
      </div>

      <section className="card">
        <h2 className="card-title">2. Lesson Launch Config</h2>
        <div className="grid-2">
          <div>
            <label className="label">Lesson Slug</label>
            <input
              className="input"
              value={lessonSlug}
              onChange={(e) => setLessonSlug(e.target.value)}
              onBlur={(e) => setLessonSlug(normalizeSlug(e.target.value))}
              placeholder="eee356_week01_intro"
            />
          </div>
          <div>
            <label className="label">Course Code</label>
            <input
              className="input"
              value={courseCode}
              onChange={(e) => setCourseCode(e.target.value.toUpperCase())}
              placeholder="EEE356"
            />
          </div>
        </div>

        <div className="spacer-12" />
        <label className="label">Lesson Title</label>
        <input
          className="input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="EEE356 Week 01: Introduction"
        />

        <div className="spacer-12" />
        <label className="label">Notebook Path inside JupyterLite content</label>
        <input
          className="input"
          value={notebookPath}
          onChange={(e) => setNotebookPath(e.target.value)}
          placeholder="EEE356/week01_intro.ipynb"
        />
        <p className="form-hint">Do not include <code>content/</code>. Use the path as JupyterLite sees it.</p>

        <div className="grid-2 spacer-12">
          <div>
            <label className="label">Assessment ID</label>
            <input
              className="input"
              value={assessmentId}
              onChange={(e) => setAssessmentId(e.target.value)}
              placeholder="Required if mock exam is enabled"
            />
          </div>
          <div>
            <label className="label">Attendance Session ID</label>
            <input
              className="input"
              value={attendanceSessionId}
              onChange={(e) => setAttendanceSessionId(e.target.value)}
              placeholder="Optional"
            />
          </div>
        </div>

        <div className="grid-2 spacer-12">
          <div>
            <label className="label">Attendance Opens</label>
            <input
              className="input"
              type="datetime-local"
              value={attendanceOpenAt}
              onChange={(e) => setAttendanceOpenAt(e.target.value)}
            />
          </div>
          <div>
            <label className="label">Attendance Closes</label>
            <input
              className="input"
              type="datetime-local"
              value={attendanceCloseAt}
              onChange={(e) => setAttendanceCloseAt(e.target.value)}
            />
          </div>
        </div>

        <div className="spacer-12" />
        <label className="label">Question Keys JSON</label>
        <textarea
          className="textarea textarea-small"
          value={questionKeysJson}
          onChange={(e) => setQuestionKeysJson(e.target.value)}
          placeholder='{"checkpoint_1": 5, "checkpoint_2": 6}'
        />
        <p className="form-hint">Use this to map notebook quiz blocks to assessment IDs, for example <code>{`{"checkpoint_1": 5}`}</code>.</p>

        <div className="checkbox-grid spacer-16">
          <label className="checkbox-row">
            <input type="checkbox" checked={showOnPortal} onChange={(e) => setShowOnPortal(e.target.checked)} />
            Show on portal
          </label>
          <label className="checkbox-row">
            <input type="checkbox" checked={allowPortalMockExam} onChange={(e) => setAllowPortalMockExam(e.target.checked)} />
            Allow portal mock exam
          </label>
          <label className="checkbox-row">
            <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
            Active
          </label>
        </div>

        <div className="button-row">
          <button className="btn btn-primary" onClick={handleCreate} disabled={saving || !lessonSlug || !courseCode || !title || !notebookPath}>
            Create Lesson Config
          </button>
          <button className="btn btn-success" onClick={handleCreateOrUpdate} disabled={saving || !lessonSlug || !courseCode || !title || !notebookPath}>
            Create or Update
          </button>
          <button className="btn btn-secondary" onClick={handleUpdate} disabled={saving || !lessonSlug}>
            Update Existing
          </button>
          <button className="btn btn-secondary" onClick={handleLoadBySlug} disabled={saving || !lessonSlug}>
            Load by Slug
          </button>
        </div>
      </section>

      <section className="card">
        <h2 className="card-title">3. After Saving</h2>
        <ol className="list compact-list">
          <li>Enroll students into a section under <strong>{courseCode || "the selected course"}</strong>.</li>
          <li>Make sure the notebook exists in JupyterLite at <strong>{notebookPath || "the configured path"}</strong>.</li>
          <li>If a quiz is enabled, make sure assessment <strong>{assessmentId || "ID"}</strong> exists, is published, and has an open window.</li>
          <li>Ask the student to log out and back in, then reload the portal.</li>
        </ol>
      </section>

      {lastResponse && (
        <section className="card">
          <h2 className="card-title">Last Backend Response</h2>
          <pre className="code-block">{JSON.stringify(lastResponse, null, 2)}</pre>
        </section>
      )}
    </main>
  );
}
