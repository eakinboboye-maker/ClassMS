import ipywidgets as widgets
from IPython.display import display


class QuestionCard:
    def __init__(self, item: dict):
        self.item = item
        self.question_id = item["question_id"]
        self.question_type = item["type"]
        self.prompt_md = item.get("prompt_md", "")
        self.marks = item.get("marks", 0)

        self.container = None
        self.input_widget = None
        self.status = widgets.HTML("")
        self._build()

    def _build_header(self):
        title = widgets.HTML(
            f"""
            <div style="font-weight:600; font-size:16px; margin-bottom:6px;">
              Q{self.question_id} ({self.marks} mark{'s' if self.marks != 1 else ''})
            </div>
            """
        )
        prompt = widgets.HTML(
            f"""
            <div style="margin-bottom:10px; line-height:1.5;">
              {self.prompt_md}
            </div>
            """
        )
        return widgets.VBox([title, prompt])

    def _build_mcq_single(self):
        options = [(opt["text"], opt["option_key"]) for opt in self.item.get("options", [])]
        self.input_widget = widgets.RadioButtons(
            options=options,
            value=None,
            description="",
            layout=widgets.Layout(width="100%"),
        )

    def _build_mcq_multi(self):
        options = [(opt["text"], opt["option_key"]) for opt in self.item.get("options", [])]
        self.input_widget = widgets.SelectMultiple(
            options=options,
            value=(),
            description="",
            layout=widgets.Layout(width="100%", height="150px"),
        )

    def _build_fill_gap(self):
        gap_widgets = {}
        rows = []
        for gap in self.item.get("gaps", []):
            key = gap["gap_key"]
            box = widgets.Text(
                placeholder=f"Enter {key}",
                layout=widgets.Layout(width="320px"),
            )
            gap_widgets[key] = box
            rows.append(
                widgets.HBox([
                    widgets.HTML(f"<b>{key}</b>", layout=widgets.Layout(width="90px")),
                    box
                ])
            )
        self.input_widget = gap_widgets
        self.gap_box = widgets.VBox(rows)

    def _build_text_response(self):
        self.input_widget = widgets.Textarea(
            value="",
            placeholder="Type your answer here...",
            layout=widgets.Layout(width="100%", height="180px"),
        )

    def _build(self):
        header = self._build_header()

        if self.question_type == "mcq_single":
            self._build_mcq_single()
            body = self.input_widget
        elif self.question_type == "mcq_multi":
            self._build_mcq_multi()
            body = self.input_widget
        elif self.question_type == "fill_gap":
            self._build_fill_gap()
            body = self.gap_box
        elif self.question_type in {"short_answer", "essay"}:
            self._build_text_response()
            body = self.input_widget
        else:
            body = widgets.HTML(
                f"<div style='color:red;'>Unsupported question type: {self.question_type}</div>"
            )

        self.container = widgets.VBox(
            [header, body, self.status],
            layout=widgets.Layout(
                border="1px solid #d1d5db",
                padding="14px",
                margin="12px 0",
                width="100%",
            ),
        )

    def value(self):
        if self.question_type == "mcq_single":
            if self.input_widget.value is None:
                return None
            return {"selected_option": self.input_widget.value}

        if self.question_type == "mcq_multi":
            return {"selected_options": list(self.input_widget.value)}

        if self.question_type == "fill_gap":
            return {"gaps": {key: widget.value for key, widget in self.input_widget.items()}}

        if self.question_type in {"short_answer", "essay"}:
            return {"answer_text": self.input_widget.value}

        return None

    def is_answered(self):
        val = self.value()

        if val is None:
            return False
        if self.question_type == "mcq_single":
            return bool(val.get("selected_option"))
        if self.question_type == "mcq_multi":
            return len(val.get("selected_options", [])) > 0
        if self.question_type == "fill_gap":
            return all(v.strip() for v in val.get("gaps", {}).values())
        if self.question_type in {"short_answer", "essay"}:
            return bool(val.get("answer_text", "").strip())
        return False

    def set_status(self, text: str, color: str = "#2563eb"):
        self.status.value = f"<div style='margin-top:8px; color:{color};'>{text}</div>"


class QuizNotebookUI:
    def __init__(self, lesson, items: list[dict]):
        self.lesson = lesson
        self.items = items
        self.cards = [QuestionCard(item) for item in items]
        self.output = widgets.Output()

        self.autosave_button = widgets.Button(description="Autosave", button_style="info")
        self.submit_button = widgets.Button(description="Submit", button_style="success")
        self.refresh_button = widgets.Button(description="Refresh Scores")
        self.progress = widgets.HTML("")

        self.autosave_button.on_click(self._autosave_clicked)
        self.submit_button.on_click(self._submit_clicked)
        self.refresh_button.on_click(self._scores_clicked)
        
        self.results_button = widgets.Button(description="Show Results", button_style="warning")
        self.results_button.on_click(self._results_clicked)

    def render(self):
        controls = widgets.HBox(
            [self.autosave_button, self.submit_button, self.refresh_button, self.results_button],
            layout=widgets.Layout(margin="8px 0 16px 0")
        )
        self._update_progress()
        display(widgets.VBox([self.progress, controls, *[card.container for card in self.cards], self.output]))

    def _update_progress(self):
        answered = sum(1 for c in self.cards if c.is_answered())
        total = len(self.cards)
        self.progress.value = f"""
        <div style="margin:8px 0 12px 0; font-weight:600;">
          Progress: {answered} / {total} answered
        </div>
        """

    def collect_answers(self):
        answers = {}
        for card in self.cards:
            answers[card.question_id] = card.value()
        return answers

    def validate_before_submit(self):
        return [card.question_id for card in self.cards if not card.is_answered()]

    def _autosave_clicked(self, _):
        import traceback
        with self.output:
            self.output.clear_output()
            try:
                self.lesson.answers = self.collect_answers()
                result = self.lesson.autosave()
                self._update_progress()
                for card in self.cards:
                    card.set_status("Saved")
                print("Autosave successful")
                print(result)
            except Exception:
                traceback.print_exc()

    def _submit_clicked(self, _):
        import traceback
        with self.output:
            self.output.clear_output()
            try:
                missing = self.validate_before_submit()
                if missing:
                    print(f"Cannot submit yet. Unanswered questions: {missing}")
                    return

                self.lesson.answers = self.collect_answers()
                self.lesson.autosave()
                result = self.lesson.submit()
                self._update_progress()
                for card in self.cards:
                    card.set_status("Submitted", color="#15803d")
                print("Submission successful")
                print(result)
            except Exception:
                traceback.print_exc()

    def _scores_clicked(self, _):
        import traceback
        with self.output:
            self.output.clear_output()
            try:
                result = self.lesson.scores()
                print(result)
            except Exception:
                traceback.print_exc()
                
    def _results_clicked(self, _):
        import traceback
        with self.output:
            self.output.clear_output()
            try:
                result = self.lesson.results()
                viewer = QuizResultsUI(result)
                viewer.render()
            except Exception:
                traceback.print_exc()
                
     
                
class QuizResultsUI:
    def __init__(self, result_payload: dict):
        self.result_payload = result_payload

    def render(self):
        import ipywidgets as widgets
        from IPython.display import display

        total_awarded = self.result_payload.get("total_awarded", 0)
        total_max = self.result_payload.get("total_max", 0)

        header = widgets.HTML(
            f"""
            <div style="padding:14px; border:1px solid #d1d5db; margin:10px 0; background:#f8fafc;">
              <div style="font-size:18px; font-weight:700;">Your Score</div>
              <div style="font-size:16px; margin-top:6px;">{total_awarded} / {total_max}</div>
            </div>
            """
        )

        cards = []
        for item in self.result_payload.get("items", []):
            status_color = "#15803d" if item["is_correct"] else "#b91c1c"
            status_label = "Correct" if item["is_correct"] else "Needs Review / Incorrect"

            explanation_block = ""
            if item.get("show_explanation_after_submit") and item.get("explanation_md"):
                explanation_block = f"""
                <div style="margin-top:10px; padding:10px; background:#f9fafb; border-radius:8px;">
                  <div style="font-weight:600;">Explanation</div>
                  <div style="margin-top:6px;">{item['explanation_md']}</div>
                </div>
                """

            correct_answer_block = ""
            if item.get("correct_answer_summary") is not None:
                correct_answer_block = f"""
                <div style="margin-top:8px;">
                  <b>Correct answer:</b> {item['correct_answer_summary']}
                </div>
                """

            card = widgets.HTML(
                f"""
                <div style="border:1px solid #d1d5db; padding:14px; margin:12px 0; border-radius:10px;">
                  <div style="font-weight:700;">Question {item['question_id']}</div>
                  <div style="margin:8px 0;">{item['prompt_md']}</div>
                  <div style="color:{status_color}; font-weight:600;">{status_label}</div>
                  <div style="margin-top:6px;">Score: {item['awarded_marks']} / {item['max_marks']}</div>
                  {correct_answer_block}
                  {explanation_block}
                </div>
                """
            )
            cards.append(card)

        display(widgets.VBox([header, *cards]))
