from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db import get_db
from app.models.teacher import Teacher
from app.models.group import Group
from app.models.student_group import StudentGroup
from app.models.student import Student
from app.models.course_module import CourseModule
from app.models.student_course import StudentCourse
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.student_lesson import StudentLesson
from app.models.lesson_quiz import LessonQuiz
from app.models.lesson_progress import LessonProgress
from app.models.grade import Grade
from app.models.attendance import Attendance
from datetime import date
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
    students = db.query(Student).filter(
        Student.is_active == True
    ).order_by(Student.full_name.asc()).all()

    course_ids = list(dict.fromkeys([g.course_id for g in groups]))
    courses = db.query(Course).filter(
        Course.id.in_(course_ids),
        Course.is_active == True
    ).all() if course_ids else []
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
                CourseModule.is_active == True,
                Lesson.is_active == True
            ).count() for cid in course_ids
        )
    }


@router.post("/assign-lesson")
def assign_teacher_lesson(
    student_id: int = Body(...),
    course_id: int = Body(...),
    title: str = Body(...),
    video_url: str | None = Body(None),
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
    ).with_for_update().first()
    if not student:
        raise HTTPException(status_code=404, detail="O‘quvchi topilmadi yoki faol emas")

    enrollment = db.query(StudentCourse).filter(
        StudentCourse.student_id == student.id,
        StudentCourse.course_id == course_id,
        StudentCourse.is_active == True
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Bu o‘quvchi ushbu kursga faol biriktirilmagan")

    module = db.query(CourseModule).join(
        Course,
        Course.id == CourseModule.course_id
    ).filter(
        CourseModule.course_id == course_id,
        CourseModule.is_active == True,
        Course.is_active == True
    ).order_by(CourseModule.sort_order.asc(), CourseModule.id.asc()).first()
    if not module:
        raise HTTPException(status_code=404, detail="Kurs uchun faol modul topilmadi")

    group = db.query(Group).join(
        StudentGroup, StudentGroup.group_id == Group.id
    ).filter(
        Group.teacher_id == teacher.id,
        Group.course_id == course_id,
        Group.is_active == True,
        StudentGroup.student_id == student.id,
        StudentGroup.is_active == True
    ).first()
    if not group:
        raise HTTPException(status_code=403, detail="Bu o‘quvchi va kurs sizga biriktirilmagan")

    title = title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Dars nomi bo‘sh bo‘lishi mumkin emas")

    lesson = Lesson(
        module_id=module.id,
        title=title,
        video_url=video_url.strip() if video_url else None,
        is_active=True
    )
    db.add(lesson)
    db.flush()

    student_lesson = StudentLesson(
        student_id=student.id,
        lesson_id=lesson.id,
        completed=False
    )
    db.add(student_lesson)
    db.commit()
    db.refresh(lesson)

    return {"message": "Dars biriktirildi", "id": lesson.id, "student_id": student.id}


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

    lesson = db.query(Lesson).join(CourseModule, Lesson.module_id == CourseModule.id).join(
        Course, Course.id == CourseModule.course_id
    ).filter(
        Lesson.id == lesson_id,
        Lesson.is_active == True,
        CourseModule.is_active == True,
        Course.is_active == True
    ).first()

    question = question.strip()
    option_a = option_a.strip()
    option_b = option_b.strip()
    option_c = option_c.strip()
    option_d = option_d.strip()
    correct_answer = correct_answer.strip().upper()

    if not question:
        raise HTTPException(status_code=400, detail="Savol bo'sh bo'lishi mumkin emas")
    if not all([option_a, option_b, option_c, option_d]):
        raise HTTPException(status_code=400, detail="Barcha javob variantlari to'ldirilishi kerak")
    if correct_answer not in {"A", "B", "C", "D"}:
        raise HTTPException(status_code=400, detail="To'g'ri javob A, B, C yoki D bo'lishi kerak")
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi yoki faol emas")

    module = db.query(CourseModule).filter(
        CourseModule.id == lesson.module_id,
        CourseModule.is_active == True
    ).first()
    if not module:
        raise HTTPException(status_code=404, detail="Darsning moduli topilmadi yoki faol emas")
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


@router.post("/quiz/unlock")
def unlock_student_quiz(
    student_id: int = Body(...),
    lesson_id: int = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
):
    token_data = decode_token(credentials.credentials)
    if not token_data or token_data.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Faqat o'qituvchi akkaunti uchun ruxsat berilgan")

    teacher_id = token_data["user_id"]
    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.is_active == True,
        Teacher.approved_by_admin == True
    ).first()
    if not teacher:
        raise HTTPException(status_code=401, detail="O'qituvchi sessiyasi noto'g'ri yoki akkaunt faol emas")

    lesson = db.query(Lesson).join(
        CourseModule, CourseModule.id == Lesson.module_id
    ).filter(
        Lesson.id == lesson_id,
        Lesson.is_active == True,
        CourseModule.is_active == True
    ).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Faol dars topilmadi")

    managed = db.query(Group).join(
        StudentGroup, StudentGroup.group_id == Group.id
    ).join(
        CourseModule, CourseModule.course_id == Group.course_id
    ).filter(
        Group.teacher_id == teacher.id,
        CourseModule.id == lesson.module_id,
        Group.is_active == True,
        StudentGroup.student_id == student_id,
        StudentGroup.is_active == True
    ).first()
    if not managed:
        raise HTTPException(status_code=403, detail="Bu o'quvchi sizga ushbu dars kursi bo'yicha biriktirilmagan")

    progress = db.query(LessonProgress).filter(
        LessonProgress.student_id == student_id,
        LessonProgress.lesson_id == lesson_id
    ).with_for_update().first()
    if not progress:
        raise HTTPException(status_code=404, detail="O'quvchining bu dars bo'yicha progressi topilmadi")

    progress.quiz_failures = 0
    progress.quiz_blocked = False
    progress.quiz_passed = False
    db.commit()

    return {
        "message": "Quiz qayta ochildi",
        "student_id": student_id,
        "lesson_id": lesson_id
    }


@router.post("/grades")
def create_teacher_grade(
    student_id: int = Body(...),
    score: float = Body(...),
    comment: str | None = Body(None),
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

    if score < 0 or score > 100:
        raise HTTPException(status_code=400, detail="Baho 0 dan 100 gacha bo‘lishi kerak")

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).with_for_update().first()
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

@router.get("/attendance")
def get_teacher_attendance(
    date: date,
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
    rows = db.query(StudentGroup, Group, Student).join(
        Group, Group.id == StudentGroup.group_id
    ).join(
        Student, Student.id == StudentGroup.student_id
    ).filter(
        Group.teacher_id == teacher.id,
        Group.is_active == True,
        StudentGroup.is_active == True,
        Student.is_active == True
    ).all()
    result = []
    for membership, group, student in rows:
        record = db.query(Attendance).filter(
            Attendance.group_id == group.id,
            Attendance.student_id == student.id,
            Attendance.date == date
        ).first()
        result.append({
            "id": student.id,
            "full_name": student.full_name,
            "group_id": group.id,
            "group_name": group.name,
            "status": record.status if record else "unmarked"
        })
    return {"date": date, "students": result}


@router.post("/attendance")
def save_teacher_attendance(
    student_id: int = Body(...),
    group_id: int = Body(...),
    date: date = Body(...),
    status: str = Body(...),
    note: str | None = Body(None),
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
    if status not in {"present", "absent", "late"}:
        raise HTTPException(status_code=400, detail="Davomat holati noto‘g‘ri")
    membership = db.query(StudentGroup).join(Group, Group.id == StudentGroup.group_id).filter(
        StudentGroup.group_id == group_id,
        Group.teacher_id == teacher.id,
        Group.is_active == True,
        StudentGroup.student_id == student_id,
        StudentGroup.is_active == True
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Bu o‘quvchi sizga biriktirilmagan")
    student_lock = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).with_for_update().first()
    if not student_lock:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi yoki faol emas")

    record = db.query(Attendance).filter(
        Attendance.group_id == membership.group_id,
        Attendance.student_id == student_id,
        Attendance.date == date
    ).first()
    if record:
        record.status = status
        record.note = note.strip() if note else None
    else:
        db.add(Attendance(
            group_id=membership.group_id,
            student_id=student_id,
            date=date,
            status=status,
            note=note.strip() if note else None
        ))
    db.commit()
    return {"message": "Davomat saqlandi", "student_id": student_id, "date": date, "status": status}
