from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import require_admin
from app.models.admin import Admin
from app.models.lesson import Lesson
from app.models.course_module import CourseModule
from app.models.course import Course


router = APIRouter(
    prefix="/admin/lessons",
    tags=["Admin Lessons"]
)


# =========================================================
# 1. DARS QO'SHISH
# =========================================================

@router.post("/")
def create_lesson(
    module_id: int,
    title: str,
    content: str = None,
    video_url: str = None,
    sort_order: int = 1,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.is_active == True
    ).first()

    if not module:
        raise HTTPException(
            status_code=404,
            detail="Modul topilmadi"
        )

    course = db.query(Course).filter(
        Course.id == module.course_id,
        Course.is_active == True
    ).first()

    if not course:
        raise HTTPException(
            status_code=400,
            detail="Dars qo'shish uchun kurs faol bo'lishi kerak"
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
        "message": "Dars muvaffaqiyatli qo'shildi",
        "id": lesson.id,
        "module_id": lesson.module_id,
        "title": lesson.title
    }


# =========================================================
# 2. MODULDAGI DARSLARNI KO'RISH
# =========================================================

@router.get("/module/{module_id}")
def get_module_lessons(
    module_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    module = db.query(CourseModule).filter(
        CourseModule.id == module_id
    ).first()

    if not module:
        raise HTTPException(
            status_code=404,
            detail="Modul topilmadi"
        )

    lessons = db.query(Lesson).filter(
        Lesson.module_id == module_id
    ).order_by(
        Lesson.sort_order.asc(),
        Lesson.id.asc()
    ).all()

    return [
        {
            "id": lesson.id,
            "module_id": lesson.module_id,
            "title": lesson.title,
            "content": lesson.content,
            "video_url": lesson.video_url,
            "sort_order": lesson.sort_order,
            "is_active": lesson.is_active
        }
        for lesson in lessons
    ]


# =========================================================
# 3. BITTA DARSNI KO'RISH
# =========================================================

@router.get("/{lesson_id}")
def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id
    ).first()

    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="Dars topilmadi"
        )

    return {
        "id": lesson.id,
        "module_id": lesson.module_id,
        "title": lesson.title,
        "content": lesson.content,
        "video_url": lesson.video_url,
        "sort_order": lesson.sort_order,
        "is_active": lesson.is_active
    }


# =========================================================
# 4. DARSNI O'ZGARTIRISH
# =========================================================

@router.put("/{lesson_id}")
def update_lesson(
    lesson_id: int,
    title: str,
    content: str = None,
    video_url: str = None,
    sort_order: int = 1,
    is_active: bool = True,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id
    ).first()

    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="Dars topilmadi"
        )

    if is_active:
        module = db.query(CourseModule).filter(
            CourseModule.id == lesson.module_id,
            CourseModule.is_active == True
        ).first()
        if not module:
            raise HTTPException(status_code=400, detail="Deaktiv moduldagi darsni faollashtirib bo'lmaydi")

        course = db.query(Course).filter(
            Course.id == module.course_id,
            Course.is_active == True
        ).first()
        if not course:
            raise HTTPException(status_code=400, detail="Deaktiv kursdagi darsni faollashtirib bo'lmaydi")

    lesson.title = title
    lesson.content = content
    lesson.video_url = video_url
    lesson.sort_order = sort_order
    lesson.is_active = is_active

    db.commit()
    db.refresh(lesson)

    return {
        "success": True,
        "message": "Dars muvaffaqiyatli yangilandi",
        "id": lesson.id,
        "title": lesson.title
    }


# =========================================================
# 5. DARSNI O'CHIRISH
# =========================================================

@router.delete("/{lesson_id}")
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id
    ).first()

    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="Dars topilmadi"
        )

    db.delete(lesson)
    db.commit()

    return {
        "success": True,
        "message": "Dars muvaffaqiyatli o'chirildi",
        "id": lesson_id
    }
