from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.db import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )

    name = Column(
        String(150),
        nullable=False
    )

    description = Column(
        String(1000),
        nullable=True
    )

    age_min = Column(
        Integer,
        nullable=True
    )

    age_max = Column(
        Integer,
        nullable=True
    )

    lesson_minutes = Column(
        Integer,
        nullable=True
    )

    lessons_per_week = Column(
        Integer,
        nullable=True
    )

    price_min = Column(
        Integer,
        nullable=True
    )

    price_max = Column(
        Integer,
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
