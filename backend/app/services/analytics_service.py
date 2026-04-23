from sqlalchemy.orm import Session

from app.models.course import Section
from app.models.assessment import Assessment, Attempt
from app.models.grading import Score


def get_section_analytics(db: Session, section_id: int) -> list[dict]:
    assessments = db.query(Assessment).filter(Assessment.section_id == section_id).all()
    rows = []

    for assessment in assessments:
        attempts = db.query(Attempt).filter(Attempt.assessment_id == assessment.id).all()
        submitted = [a for a in attempts if a.status == "submitted"]

        total_awarded = 0.0
        total_max = 0.0
        for attempt in attempts:
            scores = db.query(Score).filter(Score.attempt_id == attempt.id).all()
            total_awarded += sum(s.awarded_marks for s in scores)
            total_max += sum(s.max_marks for s in scores)

        attempts_count = len(attempts)
        avg_awarded = total_awarded / attempts_count if attempts_count else 0.0
        avg_max = total_max / attempts_count if attempts_count else 0.0

        rows.append(
            {
                "assessment_id": assessment.id,
                "assessment_title": assessment.title,
                "attempts_count": attempts_count,
                "submitted_count": len(submitted),
                "avg_awarded": avg_awarded,
                "avg_max": avg_max,
            }
        )
    return rows


def get_course_analytics(db: Session, course_id: int) -> list[dict]:
    sections = db.query(Section).filter(Section.course_id == course_id).all()
    rows = []

    for section in sections:
        assessments = db.query(Assessment).filter(Assessment.section_id == section.id).all()
        attempts_count = 0
        submitted_count = 0
        total_awarded = 0.0
        total_max = 0.0

        for assessment in assessments:
            attempts = db.query(Attempt).filter(Attempt.assessment_id == assessment.id).all()
            attempts_count += len(attempts)
            submitted_count += sum(1 for a in attempts if a.status == "submitted")

            for attempt in attempts:
                scores = db.query(Score).filter(Score.attempt_id == attempt.id).all()
                total_awarded += sum(s.awarded_marks for s in scores)
                total_max += sum(s.max_marks for s in scores)

        avg_awarded = total_awarded / attempts_count if attempts_count else 0.0
        avg_max = total_max / attempts_count if attempts_count else 0.0

        rows.append(
            {
                "section_id": section.id,
                "course_id": course_id,
                "assessments_count": len(assessments),
                "submitted_count": submitted_count,
                "avg_awarded": avg_awarded,
                "avg_max": avg_max,
            }
        )

    return rows
