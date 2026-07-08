import json

def get_browser_json(key: str):
    try:
        from js import window
        raw = window.localStorage.getItem(key)
        if raw is None or raw == "":
            return None
        return json.loads(str(raw))
    except Exception as exc:
        raise RuntimeError(
            "Could not access browser localStorage from the notebook runtime. "
            "This bridge may need small adjustment for your exact Xeus build."
        ) from exc
