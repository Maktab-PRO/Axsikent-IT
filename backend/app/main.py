from fastapi import FastAPI
from app.db import Base, engine

from app.models.student import Student
from app.models.teacher import Teacher
from app.models.admin import Admin

from app.api.student import router as student_router
from app.api.teacher import router as teacher_router
from app.api.admin import router as admin_router


app = FastAPI(
    title="Axsikent IT API",
    description="Axsikent IT o'quv markazi uchun professional platforma",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)

app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(admin_router)


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
