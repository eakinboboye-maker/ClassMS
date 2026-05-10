import ipywidgets as widgets
from IPython.display import display

class QuestionCard:
    def __init__(self, item):
        self.item = item
        self.question_id = item["question_id"]
        self.question_type = item["type"]
        self.input_widget = None
        self.status = widgets.HTML("")
        self.container = self._build()

    def _build(self):
        header = widgets.HTML(f"<div style='font-weight:700;'>Question {self.question_id}</div><div style='margin:8px 0;'>{self.item.get('prompt_md','')}</div>")
        if self.question_type == "mcq_single":
            self.input_widget = widgets.RadioButtons(options=[(o['text'], o['option_key']) for o in self.item.get("options", [])], value=None, description="")
            body = self.input_widget
        elif self.question_type == "mcq_multi":
            self.input_widget = widgets.SelectMultiple(options=[(o['text'], o['option_key']) for o in self.item.get("options", [])], value=(), description="")
            body = self.input_widget
        elif self.question_type == "fill_gap":
            inputs = {}
            rows = []
            for gap in self.item.get("gaps", []):
                box = widgets.Text(placeholder=gap["gap_key"])
                inputs[gap["gap_key"]] = box
                rows.append(widgets.HBox([widgets.HTML(f"<b>{gap['gap_key']}</b>", layout=widgets.Layout(width="100px")), box]))
            self.input_widget = inputs
            body = widgets.VBox(rows)
        else:
            self.input_widget = widgets.Textarea(placeholder="Type your answer here...", layout=widgets.Layout(width="100%", height="180px"))
            body = self.input_widget
        return widgets.VBox([header, body, self.status], layout=widgets.Layout(border="1px solid #d1d5db", padding="14px", margin="12px 0"))

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

class QuizResultsUI:
    def __init__(self, payload):
        self.payload = payload
    def render(self):
        cards = [widgets.HTML(f"<div style='padding:14px; border:1px solid #d1d5db; background:#f8fafc;'><b>Your Score</b><div>{self.payload.get('total_awarded',0)} / {self.payload.get('total_max',0)}</div></div>")]
        for item in self.payload.get("items", []):
            status = "Correct" if item.get("is_correct") else "Needs Review / Incorrect"
            color = "#15803d" if item.get("is_correct") else "#b91c1c"
            explanation = f"<div style='margin-top:8px; padding:10px; background:#f9fafb; border-radius:8px;'>{item.get('explanation_md')}</div>" if item.get("show_explanation_after_submit") and item.get("explanation_md") else ""
            cards.append(widgets.HTML(f"<div style='border:1px solid #d1d5db; padding:14px; margin:12px 0; border-radius:10px;'><div><b>Question {item['question_id']}</b></div><div style='margin:8px 0;'>{item.get('prompt_md','')}</div><div style='color:{color}; font-weight:700;'>{status}</div><div>Score: {item.get('awarded_marks',0)} / {item.get('max_marks',0)}</div>{explanation}</div>"))
        display(widgets.VBox(cards))

class QuizNotebookUI:
    def __init__(self, lesson, items):
        self.lesson = lesson
        self.cards = [QuestionCard(i) for i in items]
        self.output = widgets.Output()
        self.autosave_button = widgets.Button(description="Autosave", button_style="info")
        self.submit_button = widgets.Button(description="Submit", button_style="success")
        self.results_button = widgets.Button(description="Show Results", button_style="warning")
        self.progress = widgets.HTML("")
        self.autosave_button.on_click(self._autosave)
        self.submit_button.on_click(self._submit)
        self.results_button.on_click(self._results)

    def render(self):
        self._update_progress()
        display(widgets.VBox([self.progress, widgets.HBox([self.autosave_button, self.submit_button, self.results_button]), *[c.container for c in self.cards], self.output]))

    def _update_progress(self):
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
            print(self.lesson.submit())
            self._update_progress()

    def _results(self, _):
        with self.output:
            self.output.clear_output()
            QuizResultsUI(self.lesson.results()).render()
