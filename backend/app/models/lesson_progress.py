from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.db import Base


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

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

    completed_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
