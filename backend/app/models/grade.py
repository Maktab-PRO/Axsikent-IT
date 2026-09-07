from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime, timezone

from app.db import Base

class Grade(Base):
**tablename** = "grades"

```
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

group_id = Column(
    Integer,
    ForeignKey("groups.id"),
    nullable=False
)

teacher_id = Column(
    Integer,
    ForeignKey("teachers.id"),
    nullable=False
)

title = Column(
    String(150),
    nullable=False
)

score = Column(
    Float,
    nullable=False
)

max_score = Column(
    Float,
    default=100,
    nullable=False
)

comment = Column(
    String(500),
    nullable=True
)

created_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    nullable=False
)
```
