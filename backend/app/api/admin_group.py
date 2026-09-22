from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import require_admin

from app.models.admin import Admin
from app.models.group import Group
from app.models.course import Course
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.student_group import StudentGroup


router = APIRouter(
    prefix="/admin/groups",
    tags=["Admin Groups"]
)


# =========================================================
# SCHEMAS
# =========================================================

class GroupCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    course_id: int
    teacher_id: int
    level_id: int | None = None
    room: str | None = Field(default=None, max_length=50)
    start_date: date | None = None
    capacity: int = Field(default=15, ge=1, le=100)
    status: str = Field(default="active", max_length=30)


class GroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    course_id: int | None = None
    teacher_id: int | None = None
    level_id: int | None = None
    room: str | None = Field(default=None, max_length=50)
    start_date: date | None = None
    capacity: int | None = Field(default=None, ge=1, le=100)
    status: str | None = Field(default=None, max_length=30)


# =========================================================
# HELPER
# =========================================================

def get_group_or_404(
    group_id: int,
    db: Session
):
    group = db.query(Group).filter(
        Group.id == group_id
    ).first()

    if not group:
        raise HTTPException(
            status_code=404,
            detail="Guruh topilmadi"
        )

    return group


def get_course_or_404(
    course_id: int,
    db: Session
):
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.is_active == True
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Faol kurs topilmadi"
        )

    return course


def get_teacher_or_404(
    teacher_id: int,
    db: Session
):
    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.is_active == True
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Faol o'qituvchi topilmadi"
        )

    return teacher


# =========================================================
# GROUP LIST
# =========================================================

@router.get("/")
def get_admin_groups(
    search: str | None = None,
    status: str | None = None,
    active_only: bool = False,
    course_id: int | None = None,
    teacher_id: int | None = None,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Group)

    if search:
        query = query.filter(
            Group.name.ilike(f"%{search}%")
        )

    if status:
        query = query.filter(
            Group.status == status
        )

    if active_only:
        query = query.filter(
            Group.is_active == True
        )

    if course_id:
        query = query.filter(
            Group.course_id == course_id
        )

    if teacher_id:
        query = query.filter(
            Group.teacher_id == teacher_id
        )

    groups = query.order_by(
        Group.id.desc()
    ).all()

    result = []

    for group in groups:
        course = db.query(Course).filter(
            Course.id == group.course_id
        ).first()

        teacher = db.query(Teacher).filter(
            Teacher.id == group.teacher_id
        ).first()

        students_count = db.query(StudentGroup).filter(
            StudentGroup.group_id == group.id,
            StudentGroup.is_active == True
        ).count()

        result.append({
            "id": group.id,
            "name": group.name,

            "course": {
                "id": course.id if course else None,
                "name": course.name if course else None
            },

            "teacher": {
                "id": teacher.id if teacher else None,
                "full_name": teacher.full_name if teacher else None,
                "subject": teacher.subject if teacher else None
            },

            "level_id": group.level_id,
            "room": group.room,
            "start_date": group.start_date,
            "capacity": group.capacity,
            "students_count": students_count,
            "available_seats": max(
                (group.capacity or 0) - students_count,
                0
            ),
            "status": group.status,
            "is_active": group.is_active
        })

    return {
        "total": len(result),
        "groups": result
    }


# =========================================================
# GROUP DETAIL
# =========================================================

@router.get("/{group_id}")
def get_admin_group(
    group_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    group = get_group_or_404(
        group_id,
        db
    )

    course = db.query(Course).filter(
        Course.id == group.course_id
    ).first()

    teacher = db.query(Teacher).filter(
        Teacher.id == group.teacher_id
    ).first()

    memberships = db.query(StudentGroup).filter(
        StudentGroup.group_id == group.id,
        StudentGroup.is_active == True
    ).all()

    students = []

    for membership in memberships:
        student = db.query(Student).filter(
            Student.id == membership.student_id
        ).first()

        if student:
            students.append({
                "id": student.id,
                "full_name": student.full_name,
                "phone": student.phone,
                "is_active": student.is_active,
                "joined_at": membership.joined_at
            })

    return {
        "group": {
            "id": group.id,
            "name": group.name,
            "level_id": group.level_id,
            "room": group.room,
            "start_date": group.start_date,
            "capacity": group.capacity,
            "status": group.status,
            "is_active": group.is_active
        },

        "course": {
            "id": course.id if course else None,
            "name": course.name if course else None,
            "description": course.description if course else None
        },

        "teacher": {
            "id": teacher.id if teacher else None,
            "full_name": teacher.full_name if teacher else None,
            "phone": teacher.phone if teacher else None,
            "subject": teacher.subject if teacher else None
        },

        "students": students,

        "statistics": {
            "students_count": len(students),
            "capacity": group.capacity,
            "available_seats": max(
                (group.capacity or 0) - len(students),
                0
            )
        }
    }


# =========================================================
# CREATE GROUP
# =========================================================

@router.post("/")
def create_admin_group(
    data: GroupCreate,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Kursni tekshirish
    get_course_or_404(
        data.course_id,
        db
    )

    # O'qituvchini tekshirish
    get_teacher_or_404(
        data.teacher_id,
        db
    )

    # Bir xil nomdagi faol guruhni oldini olish
    existing = db.query(Group).filter(
        Group.name == data.name,
        Group.is_active == True
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Bu nomdagi faol guruh allaqachon mavjud"
        )

    group = Group(
        name=data.name,
        course_id=data.course_id,
        teacher_id=data.teacher_id,
        level_id=data.level_id,
        room=data.room,
        start_date=data.start_date,
        capacity=data.capacity,
        status=data.status,
        is_active=True
    )

    db.add(group)
    db.commit()
    db.refresh(group)

    return {
        "message": "Guruh muvaffaqiyatli yaratildi",
        "group_id": group.id
    }


# =========================================================
# UPDATE GROUP
# =========================================================

@router.put("/{group_id}")
def update_admin_group(
    group_id: int,
    data: GroupUpdate,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    group = get_group_or_404(
        group_id,
        db
    )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "course_id" in update_data:
        get_course_or_404(
            update_data["course_id"],
            db
        )

    if "teacher_id" in update_data:
        get_teacher_or_404(
            update_data["teacher_id"],
            db
        )

    if "name" in update_data:
        duplicate = db.query(Group).filter(
            Group.name == update_data["name"],
            Group.id != group_id,
            Group.is_active == True
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="Bu nomdagi faol guruh allaqachon mavjud"
            )

    # Sig'imni kamaytirishda mavjud o'quvchilar sonini tekshiramiz
    if "capacity" in update_data:
        students_count = db.query(StudentGroup).filter(
            StudentGroup.group_id == group.id,
            StudentGroup.is_active == True
        ).count()

        if update_data["capacity"] < students_count:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Guruhda hozir {students_count} ta o'quvchi bor. "
                    f"Sig'imni bundan past qilib bo'lmaydi."
                )
            )

    for field, value in update_data.items():
        setattr(
            group,
            field,
            value
        )

    db.commit()
    db.refresh(group)

    return {
        "message": "Guruh ma'lumotlari yangilandi",
        "group_id": group.id
    }


# =========================================================
# DEACTIVATE
# =========================================================

@router.put("/{group_id}/deactivate")
def deactivate_group(
    group_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    group = get_group_or_404(
        group_id,
        db
    )

    group.is_active = False
    group.status = "inactive"

    db.commit()

    return {
        "message": "Guruh deaktiv qilindi",
        "group_id": group.id
    }


# =========================================================
# ACTIVATE
# =========================================================

@router.put("/{group_id}/activate")
def activate_group(
    group_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    group = get_group_or_404(
        group_id,
        db
    )

    group.is_active = True

    if group.status == "inactive":
        group.status = "active"

    db.commit()

    return {
        "message": "Guruh qayta faollashtirildi",
        "group_id": group.id
    }


# =========================================================
# ADD STUDENT TO GROUP
# =========================================================

@router.post("/{group_id}/students/{student_id}")
def add_student_to_group(
    group_id: int,
    student_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    group = get_group_or_404(
        group_id,
        db
    )

    if not group.is_active:
        raise HTTPException(
            status_code=400,
            detail="Deaktiv guruhga o'quvchi qo'shib bo'lmaydi"
        )

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Faol o'quvchi topilmadi"
        )

    current_count = db.query(StudentGroup).filter(
        StudentGroup.group_id == group.id,
        StudentGroup.is_active == True
    ).count()

    if current_count >= group.capacity:
        raise HTTPException(
            status_code=400,
            detail="Guruhda bo'sh joy qolmagan"
        )

    membership = db.query(StudentGroup).filter(
        StudentGroup.student_id == student_id,
        StudentGroup.group_id == group_id
    ).first()

    if membership:
        if membership.is_active:
            raise HTTPException(
                status_code=409,
                detail="O'quvchi allaqachon shu guruhda"
            )

        membership.is_active = True

    else:
        membership = StudentGroup(
            student_id=student_id,
            group_id=group_id,
            is_active=True
        )

        db.add(membership)

    db.commit()
    db.refresh(membership)

    return {
        "message": "O'quvchi guruhga qo'shildi",
        "student_id": student_id,
        "group_id": group_id
    }


# =========================================================
# REMOVE STUDENT FROM GROUP
# =========================================================

@router.delete("/{group_id}/students/{student_id}")
def remove_student_from_group(
    group_id: int,
    student_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    membership = db.query(StudentGroup).filter(
        StudentGroup.group_id == group_id,
        StudentGroup.student_id == student_id,
        StudentGroup.is_active == True
    ).first()

    if not membership:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi bu guruhda topilmadi"
        )

    membership.is_active = False

    db.commit()

    return {
        "message": "O'quvchi guruhdan chiqarildi",
        "student_id": student_id,
        "group_id": group_id
  }
