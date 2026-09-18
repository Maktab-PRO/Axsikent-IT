from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import verify_token
from app.models.gamification import StudentGamification
from app.models.shop import ShopProduct, ShopOrder

router = APIRouter(
    prefix="/students",
    tags=["Student Rewards"]
)

security = HTTPBearer()


@router.get("/rewards")
def get_student_rewards(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    student_id = verify_token(credentials.credentials)

    if not student_id:
        raise HTTPException(
            status_code=401,
            detail="Token noto'g'ri yoki muddati tugagan"
        )

    gamification = db.query(StudentGamification).filter(
        StudentGamification.student_id == student_id
    ).first()

    if not gamification:
        gamification = StudentGamification(
            student_id=student_id,
            xp=0,
            level=1,
            coins=0,
            crystals=0,
            streak_days=0
        )

        db.add(gamification)
        db.commit()
        db.refresh(gamification)

    products = db.query(ShopProduct).filter(
        ShopProduct.is_active == True,
        ShopProduct.stock > 0
    ).order_by(
        ShopProduct.id.asc()
    ).all()

    return {
        "student": {
            "student_id": student_id,
            "xp": gamification.xp,
            "level": gamification.level,
            "coins": gamification.coins,
            "crystals": gamification.crystals,
            "streak_days": gamification.streak_days
        },
        "rewards": [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "image_url": product.image_url,
                "coin_price": product.coin_price,
                "crystal_price": product.crystal_price,
                "stock": product.stock
            }
            for product in products
        ]
    }

@router.post("/rewards/{product_id}/buy")
def buy_reward(
    product_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    student_id = verify_token(credentials.credentials)

    gamification = db.query(StudentGamification).filter(
        StudentGamification.student_id == student_id
    ).first()

    if not gamification:
        raise HTTPException(
            status_code=400,
            detail="O'quvchi gamification ma'lumotlari topilmadi"
        )

    product = db.query(ShopProduct).filter(
        ShopProduct.id == product_id,
        ShopProduct.is_active == True
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Mukofot topilmadi"
        )

    if product.stock <= 0:
        raise HTTPException(
            status_code=400,
            detail="Bu mukofot hozir mavjud emas"
        )

    if product.coin_price > gamification.coins:
        raise HTTPException(
            status_code=400,
            detail="Coin yetarli emas"
        )

    if product.crystal_price > gamification.crystals:
        raise HTTPException(
            status_code=400,
            detail="Crystal yetarli emas"
        )

    gamification.coins -= product.coin_price
    gamification.crystals -= product.crystal_price

    product.stock -= 1

    order = ShopOrder(
        student_id=student_id,
        product_id=product.id,
        quantity=1,
        coin_spent=product.coin_price,
        crystal_spent=product.crystal_price,
        status="pending"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return {
        "success": True,
        "message": "Mukofot muvaffaqiyatli buyurtma qilindi",
        "order_id": order.id,
        "student": {
            "coins": gamification.coins,
            "crystals": gamification.crystals
        },
        "reward": {
            "id": product.id,
            "name": product.name,
            "stock": product.stock
        }
    }
