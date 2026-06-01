import json
from datetime import datetime
from _shared.classlite_browser_bridge import get_browser_json, display_portal_bridge
from _shared.classlite_site_config import PORTAL_SESSION_KEY, PORTAL_LAUNCH_KEY


class ClassLiteAPIError(RuntimeError):
    """Raised when the ClassLite backend returns a non-2xx response."""

    def __init__(self, message, status_code=None, url=None, body=None):
        self.status_code = status_code
        self.url = url
        self.body = body
        parts = [message]
        if status_code is not None:
            parts.append(f"status={status_code}")
        if url:
            parts.append(f"url={url}")
        if body:
            parts.append(f"body={body}")
        super().__init__(" | ".join(parts))


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
        # v4: use the portal lesson endpoints by default. They are the endpoints
        # used by the landing portal and they avoid hard-coding /api/mock-exams/{id}.
        self.exam_api_mode = "portal"

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

    def _response_body(self, response):
        try:
            return response.text
        except Exception:
            return ""

    def _json_or_raise(self, response, action="ClassLite request failed"):
        if not response.ok:
            raise ClassLiteAPIError(
                action,
                status_code=getattr(response, "status_code", None),
                url=getattr(response, "url", None),
                body=self._response_body(response),
            )
        if not getattr(response, "text", ""):
            return {}
        try:
            return response.json()
        except Exception as exc:
            raise ClassLiteAPIError(
                f"{action}: backend did not return valid JSON",
                status_code=getattr(response, "status_code", None),
                url=getattr(response, "url", None),
                body=self._response_body(response),
            ) from exc

    def _post_json(self, path, payload=None, action="POST failed"):
        requests = self._require_requests()
        kwargs = {"headers": self.headers, "timeout": 30}
        if payload is not None:
            kwargs["data"] = json.dumps(payload)
        response = requests.post(f"{self.api_base}{path}", **kwargs)
        return self._json_or_raise(response, action=action)

    def _get_json(self, path, action="GET failed"):
        requests = self._require_requests()
        response = requests.get(f"{self.api_base}{path}", headers=self.headers, timeout=30)
        return self._json_or_raise(response, action=action)

    def prepare_portal_bridge(self):
        return display_portal_bridge()
        
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
            # If the backend launch endpoint already created/reused an attempt,
            # accept it. This makes repeated notebook opens safer.
            if launch.get("attempt_id"):
                self.attempt_info = {"attempt_id": launch.get("attempt_id")}
        return {
            "user": self.current_user,
            "lesson_slug": self.lesson_slug,
            "assessment_id": self.assessment_id,
            "attempt_id": (self.attempt_info or {}).get("attempt_id"),
        }

    def start_attempt(self):
        """
        Start a notebook-side quiz attempt.

        Default behavior:
        - use the normal assessment endpoint when assessment_id is available
        - only use the portal mock-exam endpoint when explicitly requested
        """
        # notebook quiz flow
        if self.assessment_id is not None:
            self.exam_api_mode = "assessment"
            self.attempt_info = self._post_json(
                f"/api/mock-exams/{self.assessment_id}/start",
                action="Could not start notebook quiz",
            )
            return self.attempt_info

        # fallback only if you intentionally launched a portal-only mock exam
        self.exam_api_mode = "portal"
        self.attempt_info = self._post_json(
            f"/api/jupyterlite/portal/mock-exams/{self.lesson_slug}/start",
            action="Could not start portal mock exam",
        )
        return self.attempt_info

    def fetch_paper(self):
        """
        Fetch the paper for the current notebook-side attempt.
        """
        if self.assessment_id is not None:
            self.exam_api_mode = "assessment"
            self.paper = self._get_json(
                f"/api/mock-exams/{self.assessment_id}/paper",
                action="Could not fetch notebook quiz paper",
            )
            return self.paper

        if not self.attempt_info:
            raise ValueError("Start attempt first.")

        self.exam_api_mode = "portal"
        self.paper = self._get_json(
            f"/api/jupyterlite/portal/mock-exams/{self.attempt_info['attempt_id']}/paper",
            action="Could not fetch portal mock exam paper",
        )
        return self.paper

    def autosave(self):
        if not self.attempt_info or not self.attempt_info.get("attempt_id"):
            self.start_attempt()
        payload = {"responses": [{"question_id": qid, "response": resp} for qid, resp in self.answers.items()]}
        attempt_id = self.attempt_info["attempt_id"]
        if self.exam_api_mode == "portal":
            return self._post_json(
                f"/api/jupyterlite/portal/mock-exams/{attempt_id}/autosave",
                payload,
                action="Could not autosave notebook quiz through the portal endpoint",
            )
        return self._post_json(
            f"/api/mock-exams/attempts/{attempt_id}/autosave",
            payload,
            action="Could not autosave notebook quiz through the legacy endpoint",
        )

    def submit(self):
        if not self.attempt_info or not self.attempt_info.get("attempt_id"):
            self.start_attempt()
        submitted_payload = {
            "lesson": self.lesson_slug,
            "submitted_from": "jupyterlite",
            "submitted_at": datetime.utcnow().isoformat(),
            "attendance_session_id": self.attendance_session_id,
            "done": True,
        }
        attempt_id = self.attempt_info["attempt_id"]
        if self.exam_api_mode == "portal":
            return self._post_json(
                f"/api/jupyterlite/portal/mock-exams/{attempt_id}/submit",
                {"submitted_payload": submitted_payload},
                action="Could not submit notebook quiz through the portal endpoint",
            )
        return self._post_json(
            f"/api/mock-exams/attempts/{attempt_id}/submit",
            {"submitted_payload": submitted_payload},
            action="Could not submit notebook quiz through the legacy endpoint",
        )

    def results(self):
        if not self.attempt_info or not self.attempt_info.get("attempt_id"):
            raise RuntimeError("No attempt has been started yet.")
        attempt_id = self.attempt_info["attempt_id"]
        if self.exam_api_mode == "portal":
            return self._get_json(
                f"/api/jupyterlite/portal/mock-exams/{attempt_id}/results",
                action="Could not fetch notebook quiz results through the portal endpoint",
            )
        return self._get_json(
            f"/api/mock-exams/attempts/{attempt_id}/results",
            action="Could not fetch notebook quiz results through the legacy endpoint",
        )
