import os
import json
import urllib.parse
import urllib.request

from fastapi import APIRouter, Depends, HTTPException
import operator
import re

from app.core.security import require_admin
from app.models.admin import Admin
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db import get_db
from app.models.lead import Lead
from app.services.sms import normalize_phone, verify_otp


router = APIRouter(
    prefix="/leads",
    tags=["Leads"]
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


@router.post("/")
def create_lead(
    full_name: str,
    phone: str,
    password: str,
    age: int | None = None,
    interested_course: str | None = None,
    preferred_time: str | None = None,
    previous_it_course: str | None = None,
    comment: str | None = None,
    math_a: int | None = None,
    math_b: int | None = None,
    math_operator: str | None = None,
    math_answer: int | None = None,
    privacy_consent: bool = False,
    sms_code: str | None = None,
    db: Session = Depends(get_db)
):

    # =========================================
    # LEAD YARATISH
    # =========================================

    if len(password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Parol kamida 6 ta belgidan iborat bo‘lishi kerak."
        )

    if not privacy_consent:
        raise HTTPException(
            status_code=400,
            detail="Shaxsiy ma'lumotlar qayta ishlanishiga rozilik berish majburiy."
        )

    operations = {
        "+": operator.add,
        "-": operator.sub,
        "×": operator.mul
    }

    if math_a is None or math_b is None or math_answer is None or math_operator not in operations:
        raise HTTPException(
            status_code=400,
            detail="Matematik misolni to‘g‘ri yeching."
        )

    expected_answer = operations[math_operator](math_a, math_b)

    if math_answer != expected_answer:
        raise HTTPException(
            status_code=400,
            detail="Matematik misol noto‘g‘ri yechildi."
        )

    try:
        normalized_phone = normalize_phone(phone)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not sms_code or not verify_otp(db, normalized_phone, "registration", sms_code):
        raise HTTPException(status_code=400, detail="Telefon raqam SMS kodi bilan tasdiqlanishi kerak.")

    lead = Lead(
        full_name=full_name,
        phone=phone,
        password_hash=pwd_context.hash(password),
        age=age,
        interested_course=interested_course,
        preferred_time=preferred_time,
        previous_it_course=previous_it_course,
        comment=comment
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    return {
        "message": "Ariza muvaffaqiyatli qabul qilindi",
        "lead_id": lead.id,
        "status": lead.status
    }


@router.get("/status/{lead_id}")
def get_lead_status(
    lead_id: int,
    phone: str,
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.phone == phone.strip()
    ).first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Ariza topilmadi."
        )

    return {
        "lead_id": lead.id,
        "status": lead.status,
        "full_name": lead.full_name
    }


@router.get("/")
def get_leads(
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    leads = db.query(Lead).order_by(
        Lead.created_at.desc()
    ).all()

    return [
        {
            "id": lead.id,
            "full_name": lead.full_name,
            "phone": lead.phone,
            "age": lead.age,
            "interested_course": lead.interested_course,
            "preferred_time": lead.preferred_time,
            "previous_it_course": lead.previous_it_course,
            "status": lead.status,
            "created_at": lead.created_at
        }
        for lead in leads
    ]
