from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db import get_db
from app.models.student import Student
from app.models.student_course import StudentCourse
from app.models.course import Course
from app.models.course_module import CourseModule
from app.models.lesson import Lesson
from app.schemas.student import StudentCreate, StudentLogin, StudentResponse
from app.core.security import create_access_token


router = APIRouter(prefix="/students", tags=["Students"])

security = HTTPBearer()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


@router.post("/register", response_model=StudentResponse)
def register_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    existing_student = db.query(Student).filter(
        Student.phone == student.phone
    ).first()

    if existing_student:
        raise HTTPException(
            status_code=400,
            detail="Bu telefon raqam allaqachon ro'yxatdan o'tgan"
        )

    hashed_password = pwd_context.hash(student.password)

    new_student = Student(
        full_name=student.full_name,
        phone=student.phone,
        password_hash=hashed_password
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


@router.post("/login")
def login_student(
    student: StudentLogin,
    db: Session = Depends(get_db)
):
    user = db.query(Student).filter(
        Student.phone == student.phone
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Telefon raqam yoki parol noto'g'ri"
        )

    if not pwd_context.verify(
        student.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Telefon raqam yoki parol noto'g'ri"
        )

    access_token = create_access_token(
    {
        "sub": str(user.id),
        "role": "student"
    }
)

    return {
    "message": "Login muvaffaqiyatli",
    "access_token": access_token,
    "token_type": "bearer",
    "student_id": user.id,
    "full_name": user.full_name,
    "role": "student"
}

@router.get("/me")
def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    from app.core.security import verify_token

    student_id = verify_token(credentials.credentials)

    if not student_id:
        raise HTTPException(
            status_code=401,
            detail="Token noto'g'ri yoki muddati tugagan"
        )

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    return {
        "id": student.id,
        "full_name": student.full_name,
        "phone": student.phone,
        "is_active": student.is_active
    }
@router.get("/courses")
def get_my_courses(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    from app.core.security import verify_token

    student_id = verify_token(credentials.credentials)

    if not student_id:
        raise HTTPException(
            status_code=401,
            detail="Token noto'g'ri yoki muddati tugagan"
        )

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    student_courses = db.query(
        StudentCourse,
        Course
    ).join(
        Course,
        StudentCourse.course_id == Course.id
    ).filter(
        StudentCourse.student_id == student_id,
        StudentCourse.is_active == True,
        Course.is_active == True
    ).all()

    return [
        {
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "category_id": course.category_id,
            "age_min": course.age_min,
            "age_max": course.age_max,
            "lesson_minutes": course.lesson_minutes,
            "lessons_per_week": course.lessons_per_week,
            "price_min": course.price_min,
            "price_max": course.price_max,
            "progress": student_course.progress,
            "enrolled_at": student_course.enrolled_at
        }
        for student_course, course in student_courses
    ]
@router.get("/courses/{course_id}/modules")
def get_course_modules(
    course_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    from app.core.security import verify_token

    student_id = verify_token(credentials.credentials)

    if not student_id:
        raise HTTPException(
            status_code=401,
            detail="Token noto'g'ri yoki muddati tugagan"
        )

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    student_course = db.query(StudentCourse).filter(
        StudentCourse.student_id == student_id,
        StudentCourse.course_id == course_id,
        StudentCourse.is_active == True
    ).first()

    if not student_course:
        raise HTTPException(
            status_code=403,
            detail="Bu kurs sizga biriktirilmagan"
        )

    course = db.query(Course).filter(
        Course.id == course_id,
        Course.is_active == True
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Kurs topilmadi"
        )

    modules = db.query(CourseModule).filter(
        CourseModule.course_id == course_id,
        CourseModule.is_active == True
    ).order_by(
        CourseModule.sort_order.asc(),
        CourseModule.id.asc()
    ).all()

    return [
        {
            "id": module.id,
            "course_id": module.course_id,
            "title": module.title,
            "description": module.description,
            "sort_order": module.sort_order,
            "is_active": module.is_active
        }
        for module in modules
        ]
