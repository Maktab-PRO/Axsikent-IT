from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.db import Base

class Course(Base):
**tablename** = "courses"

```
id = Column(
    Integer,
    primary_key=True,
    index=True
)

category_id = Column(
    Integer,
    ForeignKey("categories.id"),
    nullable=False
)

name = Column(
    String(150),
    nullable=False
)

description = Column(
    String(500),
    nullable=True
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
