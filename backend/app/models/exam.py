from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime, timezone

from app.db import Base


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=True)
    location = Column(String(200), nullable=True)
    capacity = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ExamRegistration(Base):
    __tablename__ = "exam_registrations"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, nullable=False)
    student_id = Column(Integer, nullable=False)
    status = Column(String(30), default="registered", nullable=False)
    registered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
