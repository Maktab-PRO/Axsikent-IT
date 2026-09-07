from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.db import Base

class Level(Base):
**tablename** = "levels"

```
id = Column(
    Integer,
    primary_key=True,
    index=True
)

course_id = Column(
    Integer,
    ForeignKey("courses.id"),
    nullable=False
)

name = Column(
    String(100),
    nullable=False
)

sort_order = Column(
    Integer,
    default=0,
    nullable=False
)

is_active = Column(
    Boolean,
    default=True,
    nullable=False
)
```
