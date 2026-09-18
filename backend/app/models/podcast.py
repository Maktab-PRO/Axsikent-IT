from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime, timezone

from app.db import Base


class Podcast(Base):
    __tablename__ = "podcasts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    audio_url = Column(String(500), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
