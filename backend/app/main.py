from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
        "https://akhsikent-it-school.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================

# DATABASE

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
