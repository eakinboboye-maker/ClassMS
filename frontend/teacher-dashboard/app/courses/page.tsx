"use client";

import { useEffect, useMemo, useState } from "react";
import { loadTeacherSession } from "../../lib/auth";
import { createCourse, createSection, listCourses } from "../../lib/courses-api";

type CourseRow = {
  id: number | string;
  code?: string;
  title?: string;
  description?: string;
  sections?: any[];
};

export default function CoursesPage() {
  const [status, setStatus] = useState("");
  const [courses, setCourses] = useState<CourseRow[]>([]);
  const [loading, setLoading] = useState(false);

  const [courseCode, setCourseCode] = useState("");
  const [courseTitle, setCourseTitle] = useState("");
  const [courseDescription, setCourseDescription] = useState("");

  const [selectedCourseId, setSelectedCourseId] = useState<string>("");
  const [sectionName, setSectionName] = useState("");
  const [sectionTerm, setSectionTerm] = useState("");
  const [sectionCapacity, setSectionCapacity] = useState("");

  useEffect(() => {
    const session = loadTeacherSession();
    if (!session?.token) {
      setStatus("No teacher session found. Please sign in on the Home page.");
      return;
    }
    refreshCourses();
  }, []);

  async function refreshCourses() {
    try {
      setLoading(true);
      const payload = await listCourses();
      const rows = Array.isArray(payload) ? payload : (payload.items || payload.courses || []);
      setCourses(rows);
      setStatus(`Loaded ${rows.length} course(s).`);
      if (rows.length > 0 && !selectedCourseId) {
        setSelectedCourseId(String(rows[0].id));
      }
    } catch (err: any) {
      setStatus(err.message || "Failed to load courses");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateCourse() {
    try {
      const created = await createCourse({
        code: courseCode,
        title: courseTitle,
        description: courseDescription || undefined,
      });
      setStatus(`Created course ${created.code || courseCode}.`);
      setCourseCode("");
      setCourseTitle("");
      setCourseDescription("");
      await refreshCourses();
    } catch (err: any) {
      setStatus(err.message || "Failed to create course");
    }
  }

  async function handleCreateSection() {
    try {
      if (!selectedCourseId) {
        throw new Error("Select a course first.");
      }
      await createSection(selectedCourseId, {
        name: sectionName,
        term: sectionTerm,
        capacity: sectionCapacity ? Number(sectionCapacity) : null,
      });
      setStatus(`Created section ${sectionName}.`);
      setSectionName("");
      setSectionTerm("");
      setSectionCapacity("");
      await refreshCourses();
    } catch (err: any) {
      setStatus(err.message || "Failed to create section");
    }
  }

  const selectedCourse = useMemo(
    () => courses.find((c) => String(c.id) === String(selectedCourseId)),
    [courses, selectedCourseId]
  );

  return (
    <main>
      <h1 className="page-title">Courses and Sections</h1>
      <p className="page-subtitle">
        Register courses, create sections, and prepare the roster structure before enrollment.
      </p>

      <section className="card card-accent">
        <h2 className="card-title">Teacher Session</h2>
        <div className="notice notice-info">
          {status || "Signed-in teacher session will be used automatically."}
        </div>
      </section>

      <div className="grid-2">
        <section className="card">
          <h2 className="card-title">Create Course</h2>
          <label className="label">Course Code</label>
          <input
            className="input"
            value={courseCode}
            onChange={(e) => setCourseCode(e.target.value)}
            placeholder="EEE355"
          />
          <div className="spacer-12" />
          <label className="label">Course Title</label>
          <input
            className="input"
            value={courseTitle}
            onChange={(e) => setCourseTitle(e.target.value)}
            placeholder="Computation Structures"
          />
          <div className="spacer-12" />
          <label className="label">Description</label>
          <textarea
            className="textarea"
            value={courseDescription}
            onChange={(e) => setCourseDescription(e.target.value)}
            placeholder="Optional course description"
          />
          <div className="button-row">
            <button
              className="btn btn-primary"
              onClick={handleCreateCourse}
              disabled={!courseCode || !courseTitle}
            >
              Create Course
            </button>
            <button className="btn btn-secondary" onClick={refreshCourses} disabled={loading}>
              Refresh
            </button>
          </div>
        </section>

        <section className="card">
          <h2 className="card-title">Create Section</h2>
          <label className="label">Select Course</label>
          <select
            className="select"
            value={selectedCourseId}
            onChange={(e) => setSelectedCourseId(e.target.value)}
          >
            <option value="">Select a course</option>
            {courses.map((course) => (
              <option key={course.id} value={String(course.id)}>
                {(course.code || "COURSE")} — {course.title || "Untitled"}
              </option>
            ))}
          </select>
          <div className="spacer-12" />
          <label className="label">Section Name</label>
          <input
            className="input"
            value={sectionName}
            onChange={(e) => setSectionName(e.target.value)}
            placeholder="A"
          />
          <div className="spacer-12" />
          <label className="label">Term / Session</label>
          <input
            className="input"
            value={sectionTerm}
            onChange={(e) => setSectionTerm(e.target.value)}
            placeholder="2026/2027"
          />
          <div className="spacer-12" />
          <label className="label">Capacity</label>
          <input
            className="input"
            value={sectionCapacity}
            onChange={(e) => setSectionCapacity(e.target.value)}
            placeholder="Optional"
          />
          <div className="button-row">
            <button
              className="btn btn-success"
              onClick={handleCreateSection}
              disabled={!selectedCourseId || !sectionName || !sectionTerm}
            >
              Create Section
            </button>
          </div>
        </section>
      </div>

      <section className="card">
        <h2 className="card-title">Courses</h2>
        {courses.length === 0 ? (
          <div className="notice notice-info">
            {loading ? "Loading courses..." : "No courses found yet."}
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Code</th>
                  <th>Title</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {courses.map((course) => (
                  <tr key={String(course.id)}>
                    <td>{String(course.id)}</td>
                    <td>{course.code || "—"}</td>
                    <td>{course.title || "—"}</td>
                    <td>{course.description || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="card">
        <h2 className="card-title">Sections for Selected Course</h2>
        {!selectedCourse ? (
          <div className="notice notice-info">Select a course to view known sections.</div>
        ) : !selectedCourse.sections || selectedCourse.sections.length === 0 ? (
          <div className="notice notice-info">
            No sections are shown in the current course payload. They may still exist if your list endpoint does not embed sections.
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Term</th>
                  <th>Capacity</th>
                </tr>
              </thead>
              <tbody>
                {selectedCourse.sections.map((section: any, idx: number) => (
                  <tr key={String(section.id || idx)}>
                    <td>{section.id || "—"}</td>
                    <td>{section.name || "—"}</td>
                    <td>{section.term || "—"}</td>
                    <td>{section.capacity ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
