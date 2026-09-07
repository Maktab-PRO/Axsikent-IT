from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime, timezone

from app.db import Base


class Event(Base):
    __tablename__ = "events"

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

    event_type = Column(
        String(30),
        nullable=False
    )

    start_at = Column(
        DateTime,
        nullable=False
    )

    end_at = Column(
        DateTime,
        nullable=True
    )

    location = Column(
        String(200),
        nullable=True
    )

    capacity = Column(
        Integer,
        nullable=True
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


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    event_id = Column(
        Integer,
        nullable=False
    )

    student_id = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(30),
        default="registered",
        nullable=False
    )

    registered_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
