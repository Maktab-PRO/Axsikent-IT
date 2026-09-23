import json
import random
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import require_admin, decode_token
from app.models.admin import Admin
from app.models.student import Student
from app.models.online_exam import OnlineExam, OnlineExamQuestion, OnlineExamAttempt
from app.models.student_course import StudentCourse
from app.models.course import Course

router = APIRouter(prefix="/online-exams", tags=["Online Exams"])
security = HTTPBearer()


class ExamCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None
    course_id: int | None = None
    time_limit_minutes: int = Field(default=30, ge=1, le=180)
    pass_score: int = Field(default=80, ge=0, le=100)
    max_attempts: int = Field(default=1, ge=1, le=10)
    question_limit: int | None = Field(default=None, ge=1, le=200)


class QuestionCreate(BaseModel):
    question: str = Field(min_length=2)
    options: list[str] = Field(min_length=2, max_length=6)
    correct_answer: int = Field(ge=0, le=5)
    sort_order: int = Field(default=0, ge=0)


class SubmitExam(BaseModel):
    answers: dict[str, int] = Field(default_factory=dict)


def parse_options(raw_options):
    try:
        parsed = json.loads(raw_options or "[]")
        return parsed if isinstance(parsed, list) else []
    except (TypeError, ValueError, json.JSONDecodeError):
        return []


def student_id_from_token(
    credentials,
    db: Session
):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "student":
        raise HTTPException(
            status_code=401,
            detail="Student token noto'g'ri yoki muddati tugagan"
        )

    student_id = payload["user_id"]
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    return student_id


@router.get("/available")
def available_exams(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    student_id = student_id_from_token(credentials, db)
    student = db.query(Student).filter(Student.id == student_id, Student.is_active == True).first()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    exams = db.query(OnlineExam).filter(
        OnlineExam.is_active == True
    ).order_by(OnlineExam.id.desc()).all()
    from app.models.course import Course

    active_course_ids = {
        row.course_id for row in db.query(StudentCourse.course_id).join(
            Course,
            Course.id == StudentCourse.course_id
        ).filter(
            StudentCourse.student_id == student_id,
            StudentCourse.is_active == True,
            Course.is_active == True
        ).all()
    }

    result = []
    for exam in exams:
        active_question_count = db.query(OnlineExamQuestion.id).filter(
            OnlineExamQuestion.exam_id == exam.id,
            OnlineExamQuestion.is_active == True
        ).count()
        if active_question_count == 0:
            continue
        # course_id berilgan test faqat shu kursga faol biriktirilgan
        # o‘quvchiga ko‘rinadi. course_id=None esa umumiy test hisoblanadi.
        if exam.course_id is not None and exam.course_id not in active_course_ids:
            continue
        attempts = db.query(OnlineExamAttempt).filter(
            OnlineExamAttempt.exam_id == exam.id,
            OnlineExamAttempt.student_id == student_id,
            OnlineExamAttempt.status == "submitted"
        ).count()

        # Tugagan in_progress urinish ham max_attempts hisobiga kiradi.
        # Faol urinish bo'lsa uni qayta davom ettirish mumkin.
        active_attempt = db.query(OnlineExamAttempt).filter(
            OnlineExamAttempt.exam_id == exam.id,
            OnlineExamAttempt.student_id == student_id,
            OnlineExamAttempt.status == "in_progress"
        ).first()

        active_attempt_expired = False
        if active_attempt:
            active_deadline = active_attempt.deadline_at
            if (
                active_attempt.started_at and
                exam.time_limit_minutes > 0 and
                (
                    active_deadline is None or
                    active_deadline <= active_attempt.started_at
                )
            ):
                active_deadline = active_attempt.started_at + timedelta(minutes=exam.time_limit_minutes)

            if active_deadline:
                if active_deadline.tzinfo is None:
                    active_deadline = active_deadline.replace(tzinfo=timezone.utc)
                active_attempt_expired = datetime.now(timezone.utc) >= active_deadline

        effective_attempts = attempts + (1 if active_attempt_expired else 0)
        can_start = effective_attempts < exam.max_attempts

        result.append({
            "id": exam.id,
            "title": exam.title,
            "description": exam.description,
            "course_id": exam.course_id,
            "time_limit_minutes": exam.time_limit_minutes,
            "pass_score": exam.pass_score,
            "max_attempts": exam.max_attempts,
            "attempts_used": effective_attempts,
            "can_start": can_start
        })
    return {"total": len(result), "exams": result}


@router.post("/{exam_id}/start")
def start_exam(exam_id: int, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    student_id = student_id_from_token(credentials, db)
    exam = db.query(OnlineExam).filter(
        OnlineExam.id == exam_id,
        OnlineExam.is_active == True
    ).with_for_update().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Imtihon topilmadi")

    if exam.course_id is not None:
        from app.models.course import Course

        enrolled = db.query(StudentCourse.id).join(
            Course,
            Course.id == StudentCourse.course_id
        ).filter(
            StudentCourse.student_id == student_id,
            StudentCourse.course_id == exam.course_id,
            StudentCourse.is_active == True,
            Course.is_active == True
        ).first()
        if not enrolled:
            raise HTTPException(status_code=403, detail="Bu test siz biriktirilgan kurs uchun mavjud emas")

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
    ).with_for_update().first()

    if active:
        # Eski urinishlarda deadline_at NULL yoki noto‘g‘ri saqlangan bo‘lishi mumkin.
        # Bunday holatda test vaqtini started_at dan qayta tiklaymiz.
        if (
            active.started_at and
            exam.time_limit_minutes > 0 and
            (
                active.deadline_at is None or
                active.deadline_at <= active.started_at
            )
        ):
            active.deadline_at = active.started_at + timedelta(minutes=exam.time_limit_minutes)
            db.commit()
            db.refresh(active)

        # SQLite/PostgreSQL sozlamalariga qarab SQLAlchemy datetime qiymatini
        # naive yoki timezone-aware qaytarishi mumkin. Ikkala holatni ham
        # bir xil UTC ko‘rinishga keltiramiz, aks holda resume paytida
        # "can't compare offset-naive and offset-aware datetimes" xatosi chiqishi mumkin.
        active_deadline = active.deadline_at
        if active_deadline and active_deadline.tzinfo is None:
            active_deadline = active_deadline.replace(tzinfo=timezone.utc)

        if active_deadline and datetime.now(timezone.utc) >= active_deadline:
            active.status = "submitted"
            active.finished_reason = "timeout"
            active.submitted_at = datetime.now(timezone.utc)
            db.commit()

            # Muddati tugagan urinish ham max_attempts hisobiga kiradi.
            # Aks holda max_attempts=1 bo'lgan testda timeoutdan keyin
            # yangi urinish ochilib, limitni chetlab o'tish mumkin edi.
            submitted_attempts = db.query(OnlineExamAttempt).filter(
                OnlineExamAttempt.exam_id == exam_id,
                OnlineExamAttempt.student_id == student_id,
                OnlineExamAttempt.status == "submitted"
            ).count()
            if submitted_attempts >= exam.max_attempts:
                raise HTTPException(status_code=403, detail="Urinishlar soni tugagan")
        else:
            selected_ids = []
            try:
                selected_ids = json.loads(active.question_ids or "[]")
            except Exception:
                selected_ids = []

            questions = db.query(OnlineExamQuestion).filter(
                OnlineExamQuestion.exam_id == exam_id
            ).all()
            question_map = {q.id: q for q in questions}
            selected = [question_map[qid] for qid in selected_ids if qid in question_map]

            return {
                "attempt_id": active.id,
                "exam_id": exam.id,
                "title": exam.title,
                "time_limit_minutes": exam.time_limit_minutes,
                "deadline_at": active_deadline.isoformat() if active_deadline else None,
                "pass_score": exam.pass_score,
                "resumed": True,
                "questions": [{
                    "id": q.id,
                    "question": q.question,
                    "options": parse_options(q.options)
                } for q in selected]
            }

    questions = db.query(OnlineExamQuestion).filter(
        OnlineExamQuestion.exam_id == exam_id,
        OnlineExamQuestion.is_active == True
    ).order_by(OnlineExamQuestion.sort_order.asc(), OnlineExamQuestion.id.asc()).all()
    if not questions:
        raise HTTPException(status_code=400, detail="Bu imtihonda hali savollar mavjud emas")

    selected = questions[:]
    random.shuffle(selected)
    if exam.question_limit:
        selected = selected[:min(exam.question_limit, len(selected))]

    if not exam.time_limit_minutes or exam.time_limit_minutes <= 0:
        raise HTTPException(status_code=400, detail="Bu testning vaqt limiti noto‘g‘ri. Admin paneldan test vaqtini 1 daqiqadan kam bo‘lmagan qiymatga o‘rnating.")

    started_at = datetime.now(timezone.utc)
    deadline_at = started_at + timedelta(minutes=exam.time_limit_minutes)
    attempt = OnlineExamAttempt(
        exam_id=exam_id,
        student_id=student_id,
        status="in_progress",
        started_at=started_at,
        deadline_at=deadline_at,
        question_ids=json.dumps([q.id for q in selected])
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {
        "attempt_id": attempt.id,
        "exam_id": exam.id,
        "title": exam.title,
        "time_limit_minutes": exam.time_limit_minutes,
        "deadline_at": deadline_at.isoformat(),
        "pass_score": exam.pass_score,
        "questions": [{"id": q.id, "question": q.question, "options": parse_options(q.options)} for q in selected]
    }


@router.post("/{exam_id}/submit")
def submit_exam(exam_id: int, data: SubmitExam, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    student_id = student_id_from_token(credentials, db)
    exam = db.query(OnlineExam).filter(
        OnlineExam.id == exam_id
    ).with_for_update().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Imtihon topilmadi")
    if not exam.is_active:
        raise HTTPException(status_code=403, detail="Bu imtihon hozir faol emas")

    if exam.course_id is not None:
        enrolled = db.query(StudentCourse.id).join(
            Course, Course.id == StudentCourse.course_id
        ).filter(
            StudentCourse.student_id == student_id,
            StudentCourse.course_id == exam.course_id,
            StudentCourse.is_active == True,
            Course.is_active == True
        ).first()
        if not enrolled:
            raise HTTPException(status_code=403, detail="Bu test siz biriktirilgan kurs uchun mavjud emas")

    attempt = db.query(OnlineExamAttempt).filter(
        OnlineExamAttempt.exam_id == exam_id,
        OnlineExamAttempt.student_id == student_id,
        OnlineExamAttempt.status == "in_progress"
    ).with_for_update().first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Faol imtihon urinishi topilmadi")

    attempt_deadline = attempt.deadline_at
    if attempt_deadline and attempt_deadline.tzinfo is None:
        attempt_deadline = attempt_deadline.replace(tzinfo=timezone.utc)

    if attempt_deadline and datetime.now(timezone.utc) >= attempt_deadline:
        attempt.status = "submitted"
        attempt.submitted_at = datetime.now(timezone.utc)
        attempt.finished_reason = "time_expired"
        attempt.answers = json.dumps(data.answers, ensure_ascii=False)
        db.commit()
        raise HTTPException(status_code=408, detail="Imtihon vaqti tugagan")

    try:
        question_ids = json.loads(attempt.question_ids or "[]")
        if not isinstance(question_ids, list):
            question_ids = []
    except (TypeError, ValueError, json.JSONDecodeError):
        question_ids = []
    if not question_ids:
        raise HTTPException(status_code=409, detail="Bu test urinishida savollar saqlanmagan")

    questions = db.query(OnlineExamQuestion).filter(
        OnlineExamQuestion.id.in_(question_ids),
        OnlineExamQuestion.exam_id == exam_id
    ).all()

    allowed_question_ids = {q.id for q in questions}
    submitted_question_ids = {
        int(key) for key in data.answers.keys()
        if str(key).isdigit() and int(key) in allowed_question_ids
    }
    if len(submitted_question_ids) != len(data.answers):
        raise HTTPException(status_code=400, detail="Javoblar ushbu test savollariga mos emas")

    for q in questions:
        answer = data.answers.get(str(q.id))
        if answer is not None and (answer < 0 or answer >= len(parse_options(q.options))):
            raise HTTPException(status_code=400, detail="Javob varianti mavjud emas")

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
    if data.time_limit_minutes <= 0:
        raise HTTPException(status_code=400, detail="Test vaqti 0 dan katta bo'lishi kerak")
    if not 0 <= data.pass_score <= 100:
        raise HTTPException(status_code=400, detail="O'tish bali 0 dan 100 gacha bo'lishi kerak")
    if data.max_attempts <= 0:
        raise HTTPException(status_code=400, detail="Urinishlar soni 0 dan katta bo'lishi kerak")
    if data.question_limit is not None and data.question_limit <= 0:
        raise HTTPException(status_code=400, detail="Savollar soni 0 dan katta bo'lishi kerak")

    if data.course_id is not None:
        course = db.query(Course).filter(
            Course.id == data.course_id,
            Course.is_active == True
        ).first()
        if not course:
            raise HTTPException(status_code=404, detail="Faol kurs topilmadi")

    exam_data = data.model_dump()
    exam_data["title"] = data.title.strip()
    if not exam_data["title"]:
        raise HTTPException(status_code=400, detail="Imtihon nomi bo'sh bo'lishi mumkin emas")
    exam = OnlineExam(**exam_data)
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return {"success": True, "exam": {"id": exam.id, "title": exam.title}}


@router.post("/admin/{exam_id}/questions")
def add_question(exam_id: int, data: QuestionCreate, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    exam = db.query(OnlineExam).filter(OnlineExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Imtihon topilmadi")
    question_text = data.question.strip()
    options = [option.strip() for option in data.options]

    if not question_text:
        raise HTTPException(status_code=400, detail="Savol bo'sh bo'lishi mumkin emas")
    if any(not option for option in options):
        raise HTTPException(status_code=400, detail="Javob variantlari bo'sh bo'lishi mumkin emas")
    if data.correct_answer < 0 or data.correct_answer >= len(options):
        raise HTTPException(status_code=400, detail="To'g'ri javob varianti mavjud emas")

    q = OnlineExamQuestion(
        exam_id=exam_id,
        question=question_text,
        options=json.dumps(options, ensure_ascii=False),
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
