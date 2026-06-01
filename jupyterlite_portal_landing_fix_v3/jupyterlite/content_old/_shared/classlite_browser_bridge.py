"""Browser-to-kernel bridge for ClassLite running in JupyterLite.

Why this exists
---------------
Pyodide kernels can often do ``from js import window`` and read
``window.localStorage`` directly. Xeus Python kernels are different: Python runs
inside a WebWorker/WASM runtime, so ``window`` may not exist in the ``js`` module.

The robust path is therefore:
1. Try direct JS access when the kernel supports it.
2. Otherwise use a tiny anywidget frontend. The widget runs in the browser page,
   reads localStorage, and syncs only the needed JSON strings back to Python.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional


_WIDGET_CLASS = None
_WIDGET = None
_LAST_PAYLOAD: Dict[str, Any] = {}


_STORAGE_TO_PAYLOAD_FIELD = {
    "classlite_portal_session": "session",
    "classlite_launch_context": "launch",
}


def _parse_json(raw: Any) -> Optional[Dict[str, Any]]:
    if raw is None:
        return None
    raw = str(raw)
    if raw == "":
        return None
    return json.loads(raw)


def _direct_local_storage_get(key: str) -> Optional[Dict[str, Any]]:
    """Best-effort direct JS/localStorage access.

    This works in some JupyterLite/Pyodide setups. It is expected to fail in many
    Xeus builds because the kernel is isolated from the browser window.
    """
    try:
        import js  # type: ignore
    except Exception:
        return None

    candidates = []
    for name in ("window", "self", "globalThis"):
        try:
            candidates.append(getattr(js, name))
        except Exception:
            pass

    try:
        document = getattr(js, "document")
        candidates.append(document.defaultView)
    except Exception:
        pass

    for obj in candidates:
        try:
            storage = getattr(obj, "localStorage")
            raw = storage.getItem(key)
            parsed = _parse_json(raw)
            if parsed is not None:
                return parsed
        except Exception:
            continue
    return None


def _ensure_widget_class():
    global _WIDGET_CLASS
    if _WIDGET_CLASS is not None:
        return _WIDGET_CLASS

    try:
        import anywidget  # type: ignore
        import traitlets  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "The ClassLite browser bridge needs anywidget in the JupyterLite "
            "Xeus environment. Add `anywidget` to environment.yml and rebuild."
        ) from exc

    class ClassLitePortalBridgeWidget(anywidget.AnyWidget):
        _esm = r"""
        export function render({ model, el }) {
          function readStorage(key) {
            try {
              return window.localStorage.getItem(key) || "";
            } catch (err) {
              return "";
            }
          }

          function sync() {
            const payload = {
              href: String(window.location.href),
              session: readStorage("classlite_portal_session"),
              launch: readStorage("classlite_launch_context"),
              synced_at: new Date().toISOString()
            };
            model.set("payload", JSON.stringify(payload));
            model.save_changes();
          }

          sync();
          window.addEventListener("storage", sync);

          el.innerHTML = `
            <div style="border:1px solid #d1d5db;border-radius:10px;padding:10px 12px;margin:8px 0;background:#f8fafc;color:#111827;font-family:system-ui,sans-serif">
              <strong>ClassLite portal bridge ready.</strong><br />
              <span style="font-size:0.9em;color:#4b5563">Now run the next bootstrap cell.</span>
            </div>`;
        }
        """

        payload = traitlets.Unicode("").tag(sync=True)

    _WIDGET_CLASS = ClassLitePortalBridgeWidget
    return _WIDGET_CLASS


def display_portal_bridge():
    """Render the frontend bridge that copies portal localStorage into Python."""
    global _WIDGET
    from IPython.display import display

    WidgetClass = _ensure_widget_class()
    if _WIDGET is None:
        _WIDGET = WidgetClass()
    display(_WIDGET)
    return {
        "status": "bridge-displayed",
        "next": "Run lesson.bootstrap_from_portal() in the next cell.",
    }


def _widget_payload() -> Dict[str, Any]:
    global _LAST_PAYLOAD
    if _WIDGET is None:
        return _LAST_PAYLOAD
    raw = getattr(_WIDGET, "payload", "") or ""
    if raw:
        try:
            _LAST_PAYLOAD = json.loads(raw)
        except Exception:
            pass
    return _LAST_PAYLOAD


def get_browser_json(key: str):
    """Read ClassLite JSON from the browser context.

    For Xeus kernels, call ``display_portal_bridge`` in a previous cell first.
    """
    direct = _direct_local_storage_get(key)
    if direct is not None:
        return direct

    field = _STORAGE_TO_PAYLOAD_FIELD.get(key, key)
    payload = _widget_payload()
    raw = payload.get(field)
    parsed = _parse_json(raw)
    if parsed is not None:
        return parsed

    raise RuntimeError(
        "Could not read the ClassLite portal session from the notebook runtime. "
        "In Xeus Python, the kernel cannot reliably access window.localStorage "
        "directly. Run the `lesson.prepare_portal_bridge()` cell first, wait for "
        "the 'ClassLite portal bridge ready' message, then run "
        "`lesson.bootstrap_from_portal()`. If you used Run All, run the first two "
        "notebook cells manually once."
    )
