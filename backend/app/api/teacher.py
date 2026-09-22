from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db import get_db
from app.models.teacher import Teacher
from app.models.group import Group
from app.models.student_group import StudentGroup
from app.models.student import Student
from app.models.course_module import CourseModule
from app.models.lesson import Lesson
from app.models.lesson_quiz import LessonQuiz
from app.models.grade import Grade
from app.schemas.teacher import (
    TeacherCreate,
    TeacherLogin,
    TeacherResponse
)
from app.core.security import create_access_token, decode_token


router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


@router.post(
    "/register",
    response_model=TeacherResponse
)
def register_teacher(
    teacher: TeacherCreate,
    db: Session = Depends(get_db)
):
    existing_teacher = db.query(Teacher).filter(
        Teacher.phone == teacher.phone
    ).first()

    raise HTTPException(
        status_code=403,
        detail="O‘qituvchi mustaqil ro‘yxatdan o‘ta olmaydi. Administrator orqali yaratiladi."
    )

    hashed_password = pwd_context.hash(
        teacher.password
    )

    new_teacher = Teacher(
        full_name=teacher.full_name,
        phone=teacher.phone,
        password_hash=hashed_password,
        subject=teacher.subject
    )

    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)

    return new_teacher


@router.post("/login")
def login_teacher(
    teacher: TeacherLogin,
    db: Session = Depends(get_db)
):
    user = db.query(Teacher).filter(
        Teacher.phone == teacher.phone,
        Teacher.is_active == True,
        Teacher.approved_by_admin == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Telefon raqam yoki parol noto'g'ri"
        )

    if not pwd_context.verify(
        teacher.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Telefon raqam yoki parol noto'g'ri"
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "role": "teacher"
        }
    )
    return {
        "message": "Teacher login muvaffaqiyatli",
        "access_token": access_token,
        "token_type": "bearer",
        "teacher_id": user.id,
        "full_name": user.full_name
    }


@router.get("/me/dashboard")
def teacher_dashboard(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
):
    from app.models.student_group import StudentGroup
    from app.models.group import Group
    from app.models.student import Student
    from app.models.course import Course
    from app.models.lesson import Lesson
    from app.models.course_module import CourseModule

    token_data = decode_token(credentials.credentials)
    if not token_data or token_data.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Faqat o‘qituvchi akkaunti uchun ruxsat berilgan")

    teacher_id = token_data["user_id"]
    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.is_active == True,
        Teacher.approved_by_admin == True
    ).first()
    if not teacher:
        raise HTTPException(status_code=401, detail="O‘qituvchi sessiyasi noto‘g‘ri yoki akkaunt faol emas")

    groups = db.query(Group).filter(
        Group.teacher_id == teacher.id,
        Group.is_active == True
    ).all()
    links = db.query(StudentGroup).filter(
        StudentGroup.group_id.in_([g.id for g in groups] or [-1]),
        StudentGroup.is_active == True
    ).all()
    student_ids = list(dict.fromkeys([x.student_id for x in links]))
    students = db.query(Student).filter(
        Student.id.in_(student_ids),
        Student.is_active == True
    ).all() if student_ids else []

    course_ids = list(dict.fromkeys([g.course_id for g in groups]))
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all() if course_ids else []
    course_map = {x.id:x.name for x in courses}

    return {
        "teacher": {
            "id": teacher.id,
            "full_name": teacher.full_name,
            "phone": teacher.phone,
            "subject": teacher.subject,
            "birth_date": teacher.birth_date
        },
        "students": [
            {"id":s.id,"full_name":s.full_name,"phone":s.phone,"subject":teacher.subject}
            for s in students
        ],
        "courses":[{"id":x.id,"name":x.name} for x in courses],
        "groups":[{"id":g.id,"name":g.name,"course_id":g.course_id,"course_name":course_map.get(g.course_id,"")} for g in groups],
        "lessons_count": sum(
            db.query(Lesson).join(CourseModule, Lesson.module_id == CourseModule.id).filter(
                CourseModule.course_id == cid,
                Lesson.is_active == True
            ).count() for cid in course_ids
        )
    }


@router.post("/quiz")
def create_teacher_quiz(
    lesson_id: int,
    question: str,
    option_a: str,
    option_b: str,
    option_c: str,
    option_d: str,
    correct_answer: str,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
):
    token_data = decode_token(credentials.credentials)
    if not token_data or token_data.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Faqat o‘qituvchi akkaunti uchun ruxsat berilgan")

    teacher_id = token_data["user_id"]
    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.is_active == True,
        Teacher.approved_by_admin == True
    ).first()
    if not teacher:
        raise HTTPException(status_code=401, detail="O‘qituvchi sessiyasi noto‘g‘ri yoki akkaunt faol emas")

    lesson = db.query(Lesson).join(CourseModule, Lesson.module_id == CourseModule.id).filter(
        Lesson.id == lesson_id,
        Lesson.is_active == True
    ).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi yoki faol emas")

    module = db.query(CourseModule).filter(
        CourseModule.id == lesson.module_id
    ).first()
    can_manage = db.query(Group).filter(
        Group.teacher_id == teacher.id,
        Group.course_id == module.course_id,
        Group.is_active == True
    ).first()
    if not can_manage:
        raise HTTPException(status_code=403, detail="Bu dars sizga biriktirilmagan")

    correct_answer = correct_answer.upper().strip()
    if correct_answer not in {"A", "B", "C", "D"}:
        raise HTTPException(status_code=400, detail="To‘g‘ri javob A, B, C yoki D bo‘lishi kerak")

    quiz = LessonQuiz(
        lesson_id=lesson.id,
        question=question.strip(),
        option_a=option_a.strip(),
        option_b=option_b.strip(),
        option_c=option_c.strip(),
        option_d=option_d.strip(),
        correct_answer=correct_answer,
        is_active=True
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return {"message": "Quiz saqlandi", "id": quiz.id}


@router.post("/grades")
def create_teacher_grade(
    student_id: int,
    score: float,
    comment: str | None = None,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
):
    token_data = decode_token(credentials.credentials)
    if not token_data or token_data.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Faqat o‘qituvchi akkaunti uchun ruxsat berilgan")

    teacher_id = token_data["user_id"]
    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.is_active == True,
        Teacher.approved_by_admin == True
    ).first()
    if not teacher:
        raise HTTPException(status_code=401, detail="O‘qituvchi sessiyasi noto‘g‘ri yoki akkaunt faol emas")

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="O‘quvchi topilmadi yoki faol emas")

    group = db.query(Group).join(
        StudentGroup, StudentGroup.group_id == Group.id
    ).filter(
        Group.teacher_id == teacher.id,
        Group.is_active == True,
        StudentGroup.student_id == student.id,
        StudentGroup.is_active == True
    ).order_by(Group.id.asc()).first()
    if not group:
        raise HTTPException(status_code=403, detail="Bu o‘quvchi sizga biriktirilmagan")

    if score < 0 or score > 100:
        raise HTTPException(status_code=400, detail="Baho 0 dan 100 gacha bo‘lishi kerak")

    grade = Grade(
        student_id=student.id,
        group_id=group.id,
        teacher_id=teacher.id,
        title="Teacher grade",
        score=score,
        max_score=100,
        comment=comment.strip() if comment else None
    )
    db.add(grade)
    db.commit()
    db.refresh(grade)

    return {"message": "Baho saqlandi", "id": grade.id}
