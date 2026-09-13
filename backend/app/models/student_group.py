from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from datetime import datetime

from app.db import Base


class StudentGroup(Base):
    __tablename__ = "student_groups"

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

    group_id = Column(
        Integer,
        ForeignKey("groups.id"),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    joined_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
