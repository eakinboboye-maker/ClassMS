
const API_BASE = "https://classlite-backend.onrender.com";
const PORTAL_SESSION_KEY = "classlite_portal_session";
const PORTAL_LAUNCH_KEY = "classlite_launch_context";

function getSession() { try { return JSON.parse(localStorage.getItem(PORTAL_SESSION_KEY) || "null"); } catch { return null; } }
function setSession(session) { localStorage.setItem(PORTAL_SESSION_KEY, JSON.stringify(session)); }
function clearSession() { localStorage.removeItem(PORTAL_SESSION_KEY); localStorage.removeItem(PORTAL_LAUNCH_KEY); }
function setLaunchContext(ctx) { localStorage.setItem(PORTAL_LAUNCH_KEY, JSON.stringify(ctx)); }

function authHeaders() {
  const s = getSession();
  if (!s?.token) throw new Error("Not logged in");
  return {"Content-Type":"application/json","Authorization":`Bearer ${s.token}`};
}

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

async function login(email, password) {
  const tokenData = await api("/api/auth/login", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({email,password})
  });
  const me = await api("/api/auth/me", {
    headers:{Authorization:`Bearer ${tokenData.access_token}`}
  });
  const session = {token: tokenData.access_token, user: me};
  setSession(session);
  return session;
}

function formatDateTime(ts) { return ts ? new Date(ts).toLocaleString() : "—"; }

function countdownText(openAt, closeAt) {
  const now = Date.now();
  const start = openAt ? new Date(openAt).getTime() : null;
  const end = closeAt ? new Date(closeAt).getTime() : null;
  if (start && now < start) return `Attendance opens in ${Math.ceil((start-now)/60000)} minute(s)`;
  if (end && now > end) return "Attendance closed";
  if (end) return `Attendance open for ${Math.ceil((end-now)/60000)} more minute(s)`;
  return "Attendance availability unknown";
}

async function loadPortalHome() { return api("/api/jupyterlite/portal/home", {headers: authHeaders()}); }
async function launchLesson(lessonSlug) { return api(`/api/jupyterlite/portal/launch/${lessonSlug}`, {method:"POST", headers: authHeaders()}); }
async function loadPerformance() { return api("/api/jupyterlite/portal/performance", {headers: authHeaders()}); }
async function startPortalMockExam(lessonSlug) { return api(`/api/jupyterlite/portal/mock-exams/${lessonSlug}/start`, {method:"POST", headers: authHeaders()}); }
async function fetchPortalMockPaper(attemptId) { return api(`/api/jupyterlite/portal/mock-exams/${attemptId}/paper`, {headers: authHeaders()}); }
async function autosavePortalMock(attemptId, responses) { return api(`/api/jupyterlite/portal/mock-exams/${attemptId}/autosave`, {method:"POST", headers: authHeaders(), body: JSON.stringify({responses})}); }
async function submitPortalMock(attemptId, submitted_payload) { return api(`/api/jupyterlite/portal/mock-exams/${attemptId}/submit`, {method:"POST", headers: authHeaders(), body: JSON.stringify({submitted_payload})}); }
async function resultsPortalMock(attemptId) { return api(`/api/jupyterlite/portal/mock-exams/${attemptId}/results`, {headers: authHeaders()}); }

async function markAttendance(lessonSlug) {
  throw new Error("Attendance marking is temporarily disabled from the frontend.");
}
