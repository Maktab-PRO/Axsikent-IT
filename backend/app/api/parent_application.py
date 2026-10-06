import secrets
import string
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import require_admin
from app.models.admin import Admin
from app.models.parent import Parent, ParentStudent
from app.models.parent_application import ParentApplication
from app.models.student import Student


router = APIRouter(prefix="/parent-applications", tags=["Parent Applications"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _normalize_phone(phone: str) -> str:
    value = (phone or "").strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if value.startswith("+"):
        value = value[1:]
    if not value.isdigit() or len(value) != 12 or not value.startswith("998"):
        raise ValueError("Telefon raqam 998XXXXXXXXX ko‘rinishida bo‘lishi kerak")
    return value


class ParentApplicationCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    phone: str = Field(min_length=9, max_length=30)
    student_phone: str = Field(min_length=9, max_length=30)
    comment: str | None = Field(default=None, max_length=2000)


def _temporary_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.post("/")
def create_parent_application(data: ParentApplicationCreate, db: Session = Depends(get_db)):
    try:
        phone = _normalize_phone(data.phone)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        student_phone = normalize_phone(data.student_phone)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    student = db.query(Student).filter(
        Student.phone == student_phone,
        Student.is_active == True,
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Faol o‘quvchi topilmadi.")

    if db.query(Parent).filter(Parent.phone == phone).first():
        raise HTTPException(status_code=409, detail="Bu telefon raqam bilan ota-ona akkaunti mavjud.")

    pending = db.query(ParentApplication).filter(
        ParentApplication.phone == phone,
        ParentApplication.status == "pending",
    ).first()
    if pending:
        raise HTTPException(status_code=409, detail="Bu telefon raqamdan yuborilgan ariza allaqachon ko‘rib chiqilmoqda.")

    application = ParentApplication(
        full_name=data.full_name.strip(),
        phone=phone,
        student_id=student.id,
        comment=data.comment,
        status="pending",
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "success": True,
        "message": "Ota-ona arizasi qabul qilindi. Administrator arizani tekshiradi.",
        "application_id": application.id,
        "status": application.status,
    }


@router.get("/status/{application_id}")
def parent_application_status(application_id: int, phone: str, db: Session = Depends(get_db)):
    try:
        normalized = _normalize_phone(phone)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    application = db.query(ParentApplication).filter(
        ParentApplication.id == application_id,
        ParentApplication.phone == normalized,
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Ariza topilmadi.")

    return {"application_id": application.id, "status": application.status}


@router.get("/admin")
def list_parent_applications(
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin),
):
    rows = db.query(ParentApplication).order_by(ParentApplication.id.desc()).all()
    return {
        "success": True,
        "applications": [
            {
                "id": row.id,
                "full_name": row.full_name,
                "phone": row.phone,
                "student_id": row.student_id,
                "comment": row.comment,
                "status": row.status,
                "created_at": row.created_at,
                "processed_at": row.processed_at,
                "parent_id": row.parent_id,
            }
            for row in rows
        ],
    }


@router.post("/admin/{application_id}/approve")
def approve_parent_application(
    application_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin),
):
    application = db.query(ParentApplication).filter(
        ParentApplication.id == application_id
    ).with_for_update().first()
    if not application:
        raise HTTPException(status_code=404, detail="Ariza topilmadi.")
    if application.status != "pending":
        raise HTTPException(status_code=409, detail="Bu ariza allaqachon ko‘rib chiqilgan.")

    student = db.query(Student).filter(
        Student.id == application.student_id,
        Student.is_active == True,
    ).first()
    if not student:
        raise HTTPException(status_code=400, detail="Biriktirilgan o‘quvchi faol emas.")

    existing = db.query(Parent).filter(Parent.phone == application.phone).first()
    if existing:
        application.status = "approved"
        application.parent_id = existing.id
        application.processed_at = datetime.now(timezone.utc)
        db.commit()
        return {"success": True, "message": "Bu telefon raqam bilan ota-ona akkaunti avval yaratilgan.", "parent_id": existing.id}

    password = _temporary_password()
    parent = Parent(
        full_name=application.full_name,
        phone=application.phone,
        password_hash=pwd_context.hash(password),
        is_active=True,
    )
    db.add(parent)
    db.flush()
    db.add(ParentStudent(parent_id=parent.id, student_id=student.id))

    application.status = "approved"
    application.parent_id = parent.id
    application.processed_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "success": True,
        "message": "Ota-ona arizasi tasdiqlandi. Parent akkaunti yaratildi.",
        "parent_id": parent.id,
        "temporary_password": password,
    }


@router.post("/admin/{application_id}/reject")
def reject_parent_application(
    application_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin),
):
    application = db.query(ParentApplication).filter(
        ParentApplication.id == application_id
    ).with_for_update().first()
    if not application:
        raise HTTPException(status_code=404, detail="Ariza topilmadi.")
    if application.status != "pending":
        raise HTTPException(status_code=409, detail="Bu ariza allaqachon ko‘rib chiqilgan.")

    application.status = "rejected"
    application.processed_at = datetime.now(timezone.utc)
    db.commit()
    return {"success": True, "message": "Ota-ona arizasi rad etildi."}
