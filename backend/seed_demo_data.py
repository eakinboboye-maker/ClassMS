from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.course import Course, Section, Enrollment
from app.models.question import Question, QuestionOption, QuestionGap, AcceptedAnswer
from app.models.assessment import Assessment, AssessmentWindow, AssessmentItem, AssessmentCandidate
from app.models.security_exam import ApprovedConfigKey


def get_or_create_user(db, email: str, full_name: str, password: str, role: str, matric_no: str | None = None):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hash_password(password),
        role=role,
        matric_no=matric_no,
    )
    db.add(user)
    db.flush()
    return user


def seed_demo():
    db = SessionLocal()
    try:
        admin = get_or_create_user(db, "admin@example.com", "System Admin", "admin123", "admin")
        instructor = get_or_create_user(db, "instructor@example.com", "Demo Instructor", "instructor123", "instructor")
        student1 = get_or_create_user(db, "student1@example.com", "Student One", "student123", "student", "MAT001")
        student2 = get_or_create_user(db, "student2@example.com", "Student Two", "student123", "student", "MAT002")

        course = db.query(Course).filter(Course.code == "EEE355").first()
        if not course:
            course = Course(code="EEE355", title="Computation Structures", description="Demo seeded course")
            db.add(course)
            db.flush()

        section = db.query(Section).filter(Section.course_id == course.id, Section.name == "A").first()
        if not section:
            section = Section(course_id=course.id, name="A", term="2026/2027", instructor_id=instructor.id)
            db.add(section)
            db.flush()

        for student in [student1, student2]:
            existing = db.query(Enrollment).filter(
                Enrollment.user_id == student.id,
                Enrollment.section_id == section.id,
            ).first()
            if not existing:
                db.add(Enrollment(user_id=student.id, section_id=section.id, status="active"))

        mcq = db.query(Question).filter(Question.prompt_md == "Which quantity is a vector?").first()
        if not mcq:
            mcq = Question(
                type="mcq_single",
                prompt_md="Which quantity is a vector?",
                marks=1,
                difficulty="easy",
                topics_json='["vectors"]',
                version=1,
            )
            db.add(mcq)
            db.flush()
            db.add_all([
                QuestionOption(question_id=mcq.id, option_key="a", text="mass", is_correct=False),
                QuestionOption(question_id=mcq.id, option_key="b", text="velocity", is_correct=True),
                QuestionOption(question_id=mcq.id, option_key="c", text="temperature", is_correct=False),
            ])

        fill_gap = db.query(Question).filter(Question.prompt_md == "Energy cannot be [GAP1] or [GAP2].").first()
        if not fill_gap:
            fill_gap = Question(
                type="fill_gap",
                prompt_md="Energy cannot be [GAP1] or [GAP2].",
                marks=2,
                difficulty="easy",
                topics_json='["thermodynamics"]',
                version=1,
            )
            db.add(fill_gap)
            db.flush()

            gap1 = QuestionGap(question_id=fill_gap.id, gap_key="GAP1", marks=1, position=1)
            gap2 = QuestionGap(question_id=fill_gap.id, gap_key="GAP2", marks=1, position=2)
            db.add(gap1)
            db.add(gap2)
            db.flush()

            db.add_all([
                AcceptedAnswer(gap_id=gap1.id, text="created", normalized_text="created"),
                AcceptedAnswer(gap_id=gap2.id, text="destroyed", normalized_text="destroyed"),
            ])

        essay = db.query(Question).filter(Question.prompt_md == "Explain the difference between Moore and Mealy machines.").first()
        if not essay:
            essay = Question(
                type="essay",
                prompt_md="Explain the difference between Moore and Mealy machines.",
                marks=10,
                difficulty="medium",
                topics_json='["fsm"]',
                answer_key_json='{"canonical_answer":"Moore depends only on state; Mealy depends on state and input.","rubric":[{"criterion":"Defines Moore machine","points":3},{"criterion":"Defines Mealy machine","points":3},{"criterion":"Explains implication","points":4}]}',
                grading_mode="ai_human_loop",
                version=1,
            )
            db.add(essay)
            db.flush()

        mock_exam = db.query(Assessment).filter(Assessment.title == "Demo Mock Exam").first()
        if not mock_exam:
            mock_exam = Assessment(
                title="Demo Mock Exam",
                type="mock",
                section_id=section.id,
                duration_minutes=45,
                shuffle_questions=False,
                status="published",
                requires_seb=False,
                allow_resume=True,
                instructions_md="Answer all questions.",
            )
            db.add(mock_exam)
            db.flush()

            db.add(AssessmentWindow(
                assessment_id=mock_exam.id,
                open_time=datetime.utcnow(),
                close_time=datetime.utcnow() + timedelta(days=14),
            ))

            db.add_all([
                AssessmentItem(assessment_id=mock_exam.id, question_id=mcq.id, order_index=1, frozen_question_version=1),
                AssessmentItem(assessment_id=mock_exam.id, question_id=fill_gap.id, order_index=2, frozen_question_version=1),
                AssessmentItem(assessment_id=mock_exam.id, question_id=essay.id, order_index=3, frozen_question_version=1),
            ])

        formal_exam = db.query(Assessment).filter(Assessment.title == "Demo Formal Exam").first()
        if not formal_exam:
            formal_exam = Assessment(
                title="Demo Formal Exam",
                type="formal",
                section_id=section.id,
                duration_minutes=30,
                shuffle_questions=False,
                status="published",
                requires_seb=True,
                allow_resume=True,
                instructions_md="Formal exam. Objective and fill-gap only.",
            )
            db.add(formal_exam)
            db.flush()

            db.add(AssessmentWindow(
                assessment_id=formal_exam.id,
                open_time=datetime.utcnow(),
                close_time=datetime.utcnow() + timedelta(days=7),
            ))

            db.add_all([
                AssessmentItem(assessment_id=formal_exam.id, question_id=mcq.id, order_index=1, frozen_question_version=1),
                AssessmentItem(assessment_id=formal_exam.id, question_id=fill_gap.id, order_index=2, frozen_question_version=1),
            ])

            db.add_all([
                AssessmentCandidate(assessment_id=formal_exam.id, user_id=student1.id),
                AssessmentCandidate(assessment_id=formal_exam.id, user_id=student2.id),
            ])

            db.add(ApprovedConfigKey(assessment_id=formal_exam.id, key_hash="demo-valid-config-key"))

        db.commit()
        print("Demo seed data loaded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo()
