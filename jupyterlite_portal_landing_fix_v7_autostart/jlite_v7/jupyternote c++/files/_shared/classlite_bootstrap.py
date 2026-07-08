"""Small, student-facing bootstrap helpers for ClassLite notebooks.

The goal is to keep lesson notebooks clean: imports, portal token loading,
ClassLiteLesson construction, and QuizNotebookUI imports live here instead of
being repeated visibly in every notebook.
"""

import builtins
from typing import Optional

from _shared.classlite_site_config import API_BASE
from _shared.classlite_jupyter import ClassLiteLesson
from _shared.classlite_quiz_ui import QuizNotebookUI
from _shared.classlite_site_config import PORTAL_LAUNCH_KEY
from _shared.classlite_browser_bridge import get_browser_json


DEFAULT_LESSON_SLUG = "week01_intro"


def _lesson_slug_from_browser(default: Optional[str] = None) -> str:
    """Infer the lesson slug from portal launch context or URL query params."""
    default = default or DEFAULT_LESSON_SLUG

    # Preferred source: the portal stores the launch payload before opening Lab.
    try:
        launch = get_browser_json(PORTAL_LAUNCH_KEY) or {}
        if launch.get("lesson_slug"):
            return str(launch["lesson_slug"])
    except Exception:
        pass

    # Fallback source: portal also appends classlite_lesson_slug to the URL.
    try:
        from js import window
        params = window.URLSearchParams.new(window.location.search)
        value = params.get("classlite_lesson_slug") or params.get("lesson_slug")
        if value:
            return str(value)
    except Exception:
        pass

    return default


def bootstrap_lesson(lesson_slug: Optional[str] = None, *, force: bool = False) -> ClassLiteLesson:
    """Create and portal-bootstrap the global `lesson` object.

    This function is safe to call more than once. If a lesson already exists in
    builtins and force=False, it is reused.
    """
    existing = getattr(builtins, "lesson", None)
    if existing is not None and not force:
        return existing

    slug = lesson_slug or _lesson_slug_from_browser()
    lesson = ClassLiteLesson(api_base=API_BASE, lesson_slug=slug)
    lesson.bootstrap_from_portal()

    # Make the useful objects available in simple notebook cells without imports.
    builtins.lesson = lesson
    builtins.ClassLiteLesson = ClassLiteLesson
    builtins.QuizNotebookUI = QuizNotebookUI
    builtins.classlite_lesson_slug = slug
    return lesson


def ensure_lesson(lesson_slug: Optional[str] = None) -> ClassLiteLesson:
    """Return the active lesson, creating it if needed."""
    existing = getattr(builtins, "lesson", None)
    if existing is not None:
        return existing
    return bootstrap_lesson(lesson_slug)


def start_quiz(lesson: Optional[ClassLiteLesson] = None):
    """Start/reuse the quiz attempt and fetch its paper.

    Returns (lesson, paper, ui). It does not display the UI; use show_quiz()
    when you want to display the quiz immediately.
    """
    lesson = lesson or ensure_lesson()
    lesson.start_attempt()
    paper = lesson.fetch_paper()
    ui = QuizNotebookUI(lesson, paper.get("items", []))
    builtins.paper = paper
    builtins.ui = ui
    return lesson, paper, ui


def show_quiz(lesson: Optional[ClassLiteLesson] = None):
    """Start/reuse the attempt, fetch the paper, render the quiz UI, and return ui."""
    _, _, ui = start_quiz(lesson)
    ui.render()
    return ui
