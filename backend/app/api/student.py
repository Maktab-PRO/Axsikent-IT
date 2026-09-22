from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from passlib.context import CryptContext

from app.db import get_db
from app.models.student import Student
from app.models.gamification import StudentGamification
from app.models.exam import Exam, ExamRegistration
from app.models.student_course import StudentCourse
from app.models.course import Course
from app.models.course_module import CourseModule
from app.models.lesson import Lesson
from app.models.lesson_quiz import LessonQuiz
from app.models.student_lesson import StudentLesson
from app.models.lesson_progress import LessonProgress
from app.schemas.student import StudentCreate, StudentLogin, StudentResponse
from app.core.security import create_access_token, decode_token


router = APIRouter(prefix="/students", tags=["Students"])

security = HTTPBearer()


def get_student_id(credentials: HTTPAuthorizationCredentials, db: Session):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "student":
        raise HTTPException(status_code=401, detail="Student token noto'g'ri yoki muddati tugagan")

    student = db.query(Student).filter(
        Student.id == payload["user_id"],
        Student.is_active == True
    ).first()
    if not student:
        raise HTTPException(status_code=403, detail="O'quvchi akkaunti faol emas")

    return student.id

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
    db.flush()

    # Har bir yangi o'quvchi uchun gamification profili darhol yaratiladi.
    # Shu sabab Ranking, Coin/XP va Mukofotlar birinchi kirishdayoq ishlaydi.
    db.add(StudentGamification(
        student_id=new_student.id,
        xp=0,
        level=1,
        coins=0,
        crystals=0,
        streak_days=0
    ))

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

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="O'quvchi akkaunti faol emas"
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

@router.get("/exams")
def student_exams(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    student_id = get_student_id(credentials, db)
    exams = db.query(Exam).filter(
        Exam.is_active == True
    ).order_by(Exam.start_at.asc()).all()

    result = []
    for exam in exams:
        registration = db.query(ExamRegistration).filter(
            ExamRegistration.exam_id == exam.id,
            ExamRegistration.student_id == student_id
        ).first()
        result.append({
            "id": exam.id,
            "title": exam.title,
            "description": exam.description,
            "start_at": exam.start_at.isoformat() if exam.start_at else None,
            "end_at": exam.end_at.isoformat() if exam.end_at else None,
            "location": exam.location,
            "capacity": exam.capacity,
            "registrations": db.query(ExamRegistration).filter(
                ExamRegistration.exam_id == exam.id
            ).count(),
            "is_registered": bool(registration),
            "registration_status": registration.status if registration else None
        })

    return result


@router.get("/me")
def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    student_id = get_student_id(credentials, db)

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

    student_id = get_student_id(credentials, db)

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

    result = []

    for student_course, course in student_courses:
        # Kurs progressini saqlangan qiymatdan emas, amaldagi faol darslardan
        # qayta hisoblaymiz. Shunda admin dars qo'shsa/o'chirsa ham student
        # kabinetidagi foiz eskirib qolmaydi.
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
            LessonProgress.student_id == student_id,
            LessonProgress.is_completed == True,
            CourseModule.course_id == course.id,
            CourseModule.is_active == True,
            Lesson.is_active == True
        ).scalar() or 0

        progress = round(completed_lessons / total_lessons * 100) if total_lessons else 0
        progress = max(0, min(100, progress))

        result.append({
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
            "progress": progress,
            "enrolled_at": student_course.enrolled_at
        })

    return result
@router.get("/courses/{course_id}/modules")
def get_course_modules(
    course_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    student_id = get_student_id(credentials, db)

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

        completed_lessons = db.query(
            func.count(func.distinct(LessonProgress.lesson_id))
        ).join(
            Lesson,
            LessonProgress.lesson_id == Lesson.id
        ).filter(
            LessonProgress.student_id == student_id,
            LessonProgress.is_completed == True,
            Lesson.module_id == module.id,
            Lesson.is_active == True
        ).scalar() or 0

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

    student_id = get_student_id(credentials, db)

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
@router.post("/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/read")
def mark_lesson_as_read(
    course_id: int,
    module_id: int,
    lesson_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    student_id = get_student_id(credentials, db)

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

    if not progress:
        progress = LessonProgress(
            student_id=student_id,
            lesson_id=lesson_id,
            is_read=True
        )
        db.add(progress)
    else:
        progress.is_read = True

    has_quiz = db.query(LessonQuiz).filter(
        LessonQuiz.lesson_id == lesson_id,
        LessonQuiz.is_active == True
    ).first() is not None

    db.commit()

    return {
        "message": "Dars o'qilgan deb belgilandi",
        "lesson_id": lesson_id,
        "is_read": True,
        "has_quiz": has_quiz,
        "quiz_passed": progress.quiz_passed,
        "is_completed": progress.is_completed
    }

@router.get("/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/quiz")
def get_lesson_quiz(
    course_id: int,
    module_id: int,
    lesson_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    student_id = get_student_id(credentials, db)

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

    quizzes = db.query(LessonQuiz).filter(
        LessonQuiz.lesson_id == lesson_id,
        LessonQuiz.is_active == True
    ).all()

    if not quizzes:
        raise HTTPException(
            status_code=404,
            detail="Bu dars uchun tekshiruv hali qo'shilmagan"
        )

    return [
        {
            "id": quiz.id,
            "question": quiz.question,
            "option_a": quiz.option_a,
            "option_b": quiz.option_b,
            "option_c": quiz.option_c,
            "option_d": quiz.option_d
        }
        for quiz in quizzes
    ]

@router.post("/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/quiz")
def submit_lesson_quiz(
    course_id: int,
    module_id: int,
    lesson_id: int,
    answers: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    student_id = get_student_id(credentials, db)

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

    if not progress or not progress.is_read:
        raise HTTPException(
            status_code=400,
            detail="Avval darsni o'qib chiqing"
        )

    quizzes = db.query(LessonQuiz).filter(
        LessonQuiz.lesson_id == lesson_id,
        LessonQuiz.is_active == True
    ).all()

    if not quizzes:
        raise HTTPException(
            status_code=404,
            detail="Bu dars uchun tekshiruv mavjud emas"
        )

    score = 0

    for quiz in quizzes:
        answer = answers.get(str(quiz.id))

        if answer and answer.upper() == quiz.correct_answer.upper():
            score += 1

    total = len(quizzes)

    passed = score == total

    # Bir marta muvaffaqiyatli o'tilgan test holatini qayta urinishda
    # noto'g'ri javoblar sabab bekor qilib yubormaymiz.
    if passed:
        progress.quiz_passed = True

    current_quiz_passed = bool(progress.quiz_passed)

    db.commit()

    return {
        "passed": current_quiz_passed,
        "score": score,
        "total": total,
        "message": (
            "✅ Tekshiruvdan muvaffaqiyatli o'tdingiz"
            if current_quiz_passed
            else "❌ Javoblarda xatolik bor. Qayta urinib ko'ring."
        )
    }

@router.post("/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/complete")
def complete_lesson(
    course_id: int,
    module_id: int,
    lesson_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    student_id = get_student_id(credentials, db)

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
    ).with_for_update().first()

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

    if not progress:
        raise HTTPException(
            status_code=400,
            detail="Avval darsni o'qib chiqing va tekshiruvdan o'ting"
        )

    if not progress.is_read:
        raise HTTPException(
            status_code=400,
            detail="Avval darsni o'qib chiqing"
        )

    has_quiz = db.query(LessonQuiz).filter(
        LessonQuiz.lesson_id == lesson_id,
        LessonQuiz.is_active == True
    ).first() is not None

    if has_quiz and not progress.quiz_passed:
        raise HTTPException(
            status_code=400,
            detail="Avval dars yakuniy tekshiruvdan o'ting"
        )

    if progress.is_completed:
        return {
            "message": "Dars allaqachon tugallangan",
            "lesson_id": lesson_id,
            "course_id": course_id,
            "progress": student_course.progress
        }

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

    # Har bir dars faqat bir marta XP beradi.
    # Shu sabab qayta bosish/race holatida XP takroran berilmaydi.
    gamification = db.query(StudentGamification).filter(
        StudentGamification.student_id == student_id
    ).first()
    if not gamification:
        gamification = StudentGamification(
            student_id=student_id,
            xp=0,
            level=1,
            coins=0,
            crystals=0,
            streak_days=0
        )
        db.add(gamification)
        db.flush()

    now_utc = datetime.now(timezone.utc)
    gamification.xp = (gamification.xp or 0) + 10
    gamification.level = max(1, (gamification.xp // 100) + 1)

    previous_activity = gamification.last_activity_at
    if previous_activity and previous_activity.tzinfo is None:
        previous_activity = previous_activity.replace(tzinfo=timezone.utc)

    if previous_activity:
        previous_date = previous_activity.astimezone(timezone.utc).date()
        today = now_utc.date()
        if previous_date == today:
            pass
        elif previous_date == today - timedelta(days=1):
            gamification.streak_days = (gamification.streak_days or 0) + 1
        else:
            gamification.streak_days = 1
    else:
        gamification.streak_days = 1

    gamification.last_activity_at = now_utc

    db.commit()
    db.refresh(progress)
    db.refresh(gamification)

    total_lessons = db.query(Lesson).join(
        CourseModule,
        Lesson.module_id == CourseModule.id
    ).filter(
        CourseModule.course_id == course_id,
        Lesson.is_active == True,
        CourseModule.is_active == True
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
        LessonProgress.student_id == student_id,
        LessonProgress.is_completed == True,
        CourseModule.course_id == course_id,
        Lesson.is_active == True,
        CourseModule.is_active == True
    ).scalar() or 0

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
