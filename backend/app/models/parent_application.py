from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.db import Base


class ParentApplication(Base):
    __tablename__ = "parent_applications"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(30), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    comment = Column(String(2000), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime(timezone=True), nullable=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=True)
