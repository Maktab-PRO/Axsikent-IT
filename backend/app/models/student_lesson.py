from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from datetime import datetime

from app.db import Base


class StudentLesson(Base):
    __tablename__ = "student_lessons"

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

    completed = Column(
        Boolean,
        default=False,
        nullable=False
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )
