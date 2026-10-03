from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.db import Base


class SmsVerification(Base):
    __tablename__ = "sms_verifications"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(30), nullable=False, index=True)
    purpose = Column(String(40), nullable=False, index=True)
    code_hash = Column(String(64), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    attempts = Column(Integer, nullable=False, default=0)
    last_sent_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
