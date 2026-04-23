import json
from dataclasses import dataclass, field
from typing import Any

import requests


@dataclass
class MockExamClient:
    base_url: str
    token: str
    assessment_id: int
    attempt_id: int | None = None
    paper: dict[str, Any] | None = None
    responses: dict[int, dict[str, Any]] = field(default_factory=dict)

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def start(self) -> dict[str, Any]:
        r = requests.post(
            f"{self.base_url}/api/mock-exams/{self.assessment_id}/start",
            headers=self.headers,
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        self.attempt_id = data["attempt_id"]
        return data

    def fetch_paper(self) -> dict[str, Any]:
        r = requests.get(
            f"{self.base_url}/api/mock-exams/{self.assessment_id}/paper",
            headers=self.headers,
            timeout=30,
        )
        r.raise_for_status()
        self.paper = r.json()
        return self.paper

    def set_response(self, question_id: int, response: dict[str, Any]) -> None:
        self.responses[question_id] = response

    def autosave(self) -> dict[str, Any]:
        if self.attempt_id is None:
            raise RuntimeError("Attempt has not been started")
        payload = {
            "responses": [
                {"question_id": qid, "response": resp}
                for qid, resp in self.responses.items()
            ]
        }
        r = requests.post(
            f"{self.base_url}/api/mock-exams/attempts/{self.attempt_id}/autosave",
            headers=self.headers,
            data=json.dumps(payload),
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def submit(self, submitted_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.attempt_id is None:
            raise RuntimeError("Attempt has not been started")
        payload = {
            "submitted_payload": submitted_payload or {
                "submitted_from": "jupyterlite",
                "done": True,
            }
        }
        r = requests.post(
            f"{self.base_url}/api/mock-exams/attempts/{self.attempt_id}/submit",
            headers=self.headers,
            data=json.dumps(payload),
            timeout=30,
        )
        r.raise_for_status()
        return r.json()
