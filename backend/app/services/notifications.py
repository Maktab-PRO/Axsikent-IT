from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.notification import Notification
from app.models.student_group import StudentGroup


def _safe_commit(db: Session):
    try:
        _safe_commit(db)
    except Exception:
        db.rollback()


def notify_all_students(
    db: Session,
    title: str,
    message: str,
    notification_type: str = "content",
):
    students = db.query(Student).filter(
        Student.is_active == True
    ).all()

    for student in students:
        db.add(
            Notification(
                student_id=student.id,
                title=title,
                message=message,
                notification_type=notification_type,
                is_read=False,
            )
        )

    _safe_commit(db)


def notify_group_students(
    db: Session,
    group_id: int,
    title: str,
    message: str,
    notification_type: str = "homework",
):
    student_ids = db.query(StudentGroup.student_id).join(
        Student,
        Student.id == StudentGroup.student_id
    ).filter(
        StudentGroup.group_id == group_id,
        StudentGroup.is_active == True,
        Student.is_active == True,
    ).all()

    for (student_id,) in student_ids:
        db.add(
            Notification(
                student_id=student_id,
                title=title,
                message=message,
                notification_type=notification_type,
                is_read=False,
            )
        )

    _safe_commit(db)


def notify_student(
    db: Session,
    student_id: int,
    title: str,
    message: str,
    notification_type: str = "content",
):
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True,
    ).first()
    if not student:
        return

    db.add(Notification(
        student_id=student_id,
        title=title,
        message=message,
        notification_type=notification_type,
        is_read=False,
    ))
    _safe_commit(db)
