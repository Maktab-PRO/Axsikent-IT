from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.homework import Homework
from app.models.teacher import Teacher
from app.models.admin import Admin
from app.core.security import verify_token

router = APIRouter(
    prefix="/homework",
    tags=["Homework"]
)

security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_id = verify_token(credentials.credentials)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Token noto'g'ri yoki muddati tugagan"
        )

    return user_id


@router.post("/")
def create_homework(
    group_id: int,
    teacher_id: int,
    title: str,
    description: str,
    deadline: str | None = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_id = verify_token(credentials.credentials)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Token noto'g'ri yoki muddati tugagan"
        )

    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.is_active == True
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="O'qituvchi topilmadi"
        )

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
    student_id = verify_token(credentials.credentials)

    if not student_id:
        raise HTTPException(
            status_code=401,
            detail="Token noto'g'ri yoki muddati tugagan"
        )

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

    homeworks = db.query(Homework).filter(
        Homework.group_id.in_(group_ids),
        Homework.status == "active"
    ).order_by(Homework.id.desc()).all()

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
