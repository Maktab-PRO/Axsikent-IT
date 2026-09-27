from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models.student import Student
from app.models.course import Course
from app.models.course_module import CourseModule
from app.models.lesson import Lesson
from app.models.lesson_progress import LessonProgress
from app.models.student_course import StudentCourse


router = APIRouter(
    prefix="/certificates",
    tags=["Certificates"]
)


@router.get("/verify/{certificate_id}")
def verify_certificate(
    certificate_id: str,
    db: Session = Depends(get_db)
):
    certificate_id = certificate_id.strip().upper()

    if not certificate_id.startswith("AKH-2026-"):
        raise HTTPException(
            status_code=400,
            detail="Sertifikat ID formati noto'g'ri. Masalan: AKH-2026-0001"
        )

    try:
        enrollment_id = int(certificate_id.replace("AKH-2026-", "", 1))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Sertifikat ID raqami noto'g'ri."
        )

    enrollment = db.query(StudentCourse).filter(
        StudentCourse.id == enrollment_id,
        StudentCourse.is_active == True
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="Bunday sertifikat topilmadi."
        )

    student = db.query(Student).filter(
        Student.id == enrollment.student_id,
        Student.is_active == True
    ).first()

    course = db.query(Course).filter(
        Course.id == enrollment.course_id,
        Course.is_active == True
    ).first()

    if not student or not course:
        raise HTTPException(
            status_code=404,
            detail="Sertifikat ma'lumotlari topilmadi."
        )

    total_lessons = db.query(Lesson).join(
        CourseModule,
        Lesson.module_id == CourseModule.id
    ).filter(
        CourseModule.course_id == course.id,
        CourseModule.is_active == True,
        Lesson.is_active == True
    ).count()

    completed_lessons = db.query(
        func.count(func.distinct(LessonProgress.lesson_id))
    ).join(
        Lesson,
        LessonProgress.lesson_id == Lesson.id
    ).join(
        CourseModule,
        Lesson.module_id == CourseModule.id
    ).filter(
        LessonProgress.student_id == student.id,
        LessonProgress.is_completed == True,
        CourseModule.course_id == course.id,
        CourseModule.is_active == True,
        Lesson.is_active == True
    ).scalar() or 0

    progress = round(
        completed_lessons / total_lessons * 100
    ) if total_lessons else 0
    progress = max(0, min(100, progress))

    if progress < 100:
        raise HTTPException(
            status_code=404,
            detail="Bu kurs bo'yicha sertifikat hali berilmagan. Kurs to'liq yakunlanmagan."
        )

    return {
        "certificate_id": certificate_id,
        "full_name": student.full_name,
        "course_name": course.name,
        "status": "Haqiqiy",
        "progress": progress
    }
