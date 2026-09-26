from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
from app.db import Base


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    __table_args__ = (
        UniqueConstraint("student_id", "lesson_id", name="uq_lesson_progress_student_lesson"),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id"),
        nullable=False
    )

    is_completed = Column(
        Boolean,
        default=False,
        nullable=False
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False
    )

    quiz_passed = Column(
        Boolean,
        default=False,
        nullable=False
    )

    quiz_failures = Column(
        Integer,
        default=0,
        nullable=False
    )

    quiz_blocked = Column(
        Boolean,
        default=False,
        nullable=False
    )

    homework_passed = Column(
        Boolean,
        default=False,
        nullable=False
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
