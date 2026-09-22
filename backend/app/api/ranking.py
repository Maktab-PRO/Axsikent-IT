from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import decode_token
from app.models.student import Student
from app.models.admin import Admin
from app.models.gamification import StudentGamification

router = APIRouter(
    prefix="/students",
    tags=["Student Ranking"]
)

security = HTTPBearer()


@router.get("/ranking")
def get_student_ranking(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token noto'g'ri yoki muddati tugagan")

    role = payload.get("role")
    if role == "student":
        student = db.query(Student).filter(
            Student.id == payload["user_id"],
            Student.is_active == True
        ).first()
        if not student:
            raise HTTPException(status_code=403, detail="O'quvchi akkaunti faol emas")
    elif role == "admin":
        admin = db.query(Admin).filter(
            Admin.id == payload["user_id"],
            Admin.is_active == True
        ).first()
        if not admin:
            raise HTTPException(status_code=403, detail="Administrator akkaunti faol emas")
    else:
        raise HTTPException(status_code=401, detail="Bu endpoint uchun ruxsat berilmagan")
    students = db.query(
        Student,
        StudentGamification
    ).outerjoin(
        StudentGamification,
        Student.id == StudentGamification.student_id
    ).filter(
        Student.is_active == True
    ).all()

    ranking = []

    for student, gamification in students:
        xp = gamification.xp if gamification else 0
        level = gamification.level if gamification else 1
        coins = gamification.coins if gamification else 0

        ranking.append({
            "student_id": student.id,
            "full_name": student.full_name,
            "xp": xp,
            "level": level,
            "coins": coins
        })

    ranking.sort(
        key=lambda item: item["xp"],
        reverse=True
    )

    for index, student in enumerate(ranking, start=1):
        student["rank"] = index

    return ranking
