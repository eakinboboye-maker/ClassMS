const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type TokenResponse = { access_token: string; token_type: string };
export type EssayReviewItem = {
  review_id: number;
  response_id: number;
  question_id: number;
  attempt_id: number;
  user_id: number | null;
  prompt_md: string;
  student_answer: string;
  proposed_score: number | null;
  confidence: number | null;
  criteria: any[];
  flags: string[];
  rationale: Record<string, any> | null;
  max_marks: number;
};

export class BackendClient {
  token?: string;
  setToken(token: string) { this.token = token; }
  private headers(extra?: Record<string,string>) {
    return {
      "Content-Type": "application/json",
      ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      ...(extra || {}),
    };
  }
  async login(email: string, password: string): Promise<TokenResponse> {
    const res = await fetch(`${API_BASE}/api/auth/login`, { method: "POST", headers: this.headers(), body: JSON.stringify({ email, password }) });
    if (!res.ok) throw new Error(`Login failed: ${res.status}`);
    return res.json();
  }
  async fetchJSON(path: string) {
    const res = await fetch(`${API_BASE}${path}`, { headers: this.headers() });
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
  }
  async postJSON(path: string, body: any) {
    const res = await fetch(`${API_BASE}${path}`, { method: "POST", headers: this.headers(), body: JSON.stringify(body) });
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
  }
  async getEssayReviewItems(): Promise<{ items: EssayReviewItem[] }> {
    return this.fetchJSON(`/api/grading/reviews/essay-items`);
  }
  async resolveEssayReview(reviewId: number, finalScore: number, reviewer_comment = "Reviewed from dashboard") {
    return this.postJSON(`/api/grading/reviews/${reviewId}/resolve`, { approved: true, final_score: finalScore, reviewer_comment });
  }
  async getGradebook(query = "") { return this.fetchJSON(`/api/grading/gradebook${query ? `?${query}` : ""}`); }
  async getIncidentDashboard(query = "") { return this.fetchJSON(`/api/admin/incidents/dashboard${query ? `?${query}` : ""}`); }
  async getCourses() { return this.fetchJSON(`/api/courses/`); }
  async getUsers() { return this.fetchJSON(`/api/users/`); }
}

export const apiBase = API_BASE;
