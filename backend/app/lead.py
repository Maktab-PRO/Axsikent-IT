from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone

from app.db import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    phone = Column(
        String(30),
        nullable=False
    )

    age = Column(
        Integer,
        nullable=True
    )

    interested_course = Column(
        String(200),
        nullable=True
    )

    preferred_time = Column(
        String(100),
        nullable=True
    )

    previous_it_course = Column(
        String(100),
        nullable=True
    )

    comment = Column(
        Text,
        nullable=True
    )

    source = Column(
        String(50),
        default="website",
        nullable=False
    )

    status = Column(
        String(30),
        default="new",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
