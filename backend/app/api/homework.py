from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.homework import Homework, HomeworkSubmission
from app.models.teacher import Teacher
from app.models.admin import Admin
from app.models.group import Group
from app.core.security import decode_token
from app.services.notifications import notify_student


router = APIRouter(
    prefix="/homework",
    tags=["Homework"]
)

security = HTTPBearer()



def get_student_id(credentials: HTTPAuthorizationCredentials):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "student":
        raise HTTPException(status_code=401, detail="Student token noto'g'ri yoki muddati tugagan")
    return payload["user_id"]


def get_teacher_id(credentials: HTTPAuthorizationCredentials):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "teacher":
        raise HTTPException(status_code=401, detail="Teacher token noto'g'ri yoki muddati tugagan")
    return payload["user_id"]


@router.post("/")
def create_homework(
    group_id: int,
    teacher_id: int,
    title: str,
    description: str,
    deadline: datetime | None = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token noto'g'ri yoki muddati tugagan")

    user_id = payload["user_id"]
    role = payload.get("role")

    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.is_active == True,
        Teacher.approved_by_admin == True
    ).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")

    if role == "teacher":
        if teacher_id != user_id:
            raise HTTPException(status_code=403, detail="Faqat o'zingizga biriktirilgan o'qituvchi sifatida vazifa yarata olasiz")
    elif role == "admin":
        admin = db.query(Admin).filter(
            Admin.id == user_id,
            Admin.is_active == True
        ).first()
        if not admin:
            raise HTTPException(status_code=403, detail="Administrator topilmadi yoki faol emas")
    else:
        raise HTTPException(status_code=403, detail="Faqat o'qituvchi yoki administrator uchun ruxsat berilgan")

    group = db.query(Group).filter(
        Group.id == group_id,
        Group.is_active == True
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Faol guruh topilmadi")

    if role == "teacher" and group.teacher_id != teacher_id:
        raise HTTPException(status_code=403, detail="Bu guruh sizga biriktirilmagan")

    homework = Homework(
        group_id=group_id,
        teacher_id=teacher_id,
        title=title,
        description=description,
        deadline=deadline
    )

    db.add(homework)
    db.commit()
    db.refresh(homework)

    return {
        "message": "Uy vazifasi yaratildi",
        "id": homework.id,
        "group_id": homework.group_id,
        "teacher_id": homework.teacher_id,
        "title": homework.title,
        "description": homework.description,
        "deadline": homework.deadline,
        "status": homework.status
    }


@router.get("/student")
def get_student_homework(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "student":
        raise HTTPException(status_code=401, detail="Student token noto'g'ri yoki muddati tugagan")
    student_id = payload["user_id"]

    from app.models.student import Student
    from app.models.student_group import StudentGroup

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    student_groups = db.query(StudentGroup).filter(
        StudentGroup.student_id == student_id,
        StudentGroup.is_active == True
    ).all()

    group_ids = [item.group_id for item in student_groups]

    if not group_ids:
        return []

    homeworks = db.query(Homework).join(
        Group,
        Group.id == Homework.group_id
    ).filter(
        Homework.group_id.in_(group_ids),
        Homework.status == "active",
        Group.is_active == True
    ).order_by(
        Homework.id.desc()
    ).all()

    return [
        {
            "id": homework.id,
            "group_id": homework.group_id,
            "teacher_id": homework.teacher_id,
            "title": homework.title,
            "description": homework.description,
            "deadline": homework.deadline,
            "status": homework.status
        }
        for homework in homeworks
    ]


@router.post("/{homework_id}/submit")
def submit_homework(
    homework_id: int,
    answer: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    from app.models.student import Student
    from app.models.student_group import StudentGroup
    from app.models.homework import HomeworkSubmission

    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "student":
        raise HTTPException(status_code=401, detail="Student token noto'g'ri yoki muddati tugagan")
    student_id = payload["user_id"]

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).with_for_update().first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    homework = db.query(Homework).join(
        Group,
        Group.id == Homework.group_id
    ).filter(
        Homework.id == homework_id,
        Homework.status == "active",
        Group.is_active == True
    ).with_for_update().first()

    if not homework:
        raise HTTPException(
            status_code=404,
            detail="Uy vazifasi topilmadi"
        )

    student_group = db.query(StudentGroup).filter(
        StudentGroup.student_id == student_id,
        StudentGroup.group_id == homework.group_id,
        StudentGroup.is_active == True
    ).first()

    if not student_group:
        raise HTTPException(
            status_code=403,
            detail="Bu uy vazifasi sizga tegishli emas"
        )

    submission_status = "submitted"
    if homework.deadline:
        deadline = homework.deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > deadline:
            submission_status = "late"

    existing_submission = db.query(
        HomeworkSubmission
    ).filter(
        HomeworkSubmission.homework_id == homework_id,
        HomeworkSubmission.student_id == student_id
    ).first()

    if existing_submission:
        existing_submission.answer = answer
        existing_submission.submitted_at = datetime.utcnow()
        existing_submission.status = submission_status
        existing_submission.score = None
        existing_submission.teacher_comment = None
        existing_submission.checked_at = None

        db.commit()
        db.refresh(existing_submission)

        return {
            "message": "Uy vazifasi qayta topshirildi",
            "id": existing_submission.id,
            "homework_id": existing_submission.homework_id,
            "student_id": existing_submission.student_id,
            "answer": existing_submission.answer,
            "status": existing_submission.status
        }

    submission = HomeworkSubmission(
        homework_id=homework_id,
        student_id=student_id,
        answer=answer,
        status=submission_status
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return {
        "message": "Uy vazifasi topshirildi",
        "id": submission.id,
        "homework_id": submission.homework_id,
        "student_id": submission.student_id,
        "answer": submission.answer,
        "status": submission.status
    }
    
@router.get("/teacher/{homework_id}/submissions")
def get_homework_submissions(
    homework_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "teacher":
        raise HTTPException(status_code=401, detail="Teacher token noto'g'ri yoki muddati tugagan")
    teacher_id = payload["user_id"]

    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.is_active == True,
        Teacher.approved_by_admin == True
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=403,
            detail="O'qituvchi topilmadi"
        )

    homework = db.query(Homework).filter(
        Homework.id == homework_id,
        Homework.teacher_id == teacher_id
    ).first()

    if not homework:
        raise HTTPException(
            status_code=404,
            detail="Uy vazifasi topilmadi yoki sizga tegishli emas"
        )

    submissions = db.query(HomeworkSubmission).filter(
        HomeworkSubmission.homework_id == homework_id
    ).order_by(
        HomeworkSubmission.id.desc()
    ).all()

    return [
        {
            "id": submission.id,
            "homework_id": submission.homework_id,
            "student_id": submission.student_id,
            "answer": submission.answer,
            "file_url": submission.file_url,
            "status": submission.status,
            "score": submission.score,
            "teacher_comment": submission.teacher_comment,
            "submitted_at": submission.submitted_at,
            "checked_at": submission.checked_at
        }
        for submission in submissions
    ]

@router.put("/teacher/submissions/{submission_id}/grade")
def grade_homework_submission(
    submission_id: int,
    score: int,
    teacher_comment: str | None = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    teacher_id = get_teacher_id(credentials)

    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.is_active == True,
        Teacher.approved_by_admin == True
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=403,
            detail="O'qituvchi topilmadi"
        )

    if score < 0 or score > 100:
        raise HTTPException(
            status_code=400,
            detail="Baho 0 dan 100 gacha bo'lishi kerak"
        )

    submission = db.query(HomeworkSubmission).filter(
        HomeworkSubmission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Topshiriq topilmadi"
        )

    homework = db.query(Homework).filter(
        Homework.id == submission.homework_id,
        Homework.teacher_id == teacher_id
    ).first()

    if not homework:
        raise HTTPException(
            status_code=403,
            detail="Bu topshiriqni baholash huquqingiz yo'q"
        )

    submission.score = score
    submission.teacher_comment = teacher_comment
    submission.status = "checked"
    submission.checked_at = datetime.utcnow()

    db.commit()
    db.refresh(submission)

    homework = db.query(Homework).filter(
        Homework.id == submission.homework_id
    ).first()
    if homework:
        notify_student(
            db,
            student_id=submission.student_id,
            title="📝 Uy vazifasi baholandi",
            message=f"{homework.title}: {submission.score}/100" + (
                f" — {submission.teacher_comment}"
                if submission.teacher_comment else ""
            ),
            notification_type="homework_result",
        )

    return {
        "message": "Uy vazifasi baholandi",
        "id": submission.id,
        "homework_id": submission.homework_id,
        "student_id": submission.student_id,
        "score": submission.score,
        "teacher_comment": submission.teacher_comment,
        "status": submission.status,
        "checked_at": submission.checked_at
    }
@router.get("/student/submissions")
def get_student_submissions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    student_id = get_student_id(credentials)

    from app.models.student import Student

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    submissions = db.query(HomeworkSubmission).filter(
        HomeworkSubmission.student_id == student_id
    ).order_by(
        HomeworkSubmission.id.desc()
    ).all()

    return [
        {
            "id": submission.id,
            "homework_id": submission.homework_id,
            "answer": submission.answer,
            "file_url": submission.file_url,
            "status": submission.status,
            "score": submission.score,
            "teacher_comment": submission.teacher_comment,
            "submitted_at": submission.submitted_at,
            "checked_at": submission.checked_at
        }
        for submission in submissions
    ]
