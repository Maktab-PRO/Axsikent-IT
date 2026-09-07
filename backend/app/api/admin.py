from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db import get_db
from app.models.admin import Admin
from app.schemas.admin import AdminLogin, AdminResponse
from app.core.security import create_access_token


router = APIRouter(
    prefix="/admins",
    tags=["Admins"]
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


@router.post("/login")
def login_admin(
    admin: AdminLogin,
    db: Session = Depends(get_db)
):
    user = db.query(Admin).filter(
        Admin.phone == admin.phone
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Telefon raqam yoki parol noto'g'ri"
        )

    if not pwd_context.verify(
        admin.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Telefon raqam yoki parol noto'g'ri"
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "message": "Login muvaffaqiyatli",
        "access_token": access_token,
        "token_type": "bearer",
        "admin_id": user.id,
        "full_name": user.full_name,
        "role": user.role
    }
