from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

from app.core.config import settings

from app.db import Base, engine

# Barcha modellarni yuklaymiz

from app import models

from app.api.student import router as student_router
from app.api.teacher import router as teacher_router
from app.api.admin import router as admin_router
from app.api.course import router as course_router
from app.api.admin_course import router as admin_course_router
from app.api.group import router as group_router
from app.api.lead import router as lead_router
from app.api.student_course import router as student_course_router
from app.api.homework import router as homework_router
from app.api.student_group import router as student_group_router
from app.api.lesson_quiz import router as lesson_quiz_router
from app.api.admin_lesson import router as admin_lesson_router
from app.api.ranking import router as ranking_router
from app.api.rewards import router as rewards_router
from app.api.admin_shop import router as admin_shop_router
from app.api.books import router as books_router
from app.api.admin_books import router as admin_books_router
from app.api.admin_student import router as admin_student_router
from app.api.admin_teacher import router as admin_teacher_router
from app.api.admin_group import router as admin_group_router
from app.api.admin_lead import router as admin_lead_router
from app.api.admin_homework import router as admin_homework_router
from app.api.student_extra import router as student_extra_router
from app.api.admin_extra import router as admin_extra_router
from app.api.notifications import router as notifications_router
from app.api.ai_homework import router as ai_homework_router
from app.api.telegram_ai import router as telegram_ai_router


from app.seed import seed_data

app = FastAPI(
title="Axsikent IT API",
description="Axsikent IT o'quv markazi uchun professional platforma",
version="1.0.0"
)

# =========================

# CORS

# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://akhsikent-it-school.onrender.com",
        "https://axsikent-it-4.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================

# DATABASE
# Admin schema migration runs before seed_data()

# =========================
# TELEGRAM WEBHOOK
# =========================
# Bot token Render Environment Variables orqali olinadi.
# Telegram webhook deploydan keyin avtomatik o'rnatiladi.
if settings.TELEGRAM_BOT_TOKEN:
    try:
        httpx.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook",
            json={"url": "https://axsikent-it-4.onrender.com/telegram/webhook"},
            timeout=10.0,
        )
    except Exception:
        pass

# =========================

Base.metadata.create_all(bind=engine)
with engine.connect() as connection:
    connection.exec_driver_sql("""
        ALTER TABLE lesson_progress
        ADD COLUMN IF NOT EXISTS is_read BOOLEAN NOT NULL DEFAULT FALSE
    """)

    connection.exec_driver_sql("""
        ALTER TABLE lesson_progress
        ADD COLUMN IF NOT EXISTS quiz_passed BOOLEAN NOT NULL DEFAULT FALSE
    """)

    connection.exec_driver_sql("""
        ALTER TABLE leads
        ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)
    """)

    connection.exec_driver_sql("""
        ALTER TABLE students
        ADD COLUMN IF NOT EXISTS telegram_chat_id VARCHAR(64) UNIQUE
    """)

    connection.exec_driver_sql("""
        ALTER TABLE admins
        ADD COLUMN IF NOT EXISTS is_superadmin BOOLEAN NOT NULL DEFAULT FALSE
    """)

    connection.exec_driver_sql("""
        ALTER TABLE teachers
        ADD COLUMN IF NOT EXISTS birth_date DATE
    """)

    connection.exec_driver_sql("""
        ALTER TABLE teachers
        ADD COLUMN IF NOT EXISTS approved_by_admin BOOLEAN NOT NULL DEFAULT TRUE
    """)

    connection.exec_driver_sql("""
        UPDATE admins
        SET is_superadmin = TRUE
        WHERE phone = '998901234569'
    """)

    connection.commit()

seed_data()

# =========================

# API ROUTERS

# =========================

app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(admin_router)
app.include_router(course_router)
app.include_router(admin_course_router)
app.include_router(group_router)
app.include_router(lead_router)
app.include_router(student_course_router)
app.include_router(homework_router)
app.include_router(student_group_router)
app.include_router(lesson_quiz_router)
app.include_router(admin_lesson_router)
app.include_router(ranking_router)
app.include_router(rewards_router)
app.include_router(admin_shop_router)
app.include_router(books_router)
app.include_router(admin_books_router)
app.include_router(admin_student_router)
app.include_router(admin_teacher_router)
app.include_router(admin_group_router)
app.include_router(admin_lead_router)
app.include_router(admin_homework_router)
app.include_router(student_extra_router)
app.include_router(admin_extra_router)
app.include_router(notifications_router)
app.include_router(ai_homework_router)
app.include_router(telegram_ai_router)

# =========================

# HOME

# =========================

@app.get("/")
def home():
    return {
        "message": "Axsikent IT platformasi ishlayapti! 🚀"
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "platform": "Axsikent IT"
    }
