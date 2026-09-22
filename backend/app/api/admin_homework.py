from datetime import datetime, timezone
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import require_admin

from app.models.admin import Admin
from app.models.homework import Homework, HomeworkSubmission
from app.models.group import Group
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.ai_telegram_submission import AITelegramSubmission
from app.services.notifications import notify_group_students, notify_student


router = APIRouter(
    prefix="/admin/homework",
    tags=["Admin Homework"]
)


# =========================================================
# SCHEMAS
# =========================================================

class HomeworkCreate(BaseModel):
    group_id: int
    teacher_id: int
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=1)
    deadline: datetime | None = None


class HomeworkUpdate(BaseModel):
    group_id: int | None = None
    teacher_id: int | None = None
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    deadline: datetime | None = None


class SubmissionGrade(BaseModel):
    score: int = Field(ge=0, le=100)
    teacher_comment: str | None = None


class SubmissionStatusUpdate(BaseModel):
    status: str = Field(min_length=2, max_length=30)


# =========================================================
# CONSTANTS
# =========================================================

ALLOWED_HOMEWORK_STATUSES = {"active", "inactive"}
ALLOWED_SUBMISSION_STATUSES = {"submitted", "checked", "late", "rejected"}


# =========================================================
# HELPERS
# =========================================================

def get_homework_or_404(homework_id: int, db: Session):
    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Uy vazifasi topilmadi.")
    return homework


def get_submission_or_404(submission_id: int, db: Session):
    submission = db.query(HomeworkSubmission).filter(
        HomeworkSubmission.id == submission_id
    ).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Topshiriq topilmadi.")
    return submission


def homework_to_dict(homework: Homework, db: Session):
    group = db.query(Group).filter(Group.id == homework.group_id).first()
    teacher = db.query(Teacher).filter(Teacher.id == homework.teacher_id).first()
    submission_count = db.query(HomeworkSubmission).filter(
        HomeworkSubmission.homework_id == homework.id
    ).count()
    checked_count = db.query(HomeworkSubmission).filter(
        HomeworkSubmission.homework_id == homework.id,
        HomeworkSubmission.status == "checked"
    ).count()
    return {
        "id": homework.id,
        "group_id": homework.group_id,
        "group_name": group.name if group else None,
        "teacher_id": homework.teacher_id,
        "teacher_name": teacher.full_name if teacher else None,
        "title": homework.title,
        "description": homework.description,
        "deadline": homework.deadline,
        "created_at": homework.created_at,
        "status": homework.status,
        "submission_count": submission_count,
        "checked_count": checked_count
    }


def submission_to_dict(submission: HomeworkSubmission, db: Session):
    student = db.query(Student).filter(Student.id == submission.student_id).first()
    homework = db.query(Homework).filter(Homework.id == submission.homework_id).first()
    return {
        "id": submission.id,
        "homework_id": submission.homework_id,
        "homework_title": homework.title if homework else None,
        "student_id": submission.student_id,
        "student_name": student.full_name if student else None,
        "answer": submission.answer,
        "file_url": submission.file_url,
        "status": submission.status,
        "score": submission.score,
        "teacher_comment": submission.teacher_comment,
        "submitted_at": submission.submitted_at,
        "checked_at": submission.checked_at
    }


# =========================================================
# 1. GET ALL HOMEWORK
# =========================================================

@router.get("/")
def get_admin_homeworks(
    search: str | None = Query(
        default=None,
        max_length=150
    ),
    status: str | None = Query(
        default=None,
        max_length=20
    ),
    group_id: int | None = None,
    teacher_id: int | None = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    query = db.query(Homework)

    if search:
        search_value = f"%{search.strip()}%"

        query = query.filter(
            Homework.title.ilike(search_value) |
            Homework.description.ilike(search_value)
        )

    if status:
        query = query.filter(
            Homework.status == status.strip().lower()
        )

    if group_id:
        query = query.filter(
            Homework.group_id == group_id
        )

    if teacher_id:
        query = query.filter(
            Homework.teacher_id == teacher_id
        )

    homeworks = query.order_by(
        Homework.created_at.desc()
    ).all()

    return {
        "total": len(homeworks),
        "homeworks": [
            homework_to_dict(
                homework,
                db
            )
            for homework in homeworks
        ]
    }


# =========================================================
# 2. HOMEWORK STATISTICS
# =========================================================

@router.get("/stats/summary")
def get_homework_stats(
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    total = db.query(Homework).count()

    active = db.query(Homework).filter(
        Homework.status == "active"
    ).count()

    inactive = db.query(Homework).filter(
        Homework.status == "inactive"
    ).count()

    submissions = db.query(
        HomeworkSubmission
    ).count()

    checked = db.query(
        HomeworkSubmission
    ).filter(
        HomeworkSubmission.status == "checked"
    ).count()

    pending = db.query(
        HomeworkSubmission
    ).filter(
        HomeworkSubmission.status == "submitted"
    ).count()

    return {
        "total_homework": total,
        "active_homework": active,
        "inactive_homework": inactive,
        "total_submissions": submissions,
        "checked_submissions": checked,
        "pending_submissions": pending
    }

    # =========================================================
# 3. GET ALL SUBMISSIONS
# =========================================================

@router.get("/ai-submissions")
def get_all_ai_submissions(
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    items = db.query(AITelegramSubmission).order_by(AITelegramSubmission.id.desc()).all()
    result = []
    for item in items:
        student = db.query(Student).filter(Student.id == item.student_id).first()
        result.append({
            "id": item.id,
            "source": "telegram_ai",
            "student_id": item.student_id,
            "student_name": student.full_name if student else None,
            "homework_id": None,
            "homework_title": "🤖 AKHSIKENT AI / Telegram",
            "task": item.task,
            "answer": item.answer,
            "status": item.status,
            "score": item.score,
            "passed": item.passed == "true",
            "mistakes": json.loads(item.mistakes) if item.mistakes else [],
            "explanation": item.explanation,
            "recommendation": item.recommendation,
            "submitted_at": item.submitted_at,
            "checked_at": item.checked_at
        })
    return {"total": len(result), "submissions": result}


@router.get("/submissions")
def get_all_admin_submissions(
    status: str | None = Query(
        default=None,
        max_length=30
    ),
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    query = db.query(
        HomeworkSubmission
    )

    if status:
        query = query.filter(
            HomeworkSubmission.status ==
            status.strip().lower()
        )

    submissions = query.order_by(
        HomeworkSubmission.id.desc()
    ).all()

    return {
        "total": len(submissions),
        "submissions": [
            submission_to_dict(
                submission,
                db
            )
            for submission in submissions
        ]
    }
@router.get("/ai-submissions/{submission_id}")
def get_admin_ai_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    item = db.query(AITelegramSubmission).filter(AITelegramSubmission.id == submission_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="AI topshiriq topilmadi.")
    student = db.query(Student).filter(Student.id == item.student_id).first()
    return {
        "id": item.id,
        "source": "telegram_ai",
        "student_id": item.student_id,
        "student_name": student.full_name if student else None,
        "homework_title": "🤖 AKHSIKENT AI / Telegram",
        "task": item.task,
        "answer": item.answer,
        "score": item.score,
        "passed": item.passed == "true",
        "mistakes": json.loads(item.mistakes) if item.mistakes else [],
        "explanation": item.explanation,
        "recommendation": item.recommendation,
        "status": item.status,
        "submitted_at": item.submitted_at,
        "checked_at": item.checked_at
    }

@router.get("/submissions/{submission_id}")
def get_admin_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    submission = get_submission_or_404(
        submission_id,
        db
    )

    return submission_to_dict(
        submission,
        db
    )




# =========================================================
# 3. GET SINGLE HOMEWORK
# =========================================================

# =========================================================
# 10. GRADE SUBMISSION
# =========================================================
@router.get("/{homework_id}")
def get_admin_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    homework = get_homework_or_404(
        homework_id,
        db
    )

    submissions = db.query(
        HomeworkSubmission
    ).filter(
        HomeworkSubmission.homework_id == homework_id
    ).order_by(
        HomeworkSubmission.id.desc()
    ).all()

    return {
        "homework": homework_to_dict(
            homework,
            db
        ),
        "submissions": [
            submission_to_dict(
                submission,
                db
            )
            for submission in submissions
        ]
    }


# =========================================================
# 4. CREATE HOMEWORK
# =========================================================

@router.post("/")
def create_admin_homework(
    data: HomeworkCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    group = db.query(Group).filter(
        Group.id == data.group_id,
        Group.is_active == True
    ).first()

    if not group:
        raise HTTPException(
            status_code=404,
            detail="Faol guruh topilmadi."
        )

    teacher = db.query(Teacher).filter(
        Teacher.id == data.teacher_id,
        Teacher.is_active == True,
        Teacher.approved_by_admin == True
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Faol va administrator tasdiqlagan o‘qituvchi topilmadi."
        )

    if group.teacher_id != teacher.id:
        raise HTTPException(
            status_code=400,
            detail="Tanlangan o‘qituvchi bu guruhga biriktirilmagan."
        )

    if data.deadline is not None:
        check_deadline = data.deadline
        if check_deadline.tzinfo is None:
            check_deadline = check_deadline.replace(tzinfo=timezone.utc)
        if check_deadline <= datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Uy vazifasi muddati kelajakdagi vaqt bo‘lishi kerak.")

    homework = Homework(
        group_id=data.group_id,
        teacher_id=data.teacher_id,
        title=data.title.strip(),
        description=data.description.strip(),
        deadline=data.deadline,
        status="active"
    )

    db.add(homework)
    db.commit()
    db.refresh(homework)

    notify_group_students(
        db,
        group_id=homework.group_id,
        title="📚 Yangi uy vazifasi",
        message=f"{homework.title} uy vazifasi sizga biriktirildi.",
        notification_type="homework",
    )

    return {
        "message": "Uy vazifasi yaratildi.",
        "homework": homework_to_dict(
            homework,
            db
        )
    }


# =========================================================
# 5. UPDATE HOMEWORK
# =========================================================

@router.put("/{homework_id}")
def update_admin_homework(
    homework_id: int,
    data: HomeworkUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    homework = db.query(Homework).filter(
        Homework.id == homework_id
    ).with_for_update().first()
    if not homework:
        raise HTTPException(status_code=404, detail="Uy vazifasi topilmadi")

    target_group_id = data.group_id if data.group_id is not None else homework.group_id
    target_teacher_id = data.teacher_id if data.teacher_id is not None else homework.teacher_id

    group = db.query(Group).filter(
        Group.id == target_group_id,
        Group.is_active == True
    ).first()
    if not group:
        raise HTTPException(
            status_code=404,
            detail="Faol guruh topilmadi."
        )

    teacher = db.query(Teacher).filter(
        Teacher.id == target_teacher_id,
        Teacher.is_active == True,
        Teacher.approved_by_admin == True
    ).first()
    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Faol va administrator tasdiqlagan o‘qituvchi topilmadi."
        )

    if group.teacher_id != teacher.id:
        raise HTTPException(
            status_code=400,
            detail="Tanlangan o‘qituvchi bu guruhga biriktirilmagan."
        )

    homework.group_id = target_group_id
    homework.teacher_id = target_teacher_id

    if data.title is not None:
        homework.title = data.title.strip()

    if data.description is not None:
        homework.description = data.description.strip()

    if data.deadline is not None:
        check_deadline = data.deadline
        if check_deadline.tzinfo is None:
            check_deadline = check_deadline.replace(tzinfo=timezone.utc)
        if check_deadline <= datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Uy vazifasi muddati kelajakdagi vaqt bo‘lishi kerak.")
        homework.deadline = data.deadline

    db.commit()
    db.refresh(homework)

    return {
        "message": "Uy vazifasi yangilandi.",
        "homework": homework_to_dict(
            homework,
            db
        )
    }


# =========================================================
# 6. DEACTIVATE HOMEWORK
# =========================================================

@router.put("/{homework_id}/deactivate")
def deactivate_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    homework = db.query(Homework).filter(
        Homework.id == homework_id
    ).with_for_update().first()

    if not homework:
        raise HTTPException(status_code=404, detail="Uy vazifasi topilmadi.")

    homework.status = "inactive"

    db.commit()
    db.refresh(homework)

    return {
        "message": "Uy vazifasi deaktivatsiya qilindi.",
        "homework_id": homework.id,
        "status": homework.status
    }


# =========================================================
# 7. ACTIVATE HOMEWORK
# =========================================================

@router.put("/{homework_id}/activate")
def activate_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    homework = db.query(Homework).filter(
        Homework.id == homework_id
    ).with_for_update().first()
    if not homework:
        raise HTTPException(status_code=404, detail="Uy vazifasi topilmadi.")

    group = db.query(Group).filter(
        Group.id == homework.group_id,
        Group.is_active == True
    ).with_for_update().first()
    teacher = db.query(Teacher).filter(
        Teacher.id == homework.teacher_id,
        Teacher.is_active == True,
        Teacher.approved_by_admin == True
    ).with_for_update().first()
    if not group or not teacher or group.teacher_id != teacher.id:
        raise HTTPException(
            status_code=400,
            detail="Uy vazifasining guruhi yoki o‘qituvchisi faol emas yoki bir-biriga mos emas."
        )

    homework.status = "active"

    db.commit()
    db.refresh(homework)

    return {
        "message": "Uy vazifasi faollashtirildi.",
        "homework_id": homework.id,
        "status": homework.status
    }


# =========================================================
# 8. GET SUBMISSIONS
# =========================================================

@router.get("/{homework_id}/submissions")
def get_admin_submissions(
    homework_id: int,
    status: str | None = Query(
        default=None,
        max_length=30
    ),
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    get_homework_or_404(
        homework_id,
        db
    )

    query = db.query(
        HomeworkSubmission
    ).filter(
        HomeworkSubmission.homework_id == homework_id
    )

    if status:
        query = query.filter(
            HomeworkSubmission.status ==
            status.strip().lower()
        )

    submissions = query.order_by(
        HomeworkSubmission.id.desc()
    ).all()

    return {
        "total": len(submissions),
        "submissions": [
            submission_to_dict(
                submission,
                db
            )
            for submission in submissions
        ]
    }


# =========================================================
# 9. GET SINGLE SUBMISSION
# =========================================================

@router.put("/submissions/{submission_id}/grade")
def grade_submission(
    submission_id: int,
    data: SubmissionGrade,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    submission = db.query(HomeworkSubmission).filter(
        HomeworkSubmission.id == submission_id
    ).with_for_update().first()
    if not submission:
        raise HTTPException(status_code=404, detail="Topshiriq topilmadi")

    submission.score = data.score
    submission.teacher_comment = data.teacher_comment
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
        "message": "Topshiriq baholandi.",
        "submission": submission_to_dict(
            submission,
            db
        )
    }


# =========================================================
# 11. UPDATE SUBMISSION STATUS
# =========================================================

@router.put("/submissions/{submission_id}/status")
def update_submission_status(
    submission_id: int,
    data: SubmissionStatusUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    submission = db.query(HomeworkSubmission).filter(
        HomeworkSubmission.id == submission_id
    ).with_for_update().first()
    if not submission:
        raise HTTPException(status_code=404, detail="Topshiriq topilmadi")

    new_status = data.status.strip().lower()

    if new_status not in ALLOWED_SUBMISSION_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Noto‘g‘ri submission status. "
                "Ruxsat etilganlar: "
                "submitted, checked, late, rejected."
            )
        )

    submission.status = new_status

    if new_status == "checked":
        submission.checked_at = datetime.utcnow()

    db.commit()
    db.refresh(submission)

    return {
        "message": "Topshiriq statusi yangilandi.",
        "submission": submission_to_dict(
            submission,
            db
        )
    }


# =========================================================
# 12. DELETE HOMEWORK
# =========================================================

@router.delete("/{homework_id}")
def delete_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    homework = db.query(Homework).filter(
        Homework.id == homework_id
    ).with_for_update().first()
    if not homework:
        raise HTTPException(status_code=404, detail="Uy vazifasi topilmadi")

    submission_count = db.query(
        HomeworkSubmission
    ).filter(
        HomeworkSubmission.homework_id == homework_id
    ).count()

    if submission_count > 0:
        raise HTTPException(
            status_code=409,
            detail=(
                "Bu uy vazifasiga topshiriqlar mavjud. "
                "O‘chirish o‘rniga deaktivatsiya qiling."
            )
        )

    db.delete(homework)
    db.commit()

    return {
        "message": "Uy vazifasi o‘chirildi.",
        "homework_id": homework_id
  }
