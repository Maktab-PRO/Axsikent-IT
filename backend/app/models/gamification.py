from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime, timezone

from app.db import Base

class StudentGamification(Base):
**tablename** = "student_gamification"

```
id = Column(
    Integer,
    primary_key=True,
    index=True
)

student_id = Column(
    Integer,
    ForeignKey("students.id"),
    nullable=False,
    unique=True
)

xp = Column(
    Integer,
    default=0,
    nullable=False
)

level = Column(
    Integer,
    default=1,
    nullable=False
)

coins = Column(
    Integer,
    default=0,
    nullable=False
)

crystals = Column(
    Integer,
    default=0,
    nullable=False
)

streak_days = Column(
    Integer,
    default=0,
    nullable=False
)

last_activity_at = Column(
    DateTime,
    nullable=True
)

updated_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    nullable=False
)
```
