from fastapi import FastAPI
from app.db import Base, engine
from app.models.student import Student

app = FastAPI(
    title="Axsikent IT API",
    description="Axsikent IT o'quv markazi uchun professional platforma",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)


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
