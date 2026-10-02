from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import create_access_token, decode_token, check_login_rate_limit, record_login_failure, clear_login_failures
from app.models.parent import Parent, ParentStudent
from app.models.student import Student
from app.models.student_course import StudentCourse
from app.models.course import Course
from app.models.student_group import StudentGroup
from app.models.group import Group
from app.models.teacher import Teacher
from app.models.attendance import Attendance
from app.models.grade import Grade
from app.models.homework import Homework, HomeworkSubmission
from app.models.schedule import Schedule
from app.models.lesson_progress import LessonProgress
from app.models.gamification import StudentGamification

router = APIRouter(prefix="/parents", tags=["Parents"])
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_parent(credentials: HTTPAuthorizationCredentials, db: Session):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "parent":
        raise HTTPException(status_code=401, detail="Ota-ona tokeni noto'g'ri yoki muddati tugagan")
    parent = db.query(Parent).filter(Parent.id == payload["user_id"], Parent.is_active == True).first()
    if not parent:
        raise HTTPException(status_code=403, detail="Ota-ona akkaunti faol emas")
    return parent


def _children(db, parent_id):
    return db.query(Student).join(ParentStudent, ParentStudent.student_id == Student.id).filter(
        ParentStudent.parent_id == parent_id, Student.is_active == True
    ).order_by(Student.full_name.asc()).all()


def _next_lesson(db, student_id):
    membership = db.query(StudentGroup).filter(
        StudentGroup.student_id == student_id, StudentGroup.is_active == True
    ).all()
    now = datetime.now(ZoneInfo("Asia/Tashkent"))
    # Python weekday: Monday=0. Platform weekday is stored as 0..6.
    candidates = []
    for item in membership:
        group = db.query(Group).filter(Group.id == item.group_id, Group.is_active == True).first()
        if not group:
            continue
        rows = db.query(Schedule).filter(Schedule.group_id == group.id, Schedule.is_active == True).all()
        for s in rows:
            delta = (s.weekday - now.weekday()) % 7
            if delta == 0 and s.start_time <= now.time():
                delta = 7
            candidates.append((delta, s.start_time, group, s))
    if not candidates:
        return None
    _, start, group, schedule = sorted(candidates, key=lambda x: (x[0], x[1]))[0]
    return {
        "group": group.name,
        "weekday": schedule.weekday,
        "start_time": start.strftime("%H:%M"),
        "end_time": schedule.end_time.strftime("%H:%M"),
        "room": schedule.room,
    }


@router.post("/login")
def login_parent(payload: dict, db: Session = Depends(get_db)):
    phone = str(payload.get("phone") or "").strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if phone.startswith("+"):
        phone = phone[1:]
    password = str(payload.get("password") or "")
    if not phone or not password:
        raise HTTPException(status_code=400, detail="Telefon raqam va parolni kiriting")
    check_login_rate_limit(phone)
    parent = db.query(Parent).filter(Parent.phone == phone).first()
    if not parent or not pwd_context.verify(password, parent.password_hash):
        record_login_failure(phone)
        raise HTTPException(status_code=401, detail="Telefon raqam yoki parol noto'g'ri")
    if not parent.is_active:
        record_login_failure(phone)
        raise HTTPException(status_code=403, detail="Ota-ona akkaunti faol emas")
    clear_login_failures(phone)
    token = create_access_token({"sub": str(parent.id), "role": "parent", "av": int(parent.auth_version or 1)})
    return {"message": "Login muvaffaqiyatli", "access_token": token, "token_type": "bearer", "parent_id": parent.id, "full_name": parent.full_name, "role": "parent"}


@router.get("/me")
def parent_me(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    parent = get_parent(credentials, db)
    children = _children(db, parent.id)
    return {"id": parent.id, "full_name": parent.full_name, "phone": parent.phone, "children": [{"id": s.id, "full_name": s.full_name} for s in children]}


@router.get("/dashboard")
def parent_dashboard(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    parent = get_parent(credentials, db)
    children = _children(db, parent.id)
    result = []
    for student in children:
        active_courses = db.query(StudentCourse).filter(StudentCourse.student_id == student.id, StudentCourse.is_active == True).all()
        progress_values = []
        for enrollment in active_courses:
            # Use the enrollment's stored progress as a stable parent-facing summary.
            progress_values.append(float(enrollment.progress or 0))
        progress = round(sum(progress_values) / len(progress_values)) if progress_values else 0

        today = datetime.now(ZoneInfo("Asia/Tashkent")).date()
        today_attendance = db.query(Attendance).filter(Attendance.student_id == student.id, Attendance.date == today).order_by(Attendance.id.desc()).first()
        grades = db.query(Grade).filter(Grade.student_id == student.id).order_by(Grade.created_at.desc()).all()
        latest_grade = grades[0] if grades else None
        homework_rows = db.query(HomeworkSubmission, Homework).join(Homework, Homework.id == HomeworkSubmission.homework_id).filter(HomeworkSubmission.student_id == student.id).order_by(HomeworkSubmission.submitted_at.desc()).all()
        latest_homework = homework_rows[0] if homework_rows else None
        comment = None
        if latest_homework:
            comment = latest_homework[0].teacher_comment
        if not comment and latest_grade:
            comment = latest_grade.comment
        next_lesson = _next_lesson(db, student.id)
        gamification = db.query(StudentGamification).filter(StudentGamification.student_id == student.id).first()
        # Store completed lesson counts by Tashkent calendar date for the latest 7 days.
        today_local = datetime.now(ZoneInfo("Asia/Tashkent")).date()
        activity_start = today_local - timedelta(days=6)
        completed_rows = db.query(LessonProgress.completed_at).filter(
            LessonProgress.student_id == student.id,
            LessonProgress.is_completed == True,
            LessonProgress.completed_at.isnot(None),
        ).all()
        activity_counts = {activity_start + timedelta(days=i): 0 for i in range(7)}
        for (completed_at,) in completed_rows:
            stamp = completed_at
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=timezone.utc)
            local_day = stamp.astimezone(ZoneInfo("Asia/Tashkent")).date()
            if local_day in activity_counts:
                activity_counts[local_day] += 1
        daily_activity = [
            {"date": day.isoformat(), "weekday": ["Du", "Se", "Cho", "Pay", "Ju", "Sha", "Ya"][day.weekday()], "completed_lessons": activity_counts[day]}
            for day in sorted(activity_counts)
        ]
        courses = []
        for enrollment in active_courses:
            course = db.query(Course).filter(Course.id == enrollment.course_id, Course.is_active == True).first()
            if course:
                courses.append({"id": course.id, "name": course.name, "progress": round(float(enrollment.progress or 0))})
        result.append({
            "id": student.id,
            "full_name": student.full_name,
            "today_attendance": today_attendance.status if today_attendance else "unknown",
            "progress": progress,
            "coins": int(gamification.coins or 0) if gamification else 0,
            "xp": int(gamification.xp or 0) if gamification else 0,
            "level": int(gamification.level or 1) if gamification else 1,
            "daily_activity": daily_activity,
            "latest_grade": round((latest_grade.score / latest_grade.max_score) * 100, 1) if latest_grade and latest_grade.max_score else None,
            "latest_grade_title": latest_grade.title if latest_grade else None,
            "teacher_comment": comment,
            "next_lesson": next_lesson,
            "courses": courses,
            "homework": {
                "title": latest_homework[1].title,
                "score": latest_homework[0].score,
                "status": latest_homework[0].status,
                "teacher_comment": latest_homework[0].teacher_comment,
            } if latest_homework else None,
        })
    return {"success": True, "parent": {"id": parent.id, "full_name": parent.full_name}, "children": result}
