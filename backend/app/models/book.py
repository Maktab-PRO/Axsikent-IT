from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime, timezone

from app.db import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    image_url = Column(
        String(500),
        nullable=True
    )

    price = Column(
        Integer,
        default=0,
        nullable=False
    )

    coin_price = Column(
        Integer,
        default=0,
        nullable=False
    )

    stock = Column(
        Integer,
        default=0,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class BookOrder(Base):
    __tablename__ = "book_orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        Integer,
        nullable=False
    )

    book_id = Column(
        Integer,
        nullable=False
    )

    quantity = Column(
        Integer,
        default=1,
        nullable=False
    )

    price_paid = Column(
        Integer,
        default=0,
        nullable=False
    )

    coin_spent = Column(
        Integer,
        default=0,
        nullable=False
    )

    status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
