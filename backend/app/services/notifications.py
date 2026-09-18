from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.notification import Notification


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

    db.commit()
