from datetime import datetime, timezone, timedelta
from math import ceil
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from app.db import get_db
from app.models.student import Student
from app.models.gamification import StudentGamification
from app.models.student_course import StudentCourse
from app.models.course import Course
from app.models.course_module import CourseModule
from app.models.lesson import Lesson
from app.models.lesson_quiz import LessonQuiz
from app.models.student_lesson import StudentLesson
from app.models.lesson_progress import LessonProgress
from app.models.reward_rule import RewardRule
from app.models.reward_transaction import RewardTransaction
from app.models.achievement import Achievement, StudentAchievement
from app.schemas.student import StudentCreate, StudentLogin, StudentResponse
from app.core.security import create_access_token, decode_token


router = APIRouter(prefix="/students", tags=["Students"])

security = HTTPBearer()


def lesson_is_available_to_student(db: Session, student_id: int, lesson_id: int) -> bool:
    """Teacher-assigned lessons are visible only to their assigned student.
    Normal lessons (without StudentLesson rows) remain visible to enrolled students.
    """
    assignments = db.query(StudentLesson).filter(
        StudentLesson.lesson_id == lesson_id
    ).all()
    if not assignments:
        return True
    return any(item.student_id == student_id for item in assignments)

def lesson_is_unlocked_to_student(db: Session, student_id: int, course_id: int, lesson_id: int) -> bool:
    rows = db.query(Lesson, CourseModule).join(CourseModule, Lesson.module_id == CourseModule.id).filter(CourseModule.course_id == course_id, CourseModule.is_active == True, Lesson.is_active == True).order_by(CourseModule.sort_order.asc(), CourseModule.id.asc(), Lesson.sort_order.asc(), Lesson.id.asc()).all()
    ordered = [lesson for lesson, _module in rows if lesson_is_available_to_student(db, student_id, lesson.id)]
    previous_id = None
    for lesson in ordered:
        if lesson.id == lesson_id:
            if previous_id is None:
                return True
            return db.query(LessonProgress).filter(LessonProgress.student_id == student_id, LessonProgress.lesson_id == previous_id).filter((LessonProgress.is_completed == True) | (LessonProgress.homework_passed == True)).first() is not None
        previous_id = lesson.id
    return False


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


def _apply_lesson_gamification_rewards(db: Session, student_id: int, lesson_id: int):
    rules = db.query(RewardRule).filter(
        RewardRule.is_active == True,
        RewardRule.action_type == "lesson_completed"
    ).all()
    for rule in rules:
        exists = db.query(RewardTransaction).filter(
            RewardTransaction.student_id == student_id,
            RewardTransaction.reward_type == rule.reward_type,
            RewardTransaction.reason == rule.name,
            RewardTransaction.reference_type == "lesson_completed",
            RewardTransaction.reference_id == lesson_id,
        ).first()
        if exists:
            continue
        amount = max(0, int(rule.reward_amount or 0))
        gamification = db.query(StudentGamification).filter(
            StudentGamification.student_id == student_id
        ).with_for_update().first()
        if not gamification:
            continue
        if rule.reward_type == "coin":
            gamification.coins = (gamification.coins or 0) + amount
        elif rule.reward_type == "crystal":
            gamification.crystals = (gamification.crystals or 0) + amount
        else:
            continue
        db.add(RewardTransaction(
            student_id=student_id,
            reward_type=rule.reward_type,
            amount=amount,
            reason=rule.name,
            reference_type="lesson_completed",
            reference_id=lesson_id,
        ))


def _check_lesson_achievements(db: Session, student_id: int):
    completed_count = db.query(func.count(func.distinct(LessonProgress.lesson_id))).filter(
        LessonProgress.student_id == student_id,
        LessonProgress.is_completed == True,
    ).scalar() or 0
    milestones = {
        1: ("Birinchi qadam", "Birinchi darsni tugatdingiz.", "🥇", 10, 5, 0),
        5: ("5 dars", "5 ta darsni tugatdingiz.", "🔥", 20, 10, 0),
        10: ("10 dars", "10 ta darsni tugatdingiz.", "🏆", 40, 20, 1),
        25: ("25 dars", "25 ta darsni tugatdingiz.", "💎", 100, 50, 3),
    }
    for threshold, data in milestones.items():
        if completed_count < threshold:
            continue
        name, description, icon, xp_reward, coin_reward, crystal_reward = data
        achievement = db.query(Achievement).filter(Achievement.name == name).first()
        if not achievement:
            achievement = Achievement(
                name=name, description=description, icon=icon,
                xp_reward=xp_reward, coin_reward=coin_reward,
                crystal_reward=crystal_reward, is_active=True
            )
            db.add(achievement)
            db.flush()
        if not achievement.is_active:
            continue
        earned = db.query(StudentAchievement).filter(
            StudentAchievement.student_id == student_id,
            StudentAchievement.achievement_id == achievement.id,
        ).first()
        if earned:
            continue
        gamification = db.query(StudentGamification).filter(
            StudentGamification.student_id == student_id
        ).with_for_update().first()
        if not gamification:
            continue
        gamification.xp = (gamification.xp or 0) + max(0, achievement.xp_reward or 0)
        gamification.coins = (gamification.coins or 0) + max(0, achievement.coin_reward or 0)
        gamification.crystals = (gamification.crystals or 0) + max(0, achievement.crystal_reward or 0)
        gamification.level = max(1, (gamification.xp // 100) + 1)
        db.add(StudentAchievement(
            student_id=student_id,
            achievement_id=achievement.id,
            earned_at=datetime.now(timezone.utc).isoformat(),
        ))


@router.get("/achievements")
def get_student_achievements(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    student_id = get_student_id(credentials, db)
    rows = db.query(StudentAchievement, Achievement).join(
        Achievement, Achievement.id == StudentAchievement.achievement_id
    ).filter(
        StudentAchievement.student_id == student_id,
        Achievement.is_active == True,
    ).order_by(StudentAchievement.id.desc()).all()
    return [
        {
            "id": achievement.id,
            "name": achievement.name,
            "description": achievement.description,
            "icon": achievement.icon,
            "xp_reward": achievement.xp_reward,
            "coin_reward": achievement.coin_reward,
            "crystal_reward": achievement.crystal_reward,
            "earned_at": earned.earned_at,
        }
        for earned, achievement in rows
    ]


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

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Bu telefon raqam allaqachon ro'yxatdan o'tgan"
        )
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
    lessons = [
        lesson for lesson in lessons
        if lesson_is_available_to_student(db, student_id, lesson.id)
    ]

    # Darslar ketma-ket ochiladi: birinchi dars ochiq,
    # keyingi dars esa undan oldingi faol dars tugagandan keyin ochiladi.
    course_lessons = db.query(Lesson, CourseModule).join(
        CourseModule,
        Lesson.module_id == CourseModule.id
    ).filter(
        CourseModule.course_id == course_id,
        CourseModule.is_active == True,
        Lesson.is_active == True
    ).order_by(
        CourseModule.sort_order.asc(),
        CourseModule.id.asc(),
        Lesson.sort_order.asc(),
        Lesson.id.asc()
    ).all()
    course_lessons = [
        (lesson, course_module) for lesson, course_module in course_lessons
        if lesson_is_available_to_student(db, student_id, lesson.id)
    ]

    completed_ids = {
        row[0]
        for row in db.query(LessonProgress.lesson_id).filter(
            LessonProgress.student_id == student_id,
            LessonProgress.is_completed == True
        ).all()
    }
    homework_passed_ids = {
        row[0]
        for row in db.query(LessonProgress.lesson_id).filter(
            LessonProgress.student_id == student_id,
            LessonProgress.homework_passed == True
        ).all()
    }
    unlock_progress_ids = completed_ids | homework_passed_ids

    unlocked_ids = set()
    previous_lesson_id = None

    for course_lesson, _module in course_lessons:
        if previous_lesson_id is None or previous_lesson_id in unlock_progress_ids:
            unlocked_ids.add(course_lesson.id)
        previous_lesson_id = course_lesson.id

    result = []
    progress_rows = db.query(LessonProgress).filter(
        LessonProgress.student_id == student_id,
        LessonProgress.lesson_id.in_([lesson.id for lesson in lessons])
    ).all() if lessons else []
    progress_map = {row.lesson_id: row for row in progress_rows}

    for lesson in lessons:
        progress_row = progress_map.get(lesson.id)
        completed = lesson.id in completed_ids
        locked = lesson.id not in unlocked_ids
        quiz_blocked = bool(progress_row.quiz_blocked) if progress_row else False
        quiz_failures = int(progress_row.quiz_failures or 0) if progress_row else 0
        quiz_passed = bool(progress_row.quiz_passed) if progress_row else False
        homework_passed = bool(progress_row.homework_passed) if progress_row else False
        result.append({
            "id": lesson.id,
            "module_id": lesson.module_id,
            "title": lesson.title,
            "content": lesson.content if not locked else None,
            "video_url": lesson.video_url if not locked else None,
            "sort_order": lesson.sort_order,
            "is_active": lesson.is_active,
            "completed": completed,
            "locked": locked,
            "lock_reason": "Avval oldingi darsni tugating" if locked else None,
            "quiz_passed": quiz_passed,
            "quiz_failures": quiz_failures,
            "quiz_blocked": quiz_blocked,
            "homework_passed": homework_passed
        })

    return result
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
    if not lesson_is_available_to_student(db, student_id, lesson_id):
        raise HTTPException(status_code=403, detail="Bu dars sizga biriktirilmagan")

    if not lesson_is_unlocked_to_student(db, student_id, course_id, lesson_id):
        raise HTTPException(status_code=403, detail="Avval oldingi darsni tugating")

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
    if not lesson_is_available_to_student(db, student_id, lesson_id):
        raise HTTPException(status_code=403, detail="Bu dars sizga biriktirilmagan")

    if not lesson_is_unlocked_to_student(db, student_id, course_id, lesson_id):
        raise HTTPException(status_code=403, detail="Avval oldingi darsni tugating")

    quizzes = db.query(LessonQuiz).filter(
        LessonQuiz.lesson_id == lesson_id,
        LessonQuiz.is_active == True
    ).all()

    if not quizzes:
        raise HTTPException(
            status_code=404,
            detail="Bu dars uchun tekshiruv hali qo'shilmagan"
        )

    progress = db.query(LessonProgress).filter(
        LessonProgress.student_id == student_id,
        LessonProgress.lesson_id == lesson_id
    ).first()
    quiz_failures = progress.quiz_failures if progress else 0
    quiz_blocked = bool(progress.quiz_blocked) if progress else False

    return [
        {
            "id": quiz.id,
            "question": quiz.question,
            "option_a": quiz.option_a,
            "option_b": quiz.option_b,
            "option_c": quiz.option_c,
            "option_d": quiz.option_d,
            "quiz_failures": quiz_failures,
            "quiz_blocked": quiz_blocked
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
    if not lesson_is_available_to_student(db, student_id, lesson_id):
        raise HTTPException(status_code=403, detail="Bu dars sizga biriktirilmagan")

    if not lesson_is_unlocked_to_student(db, student_id, course_id, lesson_id):
        raise HTTPException(status_code=403, detail="Avval oldingi darsni tugating")

    progress = db.query(LessonProgress).filter(
        LessonProgress.student_id == student_id,
        LessonProgress.lesson_id == lesson_id
    ).with_for_update().first()

    if not progress or not progress.is_read:
        raise HTTPException(
            status_code=400,
            detail="Avval darsni o'qib chiqing"
        )

    if progress.quiz_blocked:
        raise HTTPException(
            status_code=403,
            detail="Quiz 3 marta muvaffaqiyatsiz topshirildi. O'qituvchi tomonidan qayta ochilishi kerak."
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

    allowed_answer_ids = {str(quiz.id) for quiz in quizzes}
    unknown_answer_ids = [key for key in answers.keys() if str(key) not in allowed_answer_ids]
    if unknown_answer_ids:
        raise HTTPException(status_code=400, detail="Javoblar ushbu dars savollariga mos emas")

    score = 0

    for quiz in quizzes:
        answer = answers.get(str(quiz.id))

        if answer is not None and not isinstance(answer, str):
            raise HTTPException(
                status_code=400,
                detail="Quiz javob formati noto'g'ri"
            )

        if answer and answer.upper() == quiz.correct_answer.upper():
            score += 1

    total = len(quizzes)

    passed = score >= max(1, ceil(total * 0.8))

    # Bir marta muvaffaqiyatli o'tilgan test holatini qayta urinishda
    # noto'g'ri javoblar sabab bekor qilib yubormaymiz.
    if passed:
        progress.quiz_passed = True
    elif not progress.quiz_passed:
        progress.quiz_failures = (progress.quiz_failures or 0) + 1
        if progress.quiz_failures >= 3:
            progress.quiz_blocked = True

    current_quiz_passed = bool(progress.quiz_passed)
    current_quiz_blocked = bool(progress.quiz_blocked)

    db.commit()

    return {
        "passed": current_quiz_passed,
        "score": score,
        "total": total,
        "quiz_failures": progress.quiz_failures or 0,
        "quiz_blocked": current_quiz_blocked,
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
    if not lesson_is_available_to_student(db, student_id, lesson_id):
        raise HTTPException(status_code=403, detail="Bu dars sizga biriktirilmagan")

    if not lesson_is_unlocked_to_student(db, student_id, course_id, lesson_id):
        raise HTTPException(status_code=403, detail="Avval oldingi darsni tugating")

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
        total_lessons = db.query(Lesson).join(
            CourseModule,
            Lesson.module_id == CourseModule.id
        ).filter(
            CourseModule.course_id == course_id,
            CourseModule.is_active == True,
            Lesson.is_active == True
        ).count()
        completed_lessons = db.query(func.count(func.distinct(LessonProgress.lesson_id))).join(
            Lesson, LessonProgress.lesson_id == Lesson.id
        ).join(
            CourseModule, Lesson.module_id == CourseModule.id
        ).filter(
            LessonProgress.student_id == student_id,
            LessonProgress.is_completed == True,
            CourseModule.course_id == course_id,
            CourseModule.is_active == True,
            Lesson.is_active == True
        ).scalar() or 0
        current_progress = round(completed_lessons / total_lessons * 100) if total_lessons else 0
        current_progress = max(0, min(100, current_progress))
        student_course.progress = current_progress
        db.commit()
        return {
            "message": "Dars allaqachon tugallangan",
            "lesson_id": lesson_id,
            "course_id": course_id,
            "progress": current_progress
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
    ).with_for_update().first()
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

    # Yangi qatlam faqat yangi tugallangan darsdan keyin ishlaydi.
    _apply_lesson_gamification_rewards(db, student_id, lesson_id)
    _check_lesson_achievements(db, student_id)

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

    new_progress = round(completed_lessons / total_lessons * 100) if total_lessons else 0
    student_course.progress = max(0, min(100, new_progress))
    db.commit()
    db.refresh(progress)
    db.refresh(gamification)

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
