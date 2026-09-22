from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.group import Group
from datetime import date
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.admin import Admin
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
        return {
            "message": "Guruh topilmadi"
        }

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

    group = Group(
        name=name,
        course_id=course_id,
        level_id=level_id,
        teacher_id=teacher_id,
        room=room,
        start_date=start_date,
        capacity=capacity,
        status=status,
        is_active=True
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
