from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone

from app.db import Base


class AIHomeworkState(Base):
    __tablename__ = "ai_homework_states"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, unique=True, index=True)
    consecutive_failures = Column(Integer, default=0, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    blocked_at = Column(DateTime, nullable=True)
    unlocked_at = Column(DateTime, nullable=True)
