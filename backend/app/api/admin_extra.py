from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db import get_db
from app.core.security import require_admin
from app.models.admin import Admin
from app.models.podcast import Podcast
from app.models.training import Training, TrainingRegistration
from app.models.exam import Exam, ExamRegistration
from app.services.notifications import notify_all_students

router = APIRouter(prefix="/admin/content", tags=["Admin Content"])

class PodcastData(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    audio_url: str = ""
    duration_minutes: int | None = Field(default=None, ge=0)

class EventData(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    start_at: str
    end_at: str | None = None
    location: str = ""
    capacity: int | None = Field(default=None, ge=1)

def dt(value):
    try:
        return __import__("datetime").datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        raise HTTPException(status_code=400, detail="Sana vaqti ISO formatda bo'lishi kerak")


def validate_event_times(start_at, end_at):
    start = dt(start_at)
    end = dt(end_at) if end_at else None
    if end is not None and end <= start:
        raise HTTPException(status_code=400, detail="Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak")
    return start, end

@router.get("/podcasts")
def admin_podcasts(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    return [{"id": x.id, "title": x.title, "description": x.description, "audio_url": x.audio_url,
             "duration_minutes": x.duration_minutes, "is_active": x.is_active}
            for x in db.query(Podcast).order_by(Podcast.id.desc()).all()]

@router.post("/podcasts")
def create_podcast(data: PodcastData, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    x = Podcast(**data.model_dump())
    db.add(x); db.commit(); db.refresh(x)
    notify_all_students(
        db,
        "Yangi podcast qo‘shildi",
        "“" + x.title + "” podcasti Student kabinetida mavjud.",
        "podcast",
    )
    return {"success": True, "podcast": {"id": x.id, "title": x.title}}

@router.put("/podcasts/{podcast_id}/toggle")
def toggle_podcast(podcast_id: int, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    x = db.query(Podcast).filter(Podcast.id == podcast_id).with_for_update().first()
    if not x: raise HTTPException(status_code=404, detail="Podcast topilmadi")
    x.is_active = not x.is_active; db.commit()
    return {"success": True, "is_active": x.is_active}

@router.get("/trainings")
def admin_trainings(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    items = db.query(Training).order_by(Training.start_at.asc()).all()
    return [{"id": x.id, "title": x.title, "description": x.description, "start_at": x.start_at,
             "end_at": x.end_at, "location": x.location, "capacity": x.capacity, "is_active": x.is_active,
             "registrations": db.query(TrainingRegistration).filter(
                 TrainingRegistration.training_id == x.id,
                 TrainingRegistration.status == "registered"
             ).count()}
            for x in items]

@router.post("/trainings")
def create_training(data: EventData, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    start_at, end_at = validate_event_times(data.start_at, data.end_at)
    x = Training(title=data.title, description=data.description, start_at=start_at,
                 end_at=end_at, location=data.location, capacity=data.capacity)
    db.add(x); db.commit(); db.refresh(x)
    notify_all_students(
        db,
        "Yangi trening qo‘shildi",
        "“" + x.title + "” treningi Student kabinetida mavjud.",
        "training",
    )
    return {"success": True, "training": {"id": x.id, "title": x.title}}

@router.get("/trainings/registrations")
def training_registrations(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    return [{"id": x.id, "training_id": x.training_id, "student_id": x.student_id, "status": x.status, "registered_at": x.registered_at}
            for x in db.query(TrainingRegistration).order_by(TrainingRegistration.id.desc()).all()]

@router.put("/trainings/{training_id}/toggle")
def toggle_training(training_id: int, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    x = db.query(Training).filter(Training.id == training_id).with_for_update().first()
    if not x: raise HTTPException(status_code=404, detail="Trening topilmadi")
    if not x.is_active and x.end_at is not None and x.end_at <= __import__("datetime").datetime.utcnow():
        raise HTTPException(status_code=400, detail="Muddati tugagan treningni qayta faollashtirib bo‘lmaydi")
    x.is_active = not x.is_active; db.commit()
    return {"success": True, "is_active": x.is_active}

@router.get("/exams")
def admin_exams(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    items = db.query(Exam).order_by(Exam.start_at.asc()).all()
    return [{"id": x.id, "title": x.title, "description": x.description, "start_at": x.start_at,
             "end_at": x.end_at, "location": x.location, "capacity": x.capacity, "is_active": x.is_active,
             "registrations": db.query(ExamRegistration).filter(ExamRegistration.exam_id == x.id, ExamRegistration.status == "registered").count()}
            for x in items]

@router.post("/exams")
def create_exam(data: EventData, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    start_at, end_at = validate_event_times(data.start_at, data.end_at)
    x = Exam(title=data.title, description=data.description, start_at=start_at,
             end_at=end_at, location=data.location, capacity=data.capacity)
    db.add(x); db.commit(); db.refresh(x)
    notify_all_students(
        db,
        "Yangi imtihon qo‘shildi",
        "“" + x.title + "” imtihoni Student kabinetida mavjud.",
        "exam",
    )
    return {"success": True, "exam": {"id": x.id, "title": x.title}}

@router.get("/exams/registrations")
def exam_registrations(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    return [{"id": x.id, "exam_id": x.exam_id, "student_id": x.student_id, "status": x.status, "registered_at": x.registered_at}
            for x in db.query(ExamRegistration).order_by(ExamRegistration.id.desc()).all()]

@router.put("/exams/{exam_id}/toggle")
def toggle_exam(exam_id: int, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    x = db.query(Exam).filter(Exam.id == exam_id).with_for_update().first()
    if not x: raise HTTPException(status_code=404, detail="Imtihon topilmadi")
    if not x.is_active and x.end_at is not None and x.end_at <= __import__("datetime").datetime.utcnow():
        raise HTTPException(status_code=400, detail="Muddati tugagan imtihonni qayta faollashtirib bo‘lmaydi")
    x.is_active = not x.is_active; db.commit()
    return {"success": True, "is_active": x.is_active}
