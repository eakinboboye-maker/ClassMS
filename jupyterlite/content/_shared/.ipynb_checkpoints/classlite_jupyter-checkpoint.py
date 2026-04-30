import json
from datetime import datetime

import ipywidgets as widgets
from IPython.display import display, clear_output


class ClassLiteLesson:
    def __init__(self, api_base: str, lesson_slug: str):
        self.api_base = api_base.rstrip("/")
        self.lesson_slug = lesson_slug

        self.student_token = None
        self.current_user = None

        self.config = None
        self.assessment_id = None
        self.attendance_session_id = None
        self.question_keys = {}
        self.title = None
        self.course_code = None
        self.notebook_path = None

        self.attempt_info = None
        self.paper = None
        self.answers = {}

    @property
    def headers(self):
        if not self.student_token:
            raise ValueError("Student token not available. Log in first.")
        return {
            "Authorization": f"Bearer {self.student_token}",
            "Content-Type": "application/json",
        }

    def _require_requests(self):
        try:
            import requests
            return requests
        except Exception as exc:
            raise RuntimeError(
                "The Xeus kernel could not import requests. "
                "Add requests to environment.yml and rebuild the JupyterLite site."
            ) from exc

    def login_widget(self):
        requests = self._require_requests()

        email_input = widgets.Text(
            description="Email:",
            placeholder="student@example.com",
            layout=widgets.Layout(width="420px"),
        )
        password_input = widgets.Password(
            description="Password:",
            placeholder="Enter password",
            layout=widgets.Layout(width="420px"),
        )
        login_button = widgets.Button(description="Login", button_style="primary")
        out = widgets.Output()

        def _login(_):
            with out:
                clear_output()
                try:
                    r = requests.post(
                        f"{self.api_base}/api/auth/login",
                        json={
                            "email": email_input.value.strip(),
                            "password": password_input.value,
                        },
                        timeout=30,
                    )
                    r.raise_for_status()
                    data = r.json()
                    self.student_token = data["access_token"]

                    r2 = requests.get(
                        f"{self.api_base}/api/auth/me",
                        headers=self.headers,
                        timeout=30,
                    )
                    r2.raise_for_status()
                    self.current_user = r2.json()

                    print(f"Logged in as {self.current_user['full_name']} ({self.current_user['email']})")
                except Exception as exc:
                    self.student_token = None
                    self.current_user = None
                    print(f"Login failed: {exc}")

        login_button.on_click(_login)
        display(widgets.VBox([email_input, password_input, login_button, out]))

    def load_lesson_config(self):
        requests = self._require_requests()

        r = requests.get(
            f"{self.api_base}/api/jupyterlite/lesson-config/{self.lesson_slug}",
            headers=self.headers,
            timeout=30,
        )
        r.raise_for_status()

        self.config = r.json()
        self.assessment_id = self.config["assessment_id"]
        self.attendance_session_id = self.config["attendance_session_id"]
        self.question_keys = self.config.get("question_keys", {})
        self.title = self.config.get("title")
        self.course_code = self.config.get("course_code")
        self.notebook_path = self.config.get("notebook_path")
        return self.config

    def qid(self, key: str) -> int:
        if key not in self.question_keys:
            raise KeyError(f"Question key not found in lesson config: {key}")
        return self.question_keys[key]

    def start_attempt(self):
        requests = self._require_requests()
        if self.assessment_id is None:
            raise ValueError("Load lesson config first.")
        r = requests.post(
            f"{self.api_base}/api/mock-exams/{self.assessment_id}/start",
            headers=self.headers,
            timeout=30,
        )
        r.raise_for_status()
        self.attempt_info = r.json()
        return self.attempt_info

    def fetch_paper(self):
        requests = self._require_requests()
        if self.assessment_id is None:
            raise ValueError("Load lesson config first.")
        r = requests.get(
            f"{self.api_base}/api/mock-exams/{self.assessment_id}/paper",
            headers=self.headers,
            timeout=30,
        )
        r.raise_for_status()
        self.paper = r.json()
        return self.paper

    def answer_mcq(self, question_key, selected_option):
        self.answers[self.qid(question_key)] = {"selected_option": selected_option}
        return self.answers[self.qid(question_key)]

    def answer_multi(self, question_key, selected_options):
        self.answers[self.qid(question_key)] = {"selected_options": selected_options}
        return self.answers[self.qid(question_key)]

    def answer_fill_gap(self, question_key, gaps):
        self.answers[self.qid(question_key)] = {"gaps": gaps}
        return self.answers[self.qid(question_key)]

    def answer_essay(self, question_key, answer_text):
        self.answers[self.qid(question_key)] = {"answer_text": answer_text}
        return self.answers[self.qid(question_key)]

    def autosave(self):
        requests = self._require_requests()
        if not self.attempt_info:
            raise ValueError("Start attempt first.")
        payload = {
            "responses": [
                {"question_id": qid, "response": resp}
                for qid, resp in self.answers.items()
            ]
        }
        r = requests.post(
            f"{self.api_base}/api/mock-exams/attempts/{self.attempt_info['attempt_id']}/autosave",
            headers=self.headers,
            data=json.dumps(payload),
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def mark_attendance(self):
        requests = self._require_requests()
        if self.attendance_session_id is None:
            raise ValueError("Load lesson config first.")
        payload = {"attendance_session_id": self.attendance_session_id, "status": "present"}
        r = requests.post(
            f"{self.api_base}/api/courses/attendance/mark",
            headers=self.headers,
            data=json.dumps(payload),
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def submit(self):
        requests = self._require_requests()
        if not self.attempt_info:
            raise ValueError("Start attempt first.")
        submitted_payload = {
            "lesson": self.lesson_slug,
            "submitted_from": "jupyterlite",
            "submitted_at": datetime.utcnow().isoformat(),
            "attendance_session_id": self.attendance_session_id,
            "done": True,
        }
        r = requests.post(
            f"{self.api_base}/api/mock-exams/attempts/{self.attempt_info['attempt_id']}/submit",
            headers=self.headers,
            data=json.dumps({"submitted_payload": submitted_payload}),
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def scores(self):
        requests = self._require_requests()
        if not self.attempt_info:
            raise ValueError("Start attempt first.")
        r = requests.get(
            f"{self.api_base}/api/mock-exams/attempts/{self.attempt_info['attempt_id']}/scores",
            headers=self.headers,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def results(self):
        requests = self._require_requests()
        if not self.attempt_info:
            raise ValueError("Start attempt first.")
    
        r = requests.get(
            f"{self.api_base}/api/mock-exams/attempts/{self.attempt_info['attempt_id']}/results",
            headers=self.headers,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def performance(self):
        requests = self._require_requests()
        r = requests.get(
            f"{self.api_base}/api/grading/my-performance",
            headers=self.headers,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

class PerformanceUI:
    def __init__(self, payload: dict):
        self.payload = payload

    def render(self):
        import ipywidgets as widgets
        from IPython.display import display

        cards = []
        for item in self.payload.get("items", []):
            card = widgets.HTML(
                f"""
                <div style="border:1px solid #d1d5db; padding:14px; margin:10px 0; border-radius:10px;">
                  <div style="font-weight:700;">{item['assessment_title']}</div>
                  <div>Type: {item['assessment_type']}</div>
                  <div>Submitted: {item['submitted_at']}</div>
                  <div>Score: {item['total_awarded']} / {item['total_max']}</div>
                  <div>Percent: {item['percent']:.1f}%</div>
                </div>
                """
            )
            cards.append(card)

        display(widgets.VBox(cards))