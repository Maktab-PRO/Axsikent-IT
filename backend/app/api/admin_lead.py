from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import require_admin

from app.models.admin import Admin
from app.models.lead import Lead
from app.models.student import Student
from app.models.gamification import StudentGamification
from passlib.context import CryptContext


router = APIRouter(
    prefix="/admin/leads",
    tags=["Admin Leads"]
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# =========================================================
# SCHEMAS
# =========================================================

class LeadStatusUpdate(BaseModel):
    status: str = Field(
        min_length=2,
        max_length=30
    )


class LeadCommentUpdate(BaseModel):
    comment: str | None = Field(
        default=None,
        max_length=5000
    )


# =========================================================
# ALLOWED STATUSES
# =========================================================

ALLOWED_STATUSES = {
    "new",
    "contacted",
    "enrolled",
    "rejected"
}


# =========================================================
# HELPER
# =========================================================

def get_lead_or_404(
    lead_id: int,
    db: Session
):
    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Ariza topilmadi."
        )

    return lead


def lead_to_dict(lead: Lead):
    return {
        "id": lead.id,
        "full_name": lead.full_name,
        "phone": lead.phone,
        "age": lead.age,
        "interested_course": lead.interested_course,
        "preferred_time": lead.preferred_time,
        "previous_it_course": lead.previous_it_course,
        "comment": lead.comment,
        "source": lead.source,
        "status": lead.status,
        "created_at": lead.created_at
    }


# =========================================================
# 1. GET ALL LEADS
# =========================================================

@router.get("/")
def get_admin_leads(
    search: str | None = Query(
        default=None,
        max_length=150
    ),
    status: str | None = Query(
        default=None,
        max_length=30
    ),
    source: str | None = Query(
        default=None,
        max_length=50
    ),
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    query = db.query(Lead)

    # Search
    if search:
        search_value = f"%{search.strip()}%"

        query = query.filter(
            (Lead.full_name.ilike(search_value)) |
            (Lead.phone.ilike(search_value)) |
            (Lead.interested_course.ilike(search_value))
        )

    # Status filter
    if status:
        query = query.filter(
            Lead.status == status.strip().lower()
        )

    # Source filter
    if source:
        query = query.filter(
            Lead.source == source.strip()
        )

    leads = query.order_by(
        Lead.created_at.desc()
    ).all()

    return {
        "total": len(leads),
        "leads": [
            lead_to_dict(lead)
            for lead in leads
        ]
    }


# =========================================================
# 2. LEAD STATISTICS
# =========================================================

@router.get("/stats/summary")
def get_lead_stats(
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    total = db.query(Lead).count()

    new_count = db.query(Lead).filter(
        Lead.status == "new"
    ).count()

    contacted_count = db.query(Lead).filter(
        Lead.status == "contacted"
    ).count()

    enrolled_count = db.query(Lead).filter(
        Lead.status == "enrolled"
    ).count()

    rejected_count = db.query(Lead).filter(
        Lead.status == "rejected"
    ).count()

    return {
        "total": total,
        "new": new_count,
        "contacted": contacted_count,
        "enrolled": enrolled_count,
        "rejected": rejected_count
    }


# =========================================================
# 3. GET SINGLE LEAD
# =========================================================

@router.get("/{lead_id}")
def get_admin_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    lead = get_lead_or_404(
        lead_id,
        db
    )

    return lead_to_dict(lead)


# =========================================================
# 4. UPDATE STATUS
# =========================================================

@router.put("/{lead_id}/status")
def update_lead_status(
    lead_id: int,
    data: LeadStatusUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    lead = get_lead_or_404(
        lead_id,
        db
    )

    new_status = data.status.strip().lower()

    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Noto‘g‘ri status. "
                "Ruxsat etilgan statuslar: "
                "new, contacted, enrolled, rejected."
            )
        )

    if new_status == "enrolled":
        if not lead.password_hash:
            raise HTTPException(
                status_code=400,
                detail="Bu arizada o‘quvchi akkaunti uchun parol mavjud emas. O‘quvchini qayta ro‘yxatdan o‘tkazish kerak."
            )

        student = db.query(Student).filter(
            Student.phone == lead.phone
        ).first()

        if not student:
            student = Student(
                full_name=lead.full_name,
                phone=lead.phone,
                password_hash=lead.password_hash,
                is_active=True
            )
            db.add(student)
            db.flush()
            db.add(StudentGamification(
                student_id=student.id,
                xp=0,
                level=1,
                coins=0,
                crystals=0,
                streak_days=0
            ))
        elif not student.is_active:
            student.is_active = True

    lead.status = new_status

    db.commit()
    db.refresh(lead)

    return {
        "message": "Ariza statusi yangilandi.",
        "lead": lead_to_dict(lead)
    }


# =========================================================
# 5. UPDATE COMMENT
# =========================================================

@router.put("/{lead_id}/comment")
def update_lead_comment(
    lead_id: int,
    data: LeadCommentUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    lead = get_lead_or_404(
        lead_id,
        db
    )

    lead.comment = data.comment

    db.commit()
    db.refresh(lead)

    return {
        "message": "Ariza izohi yangilandi.",
        "lead": lead_to_dict(lead)
    }


# =========================================================
# 6. DELETE LEAD
# =========================================================

@router.delete("/{lead_id}")
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    lead = get_lead_or_404(
        lead_id,
        db
    )

    db.delete(lead)
    db.commit()

    return {
        "message": "Ariza o‘chirildi.",
        "lead_id": lead_id
    }
