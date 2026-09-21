from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime, timezone

from app.db import Base


class AITelegramSubmission(Base):
    __tablename__ = "ai_telegram_submissions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    telegram_chat_id = Column(String(64), nullable=False, index=True)
    task = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    score = Column(Integer, nullable=True)
    passed = Column(String(10), nullable=True)
    mistakes = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    status = Column(String(30), default="checked", nullable=False)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    checked_at = Column(DateTime, nullable=True)
