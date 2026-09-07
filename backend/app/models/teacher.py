from sqlalchemy import Column, Integer, String, Boolean
from app.db import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(
        String(150),
        nullable=False
    )

    phone = Column(
        String(30),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    subject = Column(
        String(100),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )
