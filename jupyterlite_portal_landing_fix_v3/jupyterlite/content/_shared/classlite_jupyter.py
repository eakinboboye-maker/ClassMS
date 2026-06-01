import json
from datetime import datetime
from _shared.classlite_browser_bridge import get_browser_json, bridge_debug_state
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

    def _request_json(self, method, path, payload=None, action="ClassLite request failed"):
        requests = self._require_requests()
        url = f"{self.api_base}{path}"
        kwargs = {"headers": self.headers, "timeout": 30}
        if payload is not None:
            kwargs["data"] = json.dumps(payload)
        try:
            response = requests.request(method, url, **kwargs)
        except Exception as exc:
            raise ClassLiteAPIError(
                f"{action}: browser/kernel could not load the endpoint. This is commonly CORS, a backend crash without CORS headers, or a wrong endpoint path",
                url=url,
                body=str(exc),
            ) from exc
        return self._json_or_raise(response, action=action)

    def _post_json(self, path, payload=None, action="POST failed"):
        return self._request_json("POST", path, payload=payload, action=action)

    def _get_json(self, path, action="GET failed"):
        return self._request_json("GET", path, action=action)

    def debug_state(self):
        return {
            "api_base": self.api_base,
            "lesson_slug": self.lesson_slug,
            "assessment_id": self.assessment_id,
            "attendance_session_id": self.attendance_session_id,
            "attempt_info": self.attempt_info,
            "exam_api_mode": self.exam_api_mode,
            "notebook_path": self.notebook_path,
            "has_student_token": bool(self.student_token),
            "bridge": bridge_debug_state(),
        }

    def prepare_portal_bridge(self):
        """Backward-compatible name used by older notebooks."""
        return self.bootstrap_from_portal()

    def bootstrap_from_portal(self):
        session = get_browser_json(PORTAL_SESSION_KEY) or {}
        launch = get_browser_json(PORTAL_LAUNCH_KEY) or {}
        token = session.get("token")
        if not token:
            raise RuntimeError(
                "No portal session found in the notebook runtime bridge. "
                "Open the notebook from /portal/index.html after login. "
                "If you did open it from the portal, the portal could not write "
                "_shared/classlite_runtime_launch.json through JupyterLite's contents API. "
                f"Bridge debug: {bridge_debug_state()}"
            )
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
        """Start or reuse the notebook quiz attempt.

        v4 behavior:
        1. Prefer /api/jupyterlite/portal/mock-exams/{lesson_slug}/start.
           This is the same lesson-slug based API used by the portal.
        2. Fall back to the older /api/mock-exams/{assessment_id}/start only
           if the portal endpoint is unavailable.
        3. Raise an error that includes the backend response body, instead of
           the unhelpful bare HTTPError previously shown in the notebook.
        """
        if self.attempt_info and self.attempt_info.get("attempt_id"):
            return self.attempt_info

        portal_error = None
        try:
            self.exam_api_mode = "portal"
            self.attempt_info = self._post_json(
                f"/api/jupyterlite/portal/mock-exams/{self.lesson_slug}/start",
                action="Could not start notebook quiz through the portal endpoint",
            )
            return self.attempt_info
        except ClassLiteAPIError as exc:
            portal_error = exc
            # Only fall back when the portal endpoint likely does not exist on
            # the backend. For real 400/401/403 errors, keep the useful message.
            if exc.status_code not in (404, 405):
                raise

        if self.assessment_id is None:
            raise ClassLiteAPIError(
                "No assessment_id was supplied by the portal launch context, and the portal quiz endpoint was unavailable",
                body=str(portal_error),
            )

        self.exam_api_mode = "legacy"
        self.attempt_info = self._post_json(
            f"/api/mock-exams/{self.assessment_id}/start",
            action="Could not start notebook quiz through the legacy assessment endpoint",
        )
        return self.attempt_info

    def fetch_paper(self):
        """Fetch the quiz paper without confusing assessment_id and attempt_id.

        In the legacy API family, /api/mock-exams/{id}/paper has usually meant
        assessment_id. In the portal API family, /api/jupyterlite/portal/mock-exams/{id}/paper
        means attempt_id. v5 tries the route that matches the current mode first, then
        tries safe fallbacks with clearer errors.
        """
        if not self.attempt_info or not self.attempt_info.get("attempt_id"):
            self.start_attempt()

        attempt_id = self.attempt_info.get("attempt_id")
        errors = []

        candidate_paths = []
        if self.exam_api_mode == "portal":
            candidate_paths.append((
                f"/api/jupyterlite/portal/mock-exams/{attempt_id}/paper",
                "Could not fetch paper through portal attempt endpoint",
            ))
            if self.assessment_id is not None:
                candidate_paths.append((
                    f"/api/mock-exams/{self.assessment_id}/paper",
                    "Could not fetch paper through legacy assessment endpoint",
                ))
        else:
            if self.assessment_id is not None:
                candidate_paths.append((
                    f"/api/mock-exams/{self.assessment_id}/paper",
                    "Could not fetch paper through legacy assessment endpoint",
                ))
            candidate_paths.append((
                f"/api/mock-exams/attempts/{attempt_id}/paper",
                "Could not fetch paper through legacy attempt endpoint",
            ))
            candidate_paths.append((
                f"/api/jupyterlite/portal/mock-exams/{attempt_id}/paper",
                "Could not fetch paper through portal attempt endpoint",
            ))

        for path, action in candidate_paths:
            try:
                self.paper = self._get_json(path, action=action)
                return self.paper
            except ClassLiteAPIError as exc:
                errors.append(str(exc))
                # Only try another route when the path is probably unsupported
                # or the browser could not load it. Real authorization/window
                # errors should be surfaced immediately.
                if exc.status_code not in (None, 404, 405):
                    raise

        raise ClassLiteAPIError(
            "Could not fetch notebook quiz paper from any known endpoint",
            body="\n---\n".join(errors),
        )

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
