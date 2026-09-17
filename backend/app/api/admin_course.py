from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.category import Category
from app.models.course import Course
from app.models.student import Student
from app.models.student_course import StudentCourse
from app.models.course_module import CourseModule
from app.models.lesson import Lesson
from app.models.admin import Admin
from app.core.security import require_admin


router = APIRouter(
    prefix="/admin/courses",
    tags=["Admin Courses"]
)


# =========================================================
# 1. STUDENTGA KURS BIRIKTIRISH
# =========================================================

@router.post("/assign")
def assign_course_to_student(
    student_id: int,
    course_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    course = db.query(Course).filter(
        Course.id == course_id,
        Course.is_active == True
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Kurs topilmadi"
        )

    existing = db.query(StudentCourse).filter(
        StudentCourse.student_id == student_id,
        StudentCourse.course_id == course_id
    ).first()

    if existing:

        if existing.is_active:
            raise HTTPException(
                status_code=400,
                detail="Bu kurs o'quvchiga allaqachon biriktirilgan"
            )

        existing.is_active = True
        existing.progress = 0

    else:
        student_course = StudentCourse(
            student_id=student_id,
            course_id=course_id,
            progress=0,
            is_active=True
        )

        db.add(student_course)

    db.commit()

    return {
        "success": True,
        "message": "Kurs o'quvchiga biriktirildi",
        "student_id": student_id,
        "course_id": course_id
    }


# =========================================================
# 2. KATEGORIYA YARATISH
# =========================================================

@router.post("/categories")
def create_category(
    name: str,
    icon: str | None = None,
    admin: Admin = Depends(require_admin),
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
        "success": True,
        "message": "Kategoriya yaratildi",
        "id": category.id,
        "name": category.name,
        "icon": category.icon
    }


# =========================================================
# 3. KURS YARATISH
# =========================================================

@router.post("/")
def create_course(
    category_id: int,
    name: str,
    description: str | None = None,
    admin: Admin = Depends(require_admin),
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
        "success": True,
        "message": "Kurs yaratildi",
        "id": course.id,
        "name": course.name,
        "category_id": course.category_id
    }


# =========================================================
# 4. KURSNI DEAKTIV QILISH
# =========================================================

@router.delete("/{course_id}")
def deactivate_course(
    course_id: int,
    admin: Admin = Depends(require_admin),
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
        "success": True,
        "message": "Kurs deaktiv qilindi",
        "course_id": course_id
    }


# =========================================================
# 5. KURSNI QAYTA FAOLLASHTIRISH
# =========================================================

@router.put("/{course_id}/activate")
def activate_course(
    course_id: int,
    admin: Admin = Depends(require_admin),
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

    course.is_active = True

    db.commit()
    db.refresh(course)

    return {
        "success": True,
        "message": "Kurs qayta faollashtirildi",
        "course_id": course.id,
        "name": course.name,
        "is_active": course.is_active
    }


# =========================================================
# 6. KURSGA MODUL QO'SHISH
# =========================================================

@router.post("/{course_id}/modules")
def create_course_module(
    course_id: int,
    title: str,
    description: str | None = None,
    sort_order: int = 0,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.is_active == True
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Kurs topilmadi"
        )

    module = CourseModule(
        course_id=course_id,
        title=title,
        description=description,
        sort_order=sort_order,
        is_active=True
    )

    db.add(module)
    db.commit()
    db.refresh(module)

    return {
        "success": True,
        "message": "Modul yaratildi",
        "id": module.id,
        "course_id": module.course_id,
        "title": module.title,
        "description": module.description,
        "sort_order": module.sort_order,
        "is_active": module.is_active
    }


# =========================================================
# 7. MODULGA DARS QO'SHISH
# =========================================================

@router.post("/{course_id}/modules/{module_id}/lessons")
def create_lesson(
    course_id: int,
    module_id: int,
    title: str,
    content: str | None = None,
    video_url: str | None = None,
    sort_order: int = 0,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.is_active == True
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Kurs topilmadi"
        )

    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id,
        CourseModule.is_active == True
    ).first()

    if not module:
        raise HTTPException(
            status_code=404,
            detail="Modul topilmadi yoki ushbu kursga tegishli emas"
        )

    lesson = Lesson(
        module_id=module_id,
        title=title,
        content=content,
        video_url=video_url,
        sort_order=sort_order,
        is_active=True
    )

    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    return {
        "success": True,
        "message": "Dars yaratildi",
        "id": lesson.id,
        "course_id": course_id,
        "module_id": lesson.module_id,
        "title": lesson.title,
        "content": lesson.content,
        "video_url": lesson.video_url,
        "sort_order": lesson.sort_order,
        "is_active": lesson.is_active
    }
