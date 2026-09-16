from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import verify_token
from app.models.book import Book


router = APIRouter(
    prefix="/admin/books",
    tags=["Admin Books"]
)

security = HTTPBearer()


@router.post("")
def create_book(
    title: str,
    description: str = "",
    image_url: str = "",
    price: int = 0,
    coin_price: int = 0,
    stock: int = 0,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    admin_id = verify_token(credentials.credentials)

    if not admin_id:
        raise HTTPException(
            status_code=401,
            detail="Admin token noto'g'ri"
        )

    if price < 0 or coin_price < 0 or stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Narx va stock 0 dan kichik bo'lishi mumkin emas"
        )

    book = Book(
        title=title,
        description=description,
        image_url=image_url,
        price=price,
        coin_price=coin_price,
        stock=stock,
        is_active=True
    )

    db.add(book)
    db.commit()
    db.refresh(book)

    return {
        "success": True,
        "message": "Kitob muvaffaqiyatli qo'shildi",
        "book": {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "image_url": book.image_url,
            "price": book.price,
            "coin_price": book.coin_price,
            "stock": book.stock,
            "is_active": book.is_active
        }
    }


@router.get("")
def get_books(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    admin_id = verify_token(credentials.credentials)

    if not admin_id:
        raise HTTPException(
            status_code=401,
            detail="Admin token noto'g'ri"
        )

    books = db.query(Book).order_by(
        Book.id.asc()
    ).all()

    return [
        {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "image_url": book.image_url,
            "price": book.price,
            "coin_price": book.coin_price,
            "stock": book.stock,
            "is_active": book.is_active
        }
        for book in books
    ]
