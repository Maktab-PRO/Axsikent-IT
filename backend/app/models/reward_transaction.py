from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime, timezone

from app.db import Base

class RewardTransaction(Base):
**tablename** = "reward_transactions"

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

reward_type = Column(
    String(20),
    nullable=False
)

amount = Column(
    Integer,
    nullable=False
)

reason = Column(
    String(255),
    nullable=False
)

reference_type = Column(
    String(50),
    nullable=True
)

reference_id = Column(
    Integer,
    nullable=True
)

note = Column(
    Text,
    nullable=True
)

created_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    nullable=False
)
```
