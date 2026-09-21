from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models.student import Student
from app.models.course import Course
from app.models.course_module import CourseModule
from app.models.lesson import Lesson
from app.models.lesson_progress import LessonProgress
from app.models.student_course import StudentCourse
from app.core.security import verify_token


router = APIRouter(
    prefix="/student/courses",
    tags=["Student Courses"]
)

security = HTTPBearer()


def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
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

    return student


@router.get("/")
def get_my_courses(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student_courses = db.query(StudentCourse).filter(
        StudentCourse.student_id == student.id,
        StudentCourse.is_active == True
    ).all()

    result = []

    for item in student_courses:
        course = db.query(Course).filter(
            Course.id == item.course_id,
            Course.is_active == True
        ).first()

        if not course:
            continue

        modules_count = db.query(CourseModule).filter(
            CourseModule.course_id == course.id,
            CourseModule.is_active == True
        ).count()

        # Progressni saqlangan qiymatdan emas, amaldagi faol darslardan
        # qayta hisoblaymiz. Bu /students/courses bilan bir xil natija beradi.
        total_lessons = db.query(Lesson).join(
            CourseModule,
            Lesson.module_id == CourseModule.id
        ).filter(
            CourseModule.course_id == course.id,
            CourseModule.is_active == True,
            Lesson.is_active == True
        ).count()

        completed_lessons = db.query(
            func.count(func.distinct(LessonProgress.lesson_id))
        ).join(
            Lesson,
            LessonProgress.lesson_id == Lesson.id
        ).join(
            CourseModule,
            Lesson.module_id == CourseModule.id
        ).filter(
            LessonProgress.student_id == student.id,
            LessonProgress.is_completed == True,
            CourseModule.course_id == course.id,
            CourseModule.is_active == True,
            Lesson.is_active == True
        ).scalar() or 0

        progress = round(
            completed_lessons / total_lessons * 100
        ) if total_lessons else 0
        progress = max(0, min(100, progress))

        result.append({
            "id": item.id,
            "course_id": course.id,
            "name": course.name,
            "description": course.description,
            "progress": progress,
            "modules_count": modules_count,
            "enrolled_at": item.enrolled_at
        })

    return result
