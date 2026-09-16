from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import verify_token
from app.models.shop import ShopProduct


router = APIRouter(
    prefix="/admin/shop",
    tags=["Admin Shop"]
)

security = HTTPBearer()


@router.post("/products")
def create_product(
    name: str,
    description: str = "",
    image_url: str = "",
    coin_price: int = 0,
    crystal_price: int = 0,
    stock: int = 0,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    admin_id = verify_token(credentials.credentials)

    if not admin_id:
        raise HTTPException(
            status_code=401,
            detail="Admin token noto'g'ri"
        )

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


@router.get("/products")
def get_products(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    admin_id = verify_token(credentials.credentials)

    if not admin_id:
        raise HTTPException(
            status_code=401,
            detail="Admin token noto'g'ri"
        )

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
