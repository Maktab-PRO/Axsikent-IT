from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from app.db import Base


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False,
        unique=True
    )

    description = Column(
        Text,
        nullable=True
    )

    icon = Column(
        String(20),
        nullable=True
    )

    xp_reward = Column(
        Integer,
        default=0,
        nullable=False
    )

    coin_reward = Column(
        Integer,
        default=0,
        nullable=False
    )

    crystal_reward = Column(
        Integer,
        default=0,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )


class StudentAchievement(Base):
    __tablename__ = "student_achievements"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    achievement_id = Column(
        Integer,
        ForeignKey("achievements.id"),
        nullable=False
    )

    earned_at = Column(
        String(50),
        nullable=False
    )
