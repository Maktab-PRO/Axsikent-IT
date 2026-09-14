from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.category import Category
from app.models.course import Course
from app.models.student import Student
from app.models.student_course import StudentCourse
from app.models.course_module import CourseModule
from app.models.lesson import Lesson
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
        Admin.id == admin_id,
        Admin.is_active == True
    ).first()

    if not admin:
        raise HTTPException(
            status_code=403,
            detail="Admin topilmadi"
        )

    return admin
@router.post("/assign")
def assign_course_to_student(
    student_id: int,
    course_id: int,
    admin: Admin = Depends(get_current_admin),
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
        "message": "Kurs o'quvchiga biriktirildi",
        "student_id": student_id,
        "course_id": course_id
    }

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


@router.put("/{course_id}/activate")
def activate_course(
    course_id: int,
    admin: Admin = Depends(get_current_admin),
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
        "message": "Kurs qayta faollashtirildi",
        "course_id": course.id,
        "name": course.name,
        "is_active": course.is_active
    }
@router.post("/{course_id}/modules")
def create_course_module(
    course_id: int,
    title: str,
    description: str | None = None,
    sort_order: int = 0,
    admin: Admin = Depends(get_current_admin),
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
        "message": "Modul yaratildi",
        "id": module.id,
        "course_id": module.course_id,
        "title": module.title,
        "description": module.description,
        "sort_order": module.sort_order,
        "is_active": module.is_active
    }
@router.post("/{course_id}/modules/{module_id}/lessons")
def create_lesson(
    course_id: int,
    module_id: int,
    title: str,
    content: str | None = None,
    video_url: str | None = None,
    sort_order: int = 0,
    admin: Admin = Depends(get_current_admin),
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
            detail="Modul topilmadi"
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

from app.models.lesson import Lesson


@router.post("/modules/{module_id}/lessons")
def create_lesson(
    module_id: int,
    title: str,
    content: str = None,
    video_url: str = None,
    sort_order: int = 0,
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
        Admin.id == admin_id,
        Admin.is_active == True
    ).first()

    if not admin:
        raise HTTPException(
            status_code=403,
            detail="Admin topilmadi"
        )

    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.is_active == True
    ).first()

    if not module:
        raise HTTPException(
            status_code=404,
            detail="Modul topilmadi"
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
        "message": "Dars muvaffaqiyatli yaratildi",
        "id": lesson.id,
        "module_id": lesson.module_id,
        "title": lesson.title,
        "content": lesson.content,
        "video_url": lesson.video_url,
        "sort_order": lesson.sort_order,
        "is_active": lesson.is_active
    }
