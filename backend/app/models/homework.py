from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime, timezone

from app.db import Base


class Homework(Base):
    __tablename__ = "homeworks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    group_id = Column(
        Integer,
        ForeignKey("groups.id"),
        nullable=False
    )

    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id"),
        nullable=False
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    deadline = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    status = Column(
        String(20),
        default="active",
        nullable=False
    )


class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    homework_id = Column(
        Integer,
        ForeignKey("homeworks.id"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    answer = Column(
        Text,
        nullable=True
    )

    file_url = Column(
        String(500),
        nullable=True
    )

    status = Column(
        String(30),
        default="submitted",
        nullable=False
    )

    score = Column(
        Integer,
        nullable=True
    )

    teacher_comment = Column(
        Text,
        nullable=True
    )

    submitted_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    checked_at = Column(
        DateTime,
        nullable=True
    )
