from __future__ import annotations

import json
from typing import Any

from app.core.config import settings


def build_rubric_prompt(question_prompt: str, answer_key: dict | None, rubric: list[dict], student_answer: str) -> dict:
    return {
        "question_prompt": question_prompt,
        "answer_key": answer_key or {},
        "rubric": rubric or [],
        "student_answer": student_answer,
        "instructions": [
            "Score criterion by criterion.",
            "Cite evidence spans from the student's answer where possible.",
            "Flag low confidence or off-topic answers.",
            "Do not assign a final official grade; propose only.",
            "Return valid JSON only.",
        ],
    }


def _mock_grade(question_prompt: str, answer_key: dict | None, rubric: list[dict], student_answer: str) -> dict:
    total_possible = sum(item.get("points", 0) for item in rubric)
    word_count = len(student_answer.split())

    if word_count == 0:
        return {
            "proposed_score": 0.0,
            "confidence": 0.95,
            "criteria": [],
            "flags": ["blank_answer", "needs_review"],
            "rationale": {"summary": "Blank answer."},
        }

    length_factor = min(word_count / 80.0, 1.0)
    proposed = round(total_possible * 0.6 * length_factor, 2)

    criteria = []
    for item in rubric:
        points = item.get("points", 0)
        criteria.append(
            {
                "criterion": item.get("criterion"),
                "points_awarded": round(points * 0.6 * length_factor, 2),
                "max_points": points,
                "rationale": "Mock AI estimate. Replace with provider call.",
                "evidence": [],
            }
        )

    return {
        "proposed_score": proposed,
        "confidence": 0.45,
        "criteria": criteria,
        "flags": ["needs_review"],
        "rationale": {"summary": "Mock AI proposal only. Human review required."},
    }


def _schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "proposed_score": {"type": "number"},
            "confidence": {"type": "number"},
            "criteria": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "criterion": {"type": "string"},
                        "points_awarded": {"type": "number"},
                        "max_points": {"type": "number"},
                        "rationale": {"type": "string"},
                        "evidence": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["criterion", "points_awarded", "max_points", "rationale", "evidence"],
                    "additionalProperties": False,
                },
            },
            "flags": {"type": "array", "items": {"type": "string"}},
            "rationale": {
                "type": "object",
                "properties": {"summary": {"type": "string"}},
                "required": ["summary"],
                "additionalProperties": False,
            },
        },
        "required": ["proposed_score", "confidence", "criteria", "flags", "rationale"],
        "additionalProperties": False,
    }


def _openai_grade(question_prompt: str, answer_key: dict | None, rubric: list[dict], student_answer: str) -> dict:
    try:
        from openai import OpenAI
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("openai package is not installed") from exc

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    prompt = build_rubric_prompt(question_prompt, answer_key, rubric, student_answer)

    response = client.responses.create(
        model=settings.AI_MODEL,
        input=[
            {
                "role": "system",
                "content": "You are an academic grading assistant. Grade only from the student's answer. Do not invent evidence. Return only valid JSON matching the schema.",
            },
            {"role": "user", "content": json.dumps(prompt)},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "essay_grade_result",
                "strict": True,
                "schema": _schema(),
            }
        },
    )

    parsed = getattr(response, 'output_parsed', None)
    if parsed is None:
        text = getattr(response, 'output_text', None)
        if text:
            parsed = json.loads(text)
    if parsed is None:
        raise RuntimeError("No structured output returned from OpenAI")
    return parsed


def grade_essay_response(question_prompt: str, answer_key: dict | None, rubric: list[dict], student_answer: str) -> dict:
    provider = settings.AI_PROVIDER.lower()

    try:
        if provider == "mock":
            return _mock_grade(question_prompt, answer_key, rubric, student_answer)
        if provider == "openai":
            return _openai_grade(question_prompt, answer_key, rubric, student_answer)
    except Exception as exc:
        return {
            "proposed_score": 0.0,
            "confidence": 0.0,
            "criteria": [],
            "flags": ["provider_error", "needs_review"],
            "rationale": {"summary": f"Provider call failed: {exc}"},
        }

    raise ValueError(f"Unsupported AI provider: {settings.AI_PROVIDER}")
