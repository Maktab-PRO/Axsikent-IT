from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import decode_token
from app.db import get_db
from app.models.student import Student
from app.models.homework import Homework, HomeworkSubmission
from app.models.lesson_progress import LessonProgress
from app.models.student_group import StudentGroup
from app.models.group import Group
from app.models.ai_homework_state import AIHomeworkState
from datetime import datetime, timezone
from openai import OpenAI
import json


router = APIRouter(prefix="/ai/homework", tags=["AI Homework"])
security = HTTPBearer()


class HomeworkCheckRequest(BaseModel):
    homework_id: int | None = None
    task: str
    answer: str


def get_student(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "student":
        raise HTTPException(status_code=401, detail="Student token noto'g'ri yoki muddati tugagan")
    student_id = payload["user_id"]

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    return student


@router.post("/check")
def check_homework(
    payload: HomeworkCheckRequest,
    student: Student = Depends(get_student),
    db: Session = Depends(get_db)
):
    ai_state = db.query(AIHomeworkState).filter(
        AIHomeworkState.student_id == student.id
    ).first()
    if ai_state and ai_state.is_blocked:
        raise HTTPException(
            status_code=423,
            detail="AKHSIKENT AI 3 ta ketma-ket muvaffaqiyatsiz urinishdan so'ng bloklandi. O'qituvchi qayta ochishi kerak."
        )

    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OpenAI API kaliti serverga ulanmagan")

    task = payload.task.strip()
    answer = payload.answer.strip()

    if not task or not answer:
        raise HTTPException(status_code=400, detail="Topshiriq va javob bo'sh bo'lmasligi kerak")

    homework = None
    existing_submission = None
    if payload.homework_id:
        homework = db.query(Homework).join(
            Group, Group.id == Homework.group_id
        ).join(
            StudentGroup, StudentGroup.group_id == Group.id
        ).filter(
            Homework.id == payload.homework_id,
            Homework.status == "active",
            Group.is_active == True,
            StudentGroup.student_id == student.id,
            StudentGroup.is_active == True
        ).first()
        if not homework:
            raise HTTPException(status_code=403, detail="Bu uy vazifasi sizga biriktirilmagan")
        existing_submission = db.query(HomeworkSubmission).filter(
            HomeworkSubmission.homework_id == homework.id,
            HomeworkSubmission.student_id == student.id
        ).first()
        if existing_submission and existing_submission.status == "checked":
            raise HTTPException(status_code=409, detail="Bu uy vazifasi o‘qituvchi tomonidan allaqachon baholangan.")
        task = f"{homework.title}\n{homework.description}"

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""
Siz AKHSIKENT AI (Ustoz AI), Axsikent IT o'quv markazining yordamchi ustozisiz.
O'quvchining uy vazifasini tekshiring.

TOPSHIRIQ:
{task}

O'QUVCHI JAVOBI:
{answer}

Faqat JSON qaytaring:
{{
  "score": 0-100,
  "passed": true/false,
  "correct_points": ["..."],
  "mistakes": ["..."],
  "explanation": "...",
  "recommendation": "..."
}}

Baholash adolatli bo'lsin. 80% yoki undan yuqori bo'lsa passed=true.
Xatolarni aniq va o'quvchiga tushunarli qilib ko'rsating.
""".strip()

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Siz ta'lim uchun JSON formatida baholovchi AI ustozsiz."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
    except Exception as exc:
        print(f"[AKHSIKENT AI] OpenAI error: {type(exc).__name__}: {exc}", flush=True)
        raise HTTPException(status_code=502, detail="AI tekshiruvda vaqtinchalik xatolik yuz berdi. Iltimos, qayta urinib ko‘ring.")

    raw_score = result.get("score", 0)
    try:
        score = int(raw_score)
    except (TypeError, ValueError):
        score = 0
    score = max(0, min(100, score))

    for key in ("correct_points", "mistakes"):
        value = result.get(key) or []
        if not isinstance(value, list):
            value = [value]
        result[key] = [str(item) for item in value if str(item).strip()]

    result["score"] = score
    result["passed"] = score >= 80

    ai_state = db.query(AIHomeworkState).filter(
        AIHomeworkState.student_id == student.id
    ).with_for_update().first()
    if not ai_state:
        ai_state = AIHomeworkState(
            student_id=student.id,
            consecutive_failures=0,
            is_blocked=False
        )
        db.add(ai_state)
        db.flush()

    if score >= 80:
        ai_state.consecutive_failures = 0
        ai_state.is_blocked = False
        ai_state.blocked_at = None
    else:
        ai_state.consecutive_failures = (ai_state.consecutive_failures or 0) + 1
        if ai_state.consecutive_failures >= 3:
            ai_state.is_blocked = True
            ai_state.blocked_at = datetime.now(timezone.utc)

    # AI tekshiruv natijasini mavjud homework submission tarixiga saqlaymiz.
    if homework:
        if not existing_submission:
            existing_submission = HomeworkSubmission(
                homework_id=homework.id,
                student_id=student.id,
                answer=answer,
                status="ai_checked"
            )
            db.add(existing_submission)
        else:
            existing_submission.answer = answer
            existing_submission.status = "ai_checked"
        existing_submission.score = score
        existing_submission.teacher_comment = "AKHSIKENT AI: " + (result.get("explanation") or result.get("recommendation") or "AI tekshiruv natijasi saqlandi.")
        existing_submission.checked_at = datetime.utcnow()

        if score >= 80 and homework.lesson_id:
            progress = db.query(LessonProgress).filter(
                LessonProgress.student_id == student.id,
                LessonProgress.lesson_id == homework.lesson_id
            ).with_for_update().first()
            if not progress:
                progress = LessonProgress(student_id=student.id, lesson_id=homework.lesson_id, homework_passed=True)
                db.add(progress)
            else:
                progress.homework_passed = True

    db.commit()

    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "ai": "AKHSIKENT AI",
        **result,
        "ai_consecutive_failures": ai_state.consecutive_failures,
        "ai_blocked": ai_state.is_blocked
    }
