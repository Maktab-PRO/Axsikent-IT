from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.group import Group
from datetime import date
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.admin import Admin
from app.models.course import Course
from app.models.level import Level
from app.models.teacher import Teacher
from app.core.security import decode_token

router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)

security = HTTPBearer()

@router.get("/")
def get_groups(
    db: Session = Depends(get_db)
):
    groups = db.query(Group).filter(
        Group.is_active == True
    ).all()

    return [
        {
            "id": group.id,
            "name": group.name,
            "course_id": group.course_id,
            "level_id": group.level_id,
            "teacher_id": group.teacher_id,
            "room": group.room,
            "start_date": group.start_date,
            "capacity": group.capacity,
            "status": group.status
        }
        for group in groups
    ]


@router.get("/{group_id}")
def get_group(
    group_id: int,
    db: Session = Depends(get_db)
):
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.is_active == True
    ).first()

    if not group:
        raise HTTPException(
            status_code=404,
            detail="Guruh topilmadi"
        )

    return {
        "id": group.id,
        "name": group.name,
        "course_id": group.course_id,
        "level_id": group.level_id,
        "teacher_id": group.teacher_id,
        "room": group.room,
        "start_date": group.start_date,
        "capacity": group.capacity,
        "status": group.status
    }

@router.post("/")
def create_group(
    name: str,
    course_id: int,
    level_id: int | None = None,
    teacher_id: int | None = None,
    room: str | None = None,
    start_date: str | None = None,
    capacity: int = 15,
    status: str = "active",
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Admin token noto'g'ri yoki muddati tugagan")
    admin_id = payload["user_id"]

    admin = db.query(Admin).filter(
        Admin.id == admin_id,
        Admin.is_active == True
    ).first()

    if not admin:
        raise HTTPException(
            status_code=403,
            detail="Admin topilmadi"
        )

    if teacher_id is None:
        raise HTTPException(
            status_code=400,
            detail="Guruh uchun o‘qituvchi tanlanishi shart"
        )

    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Guruh nomi bo'sh bo'lishi mumkin emas")
    if len(name) > 100:
        raise HTTPException(status_code=400, detail="Guruh nomi 100 belgidan oshmasligi kerak")
    if room is not None:
        room = room.strip()
        if len(room) > 50:
            raise HTTPException(status_code=400, detail="Xona nomi 50 belgidan oshmasligi kerak")

    if capacity < 1 or capacity > 100:
        raise HTTPException(
            status_code=400,
            detail="Guruh sig‘imi 1 dan 100 gacha bo‘lishi kerak"
        )

    if status not in {"active", "inactive"}:
        raise HTTPException(
            status_code=400,
            detail="Guruh statusi faqat active yoki inactive bo'lishi kerak"
        )

    course = db.query(Course).filter(
        Course.id == course_id,
        Course.is_active == True
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Faol kurs topilmadi")

    if level_id is not None:
        level = db.query(Level).filter(
            Level.id == level_id,
            Level.course_id == course_id,
            Level.is_active == True
        ).first()
        if not level:
            raise HTTPException(status_code=404, detail="Tanlangan level bu kursga tegishli yoki faol emas")

    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.is_active == True,
        Teacher.approved_by_admin == True
    ).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Faol tasdiqlangan o‘qituvchi topilmadi")

    try:
        parsed_start_date = date.fromisoformat(start_date) if start_date else None
    except ValueError:
        raise HTTPException(status_code=400, detail="start_date YYYY-MM-DD formatida bo'lishi kerak")

    group = Group(
        name=name,
        course_id=course_id,
        level_id=level_id,
        teacher_id=teacher_id,
        room=room,
        start_date=parsed_start_date,
        capacity=capacity,
        status=status,
        is_active=(status == "active")
    )

    db.add(group)
    db.commit()
    db.refresh(group)

    return {
        "message": "Guruh yaratildi",
        "id": group.id,
        "name": group.name,
        "course_id": group.course_id,
        "level_id": group.level_id,
        "teacher_id": group.teacher_id,
        "room": group.room,
        "start_date": group.start_date,
        "capacity": group.capacity,
        "status": group.status
    }
