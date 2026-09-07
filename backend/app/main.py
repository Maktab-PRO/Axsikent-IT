from fastapi import FastAPI

app = FastAPI(
    title="Axsikent IT API",
    description="Axsikent IT o'quv markazi uchun professional platforma",
    version="1.0.0"
)


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
