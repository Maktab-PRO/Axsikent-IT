from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.category import Category
from app.models.course import Course


router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)


@router.get("/categories")
def get_categories(
    db: Session = Depends(get_db)
):
    categories = db.query(Category).filter(
        Category.is_active == True
    ).order_by(
        Category.sort_order
    ).all()

    return [
        {
            "id": category.id,
            "name": category.name,
            "icon": category.icon
        }
        for category in categories
    ]


@router.get("/")
def get_courses(
    db: Session = Depends(get_db)
):
    courses = db.query(Course).filter(
        Course.is_active == True
    ).order_by(
        Course.sort_order
    ).all()

    return [
        {
            "id": course.id,
            "category_id": course.category_id,
            "name": course.name,
            "description": course.description
        }
        for course in courses
    ]
