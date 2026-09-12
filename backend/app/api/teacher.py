from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db import get_db
from app.models.teacher import Teacher
from app.schemas.teacher import (
    TeacherCreate,
    TeacherLogin,
    TeacherResponse
)
from app.core.security import create_access_token


router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


@router.post(
    "/register",
    response_model=TeacherResponse
)
def register_teacher(
    teacher: TeacherCreate,
    db: Session = Depends(get_db)
):
    existing_teacher = db.query(Teacher).filter(
        Teacher.phone == teacher.phone
    ).first()

    if existing_teacher:
        raise HTTPException(
            status_code=400,
            detail="Bu telefon raqam allaqachon ro'yxatdan o'tgan"
        )

    hashed_password = pwd_context.hash(
        teacher.password
    )

    new_teacher = Teacher(
        full_name=teacher.full_name,
        phone=teacher.phone,
        password_hash=hashed_password,
        subject=teacher.subject
    )

    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)

    return new_teacher


@router.post("/login")
def login_teacher(
    teacher: TeacherLogin,
    db: Session = Depends(get_db)
):
    user = db.query(Teacher).filter(
        Teacher.phone == teacher.phone
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Telefon raqam yoki parol noto'g'ri"
        )

    if not pwd_context.verify(
        teacher.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Telefon raqam yoki parol noto'g'ri"
        )

    access_token = create_access_token(
    {
        "sub": str(user.id),
        "role": "teacher"
    }
)
    return {
        "message": "Teacher login muvaffaqiyatli",
        "access_token": access_token,
        "token_type": "bearer",
        "teacher_id": user.id,
        "full_name": user.full_name
    }
