from sqlalchemy.orm import Session

from app.models.assessment import Assessment, Attempt
from app.models.course import Section
from app.models.grading import Score, GradePublication


def get_gradebook_rows(
    db: Session,
    course_id: int | None = None,
    section_id: int | None = None,
    assessment_id: int | None = None,
    published_only: bool = False,
) -> list[dict]:
    query = db.query(Attempt, Assessment, Section).join(
        Assessment, Assessment.id == Attempt.assessment_id
    ).join(
        Section, Section.id == Assessment.section_id
    )

    if course_id is not None:
        query = query.filter(Section.course_id == course_id)
    if section_id is not None:
        query = query.filter(Assessment.section_id == section_id)
    if assessment_id is not None:
        query = query.filter(Assessment.id == assessment_id)

    rows = []
    for attempt, assessment, section in query.all():
        publication = (
            db.query(GradePublication)
            .filter(GradePublication.assessment_id == assessment.id)
            .first()
        )
        if published_only and not publication:
            continue

        scores = db.query(Score).filter(Score.attempt_id == attempt.id).all()
        rows.append(
            {
                "user_id": attempt.user_id,
                "attempt_id": attempt.id,
                "total_awarded": sum(s.awarded_marks for s in scores),
                "total_max": sum(s.max_marks for s in scores),
                "published": publication is not None,
                "assessment_id": assessment.id,
                "section_id": assessment.section_id,
                "course_id": section.course_id,
            }
        )
    return rows
