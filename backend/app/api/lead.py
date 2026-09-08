from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.lead import Lead


router = APIRouter(
    prefix="/leads",
    tags=["Leads"]
)


@router.post("/")
def create_lead(
    full_name: str,
    phone: str,
    age: int | None = None,
    interested_course: str | None = None,
    preferred_time: str | None = None,
    previous_it_course: str | None = None,
    comment: str | None = None,
    db: Session = Depends(get_db)
):
    lead = Lead(
        full_name=full_name,
        phone=phone,
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
