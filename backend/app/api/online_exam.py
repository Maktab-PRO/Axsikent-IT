import json
import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import require_admin, verify_token
from app.models.admin import Admin
from app.models.student import Student
from app.models.online_exam import OnlineExam, OnlineExamQuestion, OnlineExamAttempt

router = APIRouter(prefix="/online-exams", tags=["Online Exams"])
security = HTTPBearer()


class ExamCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None
    course_id: int | None = None
    time_limit_minutes: int = Field(default=30, ge=1, le=180)
    pass_score: int = Field(default=80, ge=0, le=100)
    max_attempts: int = Field(default=1, ge=1, le=10)


class QuestionCreate(BaseModel):
    question: str = Field(min_length=2)
    options: list[str] = Field(min_length=2, max_length=6)
    correct_answer: int = Field(ge=0, le=5)
    sort_order: int = Field(default=0, ge=0)


class SubmitExam(BaseModel):
    answers: dict[str, int] = Field(default_factory=dict)


def student_id_from_token(credentials):
    student_id = verify_token(credentials.credentials)
    if not student_id:
        raise HTTPException(status_code=401, detail="Token noto'g'ri yoki muddati tugagan")
    return student_id


@router.get("/available")
def available_exams(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    student_id = student_id_from_token(credentials)
    student = db.query(Student).filter(Student.id == student_id, Student.is_active == True).first()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    exams = db.query(OnlineExam).filter(OnlineExam.is_active == True).order_by(OnlineExam.id.desc()).all()
    result = []
    for exam in exams:
        attempts = db.query(OnlineExamAttempt).filter(
            OnlineExamAttempt.exam_id == exam.id,
            OnlineExamAttempt.student_id == student_id,
            OnlineExamAttempt.status == "submitted"
        ).count()
        result.append({
            "id": exam.id,
            "title": exam.title,
            "description": exam.description,
            "course_id": exam.course_id,
            "time_limit_minutes": exam.time_limit_minutes,
            "pass_score": exam.pass_score,
            "max_attempts": exam.max_attempts,
            "attempts_used": attempts,
            "can_start": attempts < exam.max_attempts
        })
    return {"total": len(result), "exams": result}


@router.post("/{exam_id}/start")
def start_exam(exam_id: int, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    student_id = student_id_from_token(credentials)
    exam = db.query(OnlineExam).filter(OnlineExam.id == exam_id, OnlineExam.is_active == True).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Imtihon topilmadi")

    attempts = db.query(OnlineExamAttempt).filter(
        OnlineExamAttempt.exam_id == exam_id,
        OnlineExamAttempt.student_id == student_id,
        OnlineExamAttempt.status == "submitted"
    ).count()
    if attempts >= exam.max_attempts:
        raise HTTPException(status_code=403, detail="Urinishlar soni tugagan")

    active = db.query(OnlineExamAttempt).filter(
        OnlineExamAttempt.exam_id == exam_id,
        OnlineExamAttempt.student_id == student_id,
        OnlineExamAttempt.status == "in_progress"
    ).first()
    if active:
        raise HTTPException(status_code=409, detail="Sizda boshlangan imtihon mavjud")

    questions = db.query(OnlineExamQuestion).filter(
        OnlineExamQuestion.exam_id == exam_id,
        OnlineExamQuestion.is_active == True
    ).order_by(OnlineExamQuestion.sort_order.asc(), OnlineExamQuestion.id.asc()).all()
    if not questions:
        raise HTTPException(status_code=400, detail="Bu imtihonda hali savollar mavjud emas")

    selected = questions[:]
    random.shuffle(selected)

    attempt = OnlineExamAttempt(exam_id=exam_id, student_id=student_id, status="in_progress")
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {
        "attempt_id": attempt.id,
        "exam_id": exam.id,
        "title": exam.title,
        "time_limit_minutes": exam.time_limit_minutes,
        "pass_score": exam.pass_score,
        "questions": [{"id": q.id, "question": q.question, "options": json.loads(q.options)} for q in selected]
    }


@router.post("/{exam_id}/submit")
def submit_exam(exam_id: int, data: SubmitExam, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    student_id = student_id_from_token(credentials)
    exam = db.query(OnlineExam).filter(OnlineExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Imtihon topilmadi")

    attempt = db.query(OnlineExamAttempt).filter(
        OnlineExamAttempt.exam_id == exam_id,
        OnlineExamAttempt.student_id == student_id,
        OnlineExamAttempt.status == "in_progress"
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Faol imtihon urinishi topilmadi")

    questions = db.query(OnlineExamQuestion).filter(
        OnlineExamQuestion.exam_id == exam_id,
        OnlineExamQuestion.is_active == True
    ).all()

    correct = sum(
        1 for q in questions
        if str(data.answers.get(str(q.id), "")) == q.correct_answer
    )
    score = round(correct / len(questions) * 100) if questions else 0
    passed = score >= exam.pass_score

    attempt.answers = json.dumps(data.answers, ensure_ascii=False)
    attempt.score = score
    attempt.passed = passed
    attempt.status = "submitted"
    attempt.submitted_at = datetime.now(timezone.utc)
    attempt.finished_reason = "submitted"
    db.commit()

    return {
        "attempt_id": attempt.id,
        "score": score,
        "passed": passed,
        "pass_score": exam.pass_score,
        "correct": correct,
        "total": len(questions)
    }


@router.post("/admin/create")
def create_exam(data: ExamCreate, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    exam = OnlineExam(**data.model_dump())
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return {"success": True, "exam": {"id": exam.id, "title": exam.title}}


@router.post("/admin/{exam_id}/questions")
def add_question(exam_id: int, data: QuestionCreate, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    exam = db.query(OnlineExam).filter(OnlineExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Imtihon topilmadi")
    if data.correct_answer >= len(data.options):
        raise HTTPException(status_code=400, detail="To'g'ri javob varianti mavjud emas")

    q = OnlineExamQuestion(
        exam_id=exam_id,
        question=data.question,
        options=json.dumps(data.options, ensure_ascii=False),
        correct_answer=str(data.correct_answer),
        sort_order=data.sort_order,
        is_active=True
    )
    db.add(q)
    exam.question_count = (exam.question_count or 0) + 1
    db.commit()
    db.refresh(q)
    return {"success": True, "question_id": q.id}


@router.get("/admin/{exam_id}/questions")
def admin_questions(exam_id: int, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    questions = db.query(OnlineExamQuestion).filter(
        OnlineExamQuestion.exam_id == exam_id
    ).order_by(OnlineExamQuestion.sort_order, OnlineExamQuestion.id).all()

    return {
        "exam_id": exam_id,
        "questions": [
            {
                "id": q.id,
                "question": q.question,
                "options": json.loads(q.options),
                "correct_answer": int(q.correct_answer),
                "is_active": q.is_active
            } for q in questions
        ]
    }
