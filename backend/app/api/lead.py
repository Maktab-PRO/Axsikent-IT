import os
import json
import urllib.parse
import urllib.request

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db import get_db
from app.models.lead import Lead


router = APIRouter(
    prefix="/leads",
    tags=["Leads"]
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def verify_turnstile(token: str) -> bool:
    """
    Cloudflare Turnstile tokenini tekshiradi.
    """

    secret_key = os.getenv("TURNSTILE_SECRET_KEY")

    if not secret_key:
        return False

    if not token:
        return False

    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

    data = urllib.parse.urlencode({
        "secret": secret_key,
        "response": token
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        return result.get("success", False)

    except Exception:
        return False


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
    cf_turnstile_response: str | None = None,
    db: Session = Depends(get_db)
):

    # =========================================
    # CLOUDFLARE TURNSTILE TEKSHIRUVI
    # =========================================

    if not verify_turnstile(cf_turnstile_response or ""):
        raise HTTPException(
            status_code=403,
            detail="Robot tekshiruvidan o‘ting."
        )

    # =========================================
    # LEAD YARATISH
    # =========================================

    if len(password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Parol kamida 6 ta belgidan iborat bo‘lishi kerak."
        )

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


@router.get("/")
def get_leads(
    db: Session = Depends(get_db)
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
