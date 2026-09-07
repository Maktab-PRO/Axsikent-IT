from sqlalchemy import Column, Integer, String, Boolean
from app.db import Base

class Category(Base):
**tablename** = "categories"

```
id = Column(
    Integer,
    primary_key=True,
    index=True
)

name = Column(
    String(100),
    nullable=False,
    unique=True
)

icon = Column(
    String(20),
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
