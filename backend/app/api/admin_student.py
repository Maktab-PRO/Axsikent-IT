from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import require_admin

from app.models.admin import Admin
from app.models.student import Student
from app.models.student_course import StudentCourse
from app.models.course import Course


router = APIRouter(
    prefix="/admin/students",
    tags=["Admin Students"]
)


# =========================================================
# STUDENTS LIST
# =========================================================

@router.get("/")
def get_students(
    search: str | None = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    query = db.query(Student)

    if active_only:
        query = query.filter(
            Student.is_active == True
        )

    if search:
        search_value = f"%{search}%"

        query = query.filter(
            (Student.full_name.ilike(search_value)) |
            (Student.phone.ilike(search_value))
        )

    students = query.order_by(
        Student.id.desc()
    ).all()

    result = []

    for student in students:

        enrollments = db.query(StudentCourse).filter(
            StudentCourse.student_id == student.id,
            StudentCourse.is_active == True
        ).all()

        courses = []

        for enrollment in enrollments:
            course = db.query(Course).filter(
                Course.id == enrollment.course_id
            ).first()

            if course:
                courses.append({
                    "id": course.id,
                    "name": course.name,
                    "progress": enrollment.progress
                })

        result.append({
            "id": student.id,
            "full_name": student.full_name,
            "phone": student.phone,
            "role": student.role,
            "is_active": student.is_active,
            "courses": courses
        })

    return {
        "success": True,
        "total": len(result),
        "students": result
    }


# =========================================================
# STUDENT PROFILE
# =========================================================

@router.get("/{student_id}")
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    enrollments = db.query(StudentCourse).filter(
        StudentCourse.student_id == student.id
    ).all()

    courses = []

    for enrollment in enrollments:

        course = db.query(Course).filter(
            Course.id == enrollment.course_id
        ).first()

        if course:
            courses.append({
                "id": course.id,
                "name": course.name,
                "progress": enrollment.progress,
                "is_active": enrollment.is_active,
                "enrolled_at": enrollment.enrolled_at
            })

    return {
        "success": True,

        "student": {
            "id": student.id,
            "full_name": student.full_name,
            "phone": student.phone,
            "role": student.role,
            "is_active": student.is_active
        },

        "courses": courses
    }


# =========================================================
# DEACTIVATE STUDENT
# =========================================================

@router.put("/{student_id}/deactivate")
def deactivate_student(
    student_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    student.is_active = False

    db.commit()

    return {
        "success": True,
        "message": "O'quvchi deaktiv qilindi",
        "student_id": student.id
    }


# =========================================================
# ACTIVATE STUDENT
# =========================================================

@router.put("/{student_id}/activate")
def activate_student(
    student_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    student.is_active = True

    db.commit()

    return {
        "success": True,
        "message": "O'quvchi qayta faollashtirildi",
        "student_id": student.id
    }
