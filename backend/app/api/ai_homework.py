from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import verify_token
from app.db import get_db
from app.models.student import Student
from app.models.homework import Homework
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
    student_id = verify_token(credentials.credentials)
    if not student_id:
        raise HTTPException(status_code=401, detail="Token noto'g'ri yoki muddati tugagan")

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
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OpenAI API kaliti serverga ulanmagan")

    task = payload.task.strip()
    answer = payload.answer.strip()

    if not task or not answer:
        raise HTTPException(status_code=400, detail="Topshiriq va javob bo'sh bo'lmasligi kerak")

    if payload.homework_id:
        homework = db.query(Homework).filter(Homework.id == payload.homework_id).first()
        if homework:
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
        raise HTTPException(status_code=502, detail=f"AI tekshiruv xatosi: {exc}")

    score = max(0, min(100, int(result.get("score", 0))))
    result["score"] = score
    result["passed"] = score >= 80

    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "ai": "AKHSIKENT AI",
        **result
    }
