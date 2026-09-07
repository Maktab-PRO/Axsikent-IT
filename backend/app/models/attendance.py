from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from datetime import datetime, timezone

from app.db import Base

class Attendance(Base):
**tablename** = "attendance"

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

date = Column(
    Date,
    nullable=False
)

status = Column(
    String(20),
    nullable=False
)

note = Column(
    String(255),
    nullable=True
)

created_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    nullable=False
)
```
