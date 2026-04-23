from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.course import Course, Section, Enrollment
from app.models.question import Question, QuestionOption
from app.models.assessment import Assessment, AssessmentWindow, AssessmentItem


def seed():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin = User(
                email="admin@example.com",
                full_name="System Admin",
                hashed_password=hash_password("admin123"),
                role="admin",
            )
            db.add(admin)
            db.flush()

        student = db.query(User).filter(User.email == "student@example.com").first()
        if not student:
            student = User(
                email="student@example.com",
                full_name="Student Demo",
                hashed_password=hash_password("student123"),
                role="student",
                matric_no="DEMO001",
            )
            db.add(student)
            db.flush()

        course = db.query(Course).filter(Course.code == "EEE355").first()
        if not course:
            course = Course(
                code="EEE355",
                title="Computation Structures",
                description="Seed course",
            )
            db.add(course)
            db.flush()

        section = db.query(Section).filter(Section.course_id == course.id, Section.name == "A").first()
        if not section:
            section = Section(
                course_id=course.id,
                name="A",
                term="2026/2027",
                instructor_id=admin.id,
            )
            db.add(section)
            db.flush()

        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == student.id,
            Enrollment.section_id == section.id,
        ).first()
        if not enrollment:
            db.add(Enrollment(user_id=student.id, section_id=section.id, status="active"))

        question = db.query(Question).filter(Question.prompt_md == "Which quantity is a vector?").first()
        if not question:
            question = Question(
                type="mcq_single",
                prompt_md="Which quantity is a vector?",
                marks=1,
                difficulty="easy",
                topics_json='["vectors"]',
                version=1,
            )
            db.add(question)
            db.flush()

            db.add_all(
                [
                    QuestionOption(question_id=question.id, option_key="a", text="mass", is_correct=False),
                    QuestionOption(question_id=question.id, option_key="b", text="velocity", is_correct=True),
                    QuestionOption(question_id=question.id, option_key="c", text="temperature", is_correct=False),
                ]
            )

        assessment = db.query(Assessment).filter(Assessment.title == "Seed Mock Exam").first()
        if not assessment:
            assessment = Assessment(
                title="Seed Mock Exam",
                type="mock",
                section_id=section.id,
                duration_minutes=30,
                shuffle_questions=False,
                status="published",
                requires_seb=False,
                allow_resume=True,
            )
            db.add(assessment)
            db.flush()

            db.add(
                AssessmentWindow(
                    assessment_id=assessment.id,
                    open_time=datetime.utcnow(),
                    close_time=datetime.utcnow() + timedelta(days=30),
                )
            )
            db.add(
                AssessmentItem(
                    assessment_id=assessment.id,
                    question_id=question.id,
                    order_index=1,
                    frozen_question_version=question.version,
                )
            )

        db.commit()
        print("Seed data loaded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
