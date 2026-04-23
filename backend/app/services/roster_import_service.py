import csv
import io
from typing import Any

from app.schemas.user import RosterUserCreate


EXPECTED_COLUMNS = {
    "email": ["email", "email address", "mail"],
    "full_name": ["full_name", "full name", "name", "names"],
    "matric_no": ["matric_no", "matric no", "reg no.", "reg no", "registration number"],
    "role": ["role"],
    "password": ["password"],
}


def _normalize_header(header: str) -> str:
    return header.strip().lower()


def _map_columns(headers: list[str]) -> dict[str, str]:
    normalized = {_normalize_header(h): h for h in headers}
    mapping: dict[str, str] = {}

    for canonical, aliases in EXPECTED_COLUMNS.items():
        for alias in aliases:
            if alias in normalized:
                mapping[canonical] = normalized[alias]
                break
    return mapping


def parse_csv_roster(content: str) -> tuple[list[RosterUserCreate], list[dict[str, Any]]]:
    buffer = io.StringIO(content)
    reader = csv.DictReader(buffer)

    if not reader.fieldnames:
        return [], [{"row": 0, "error": "Missing header row"}]

    mapping = _map_columns(reader.fieldnames)
    if "email" not in mapping or "full_name" not in mapping:
        return [], [{"row": 0, "error": "Required columns missing: email, full_name"}]

    rows: list[RosterUserCreate] = []
    errors: list[dict[str, Any]] = []

    for idx, row in enumerate(reader, start=2):
        try:
            parsed = RosterUserCreate(
                email=(row.get(mapping["email"]) or "").strip(),
                full_name=(row.get(mapping["full_name"]) or "").strip(),
                matric_no=(row.get(mapping["matric_no"]) or "").strip() or None if "matric_no" in mapping else None,
                role=(row.get(mapping["role"]) or "student").strip() if "role" in mapping else "student",
                password=(row.get(mapping["password"]) or "").strip() or None if "password" in mapping else None,
            )
            rows.append(parsed)
        except Exception as exc:
            errors.append({"row": idx, "error": str(exc), "data": row})

    return rows, errors


def parse_xlsx_roster_rows(rows: list[dict[str, Any]]) -> tuple[list[RosterUserCreate], list[dict[str, Any]]]:
    if not rows:
        return [], [{"row": 0, "error": "No rows provided"}]

    headers = list(rows[0].keys())
    mapping = _map_columns(headers)
    if "email" not in mapping or "full_name" not in mapping:
        return [], [{"row": 0, "error": "Required columns missing: email, full_name"}]

    parsed_rows: list[RosterUserCreate] = []
    errors: list[dict[str, Any]] = []

    for idx, row in enumerate(rows, start=1):
        try:
            parsed = RosterUserCreate(
                email=str(row.get(mapping["email"], "")).strip(),
                full_name=str(row.get(mapping["full_name"], "")).strip(),
                matric_no=str(row.get(mapping["matric_no"], "")).strip() or None if "matric_no" in mapping else None,
                role=str(row.get(mapping["role"], "student")).strip() if "role" in mapping else "student",
                password=str(row.get(mapping["password"], "")).strip() or None if "password" in mapping else None,
            )
            parsed_rows.append(parsed)
        except Exception as exc:
            errors.append({"row": idx, "error": str(exc), "data": row})

    return parsed_rows, errors
