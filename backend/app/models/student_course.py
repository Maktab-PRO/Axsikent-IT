from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from datetime import datetime

from app.db import Base


class StudentCourse(Base):
    __tablename__ = "student_courses"

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

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    progress = Column(
        Integer,
        default=0,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    enrolled_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
