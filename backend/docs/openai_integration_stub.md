# OpenAI Essay Grading Integration Stub

This document describes the intended implementation for `app/services/ai_grader.py` when using a real provider.

## Expected flow

1. Build a structured grading prompt with:
   - question prompt
   - canonical answer
   - rubric
   - student answer
   - instructions requiring JSON output

2. Send it to the configured model.

3. Require structured JSON output in the form:

```json
{
  "proposed_score": 7.5,
  "confidence": 0.82,
  "criteria": [
    {
      "criterion": "Defines Moore machine",
      "points_awarded": 3,
      "max_points": 3,
      "rationale": "Correctly states output depends only on state.",
      "evidence": ["Moore machines depend only on the current state."]
    }
  ],
  "flags": ["needs_review"],
  "rationale": {
    "summary": "Strong answer with minor omissions."
  }
}

4. Validate that payload server-side before storing.
