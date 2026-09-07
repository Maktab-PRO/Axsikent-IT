from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from app.db import Base

class Group(Base):
**tablename** = "groups"

```
id = Column(
    Integer,
    primary_key=True,
    index=True
)

name = Column(
    String(100),
    nullable=False
)

course_id = Column(
    Integer,
    ForeignKey("courses.id"),
    nullable=False
)

level_id = Column(
    Integer,
    ForeignKey("levels.id"),
    nullable=True
)

teacher_id = Column(
    Integer,
    ForeignKey("teachers.id"),
    nullable=False
)

room = Column(
    String(50),
    nullable=True
)

start_date = Column(
    Date,
    nullable=True
)

capacity = Column(
    Integer,
    default=15,
    nullable=False
)

status = Column(
    String(30),
    default="active",
    nullable=False
)

is_active = Column(
    Boolean,
    default=True,
    nullable=False
)
```
