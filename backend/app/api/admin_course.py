from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.category import Category
from app.models.course import Course


router = APIRouter(
    prefix="/admin/courses",
    tags=["Admin Courses"]
)


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
