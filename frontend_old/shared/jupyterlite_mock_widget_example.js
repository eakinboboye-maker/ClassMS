export class JupyterLiteMockExamClient {
  constructor({ baseUrl, token, assessmentId }) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.token = token;
    this.assessmentId = assessmentId;
    this.attemptId = null;
    this.paper = null;
    this.responses = {};
  }

  headers() {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.token}`,
    };
  }

  async start() {
    const res = await fetch(`${this.baseUrl}/api/mock-exams/${this.assessmentId}/start`, {
      method: "POST",
      headers: this.headers(),
    });
    if (!res.ok) throw new Error(`Failed to start mock exam: ${res.status}`);
    const data = await res.json();
    this.attemptId = data.attempt_id;
    return data;
  }

  async fetchPaper() {
    const res = await fetch(`${this.baseUrl}/api/mock-exams/${this.assessmentId}/paper`, {
      method: "GET",
      headers: this.headers(),
    });
    if (!res.ok) throw new Error(`Failed to fetch paper: ${res.status}`);
    const data = await res.json();
    this.paper = data;
    return data;
  }

  setResponse(questionId, response) {
    this.responses[questionId] = response;
  }

  async autosave() {
    if (!this.attemptId) throw new Error("Attempt not started");
    const payload = {
      responses: Object.entries(this.responses).map(([question_id, response]) => ({
        question_id: Number(question_id),
        response,
      })),
    };
    const res = await fetch(`${this.baseUrl}/api/mock-exams/attempts/${this.attemptId}/autosave`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Autosave failed: ${res.status}`);
    return res.json();
  }

  async submit() {
    if (!this.attemptId) throw new Error("Attempt not started");
    const res = await fetch(`${this.baseUrl}/api/mock-exams/attempts/${this.attemptId}/submit`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({
        submitted_payload: {
          submitted_from: "jupyterlite",
          done: true,
        },
      }),
    });
    if (!res.ok) throw new Error(`Submit failed: ${res.status}`);
    return res.json();
  }
}
