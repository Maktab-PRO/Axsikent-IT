from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import require_admin
from app.models.admin import Admin
from app.models.shop import ShopProduct


router = APIRouter(
    prefix="/admin/shop",
    tags=["Admin Shop"]
)


# =========================================================
# MUKOFOT QO'SHISH
# =========================================================

@router.post("/products")
def create_product(
    name: str,
    description: str = "",
    image_url: str = "",
    coin_price: int = 0,
    crystal_price: int = 0,
    stock: int = 0,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    if coin_price < 0 or crystal_price < 0 or stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Narx va stock 0 dan kichik bo'lishi mumkin emas"
        )

    product = ShopProduct(
        name=name,
        description=description,
        image_url=image_url,
        coin_price=coin_price,
        crystal_price=crystal_price,
        stock=stock,
        is_active=True
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return {
        "success": True,
        "message": "Mukofot muvaffaqiyatli qo'shildi",
        "product": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "image_url": product.image_url,
            "coin_price": product.coin_price,
            "crystal_price": product.crystal_price,
            "stock": product.stock,
            "is_active": product.is_active
        }
    }


# =========================================================
# MUKOFOTLAR RO'YXATI
# =========================================================

@router.get("/products")
def get_products(
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    products = db.query(ShopProduct).order_by(
        ShopProduct.id.asc()
    ).all()

    return [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "image_url": product.image_url,
            "coin_price": product.coin_price,
            "crystal_price": product.crystal_price,
            "stock": product.stock,
            "is_active": product.is_active
        }
        for product in products
    ]
