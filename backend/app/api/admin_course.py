from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.category import Category
from app.models.course import Course
from app.models.student import Student
from app.models.student_course import StudentCourse
from app.models.admin import Admin
from app.core.security import verify_token


router = APIRouter(
    prefix="/admin/courses",
    tags=["Admin Courses"]
)
security = HTTPBearer()

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    admin_id = verify_token(credentials.credentials)

    if not admin_id:
        raise HTTPException(
            status_code=401,
            detail="Token noto'g'ri yoki muddati tugagan"
        )

    admin = db.query(Admin).filter(
        Admin.id == admin_id
    ).first()

    if not admin:
        raise HTTPException(
            status_code=403,
            detail="Faqat admin uchun"
        )

    return admin

@router.post("/categories")
def create_category(
    name: str,
    icon: str | None = None,
    db: Session = Depends(get_db)
):
    existing = db.query(Category).filter(
        Category.name == name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Bu kategoriya allaqachon mavjud"
        )

    category = Category(
        name=name,
        icon=icon
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return {
        "message": "Kategoriya yaratildi",
        "id": category.id,
        "name": category.name,
        "icon": category.icon
    }


@router.post("/")
def create_course(
    category_id: int,
    name: str,
    description: str | None = None,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Kategoriya topilmadi"
        )

    course = Course(
        category_id=category_id,
        name=name,
        description=description
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return {
        "message": "Kurs yaratildi",
        "id": course.id,
        "name": course.name,
        "category_id": course.category_id
    }


@router.delete("/{course_id}")
def deactivate_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Kurs topilmadi"
        )

    course.is_active = False

    db.commit()

    return {
        "message": "Kurs deaktiv qilindi"
    }
