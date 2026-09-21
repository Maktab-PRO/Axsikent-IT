from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.lesson_quiz import LessonQuiz
from app.models.lesson import Lesson
from app.core.security import require_admin
from app.models.admin import Admin

router = APIRouter(
    prefix="/admin/lesson-quizzes",
    tags=["Admin Lesson Quiz"]
)


@router.post("/")
def create_lesson_quiz(
    lesson_id: int,
    question: str,
    option_a: str,
    option_b: str,
    option_c: str,
    option_d: str,
    correct_answer: str,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.is_active == True
    ).first()

    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="Faol dars topilmadi"
        )

    correct_answer = correct_answer.upper()

    if correct_answer not in ["A", "B", "C", "D"]:
        raise HTTPException(
            status_code=400,
            detail="To'g'ri javob faqat A, B, C yoki D bo'lishi kerak"
        )

    quiz = LessonQuiz(
        lesson_id=lesson_id,
        question=question,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_answer=correct_answer,
        is_active=True
    )

    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return {
        "message": "Quiz muvaffaqiyatli qo'shildi",
        "id": quiz.id,
        "lesson_id": quiz.lesson_id
    }
