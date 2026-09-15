from datetime import datetime
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
from app.models.student_lesson import StudentLesson
from app.models.lesson_progress import LessonProgress
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
    result = []

    for module in modules:

        total_lessons = db.query(Lesson).filter(
            Lesson.module_id == module.id,
            Lesson.is_active == True
        ).count()

        completed_lessons = db.query(LessonProgress).join(
            Lesson,
            LessonProgress.lesson_id == Lesson.id
        ).filter(
            LessonProgress.student_id == student_id,
            LessonProgress.is_completed == True,
            Lesson.module_id == module.id,
            Lesson.is_active == True
        ).count()

        if total_lessons > 0:
            progress = round(
                completed_lessons / total_lessons * 100
            )
        else:
            progress = 0

        result.append({
            "id": module.id,
            "course_id": module.course_id,
            "title": module.title,
            "description": module.description,
            "sort_order": module.sort_order,
            "is_active": module.is_active,
            "progress": progress,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons
        })

    return result
    
@router.get("/courses/{course_id}/modules/{module_id}/lessons")
def get_module_lessons(
    course_id: int,
    module_id: int,
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

    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id,
        CourseModule.is_active == True
    ).first()

    if not module:
        raise HTTPException(
            status_code=404,
            detail="Modul topilmadi"
        )

    lessons = db.query(Lesson).filter(
        Lesson.module_id == module_id,
        Lesson.is_active == True
    ).order_by(
        Lesson.sort_order.asc(),
        Lesson.id.asc()
    ).all()

        return [
        {
            "id": lesson.id,
            "module_id": lesson.module_id,
            "title": lesson.title,
            "content": lesson.content,
            "video_url": lesson.video_url,
            "sort_order": lesson.sort_order,
            "is_active": lesson.is_active,
            "completed": db.query(LessonProgress).filter(
    LessonProgress.student_id == student_id,
    LessonProgress.lesson_id == lesson.id,
    LessonProgress.is_completed == True
).first() is not None
        }
        for lesson in lessons
    ]
@router.post("/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/complete")
def complete_lesson(
    course_id: int,
    module_id: int,
    lesson_id: int,
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

    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id,
        CourseModule.is_active == True
    ).first()

    if not module:
        raise HTTPException(
            status_code=404,
            detail="Modul topilmadi"
        )

    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.module_id == module_id,
        Lesson.is_active == True
    ).first()

    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="Dars topilmadi"
        )

    progress = db.query(LessonProgress).filter(
        LessonProgress.student_id == student_id,
        LessonProgress.lesson_id == lesson_id
    ).first()

    if progress:
        progress.is_completed = True
        progress.completed_at = datetime.utcnow()
    else:
        progress = LessonProgress(
            student_id=student_id,
            lesson_id=lesson_id,
            is_completed=True,
            completed_at=datetime.utcnow()
        )
        db.add(progress)

    db.commit()
    db.refresh(progress)

    total_lessons = db.query(Lesson).join(
        CourseModule,
        Lesson.module_id == CourseModule.id
    ).filter(
        CourseModule.course_id == course_id,
        Lesson.is_active == True,
        CourseModule.is_active == True
    ).count()

    completed_lessons = db.query(LessonProgress).join(
        Lesson,
        LessonProgress.lesson_id == Lesson.id
    ).join(
        CourseModule,
        Lesson.module_id == CourseModule.id
    ).filter(
        LessonProgress.student_id == student_id,
        LessonProgress.is_completed == True,
        CourseModule.course_id == course_id,
        Lesson.is_active == True,
        CourseModule.is_active == True
    ).count()

    if total_lessons > 0:
        student_course.progress = round(
            completed_lessons / total_lessons * 100
        )
    else:
        student_course.progress = 0

    db.commit()

    return {
        "message": "Dars tugallandi",
        "lesson_id": lesson_id,
        "course_id": course_id,
        "progress": student_course.progress,
        "completed_lessons": completed_lessons,
        "total_lessons": total_lessons
    }
