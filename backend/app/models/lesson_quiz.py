from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from app.db import Base


class LessonQuiz(Base):
    __tablename__ = "lesson_quizzes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id"),
        nullable=False
    )

    question = Column(
        Text,
        nullable=False
    )

    option_a = Column(
        String(500),
        nullable=False
    )

    option_b = Column(
        String(500),
        nullable=False
    )

    option_c = Column(
        String(500),
        nullable=False
    )

    option_d = Column(
        String(500),
        nullable=False
    )

    correct_answer = Column(
        String(1),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
  )
