"""Browser/portal bridge helpers for ClassLite notebooks.

Important JupyterLite/Xeus detail:
    The xeus-python kernel runs in a WebWorker/WASM runtime. In many builds it
    cannot access the page's `window.localStorage` directly. Therefore the
    portal writes the session/launch payload into a small JupyterLite contents
    file before opening Lab. The kernel reads that file from /drive/_shared/.

The older localStorage bridge is kept only as a fallback for runtimes that
support `from js import window`.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


RUNTIME_BRIDGE_FILENAME = "classlite_runtime_launch.json"


def _runtime_file_candidates():
    """Possible locations for the runtime bridge file inside JupyterLite."""
    return [
        Path("/drive/_shared") / RUNTIME_BRIDGE_FILENAME,
        Path("/_shared") / RUNTIME_BRIDGE_FILENAME,
        Path.cwd() / "_shared" / RUNTIME_BRIDGE_FILENAME,
        Path.cwd().parent / "_shared" / RUNTIME_BRIDGE_FILENAME,
        Path.cwd().parent.parent / "_shared" / RUNTIME_BRIDGE_FILENAME,
        Path("_shared") / RUNTIME_BRIDGE_FILENAME,
        Path(RUNTIME_BRIDGE_FILENAME),
    ]


def read_runtime_bridge() -> Optional[Dict[str, Any]]:
    """Read the portal-written runtime bridge JSON, if present."""
    for path in _runtime_file_candidates():
        try:
            if path.exists():
                raw = path.read_text(encoding="utf-8")
                if raw.strip():
                    data = json.loads(raw)
                    if isinstance(data, dict):
                        return data
        except Exception:
            # Try the next possible mount/path.
            continue
    return None


def _env_json(key: str) -> Optional[Dict[str, Any]]:
    raw = os.environ.get(key)
    if not raw:
        return None
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _js_local_storage_json(key: str) -> Optional[Dict[str, Any]]:
    """Best-effort localStorage fallback for Pyodide-like runtimes.

    This intentionally returns None on failure instead of raising, because Xeus
    commonly has no direct `window` object.
    """
    try:
        from js import window  # type: ignore
        raw = window.localStorage.getItem(key)
        if raw is None or raw == "":
            return None
        data = json.loads(str(raw))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def get_browser_json(key: str):
    """Return a portal session/launch object by key.

    Resolution order:
      1. Environment JSON overrides, useful for tests.
      2. Portal-written file: /drive/_shared/classlite_runtime_launch.json.
      3. Direct JS localStorage fallback, only where available.
    """
    # Test/dev override.
    env_map = {
        "classlite_portal_session": "CLASSLITE_PORTAL_SESSION_JSON",
        "classlite_launch_context": "CLASSLITE_LAUNCH_CONTEXT_JSON",
    }
    env_value = _env_json(env_map.get(key, "")) if key in env_map else None
    if env_value:
        return env_value

    bridge = read_runtime_bridge() or {}
    if key == "classlite_portal_session":
        session = bridge.get("session")
        if isinstance(session, dict):
            return session
    if key == "classlite_launch_context":
        launch = bridge.get("launch")
        if isinstance(launch, dict):
            return launch

    # Backwards compatibility if running on a runtime where localStorage is
    # directly visible from Python.
    return _js_local_storage_json(key)


def bridge_debug_state():
    """Return diagnostic details without exposing token values."""
    bridge = read_runtime_bridge() or {}
    candidates = []
    for path in _runtime_file_candidates():
        try:
            candidates.append({"path": str(path), "exists": path.exists()})
        except Exception:
            candidates.append({"path": str(path), "exists": False})
    session = bridge.get("session") if isinstance(bridge, dict) else None
    launch = bridge.get("launch") if isinstance(bridge, dict) else None
    return {
        "runtime_bridge_file": RUNTIME_BRIDGE_FILENAME,
        "candidates": candidates,
        "bridge_loaded": bool(bridge),
        "has_session": isinstance(session, dict),
        "has_token": bool(session.get("token")) if isinstance(session, dict) else False,
        "has_launch": isinstance(launch, dict),
        "lesson_slug": launch.get("lesson_slug") if isinstance(launch, dict) else None,
        "assessment_id": launch.get("assessment_id") if isinstance(launch, dict) else None,
    }
