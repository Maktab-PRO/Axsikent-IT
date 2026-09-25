from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import decode_token
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.group import Group
from app.models.student_group import StudentGroup
from app.models.ai_homework_state import AIHomeworkState


router = APIRouter(prefix="/teachers/ai-homework", tags=["Teacher AI Homework"])
security = HTTPBearer()


@router.post("/unlock")
def unlock_ai_homework(
    student_id: int = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token_data = decode_token(credentials.credentials)
    if not token_data or token_data.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Faqat o'qituvchi akkaunti uchun ruxsat berilgan")

    teacher = db.query(Teacher).filter(
        Teacher.id == token_data["user_id"],
        Teacher.is_active == True,
        Teacher.approved_by_admin == True
    ).first()
    if not teacher:
        raise HTTPException(status_code=401, detail="O'qituvchi sessiyasi noto'g'ri yoki akkaunt faol emas")

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi yoki faol emas")

    managed = db.query(StudentGroup).join(
        Group, Group.id == StudentGroup.group_id
    ).filter(
        Group.teacher_id == teacher.id,
        Group.is_active == True,
        StudentGroup.student_id == student.id,
        StudentGroup.is_active == True
    ).first()
    if not managed:
        raise HTTPException(status_code=403, detail="Bu o'quvchi sizga biriktirilmagan")

    state = db.query(AIHomeworkState).filter(
        AIHomeworkState.student_id == student.id
    ).with_for_update().first()

    if not state:
        state = AIHomeworkState(
            student_id=student.id,
            consecutive_failures=0,
            is_blocked=False,
            unlocked_at=datetime.now(timezone.utc)
        )
        db.add(state)
    else:
        state.consecutive_failures = 0
        state.is_blocked = False
        state.blocked_at = None
        state.unlocked_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "message": "AKHSIKENT AI qayta ochildi",
        "student_id": student.id,
        "consecutive_failures": 0,
        "is_blocked": False
    }
