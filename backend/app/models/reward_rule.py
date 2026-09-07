from sqlalchemy import Column, Integer, String, Boolean, Text
from app.db import Base


class RewardRule(Base):
    __tablename__ = "reward_rules"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(150),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    action_type = Column(
        String(50),
        nullable=False
    )

    reward_type = Column(
        String(20),
        nullable=False
    )

    reward_amount = Column(
        Integer,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )
