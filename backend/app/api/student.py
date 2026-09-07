from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentLogin, StudentResponse


router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/register", response_model=StudentResponse)
def register_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    existing_student = db.query(Student).filter(
        Student.phone == student.phone
    ).first()

    if existing_student:
        raise HTTPException(
            status_code=400,
            detail="Bu telefon raqam allaqachon ro'yxatdan o'tgan"
        )

    new_student = Student(
        full_name=student.full_name,
        phone=student.phone,
        password_hash=student.password
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


@router.post("/login")
def login_student(
    student: StudentLogin,
    db: Session = Depends(get_db)
):
    user = db.query(Student).filter(
        Student.phone == student.phone
    ).first()

    if not user or user.password_hash != student.password:
        raise HTTPException(
            status_code=401,
            detail="Telefon raqam yoki parol noto'g'ri"
        )

    return {
        "message": "Login muvaffaqiyatli",
        "student_id": user.id,
        "full_name": user.full_name
    }
