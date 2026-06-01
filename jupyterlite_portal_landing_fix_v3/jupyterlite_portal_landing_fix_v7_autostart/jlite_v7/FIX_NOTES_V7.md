# ClassLite JupyterLite v7 — automatic lesson bootstrap

This version hides and automates the notebook setup code.

## What changed

1. Added `_shared/classlite_bootstrap.py`:
   - `bootstrap_lesson()` creates and portal-bootstraps the `ClassLiteLesson`.
   - `ensure_lesson()` returns the active lesson.
   - `show_quiz()` starts/reuses the attempt, fetches the paper, and renders the quiz.

2. Added `_shared/classlite_autostart.py` plus `sitecustomize.py`:
   - Python automatically imports `sitecustomize.py` when the xeus-python kernel starts.
   - The file calls the ClassLite bootstrap and exposes these names globally:
     - `lesson`
     - `ClassLiteLesson`
     - `QuizNotebookUI`
     - `classlite_lesson_slug`
   - Startup errors are captured in:
     - `_classlite_autostart_ok`
     - `_classlite_autostart_error`
     - `_classlite_autostart_traceback`

3. Added both:
   - `content/sitecustomize.py`
   - `content/EEE355/sitecustomize.py`

   This makes autostart work whether xeus starts with `/drive` or `/drive/EEE355` on `sys.path`.

4. Updated `portal/index.html` so notebook launches include:

   ```text
   classlite_autostart=1
   classlite_lesson_slug=week01_intro
   ```

5. Updated `content/EEE355/week01_class_note.ipynb`:
   - The old visible import/setup cell is now a hidden fallback cell.
   - The quiz cell is now only:

   ```python
   from _shared.classlite_bootstrap import show_quiz
   ui = show_quiz()
   ```

## Important note

This implementation automatically prepares the lesson object when the notebook kernel starts.
It does not auto-render the quiz UI before a notebook cell runs, because JupyterLab needs a cell output area for widgets. The student no longer sees the long imports and instantiation code.

Security still belongs on the backend. Hidden notebook code is for user experience, not authorization.
