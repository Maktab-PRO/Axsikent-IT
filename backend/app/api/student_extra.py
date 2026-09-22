from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import get_db
from app.core.security import decode_token
from app.models.student import Student
from app.models.podcast import Podcast
from app.models.training import Training, TrainingRegistration
from app.models.exam import Exam, ExamRegistration

router = APIRouter(prefix="/students", tags=["Student Content"])
security = HTTPBearer()


def student_id_from_token(
    credentials,
    db: Session
):
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
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    return student_id


@router.get("/podcasts")
def get_podcasts(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    student_id = student_id_from_token(credentials, db)
    return [
        {"id": x.id, "title": x.title, "description": x.description, "audio_url": x.audio_url,
         "duration_minutes": x.duration_minutes}
        for x in db.query(Podcast).filter(Podcast.is_active == True).order_by(Podcast.id.desc()).all()
    ]


@router.get("/trainings")
def get_trainings(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    student_id = student_id_from_token(credentials, db)
    registrations = {
        x.training_id: x.status
        for x in db.query(TrainingRegistration).filter(TrainingRegistration.student_id == student_id).all()
    }
    return [
        {"id": x.id, "title": x.title, "description": x.description, "start_at": x.start_at,
         "end_at": x.end_at, "location": x.location, "capacity": x.capacity,
         "registered": registrations.get(x.id) == "registered", "registration_status": registrations.get(x.id)}
        for x in db.query(Training).filter(
            Training.is_active == True,
            Training.end_at.is_(None) | (Training.end_at > datetime.utcnow())
        ).order_by(Training.start_at.asc()).all()
    ]


@router.post("/trainings/{training_id}/register")
def register_training(training_id: int, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    student_id = student_id_from_token(credentials, db)

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).with_for_update().first()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")
    training = db.query(Training).filter(Training.id == training_id, Training.is_active == True).with_for_update().first()
    if not training:
        raise HTTPException(status_code=404, detail="Trening topilmadi")
    existing = db.query(TrainingRegistration).filter(
        TrainingRegistration.training_id == training_id,
        TrainingRegistration.student_id == student_id
    ).first()
    if existing and existing.status == "registered":
        raise HTTPException(status_code=400, detail="Siz bu treningka allaqachon ro'yxatdan o'tgansiz")
    now = datetime.utcnow()
    if training.start_at is not None and training.start_at <= now:
        raise HTTPException(status_code=400, detail="Bu trening allaqachon boshlangan")
    if training.end_at is not None and training.end_at <= now:
        raise HTTPException(status_code=400, detail="Bu trening allaqachon yakunlangan")
    if training.capacity is not None:
        count = db.query(TrainingRegistration).filter(
            TrainingRegistration.training_id == training_id,
            TrainingRegistration.status == "registered"
        ).count()
        if count >= training.capacity:
            raise HTTPException(status_code=400, detail="Trening uchun joy qolmagan")
    if existing:
        existing.status = "registered"
        existing.registered_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return {"success": True, "message": "Treningka qayta ro'yxatdan o'tildi", "registration_id": existing.id}
    item = TrainingRegistration(training_id=training_id, student_id=student_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"success": True, "message": "Treningka ro'yxatdan o'tildi", "registration_id": item.id}


@router.get("/exams")
def get_exams(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    student_id = student_id_from_token(credentials, db)
    registrations = {
        x.exam_id: x.status
        for x in db.query(ExamRegistration).filter(ExamRegistration.student_id == student_id).all()
    }
    return [
        {"id": x.id, "title": x.title, "description": x.description, "start_at": x.start_at,
         "end_at": x.end_at, "location": x.location, "capacity": x.capacity,
         "registered": registrations.get(x.id) == "registered", "registration_status": registrations.get(x.id)}
        for x in db.query(Exam).filter(
            Exam.is_active == True,
            Exam.end_at.is_(None) | (Exam.end_at > datetime.utcnow())
        ).order_by(Exam.start_at.asc()).all()
    ]


@router.post("/exams/{exam_id}/register")
def register_exam(exam_id: int, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    student_id = student_id_from_token(credentials, db)

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).with_for_update().first()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")
    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.is_active == True).with_for_update().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Imtihon topilmadi")
    existing = db.query(ExamRegistration).filter(
        ExamRegistration.exam_id == exam_id,
        ExamRegistration.student_id == student_id
    ).first()
    if existing and existing.status == "registered":
        raise HTTPException(status_code=400, detail="Siz bu imtihonga allaqachon ro'yxatdan o'tgansiz")
    if exam.end_at is not None and exam.end_at <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Bu imtihon allaqachon yakunlangan")
    if exam.capacity is not None:
        count = db.query(ExamRegistration).filter(
            ExamRegistration.exam_id == exam_id,
            ExamRegistration.status == "registered"
        ).count()
        if count >= exam.capacity:
            raise HTTPException(status_code=400, detail="Imtihon uchun joy qolmagan")
    if existing:
        existing.status = "registered"
        existing.registered_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return {"success": True, "message": "Imtihonga qayta ro'yxatdan o'tildi", "registration_id": existing.id}
    item = ExamRegistration(exam_id=exam_id, student_id=student_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"success": True, "message": "Imtihonga ro'yxatdan o'tildi", "registration_id": item.id}
