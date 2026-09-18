from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import verify_token
from app.models.notification import Notification

router = APIRouter(prefix="/students/notifications", tags=["Student Notifications"])
security = HTTPBearer()


def get_student_id(credentials: HTTPAuthorizationCredentials) -> int:
    student_id = verify_token(credentials.credentials)
    if not student_id:
        raise HTTPException(status_code=401, detail="Token noto'g'ri yoki muddati tugagan")
    return int(student_id)


@router.get("")
def get_notifications(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    student_id = get_student_id(credentials)
    items = db.query(Notification).filter(
        Notification.student_id == student_id
    ).order_by(
        Notification.id.desc()
    ).limit(30).all()

    unread = sum(1 for item in items if not item.is_read)

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
    student_id = get_student_id(credentials)
    item = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.student_id == student_id,
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Bildirishnoma topilmadi")

    item.is_read = True
    db.commit()

    return {"success": True, "notification_id": item.id}
