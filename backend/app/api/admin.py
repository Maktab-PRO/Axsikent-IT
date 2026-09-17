from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from passlib.context import CryptContext

from app.db import get_db

from app.models.admin import Admin
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.course import Course
from app.models.group import Group
from app.models.lead import Lead
from app.models.gamification import StudentGamification

from app.schemas.admin import AdminLogin
from app.core.security import create_access_token, require_admin


router = APIRouter(
    prefix="/admins",
    tags=["Admins"]
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# =========================================================
# ADMIN LOGIN
# =========================================================

@router.post("/login")
def login_admin(
    admin: AdminLogin,
    db: Session = Depends(get_db)
):

    user = db.query(Admin).filter(
        Admin.phone == admin.phone
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Telefon raqam yoki parol noto'g'ri"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Administrator akkaunti faol emas"
        )

    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Bu akkaunt administrator emas"
        )

    if not pwd_context.verify(
        admin.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Telefon raqam yoki parol noto'g'ri"
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "message": "Login muvaffaqiyatli",
        "access_token": access_token,
        "token_type": "bearer",
        "admin_id": user.id,
        "full_name": user.full_name,
        "role": user.role
    }


# =========================================================
# ADMIN PROFILE
# =========================================================

@router.get("/me")
def get_admin_profile(
    admin: Admin = Depends(require_admin)
):
    return {
        "id": admin.id,
        "full_name": admin.full_name,
        "phone": admin.phone,
        "role": admin.role,
        "is_active": admin.is_active
    }


# =========================================================
# COMMAND CENTER DASHBOARD
# =========================================================

@router.get("/dashboard")
def admin_dashboard(
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # ASOSIY SONLAR
    # -----------------------------------------------------

    total_students = db.query(Student).count()

    active_students = db.query(Student).filter(
        Student.is_active == True
    ).count()

    inactive_students = db.query(Student).filter(
        Student.is_active == False
    ).count()


    total_teachers = db.query(Teacher).count()

    active_teachers = db.query(Teacher).filter(
        Teacher.is_active == True
    ).count()


    total_courses = db.query(Course).count()

    active_courses = db.query(Course).filter(
        Course.is_active == True
    ).count()


    total_groups = db.query(Group).count()

    active_groups = db.query(Group).filter(
        Group.is_active == True
    ).count()


    total_leads = db.query(Lead).count()

    new_leads = db.query(Lead).filter(
        Lead.status == "new"
    ).count()

    contacted_leads = db.query(Lead).filter(
        Lead.status == "contacted"
    ).count()

    accepted_leads = db.query(Lead).filter(
        Lead.status == "accepted"
    ).count()


    # -----------------------------------------------------
    # GAMIFICATION
    # -----------------------------------------------------

    total_xp = db.query(
        StudentGamification
    ).with_entities(
        StudentGamification.xp
    ).all()

    total_coins = db.query(
        StudentGamification
    ).with_entities(
        StudentGamification.coins
    ).all()

    total_crystals = db.query(
        StudentGamification
    ).with_entities(
        StudentGamification.crystals
    ).all()


    xp_sum = sum(
        item[0] or 0
        for item in total_xp
    )

    coins_sum = sum(
        item[0] or 0
        for item in total_coins
    )

    crystals_sum = sum(
        item[0] or 0
        for item in total_crystals
    )


    # -----------------------------------------------------
    # DASHBOARD RESPONSE
    # -----------------------------------------------------

    return {
        "success": True,

        "admin": {
            "id": admin.id,
            "full_name": admin.full_name,
            "role": admin.role
        },

        "overview": {

            "students": {
                "total": total_students,
                "active": active_students,
                "inactive": inactive_students
            },

            "teachers": {
                "total": total_teachers,
                "active": active_teachers
            },

            "courses": {
                "total": total_courses,
                "active": active_courses
            },

            "groups": {
                "total": total_groups,
                "active": active_groups
            },

            "leads": {
                "total": total_leads,
                "new": new_leads,
                "contacted": contacted_leads,
                "accepted": accepted_leads
            },

            "gamification": {
                "total_xp": xp_sum,
                "total_coins": coins_sum,
                "total_crystals": crystals_sum
            }
        }
    }
