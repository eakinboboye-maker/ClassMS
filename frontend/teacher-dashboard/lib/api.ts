const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type EssayReviewItem = {
  review_id: number;
  prompt_md: string;
  student_answer: string;
  proposed_score: number | null;
  confidence: number | null;
  max_marks?: number | null;
  question_id?: number | null;
  attempt_id?: number | null;
  flags?: string[];
};

type ClientOptions = {
  baseUrl: string;
  token?: string;
};

export async function apiFetch(path: string, token?: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${apiBase}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    throw new Error(`${res.status} ${await res.text()}`);
  }

  return res.json();
}

export async function login(email: string, password: string) {
  return apiFetch("/api/auth/login", undefined, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}



export class BackendClient {
  baseUrl: string;
  token?: string;

  constructor(options: ClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/$/, "");
    this.token = options.token;
  }

  setToken(token: string) {
    this.token = token;
  }

  private headers(extra?: Record<string, string>) {
    return {
      "Content-Type": "application/json",
      ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      ...(extra || {}),
    };
  }

  async login(email: string, password: string) {
    const result = await login(email, password);
    if (result?.access_token) this.token = result.access_token;
    return result;
  }

  async getEssayReviewItems(): Promise<{ items: EssayReviewItem[] }> {
    return apiFetch("/api/grading/reviews/essay-items", this.token || undefined);
  }

  async resolveEssayReview(reviewId: number, finalScore: number, reviewerComment = "Reviewed from dashboard") {
    return apiFetch(`/api/grading/reviews/${reviewId}/resolve`, this.token || undefined, {
      method: "POST",
      body: JSON.stringify({
        approved: true,
        final_score: finalScore,
        reviewer_comment: reviewerComment,
      }),
    });
  }
    
  async getIncidentDashboard(query: string = "") {
    const suffix = query ? `?${query}` : "";
    const res = await fetch(`${this.baseUrl}/api/admin/incidents${suffix}`, {
      method: "GET",
      headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.token}`,
    },
  });

    if (!res.ok) {
      throw new Error(`Failed to load incident dashboard: ${res.status} ${await res.text()}`);
    }

    return res.json();
 }
    
  async getGradebook(query = "") {
    const suffix = query ? `?${query}` : "";
    return apiFetch(`/api/grading/gradebook${suffix}`, this.token || undefined);
  }

  async getIncidents(query = "") {
    const suffix = query ? `?${query}` : "";
    return apiFetch(`/api/admin/incidents${suffix}`, this.token || undefined);
  }

  async getMyPerformance() {
    return apiFetch("/api/grading/my-performance", this.token || undefined);
  }

  async parseQuestionText(text: string) {
    return apiFetch("/api/imports/questions/parse-text", this.token || undefined, {
      method: "POST",
      body: JSON.stringify({ text }),
    });
  }

  async parseQuestionCsv(text: string) {
    return apiFetch("/api/imports/questions/parse-csv", this.token || undefined, {
      method: "POST",
      body: JSON.stringify({ text }),
    });
  }

  async publishQuestions(items: any[]) {
    return apiFetch("/api/imports/questions/publish", this.token || undefined, {
      method: "POST",
      body: JSON.stringify({ items }),
    });
  }

  async parseUsersCsv(text: string) {
    return apiFetch("/api/imports/users/parse-csv", this.token || undefined, {
      method: "POST",
      body: JSON.stringify({ text }),
    });
  }

  async bulkCreateUsers(users: any[], default_password = "changeme123", skip_existing = true) {
    return apiFetch("/api/imports/users/bulk-create", this.token || undefined, {
      method: "POST",
      body: JSON.stringify({ users, default_password, skip_existing }),
    });
  }

  async parseEnrollment(rows: any[]) {
    return apiFetch("/api/imports/enrollment/parse", this.token || undefined, {
      method: "POST",
      body: JSON.stringify({ rows }),
    });
  }

  async publishEnrollment(rows: any[]) {
    return apiFetch("/api/imports/enrollment/publish", this.token || undefined, {
      method: "POST",
      body: JSON.stringify({ rows }),
    });
  }
}

export { apiBase };