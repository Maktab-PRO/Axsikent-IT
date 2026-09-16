from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.student import Student
from app.models.gamification import StudentGamification

router = APIRouter(
    prefix="/students",
    tags=["Student Ranking"]
)


@router.get("/ranking")
def get_student_ranking(
    db: Session = Depends(get_db)
):
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
