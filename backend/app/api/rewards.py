from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import verify_token
from app.models.gamification import StudentGamification
from app.models.shop import ShopProduct

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
