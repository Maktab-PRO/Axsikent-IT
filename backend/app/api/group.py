from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.group import Group


router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)


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
