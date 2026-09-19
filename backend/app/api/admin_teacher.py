from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import require_admin

from app.models.admin import Admin
from app.models.teacher import Teacher
from app.models.group import Group
from app.models.course import Course
from app.models.student import Student
from app.models.student_group import StudentGroup


router = APIRouter(
    prefix="/admin/teachers",
    tags=["Admin Teachers"]
)


# =========================================================
# 1. TEACHERS LIST
# =========================================================

@router.get("/")
def get_teachers(
    search: str | None = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    query = db.query(Teacher)

    if active_only:
        query = query.filter(
            Teacher.is_active == True
        )

    if search:
        search_value = f"%{search}%"

        query = query.filter(
            (Teacher.full_name.ilike(search_value)) |
            (Teacher.phone.ilike(search_value)) |
            (Teacher.subject.ilike(search_value))
        )

    teachers = query.order_by(
        Teacher.id.desc()
    ).all()

    result = []

    for teacher in teachers:

        groups = db.query(Group).filter(
            Group.teacher_id == teacher.id
        ).all()

        result.append({
            "id": teacher.id,
            "full_name": teacher.full_name,
            "phone": teacher.phone,
            "subject": teacher.subject,
            "is_active": teacher.is_active,
            "groups_count": len(groups)
        })

    return {
        "success": True,
        "total": len(result),
        "teachers": result
    }


# =========================================================
# 2. TEACHER PROFILE
# =========================================================

@router.get("/{teacher_id}")
def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Ustoz topilmadi"
        )

    groups = db.query(Group).filter(
        Group.teacher_id == teacher_id
    ).order_by(
        Group.id.desc()
    ).all()

    group_data = []

    for group in groups:

        course = db.query(Course).filter(
            Course.id == group.course_id
        ).first()

        student_links = db.query(StudentGroup).filter(
            StudentGroup.group_id == group.id,
            StudentGroup.is_active == True
        ).all()

        students = []

        for link in student_links:

            student = db.query(Student).filter(
                Student.id == link.student_id
            ).first()

            if student:
                students.append({
                    "id": student.id,
                    "full_name": student.full_name,
                    "phone": student.phone,
                    "is_active": student.is_active
                })

        group_data.append({
            "id": group.id,
            "name": group.name,
            "course": (
                {
                    "id": course.id,
                    "name": course.name
                }
                if course else None
            ),
            "room": group.room,
            "start_date": group.start_date,
            "capacity": group.capacity,
            "status": group.status,
            "is_active": group.is_active,
            "students_count": len(students),
            "students": students
        })

    return {
        "success": True,

        "teacher": {
            "id": teacher.id,
            "full_name": teacher.full_name,
            "phone": teacher.phone,
            "subject": teacher.subject,
            "is_active": teacher.is_active
        },

        "groups": group_data
    }


# =========================================================
# 3. DEACTIVATE TEACHER
# =========================================================

@router.put("/{teacher_id}/deactivate")
def deactivate_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Ustoz topilmadi"
        )

    teacher.is_active = False

    db.commit()

    return {
        "success": True,
        "message": "Ustoz deaktiv qilindi",
        "teacher_id": teacher.id
    }


# =========================================================
# 4. ACTIVATE TEACHER
# =========================================================

@router.put("/{teacher_id}/activate")
def activate_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Ustoz topilmadi"
        )

    teacher.is_active = True

    db.commit()

    return {
        "success": True,
        "message": "Ustoz qayta faollashtirildi",
        "teacher_id": teacher.id
    }


@router.post("")
def create_teacher(
    full_name: str,
    phone: str,
    password: str,
    subject: str,
    birth_date: str | None = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    import re
    from datetime import date
    from passlib.context import CryptContext

    if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password) or not re.search(r"[^A-Za-z0-9]", password):
        raise HTTPException(status_code=400, detail="Parol kamida 8 ta belgi: harf, raqam va maxsus belgi.")

    if not phone.startswith("+") or len(re.sub(r"\D", "", phone)) < 8:
        raise HTTPException(status_code=400, detail="Telefon raqam + bilan boshlanishi va kamida 8 ta raqamdan iborat bo‘lishi kerak.")

    if db.query(Teacher).filter(Teacher.phone == phone).first():
        raise HTTPException(status_code=400, detail="Bu telefon raqam allaqachon ro‘yxatdan o‘tgan.")

    birth = None
    if birth_date:
        try:
            birth = date.fromisoformat(birth_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Tug‘ilgan sana noto‘g‘ri.")

    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    teacher = Teacher(
        full_name=full_name.strip(),
        phone=phone.strip(),
        password_hash=pwd.hash(password),
        subject=subject.strip(),
        birth_date=birth,
        approved_by_admin=True,
        is_active=True
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return {
        "success": True,
        "message": "O‘qituvchi ro‘yxatdan muvaffaqiyatli o‘tkazildi",
        "teacher": {
            "id": teacher.id,
            "full_name": teacher.full_name,
            "phone": teacher.phone,
            "subject": teacher.subject,
            "birth_date": teacher.birth_date,
            "is_active": teacher.is_active
        }
    }
