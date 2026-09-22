from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import decode_token
from app.models.student import Student
from app.models.notification import Notification

router = APIRouter(prefix="/students/notifications", tags=["Student Notifications"])
security = HTTPBearer()


def get_student_id(
    credentials: HTTPAuthorizationCredentials,
    db: Session
) -> int:
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "student":
        raise HTTPException(
            status_code=401,
            detail="Student token noto'g'ri yoki muddati tugagan"
        )

    student_id = payload["user_id"]
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    return int(student_id)


@router.get("")
def get_notifications(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    student_id = get_student_id(credentials, db)
    items = db.query(Notification).filter(
        Notification.student_id == student_id
    ).order_by(
        Notification.id.desc()
    ).limit(30).all()

    unread = db.query(Notification).filter(
        Notification.student_id == student_id,
        Notification.is_read == False
    ).count()

    return {
        "unread": unread,
        "notifications": [
            {
                "id": item.id,
                "title": item.title,
                "message": item.message,
                "notification_type": item.notification_type,
                "is_read": item.is_read,
                "created_at": item.created_at,
            }
            for item in items
        ],
    }


@router.put("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    student_id = get_student_id(credentials, db)
    item = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.student_id == student_id,
    ).with_for_update().first()

    if not item:
        raise HTTPException(status_code=404, detail="Bildirishnoma topilmadi")

    item.is_read = True
    db.commit()

    return {"success": True, "notification_id": item.id}
