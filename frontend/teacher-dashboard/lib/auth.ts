const STORAGE_KEY = "classlite_teacher_session";

export type TeacherSession = {
  token: string;
  user?: any;
};

export function saveTeacherSession(session: TeacherSession) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function loadTeacherSession(): TeacherSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function clearTeacherSession() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(STORAGE_KEY);
}

export function getTeacherToken(): string {
  const session = loadTeacherSession();
  if (!session?.token) {
    throw new Error("No teacher session found. Please sign in on the Home page.");
  }
  return session.token;
}
