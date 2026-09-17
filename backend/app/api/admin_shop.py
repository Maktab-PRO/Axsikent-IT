from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import require_admin
from app.models.admin import Admin
from app.models.shop import ShopProduct, ShopOrder
from app.models.reward_rule import RewardRule
from app.models.reward_transaction import RewardTransaction


router = APIRouter(
    prefix="/admin/shop",
    tags=["Admin Shop"]
)


# =========================================================
# SCHEMAS
# =========================================================

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str = ""
    image_url: str = ""
    coin_price: int = Field(default=0, ge=0)
    crystal_price: int = Field(default=0, ge=0)
    stock: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    image_url: str | None = None
    coin_price: int | None = Field(default=None, ge=0)
    crystal_price: int | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., min_length=1, max_length=30)


class RuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str = ""
    action_type: str = Field(..., min_length=1, max_length=50)
    reward_type: str = Field(..., min_length=1, max_length=20)
    reward_amount: int = Field(..., ge=0)


class RuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    action_type: str | None = Field(default=None, max_length=50)
    reward_type: str | None = Field(default=None, max_length=20)
    reward_amount: int | None = Field(default=None, ge=0)


# =========================================================
# HELPERS
# =========================================================

def product_to_dict(product: ShopProduct):
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "image_url": product.image_url,
        "coin_price": product.coin_price,
        "crystal_price": product.crystal_price,
        "stock": product.stock,
        "is_active": product.is_active,
        "created_at": product.created_at,
    }


def order_to_dict(order: ShopOrder, db: Session):
    product = db.query(ShopProduct).filter(
        ShopProduct.id == order.product_id
    ).first()

    return {
        "id": order.id,
        "student_id": order.student_id,
        "product_id": order.product_id,
        "product_name": product.name if product else None,
        "quantity": order.quantity,
        "coin_spent": order.coin_spent,
        "crystal_spent": order.crystal_spent,
        "status": order.status,
        "created_at": order.created_at,
        "completed_at": order.completed_at,
    }


def rule_to_dict(rule: RewardRule):
    return {
        "id": rule.id,
        "name": rule.name,
        "description": rule.description,
        "action_type": rule.action_type,
        "reward_type": rule.reward_type,
        "reward_amount": rule.reward_amount,
        "is_active": rule.is_active,
    }


def transaction_to_dict(transaction: RewardTransaction):
    return {
        "id": transaction.id,
        "student_id": transaction.student_id,
        "reward_type": transaction.reward_type,
        "amount": transaction.amount,
        "reason": transaction.reason,
        "reference_type": transaction.reference_type,
        "reference_id": transaction.reference_id,
        "note": transaction.note,
        "created_at": transaction.created_at,
    }


# =========================================================
# DASHBOARD STATISTICS
# =========================================================

@router.get("/stats/summary")
def get_shop_stats(
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    products_total = db.query(ShopProduct).count()

    products_active = db.query(ShopProduct).filter(
        ShopProduct.is_active == True
    ).count()

    products_inactive = db.query(ShopProduct).filter(
        ShopProduct.is_active == False
    ).count()

    orders_total = db.query(ShopOrder).count()

    orders_pending = db.query(ShopOrder).filter(
        ShopOrder.status == "pending"
    ).count()

    orders_completed = db.query(ShopOrder).filter(
        ShopOrder.status == "completed"
    ).count()

    orders_cancelled = db.query(ShopOrder).filter(
        ShopOrder.status == "cancelled"
    ).count()

    rules_total = db.query(RewardRule).count()

    rules_active = db.query(RewardRule).filter(
        RewardRule.is_active == True
    ).count()

    transactions_total = db.query(RewardTransaction).count()

    return {
        "products": {
            "total": products_total,
            "active": products_active,
            "inactive": products_inactive,
        },
        "orders": {
            "total": orders_total,
            "pending": orders_pending,
            "completed": orders_completed,
            "cancelled": orders_cancelled,
        },
        "reward_rules": {
            "total": rules_total,
            "active": rules_active,
        },
        "transactions": {
            "total": transactions_total,
        },
    }


# =========================================================
# PRODUCTS — MUKOFOTLAR
# =========================================================

@router.get("/products")
def get_products(
    active_only: bool = False,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    query = db.query(ShopProduct)

    if active_only:
        query = query.filter(
            ShopProduct.is_active == True
        )

    products = query.order_by(
        ShopProduct.id.asc()
    ).all()

    return [
        product_to_dict(product)
        for product in products
    ]


@router.get("/products/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    product = db.query(ShopProduct).filter(
        ShopProduct.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Mukofot topilmadi"
        )

    return product_to_dict(product)


@router.post("/products")
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    product = ShopProduct(
        name=data.name,
        description=data.description,
        image_url=data.image_url,
        coin_price=data.coin_price,
        crystal_price=data.crystal_price,
        stock=data.stock,
        is_active=True,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return {
        "success": True,
        "message": "Mukofot muvaffaqiyatli qo'shildi",
        "product": product_to_dict(product),
    }


@router.put("/products/{product_id}")
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    product = db.query(ShopProduct).filter(
        ShopProduct.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Mukofot topilmadi"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return {
        "success": True,
        "message": "Mukofot yangilandi",
        "product": product_to_dict(product),
    }


@router.put("/products/{product_id}/activate")
def activate_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    product = db.query(ShopProduct).filter(
        ShopProduct.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Mukofot topilmadi"
        )

    product.is_active = True

    db.commit()
    db.refresh(product)

    return {
        "success": True,
        "message": "Mukofot faollashtirildi",
        "product": product_to_dict(product),
    }


@router.put("/products/{product_id}/deactivate")
def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    product = db.query(ShopProduct).filter(
        ShopProduct.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Mukofot topilmadi"
        )

    product.is_active = False

    db.commit()
    db.refresh(product)

    return {
        "success": True,
        "message": "Mukofot deaktiv qilindi",
        "product": product_to_dict(product),
    }


@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    product = db.query(ShopProduct).filter(
        ShopProduct.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Mukofot topilmadi"
        )

    existing_order = db.query(ShopOrder).filter(
        ShopOrder.product_id == product_id
    ).first()

    if existing_order:
        raise HTTPException(
            status_code=400,
            detail="Bu mukofot bo'yicha buyurtmalar mavjud. O'chirish o'rniga deaktiv qiling."
        )

    db.delete(product)
    db.commit()

    return {
        "success": True,
        "message": "Mukofot o'chirildi"
    }


# =========================================================
# ORDERS — BUYURTMALAR
# =========================================================

@router.get("/orders")
def get_orders(
    status: str | None = None,
    student_id: int | None = None,
    product_id: int | None = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    query = db.query(ShopOrder)

    if status:
        query = query.filter(
            ShopOrder.status == status
        )

    if student_id:
        query = query.filter(
            ShopOrder.student_id == student_id
        )

    if product_id:
        query = query.filter(
            ShopOrder.product_id == product_id
        )

    orders = query.order_by(
        ShopOrder.created_at.desc()
    ).all()

    return [
        order_to_dict(order, db)
        for order in orders
    ]


@router.get("/orders/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    order = db.query(ShopOrder).filter(
        ShopOrder.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Buyurtma topilmadi"
        )

    return order_to_dict(order, db)


@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    allowed_statuses = {
        "pending",
        "completed",
        "cancelled",
        "processing",
    }

    if data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status quyidagilardan biri bo'lishi kerak: {', '.join(sorted(allowed_statuses))}"
        )

    order = db.query(ShopOrder).filter(
        ShopOrder.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Buyurtma topilmadi"
        )

    order.status = data.status

    if data.status == "completed":
        order.completed_at = datetime.now(timezone.utc)

    elif data.status != "completed":
        order.completed_at = None

    db.commit()
    db.refresh(order)

    return {
        "success": True,
        "message": "Buyurtma statusi yangilandi",
        "order": order_to_dict(order, db),
    }


# =========================================================
# REWARD RULES — AVTOMATIK MUKOFOT QOIDALARI
# =========================================================

@router.get("/rules")
def get_reward_rules(
    active_only: bool = False,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    query = db.query(RewardRule)

    if active_only:
        query = query.filter(
            RewardRule.is_active == True
        )

    rules = query.order_by(
        RewardRule.id.asc()
    ).all()

    return [
        rule_to_dict(rule)
        for rule in rules
    ]


@router.get("/rules/{rule_id}")
def get_reward_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    rule = db.query(RewardRule).filter(
        RewardRule.id == rule_id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=404,
            detail="Reward qoidasi topilmadi"
        )

    return rule_to_dict(rule)


@router.post("/rules")
def create_reward_rule(
    data: RuleCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    reward_type = data.reward_type.lower()

    if reward_type not in {"coin", "crystal"}:
        raise HTTPException(
            status_code=400,
            detail="reward_type faqat 'coin' yoki 'crystal' bo'lishi mumkin"
        )

    rule = RewardRule(
        name=data.name,
        description=data.description,
        action_type=data.action_type,
        reward_type=reward_type,
        reward_amount=data.reward_amount,
        is_active=True,
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    return {
        "success": True,
        "message": "Reward qoidasi yaratildi",
        "rule": rule_to_dict(rule),
    }


@router.put("/rules/{rule_id}")
def update_reward_rule(
    rule_id: int,
    data: RuleUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    rule = db.query(RewardRule).filter(
        RewardRule.id == rule_id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=404,
            detail="Reward qoidasi topilmadi"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "reward_type" in update_data:
        reward_type = update_data["reward_type"].lower()

        if reward_type not in {"coin", "crystal"}:
            raise HTTPException(
                status_code=400,
                detail="reward_type faqat 'coin' yoki 'crystal' bo'lishi mumkin"
            )

        update_data["reward_type"] = reward_type

    for field, value in update_data.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)

    return {
        "success": True,
        "message": "Reward qoidasi yangilandi",
        "rule": rule_to_dict(rule),
    }


@router.put("/rules/{rule_id}/activate")
def activate_reward_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    rule = db.query(RewardRule).filter(
        RewardRule.id == rule_id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=404,
            detail="Reward qoidasi topilmadi"
        )

    rule.is_active = True

    db.commit()
    db.refresh(rule)

    return {
        "success": True,
        "message": "Reward qoidasi faollashtirildi",
        "rule": rule_to_dict(rule),
    }


@router.put("/rules/{rule_id}/deactivate")
def deactivate_reward_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    rule = db.query(RewardRule).filter(
        RewardRule.id == rule_id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=404,
            detail="Reward qoidasi topilmadi"
        )

    rule.is_active = False

    db.commit()
    db.refresh(rule)

    return {
        "success": True,
        "message": "Reward qoidasi deaktiv qilindi",
        "rule": rule_to_dict(rule),
    }


@router.delete("/rules/{rule_id}")
def delete_reward_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    rule = db.query(RewardRule).filter(
        RewardRule.id == rule_id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=404,
            detail="Reward qoidasi topilmadi"
        )

    db.delete(rule)
    db.commit()

    return {
        "success": True,
        "message": "Reward qoidasi o'chirildi"
    }


# =========================================================
# REWARD TRANSACTIONS — TRANZAKSIYALAR
# =========================================================

@router.get("/transactions")
def get_transactions(
    student_id: int | None = None,
    reward_type: str | None = None,
    reference_type: str | None = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    query = db.query(RewardTransaction)

    if student_id:
        query = query.filter(
            RewardTransaction.student_id == student_id
        )

    if reward_type:
        query = query.filter(
            RewardTransaction.reward_type == reward_type
        )

    if reference_type:
        query = query.filter(
            RewardTransaction.reference_type == reference_type
        )

    transactions = query.order_by(
        RewardTransaction.created_at.desc()
    ).all()

    return [
        transaction_to_dict(transaction)
        for transaction in transactions
    ]


@router.get("/transactions/{transaction_id}")
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    transaction = db.query(RewardTransaction).filter(
        RewardTransaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Reward tranzaksiyasi topilmadi"
        )

    return transaction_to_dict(transaction)
