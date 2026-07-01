"""ClassLite automatic notebook setup for EEE355 notebooks."""

try:
    import sys
    from pathlib import Path
    parent = str(Path(__file__).resolve().parents[1])
    if parent not in sys.path:
        sys.path.insert(0, parent)
    from _shared.classlite_autostart import run
    run()
except Exception:
    pass
