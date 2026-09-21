from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import verify_token
from app.models.book import Book, BookOrder
from app.models.gamification import StudentGamification
from app.models.student import Student
from app.services.notifications import notify_student


router = APIRouter(
    prefix="/students/books",
    tags=["Student Books"]
)

security = HTTPBearer()


@router.get("")
def get_books(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    student_id = verify_token(credentials.credentials)
    if not student_id:
        raise HTTPException(status_code=401, detail="Token noto'g'ri yoki muddati tugagan")

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    books = db.query(Book).filter(
        Book.is_active == True,
        Book.stock > 0
    ).order_by(
        Book.id.asc()
    ).all()

    return {
        "student_id": student_id,
        "books": [
            {
                "id": book.id,
                "title": book.title,
                "description": book.description,
                "image_url": book.image_url,
                "price": book.price,
                "coin_price": book.coin_price,
                "stock": book.stock
            }
            for book in books
        ]
    }


@router.post("/{book_id}/buy")
def buy_book(
    book_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    student_id = verify_token(credentials.credentials)

    if not student_id:
        raise HTTPException(status_code=401, detail="Token noto'g'ri yoki muddati tugagan")

    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    book = db.query(Book).filter(
        Book.id == book_id,
        Book.is_active == True
    ).with_for_update().first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Kitob topilmadi"
        )

    if book.stock <= 0:
        raise HTTPException(
            status_code=400,
            detail="Bu kitob hozir mavjud emas"
        )

    gamification = db.query(StudentGamification).filter(
        StudentGamification.student_id == student_id
    ).with_for_update().first()

    if not gamification:
        raise HTTPException(
            status_code=400,
            detail="O'quvchi gamification ma'lumotlari topilmadi"
        )

    if book.coin_price > gamification.coins:
        raise HTTPException(
            status_code=400,
            detail="Coin yetarli emas"
        )

    gamification.coins -= book.coin_price
    book.stock -= 1

    order = BookOrder(
        student_id=student_id,
        book_id=book.id,
        quantity=1,
        price_paid=book.price,
        coin_spent=book.coin_price,
        status="pending"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    notify_student(
        db,
        student_id=student_id,
        title="📚 Kitob buyurtmasi",
        message=f"{book.title} uchun buyurtmangiz qabul qilindi. Buyurtma №{order.id}.",
        notification_type="book_order",
    )

    return {
        "success": True,
        "message": "Kitob muvaffaqiyatli buyurtma qilindi",
        "order_id": order.id,
        "student": {
            "coins": gamification.coins
        },
        "book": {
            "id": book.id,
            "title": book.title,
            "stock": book.stock
        }
    }
