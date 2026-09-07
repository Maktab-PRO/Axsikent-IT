from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone

from app.db import Base

class ShopProduct(Base):
**tablename** = "shop_products"

```
id = Column(
    Integer,
    primary_key=True,
    index=True
)

name = Column(
    String(150),
    nullable=False
)

description = Column(
    Text,
    nullable=True
)

image_url = Column(
    String(500),
    nullable=True
)

coin_price = Column(
    Integer,
    default=0,
    nullable=False
)

crystal_price = Column(
    Integer,
    default=0,
    nullable=False
)

stock = Column(
    Integer,
    default=0,
    nullable=False
)

is_active = Column(
    Boolean,
    default=True,
    nullable=False
)

created_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    nullable=False
)
```

class ShopOrder(Base):
**tablename** = "shop_orders"

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

product_id = Column(
    Integer,
    ForeignKey("shop_products.id"),
    nullable=False
)

quantity = Column(
    Integer,
    default=1,
    nullable=False
)

coin_spent = Column(
    Integer,
    default=0,
    nullable=False
)

crystal_spent = Column(
    Integer,
    default=0,
    nullable=False
)

status = Column(
    String(30),
    default="pending",
    nullable=False
)

created_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    nullable=False
)

completed_at = Column(
    DateTime,
    nullable=True
)
```
