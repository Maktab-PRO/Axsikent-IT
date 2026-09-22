from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.student_group import StudentGroup
from app.models.student import Student
from app.models.group import Group
from app.models.admin import Admin
from app.core.security import decode_token


router = APIRouter(
    prefix="/student-groups",
    tags=["Student Groups"]
)

security = HTTPBearer()


@router.post("/")
def assign_student_to_group(
    student_id: int,
    group_id: int,
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

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    group = db.query(Group).filter(
        Group.id == group_id,
        Group.is_active == True
    ).first()

    if not group:
        raise HTTPException(
            status_code=404,
            detail="Guruh topilmadi"
        )

    current_count = db.query(StudentGroup).filter(
        StudentGroup.group_id == group_id,
        StudentGroup.is_active == True
    ).count()

    existing = db.query(StudentGroup).filter(
        StudentGroup.student_id == student_id,
        StudentGroup.group_id == group_id
    ).first()

    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=409,
                detail="O'quvchi bu guruhga allaqachon biriktirilgan"
            )
        if current_count >= group.capacity:
            raise HTTPException(
                status_code=400,
                detail="Guruhda bo'sh joy qolmagan"
            )
        existing.is_active = True
        student_group = existing
    else:
        if current_count >= group.capacity:
            raise HTTPException(
                status_code=400,
                detail="Guruhda bo'sh joy qolmagan"
            )
        student_group = StudentGroup(
            student_id=student_id,
            group_id=group_id,
            is_active=True
        )
        db.add(student_group)
    db.commit()
    db.refresh(student_group)

    return {
        "message": "O'quvchi guruhga biriktirildi",
        "id": student_group.id,
        "student_id": student_group.student_id,
        "group_id": student_group.group_id,
        "is_active": student_group.is_active
    }
