from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import require_admin

from app.models.admin import Admin
from app.models.student import Student
from app.models.student_course import StudentCourse
from app.models.course import Course
from app.models.group import Group
from app.models.student_group import StudentGroup
from app.models.attendance import Attendance
from app.models.grade import Grade
from app.models.teacher import Teacher
from app.models.homework import Homework
from app.models.homework import HomeworkSubmission
from app.models.gamification import StudentGamification


router = APIRouter(
    prefix="/admin/students",
    tags=["Admin Students"]
)


# =========================================================
# STUDENTS LIST
# =========================================================

@router.get("/")
def get_students(
    search: str | None = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    query = db.query(Student)

    if active_only:
        query = query.filter(
            Student.is_active == True
        )

    if search:
        search_value = f"%{search}%"

        query = query.filter(
            (Student.full_name.ilike(search_value)) |
            (Student.phone.ilike(search_value))
        )

    students = query.order_by(
        Student.id.desc()
    ).all()

    result = []

    for student in students:

        enrollments = db.query(StudentCourse).filter(
            StudentCourse.student_id == student.id,
            StudentCourse.is_active == True
        ).all()

        courses = []

        for enrollment in enrollments:
            course = db.query(Course).filter(
                Course.id == enrollment.course_id
            ).first()

            if course:
                courses.append({
                    "id": course.id,
                    "name": course.name,
                    "progress": enrollment.progress
                })

        result.append({
            "id": student.id,
            "full_name": student.full_name,
            "phone": student.phone,
            "role": student.role,
            "is_active": student.is_active,
            "courses": courses
        })

    return {
        "success": True,
        "total": len(result),
        "students": result
    }


# =========================================================
# STUDENT PROFILE
# =========================================================

@router.get("/{student_id}")
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    enrollments = db.query(StudentCourse).filter(
        StudentCourse.student_id == student.id
    ).all()

    courses = []

    for enrollment in enrollments:

        course = db.query(Course).filter(
            Course.id == enrollment.course_id
        ).first()

        if course:
            courses.append({
                "id": course.id,
                "name": course.name,
                "progress": enrollment.progress,
                "is_active": enrollment.is_active,
                "enrolled_at": enrollment.enrolled_at
            })

    return {
        "success": True,

        "student": {
            "id": student.id,
            "full_name": student.full_name,
            "phone": student.phone,
            "role": student.role,
            "is_active": student.is_active
        },

        "courses": courses
    }


# =========================================================
# DEACTIVATE STUDENT
# =========================================================

@router.put("/{student_id}/deactivate")
def deactivate_student(
    student_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    student.is_active = False

    db.commit()

    return {
        "success": True,
        "message": "O'quvchi deaktiv qilindi",
        "student_id": student.id
    }


# =========================================================
# ACTIVATE STUDENT
# =========================================================

@router.put("/{student_id}/activate")
def activate_student(
    student_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    student.is_active = True

    db.commit()

    return {
        "success": True,
        "message": "O'quvchi qayta faollashtirildi",
        "student_id": student.id
    }

# =========================================================
# FULL STUDENT PROFILE
# =========================================================

@router.get("/{student_id}/profile")
def get_student_full_profile(
    student_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    # -----------------------------------------------------
    # STUDENT
    # -----------------------------------------------------

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    # -----------------------------------------------------
    # COURSES
    # -----------------------------------------------------

    enrollments = db.query(StudentCourse).filter(
        StudentCourse.student_id == student_id
    ).all()

    courses = []

    for enrollment in enrollments:

        course = db.query(Course).filter(
            Course.id == enrollment.course_id
        ).first()

        if course:
            courses.append({
                "id": course.id,
                "name": course.name,
                "progress": enrollment.progress,
                "is_active": enrollment.is_active,
                "enrolled_at": enrollment.enrolled_at
            })

    # -----------------------------------------------------
    # GROUPS
    # -----------------------------------------------------

    student_groups = db.query(StudentGroup).filter(
        StudentGroup.student_id == student_id,
        StudentGroup.is_active == True
    ).all()

    groups = []

    for membership in student_groups:

        group = db.query(Group).filter(
            Group.id == membership.group_id
        ).first()

        if not group:
            continue

        course = db.query(Course).filter(
            Course.id == group.course_id
        ).first()

        teacher = db.query(Teacher).filter(
            Teacher.id == group.teacher_id
        ).first()

        groups.append({
            "id": group.id,
            "name": group.name,
            "course": course.name if course else None,
            "teacher": teacher.full_name if teacher else None,
            "room": group.room,
            "start_date": group.start_date,
            "status": group.status,
            "is_active": membership.is_active,
            "joined_at": membership.joined_at
        })

    # -----------------------------------------------------
    # ATTENDANCE
    # -----------------------------------------------------

    attendance_records = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).order_by(
        Attendance.date.desc()
    ).all()

    attendance = []

    present_count = 0
    absent_count = 0
    late_count = 0

    for record in attendance_records:

        status = record.status

        if status == "present":
            present_count += 1

        elif status == "absent":
            absent_count += 1

        elif status == "late":
            late_count += 1

        attendance.append({
            "id": record.id,
            "group_id": record.group_id,
            "date": record.date,
            "status": record.status,
            "note": record.note
        })

    # -----------------------------------------------------
    # GRADES
    # -----------------------------------------------------

    grade_records = db.query(Grade).filter(
        Grade.student_id == student_id
    ).order_by(
        Grade.created_at.desc()
    ).all()

    grades = []

    for grade in grade_records:

        teacher = db.query(Teacher).filter(
            Teacher.id == grade.teacher_id
        ).first()

        grades.append({
            "id": grade.id,
            "title": grade.title,
            "score": grade.score,
            "max_score": grade.max_score,
            "comment": grade.comment,
            "teacher": teacher.full_name if teacher else None,
            "group_id": grade.group_id,
            "created_at": grade.created_at
        })

    # -----------------------------------------------------
    # HOMEWORK
    # -----------------------------------------------------

    submissions = db.query(
        HomeworkSubmission
    ).filter(
        HomeworkSubmission.student_id == student_id
    ).order_by(
        HomeworkSubmission.submitted_at.desc()
    ).all()

    homework = []

    for submission in submissions:

        assignment = db.query(Homework).filter(
            Homework.id == submission.homework_id
        ).first()

        if not assignment:
            continue

        homework.append({
            "submission_id": submission.id,
            "homework_id": assignment.id,
            "title": assignment.title,
            "status": submission.status,
            "score": submission.score,
            "teacher_comment": submission.teacher_comment,
            "submitted_at": submission.submitted_at,
            "checked_at": submission.checked_at
        })

    # -----------------------------------------------------
    # GAMIFICATION
    # -----------------------------------------------------

    game = db.query(StudentGamification).filter(
        StudentGamification.student_id == student_id
    ).first()

    if game:
        gamification = {
            "xp": game.xp,
            "level": game.level,
            "coins": game.coins,
            "crystals": game.crystals,
            "streak_days": game.streak_days,
            "last_activity_at": game.last_activity_at
        }
    else:
        gamification = {
            "xp": 0,
            "level": 1,
            "coins": 0,
            "crystals": 0,
            "streak_days": 0,
            "last_activity_at": None
        }

    # -----------------------------------------------------
    # ATTENDANCE SUMMARY
    # -----------------------------------------------------

    total_attendance = len(attendance_records)

    attendance_rate = 0

    if total_attendance > 0:
        attendance_rate = round(
            (present_count / total_attendance) * 100,
            1
        )

    # -----------------------------------------------------
    # FINAL PROFILE
    # -----------------------------------------------------

    return {
        "success": True,

        "student": {
            "id": student.id,
            "full_name": student.full_name,
            "phone": student.phone,
            "role": student.role,
            "is_active": student.is_active
        },

        "courses": courses,

        "groups": groups,

        "attendance": {
            "total": total_attendance,
            "present": present_count,
            "absent": absent_count,
            "late": late_count,
            "rate": attendance_rate,
            "records": attendance
        },

        "grades": grades,

        "homework": homework,

        "gamification": gamification
    }
