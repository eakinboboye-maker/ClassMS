import json
from datetime import datetime
from _shared.classlite_browser_bridge import get_browser_json
from _shared.classlite_site_config import PORTAL_SESSION_KEY, PORTAL_LAUNCH_KEY


class ClassLiteLesson:
    def __init__(self, api_base: str, lesson_slug: str):
        self.api_base = api_base.rstrip("/")
        self.lesson_slug = lesson_slug
        self.student_token = None
        self.current_user = None
        self.assessment_id = None
        self.attendance_session_id = None
        self.question_keys = {}
        self.notebook_path = None
        self.attempt_info = None
        self.paper = None
        self.answers = {}

    @property
    def headers(self):
        if not self.student_token:
            raise ValueError("Open this notebook from the portal after login.")
        return {"Authorization": f"Bearer {self.student_token}", "Content-Type": "application/json"}

    def _require_requests(self):
        try:
            import requests
            return requests
        except Exception as exc:
            raise RuntimeError("The Xeus kernel could not import requests. Add requests to environment.yml and rebuild.") from exc

    def bootstrap_from_portal(self):
        session = get_browser_json(PORTAL_SESSION_KEY) or {}
        launch = get_browser_json(PORTAL_LAUNCH_KEY) or {}
        token = session.get("token")
        if not token:
            raise RuntimeError("No portal session found. Return to the portal and log in.")
        self.student_token = token
        self.current_user = session.get("user")
        if launch:
            self.lesson_slug = launch.get("lesson_slug", self.lesson_slug)
            self.assessment_id = launch.get("assessment_id")
            self.attendance_session_id = launch.get("attendance_session_id")
            self.question_keys = launch.get("question_keys", {})
            self.notebook_path = launch.get("notebook_path")
        return {"user": self.current_user, "lesson_slug": self.lesson_slug, "assessment_id": self.assessment_id}

    def fetch_paper(self):
        requests = self._require_requests()
        r = requests.get(f"{self.api_base}/api/mock-exams/{self.assessment_id}/paper", headers=self.headers, timeout=30)
        r.raise_for_status()
        self.paper = r.json()
        return self.paper

    def start_attempt(self):
        requests = self._require_requests()
        r = requests.post(f"{self.api_base}/api/mock-exams/{self.assessment_id}/start", headers=self.headers, timeout=30)
        r.raise_for_status()
        self.attempt_info = r.json()
        return self.attempt_info

    def autosave(self):
        requests = self._require_requests()
        payload = {"responses": [{"question_id": qid, "response": resp} for qid, resp in self.answers.items()]}
        r = requests.post(f"{self.api_base}/api/mock-exams/attempts/{self.attempt_info['attempt_id']}/autosave", headers=self.headers, data=json.dumps(payload), timeout=30)
        r.raise_for_status()
        return r.json()

    def submit(self):
        requests = self._require_requests()
        submitted_payload = {
            "lesson": self.lesson_slug,
            "submitted_from": "jupyterlite",
            "submitted_at": datetime.utcnow().isoformat(),
            "attendance_session_id": self.attendance_session_id,
            "done": True,
        }
        r = requests.post(f"{self.api_base}/api/mock-exams/attempts/{self.attempt_info['attempt_id']}/submit", headers=self.headers, data=json.dumps({"submitted_payload": submitted_payload}), timeout=30)
        r.raise_for_status()
        return r.json()

    def results(self):
        requests = self._require_requests()
        r = requests.get(f"{self.api_base}/api/mock-exams/attempts/{self.attempt_info['attempt_id']}/results", headers=self.headers, timeout=30)
        r.raise_for_status()
        return r.json()
