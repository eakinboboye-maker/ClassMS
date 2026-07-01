import html

import ipywidgets as widgets
from IPython.display import display


_QUIZ_CSS = widgets.HTML(
    """
    <style>
      .classlite-question-card {
        overflow: visible !important;
      }
      .classlite-question-card .widget-radio-box,
      .classlite-question-card .widget-checkbox-box {
        overflow: visible !important;
      }
      .classlite-question-card .widget-radio-box label,
      .classlite-question-card .widget-checkbox-box label {
        height: auto !important;
        min-height: 28px !important;
        line-height: 1.4 !important;
        align-items: flex-start !important;
        white-space: normal !important;
        overflow: visible !important;
        margin: 7px 0 !important;
      }
      .classlite-question-card .widget-radio-box label > div,
      .classlite-question-card .widget-checkbox-box label > div,
      .classlite-question-card .widget-label {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
      }
      .classlite-option-row {
        overflow: visible !important;
        line-height: 1.4;
        margin: 7px 0;
      }
      .classlite-option-text {
        white-space: normal;
        overflow-wrap: anywhere;
        line-height: 1.4;
        padding-top: 2px;
      }
      .classlite-toolbar .widget-button {
        margin-right: 6px;
      }
    </style>
    """
)


def _as_option_tuple(option):
    """Return the (label, value) tuple expected by ipywidgets selection widgets."""
    return (str(option.get("text", "")), option.get("option_key"))


def _html(text):
    """Render user/backend text safely as simple HTML with line breaks preserved."""
    return html.escape(str(text or "")).replace("\n", "<br>")


class MultiCheckboxGroup:
    """A clearer multi-select control than SelectMultiple for notebook quizzes."""

    def __init__(self, options, on_change=None):
        self.options = list(options or [])
        self.checkboxes = []
        self.on_change = on_change
        rows = []
        for option in self.options:
            key = option.get("option_key")
            checkbox = widgets.Checkbox(
                value=False,
                description="",
                indent=False,
                layout=widgets.Layout(width="30px", flex="0 0 30px"),
            )
            checkbox._classlite_option_key = key
            checkbox.observe(self._changed, names="value")
            label = widgets.HTML(
                f"<div class='classlite-option-text'>{_html(option.get('text', ''))}</div>",
                layout=widgets.Layout(width="auto", flex="1 1 auto"),
            )
            row = widgets.HBox(
                [checkbox, label],
                layout=widgets.Layout(
                    align_items="flex-start",
                    width="100%",
                    overflow="visible",
                ),
            )
            row.add_class("classlite-option-row")
            self.checkboxes.append(checkbox)
            rows.append(row)
        self.widget = widgets.VBox(rows, layout=widgets.Layout(width="100%", overflow="visible"))

    @property
    def value(self):
        return tuple(
            cb._classlite_option_key
            for cb in self.checkboxes
            if cb.value
        )

    def disable(self):
        for cb in self.checkboxes:
            cb.disabled = True

    def _changed(self, change):
        if self.on_change:
            self.on_change(change)


class QuestionCard:
    def __init__(self, item, on_change=None):
        self.item = item
        self.question_id = item["question_id"]
        self.question_type = item["type"]
        self.on_change = on_change
        self.input_widget = None
        self.status = widgets.HTML("")
        self.container = self._build()
        self.container.add_class("classlite-question-card")

    def _build(self):
        header = widgets.HTML(
            "<div style='font-weight:700;'>Question {}</div>"
            "<div style='margin:8px 0 14px 0; line-height:1.45;'>{}</div>".format(
                html.escape(str(self.question_id)),
                self.item.get("prompt_md", ""),
            )
        )

        if self.question_type == "mcq_single":
            # Keep true radio-button semantics for single-answer objective questions.
            self.input_widget = widgets.RadioButtons(
                options=[_as_option_tuple(o) for o in self.item.get("options", [])],
                value=None,
                description="",
                layout=widgets.Layout(width="100%", overflow="visible"),
                style={"description_width": "0px"},
            )
            self.input_widget.observe(self._changed, names="value")
            body = self.input_widget

        elif self.question_type == "mcq_multi":
            # Multiple-answer questions need checkboxes, not a SelectMultiple listbox.
            self.input_widget = MultiCheckboxGroup(
                self.item.get("options", []),
                on_change=self._changed,
            )
            body = self.input_widget.widget

        elif self.question_type == "fill_gap":
            inputs = {}
            rows = []
            for gap in self.item.get("gaps", []):
                box = widgets.Text(placeholder=gap["gap_key"])
                box.observe(self._changed, names="value")
                inputs[gap["gap_key"]] = box
                rows.append(
                    widgets.HBox(
                        [
                            widgets.HTML(
                                f"<b>{html.escape(str(gap['gap_key']))}</b>",
                                layout=widgets.Layout(width="100px"),
                            ),
                            box,
                        ]
                    )
                )
            self.input_widget = inputs
            body = widgets.VBox(rows)

        else:
            self.input_widget = widgets.Textarea(
                placeholder="Type your answer here...",
                layout=widgets.Layout(width="100%", height="180px"),
            )
            self.input_widget.observe(self._changed, names="value")
            body = self.input_widget

        return widgets.VBox(
            [header, body, self.status],
            layout=widgets.Layout(
                border="1px solid #d1d5db",
                padding="14px",
                margin="12px 0",
                width="100%",
                overflow="visible",
            ),
        )

    def _changed(self, change):
        if self.on_change:
            self.on_change()

    def value(self):
        if self.question_type == "mcq_single":
            return {"selected_option": self.input_widget.value}
        if self.question_type == "mcq_multi":
            return {"selected_options": list(self.input_widget.value)}
        if self.question_type == "fill_gap":
            return {"gaps": {k: v.value for k, v in self.input_widget.items()}}
        return {"answer_text": self.input_widget.value}

    def is_answered(self):
        v = self.value()
        if self.question_type == "mcq_single":
            return bool(v.get("selected_option"))
        if self.question_type == "mcq_multi":
            return len(v.get("selected_options", [])) > 0
        if self.question_type == "fill_gap":
            return all(x.strip() for x in v.get("gaps", {}).values())
        return bool(v.get("answer_text", "").strip())

    def disable(self):
        if self.question_type == "mcq_multi":
            self.input_widget.disable()
        elif self.question_type == "fill_gap":
            for widget in self.input_widget.values():
                widget.disabled = True
        else:
            self.input_widget.disabled = True


class QuizResultsUI:
    def __init__(self, payload):
        self.payload = payload

    def render(self):
        cards = [
            widgets.HTML(
                "<div style='padding:14px; border:1px solid #d1d5db; background:#f8fafc;'>"
                f"<b>Your Score</b><div>{self.payload.get('total_awarded',0)} / {self.payload.get('total_max',0)}</div>"
                "</div>"
            )
        ]
        for item in self.payload.get("items", []):
            status = "Correct" if item.get("is_correct") else "Needs Review / Incorrect"
            color = "#15803d" if item.get("is_correct") else "#b91c1c"
            explanation = (
                "<div style='margin-top:8px; padding:10px; background:#f9fafb; border-radius:8px;'>"
                f"{item.get('explanation_md')}"
                "</div>"
                if item.get("show_explanation_after_submit") and item.get("explanation_md")
                else ""
            )
            cards.append(
                widgets.HTML(
                    "<div style='border:1px solid #d1d5db; padding:14px; margin:12px 0; border-radius:10px;'>"
                    f"<div><b>Question {item['question_id']}</b></div>"
                    f"<div style='margin:8px 0;'>{item.get('prompt_md','')}</div>"
                    f"<div style='color:{color}; font-weight:700;'>{status}</div>"
                    f"<div>Score: {item.get('awarded_marks',0)} / {item.get('max_marks',0)}</div>"
                    f"{explanation}</div>"
                )
            )
        display(widgets.VBox(cards))


class QuizNotebookUI:
    def __init__(self, lesson, items):
        self.lesson = lesson
        self.cards = [QuestionCard(i, on_change=self._update_progress) for i in items]
        self.output = widgets.Output()
        self.autosave_button = widgets.Button(description="Autosave", button_style="info")
        self.submit_button = widgets.Button(description="Submit", button_style="success")
        self.results_button = widgets.Button(description="Show Results", button_style="warning")
        self.results_button.disabled = True
        self.results_button.tooltip = "Submit the quiz before viewing results."
        self.progress = widgets.HTML("")
        self.autosave_button.on_click(self._autosave)
        self.submit_button.on_click(self._submit)
        self.results_button.on_click(self._results)

    def render(self):
        self._update_progress()
        toolbar = widgets.HBox(
            [self.autosave_button, self.submit_button, self.results_button],
            layout=widgets.Layout(margin="0 0 14px 0"),
        )
        toolbar.add_class("classlite-toolbar")
        display(widgets.VBox([_QUIZ_CSS, self.progress, toolbar, *[c.container for c in self.cards], self.output]))

    def _update_progress(self, *_):
        answered = sum(1 for c in self.cards if c.is_answered())
        total = len(self.cards)
        self.progress.value = f"<div style='font-weight:700; margin:8px 0 12px 0;'>Progress: {answered} / {total} answered</div>"

    def _collect(self):
        return {c.question_id: c.value() for c in self.cards}

    def _autosave(self, _):
        with self.output:
            self.output.clear_output()
            self.lesson.answers = self._collect()
            print(self.lesson.autosave())
            self._update_progress()

    def _submit(self, _):
        with self.output:
            self.output.clear_output()
            self.lesson.answers = self._collect()
            self.lesson.autosave()
            result = self.lesson.submit()
            print(result)
            self._update_progress()
            for card in self.cards:
                card.disable()
            self.submit_button.disabled = True
            self.autosave_button.disabled = True
            self.results_button.disabled = False
            self.results_button.tooltip = "View score, correctness, and explanations after submission."

    def _results(self, _):
        with self.output:
            self.output.clear_output()
            if self.results_button.disabled:
                print("Submit the quiz first. Results are only available after submission.")
                return
            QuizResultsUI(self.lesson.results()).render()
