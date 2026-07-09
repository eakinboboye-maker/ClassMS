"""ClassLite kernel-start autostart.

This is imported by sitecustomize.py when the xeus-python kernel starts.
It prepares the `lesson` object automatically for notebooks opened from the
ClassLite portal. It deliberately does not render the quiz UI at startup,
because there is no reliable notebook cell output area before a cell executes.
"""

import builtins
import traceback


def run():
    try:
        from _shared.classlite_bootstrap import bootstrap_lesson
        lesson = bootstrap_lesson()
        builtins._classlite_autostart_ok = True
        builtins._classlite_autostart_error = None
        return lesson
    except Exception as exc:
        # Never make kernel startup unusable because of portal/session issues.
        # The hidden fallback cell or visible diagnostic can surface this later.
        builtins._classlite_autostart_ok = False
        builtins._classlite_autostart_error = f"{type(exc).__name__}: {exc}"
        builtins._classlite_autostart_traceback = traceback.format_exc()
        return None
