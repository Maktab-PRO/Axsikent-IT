from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from app.db import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)

    module_id = Column(
        Integer,
        ForeignKey("course_modules.id"),
        nullable=False
    )

    title = Column(String(200), nullable=False)

    content = Column(Text, nullable=True)

    video_url = Column(String(500), nullable=True)

    sort_order = Column(Integer, default=0, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
