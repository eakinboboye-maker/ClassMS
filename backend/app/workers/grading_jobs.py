import argparse
import json
from datetime import datetime

from app.core.database import SessionLocal
from app.models.response import Response
from app.models.question import Question
from app.models.grading import AIGradingJob, AIGradingResult, GradingReview
from app.services.ai_grader import grade_essay_response
from app.services.expiry_service import auto_submit_expired_attempts


def run_ai_grading_job(job_id: int):
    db = SessionLocal()
    try:
        job = db.get(AIGradingJob, job_id)
        if not job:
            print(f"Job {job_id} not found")
            return

        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()

        response = db.get(Response, job.response_id)
        if not response:
            job.status = "failed"
            db.commit()
            return

        question = db.get(Question, response.question_id)
        if not question:
            job.status = "failed"
            db.commit()
            return

        response_payload = json.loads(response.response_json)
        student_answer = response_payload.get("answer_text", "")

        answer_key = json.loads(question.answer_key_json) if question.answer_key_json else {}
        rubric = answer_key.get("rubric", [])

        result = grade_essay_response(
            question_prompt=question.prompt_md,
            answer_key=answer_key,
            rubric=rubric,
            student_answer=student_answer,
        )

        db.add(
            AIGradingResult(
                job_id=job.id,
                proposed_score=result["proposed_score"],
                confidence=result["confidence"],
                criteria_json=json.dumps(result["criteria"]),
                flags_json=json.dumps(result["flags"]),
                rationale_json=json.dumps(result["rationale"]),
            )
        )

        existing_review = db.query(GradingReview).filter(GradingReview.response_id == response.id).first()
        if not existing_review:
            db.add(GradingReview(response_id=response.id, status="pending"))

        job.status = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()
        print(f"Completed job {job_id}")
    finally:
        db.close()


def run_pending_jobs(limit: int = 20):
    db = SessionLocal()
    try:
        jobs = (
            db.query(AIGradingJob)
            .filter(AIGradingJob.status == "queued")
            .order_by(AIGradingJob.queued_at.asc())
            .limit(limit)
            .all()
        )
        job_ids = [job.id for job in jobs]
    finally:
        db.close()

    for job_id in job_ids:
        run_ai_grading_job(job_id)


def run_expiry_check(assessment_type: str | None = None):
    db = SessionLocal()
    try:
        submitted = auto_submit_expired_attempts(db, assessment_type=assessment_type)
        db.commit()
        print(f"Auto-submitted attempts: {submitted}")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="AI grading and expiry worker")
    parser.add_argument("--job-id", type=int, help="Run a single grading job by ID")
    parser.add_argument("--pending", action="store_true", help="Run pending queued grading jobs")
    parser.add_argument("--limit", type=int, default=20, help="Limit for pending grading jobs")
    parser.add_argument("--expiry-check", action="store_true", help="Run attempt expiry auto-submit check")
    parser.add_argument("--assessment-type", type=str, help="Optional assessment type filter for expiry check")
    args = parser.parse_args()

    if args.job_id:
        run_ai_grading_job(args.job_id)
    elif args.pending:
        run_pending_jobs(limit=args.limit)
    elif args.expiry_check:
        run_expiry_check(assessment_type=args.assessment_type)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
