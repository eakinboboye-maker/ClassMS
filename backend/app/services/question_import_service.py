import csv
import io
import json
import re
from typing import Any

from app.schemas.imports import ParsedQuestionRow, ParsedQuestionOption, ParsedEnrollmentRow


def _split_semicolon_values(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def parse_quiz_text(text: str) -> tuple[list[ParsedQuestionRow], list[str]]:
    blocks = re.findall(r"!bquiz(.*?)!equiz", text, flags=re.DOTALL | re.IGNORECASE)
    questions: list[ParsedQuestionRow] = []
    warnings: list[str] = []

    for block_index, block in enumerate(blocks, start=1):
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        prompt = None
        topics: list[str] = []
        labels: list[str] = []
        show_explanation_after_submit = False
        explanation_md = None
        options: list[ParsedQuestionOption] = []
        pending_option_index: int | None = None

        for line in lines:
            if line.startswith("Q:"):
                prompt = line[2:].strip()
            elif line.startswith("K:"):
                topics = _split_semicolon_values(line[2:].strip())
            elif line.startswith("L:"):
                labels = _split_semicolon_values(line[2:].strip())
            elif line.startswith("X:"):
                meta = line[2:].strip().lower()
                if "show_explanation_after_submit=true" in meta:
                    show_explanation_after_submit = True
            elif line.startswith("Cr:"):
                text_value = line[3:].strip()
                option_key = chr(ord("a") + len(options))
                options.append(
                    ParsedQuestionOption(
                        option_key=option_key,
                        text=text_value,
                        is_correct=True,
                    )
                )
                pending_option_index = len(options) - 1
            elif line.startswith("Cw:"):
                text_value = line[3:].strip()
                option_key = chr(ord("a") + len(options))
                options.append(
                    ParsedQuestionOption(
                        option_key=option_key,
                        text=text_value,
                        is_correct=False,
                    )
                )
                pending_option_index = len(options) - 1
            elif line.startswith("E:"):
                exp = line[2:].strip()
                if pending_option_index is not None:
                    options[pending_option_index].explanation_md = exp
                else:
                    explanation_md = exp

        if not prompt:
            warnings.append(f"Block {block_index}: missing Q: prompt")
            continue

        if not options:
            warnings.append(f"Block {block_index}: no options found")
            continue

        questions.append(
            ParsedQuestionRow(
                type="mcq_single",
                prompt_md=prompt,
                marks=1,
                topics=topics,
                labels=labels,
                options=options,
                explanation_md=explanation_md,
                show_explanation_after_submit=show_explanation_after_submit,
            )
        )

    return questions, warnings


def parse_mixed_question_csv_text(csv_text: str) -> tuple[list[ParsedQuestionRow], list[dict[str, Any]]]:
    reader = csv.DictReader(io.StringIO(csv_text))
    rows: list[ParsedQuestionRow] = []
    errors: list[dict[str, Any]] = []

    for idx, row in enumerate(reader, start=2):
        try:
            options_json = row.get("options_json", "") or "[]"
            answer_key_json = row.get("answer_key_json", "") or "{}"
            parsed = ParsedQuestionRow(
                type=(row.get("type") or "").strip(),
                prompt_md=(row.get("prompt_md") or "").strip(),
                marks=int(row.get("marks") or 1),
                topics=_split_semicolon_values(row.get("topic")),
                labels=_split_semicolon_values(row.get("label")),
                options=[ParsedQuestionOption(**opt) for opt in json.loads(options_json)],
                answer_key=json.loads(answer_key_json),
                explanation_md=(row.get("explanation_md") or "").strip() or None,
                show_explanation_after_submit=str(row.get("show_explanation_after_submit", "")).strip().lower() == "true",
                grading_mode="ai_human_loop" if (row.get("type") or "").strip() in {"essay", "short_answer"} else None,
            )
            rows.append(parsed)
        except Exception as exc:
            errors.append({"row": idx, "error": str(exc), "data": row})

    return rows, errors


def parse_enrollment_rows(rows: list[dict]) -> tuple[list[ParsedEnrollmentRow], list[dict]]:
    parsed: list[ParsedEnrollmentRow] = []
    errors: list[dict] = []

    for idx, row in enumerate(rows, start=1):
        try:
            parsed.append(
                ParsedEnrollmentRow(
                    reg_no=str(row.get("Reg No.", "")).strip(),
                    course_code=str(row.get("Course Code", "")).strip(),
                    section=str(row.get("Section", "")).strip(),
                    session=str(row.get("Session", "")).strip(),
                )
            )
        except Exception as exc:
            errors.append({"row": idx, "error": str(exc), "data": row})
    return parsed, errors
