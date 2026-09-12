from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentLogin, StudentResponse
from app.core.security import create_access_token


router = APIRouter(prefix="/students", tags=["Students"])

security = HTTPBearer()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


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

    hashed_password = pwd_context.hash(student.password)

    new_student = Student(
        full_name=student.full_name,
        phone=student.phone,
        password_hash=hashed_password
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

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Telefon raqam yoki parol noto'g'ri"
        )

    if not pwd_context.verify(
        student.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Telefon raqam yoki parol noto'g'ri"
        )

    access_token = create_access_token(
    {
        "sub": str(user.id),
        "role": "student"
    }
)

    return {
    "message": "Login muvaffaqiyatli",
    "access_token": access_token,
    "token_type": "bearer",
    "student_id": user.id,
    "full_name": user.full_name,
    "role": "student"
}

@router.get("/me")
def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    from app.core.security import verify_token

    student_id = verify_token(credentials.credentials)

    if not student_id:
        raise HTTPException(
            status_code=401,
            detail="Token noto'g'ri yoki muddati tugagan"
        )

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    return {
        "id": student.id,
        "full_name": student.full_name,
        "phone": student.phone,
        "is_active": student.is_active
    }
