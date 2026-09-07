from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone

from app.db import Base


class Content(Base):
    __tablename__ = "contents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    content_type = Column(
        String(30),
        nullable=False
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=True
    )

    level_id = Column(
        Integer,
        ForeignKey("levels.id"),
        nullable=True
    )

    thumbnail_url = Column(
        String(500),
        nullable=True
    )

    content_url = Column(
        String(500),
        nullable=True
    )

    duration_minutes = Column(
        Integer,
        nullable=True
    )

    sort_order = Column(
        Integer,
        default=0,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class ContentProgress(Base):
    __tablename__ = "content_progress"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    content_id = Column(
        Integer,
        ForeignKey("contents.id"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    progress_percent = Column(
        Integer,
        default=0,
        nullable=False
    )

    last_position_seconds = Column(
        Integer,
        default=0,
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

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
