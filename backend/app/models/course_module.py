from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey

from app.db import Base


class CourseModule(Base):
    __tablename__ = "course_modules"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    sort_order = Column(
        Integer,
        default=0,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )
