from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone

from app.db import Base

class GroupStudent(Base):
**tablename** = "group_students"

```
id = Column(
    Integer,
    primary_key=True,
    index=True
)

group_id = Column(
    Integer,
    ForeignKey("groups.id"),
    nullable=False
)

student_id = Column(
    Integer,
    ForeignKey("students.id"),
    nullable=False
)

joined_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    nullable=False
)

status = Column(
    String(30),
    default="active",
    nullable=False
)
```
