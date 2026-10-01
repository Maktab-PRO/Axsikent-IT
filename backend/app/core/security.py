from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db import get_db, SessionLocal
from app.models.student import Student
from app.models.teacher import Teacher
from app.core.config import settings
from app.models.admin import Admin


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer(auto_error=True)


def create_access_token(data: dict):
    """
    JWT token yaratish.
    Token ichida:
    - sub  -> foydalanuvchi ID
    - role -> foydalanuvchi roli
    - exp  -> amal qilish vaqti
    """

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    # Session revocation marker. Tokens without auth version are rejected.
    if "av" not in to_encode:
        raise ValueError("auth_version is required for access tokens")

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_token(token: str):
    """
    JWT tokenni to'liq tekshiradi va payload qaytaradi.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")
        role = payload.get("role")
        auth_version = payload.get("av")

        if user_id is None or role not in {"student", "teacher", "admin"} or auth_version is None:
            return None

        user_id = int(user_id)
        auth_version = int(auth_version)

        db = SessionLocal()
        try:
            if role == "student":
                user = db.query(Student).filter(Student.id == user_id, Student.is_active == True).first()
            elif role == "teacher":
                user = db.query(Teacher).filter(
                    Teacher.id == user_id,
                    Teacher.is_active == True,
                    Teacher.approved_by_admin == True
                ).first()
            else:
                user = db.query(Admin).filter(Admin.id == user_id, Admin.is_active == True).first()

            if not user or int(user.auth_version or 1) != auth_version:
                return None
        finally:
            db.close()

        return {
            "user_id": user_id,
            "role": role,
            "auth_version": auth_version
        }

    except (JWTError, ValueError, TypeError):
        return None


def verify_token(token: str):
    """
    Eski endpointlar bilan moslikni saqlash uchun.

    Faqat user ID qaytaradi.
    """

    payload = decode_token(token)

    if not payload:
        return None

    return payload["user_id"]


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Faqat faol ADMIN foydalanuvchini o'tkazadi.

    Tekshiruvlar:
    1. Token mavjudmi?
    2. JWT to'g'rimi?
    3. Role = adminmi?
    4. Admin bazada mavjudmi?
    5. Admin faolmi?
    """

    payload = decode_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token noto'g'ri yoki muddati tugagan"
        )

    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faqat administrator uchun ruxsat berilgan"
        )

    admin_id = payload.get("user_id")

    admin = db.query(Admin).filter(
        Admin.id == admin_id,
        Admin.is_active == True
    ).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator topilmadi yoki faol emas"
        )

    return admin


def require_admin(
    admin: Admin = Depends(get_current_admin)
):
    """
    Admin himoyasi uchun qisqa dependency.

    Endpointga Depends(require_admin) qo'yish kifoya.
    """

    return admin


def require_superadmin(
    admin: Admin = Depends(get_current_admin)
):
    """
    Faqat bosh administrator uchun.
    """

    if not admin.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu amal faqat bosh administrator uchun ruxsat etilgan"
        )

    return admin
