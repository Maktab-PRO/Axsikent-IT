from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey
from app.db import Base

class Schedule(Base):
**tablename** = "schedules"

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

weekday = Column(
    Integer,
    nullable=False
)

start_time = Column(
    Time,
    nullable=False
)

end_time = Column(
    Time,
    nullable=False
)

room = Column(
    String(50),
    nullable=True
)

is_active = Column(
    Boolean,
    default=True,
    nullable=False
)
```
