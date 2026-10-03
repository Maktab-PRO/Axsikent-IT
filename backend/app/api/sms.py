from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.sms_verification import SmsVerification
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.parent import Parent
from app.models.lead import Lead
from app.services.sms import create_and_send_otp, normalize_phone, verify_otp


router = APIRouter(prefix="/sms", tags=["SMS"])


class CodeRequest(BaseModel):
    phone: str = Field(min_length=9, max_length=30)


class CodeVerify(CodeRequest):
    code: str = Field(min_length=6, max_length=6)


@router.post("/registration/request")
def request_registration_code(data: CodeRequest, db: Session = Depends(get_db)):
    try:
        phone = normalize_phone(data.phone)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if db.query(Student).filter(Student.phone == phone).first() or db.query(Lead).filter(Lead.phone == phone, Lead.status != "rejected").first():
        raise HTTPException(status_code=409, detail="Bu telefon raqam allaqachon ro‘yxatdan o‘tgan yoki ariza yuborilgan.")

    sent, retry_after = create_and_send_otp(db, phone, "registration", "Akhsikent IT tasdiqlash kodi")
    if retry_after:
        raise HTTPException(status_code=429, detail=f"Kodni qayta yuborishdan oldin {retry_after} soniya kuting.")
    if not sent:
        raise HTTPException(status_code=503, detail="SMS xizmati hozir sozlanmagan yoki SMS yuborilmadi.")
    return {"success": True, "message": "Tasdiqlash kodi telefon raqamiga yuborildi."}


@router.post("/registration/verify")
def verify_registration_code(data: CodeVerify, db: Session = Depends(get_db)):
    try:
        valid = verify_otp(db, data.phone, "registration", data.code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not valid:
        raise HTTPException(status_code=400, detail="Tasdiqlash kodi noto‘g‘ri yoki muddati tugagan.")
    return {"success": True, "verified": True}


@router.post("/password-reset/request")
def request_password_reset_code(data: CodeRequest, db: Session = Depends(get_db)):
    try:
        phone = normalize_phone(data.phone)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    exists = any([
        db.query(Student).filter(Student.phone == phone).first(),
        db.query(Teacher).filter(Teacher.phone == phone).first(),
        db.query(Parent).filter(Parent.phone == phone).first(),
    ])
    # Always return a neutral response for unknown numbers.
    if not exists:
        return {"success": True, "message": "Agar akkaunt mavjud bo‘lsa, tasdiqlash kodi yuborildi."}

    sent, retry_after = create_and_send_otp(db, phone, "password_reset", "Akhsikent IT parolni tiklash kodi")
    if retry_after:
        raise HTTPException(status_code=429, detail=f"Kodni qayta yuborishdan oldin {retry_after} soniya kuting.")
    if not sent:
        raise HTTPException(status_code=503, detail="SMS xizmati hozir sozlanmagan yoki SMS yuborilmadi.")
    return {"success": True, "message": "Agar akkaunt mavjud bo‘lsa, tasdiqlash kodi yuborildi."}


class PasswordReset(BaseModel):
    phone: str = Field(min_length=9, max_length=30)
    code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=128)


@router.post("/password-reset/confirm")
def confirm_password_reset(data: PasswordReset, db: Session = Depends(get_db)):
    try:
        phone = normalize_phone(data.phone)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not verify_otp(db, phone, "password_reset", data.code):
        raise HTTPException(status_code=400, detail="Tasdiqlash kodi noto‘g‘ri yoki muddati tugagan.")

    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = (
        db.query(Student).filter(Student.phone == phone).first()
        or db.query(Teacher).filter(Teacher.phone == phone).first()
        or db.query(Parent).filter(Parent.phone == phone).first()
    )
    if not user:
        raise HTTPException(status_code=400, detail="Akkaunt topilmadi.")

    user.password_hash = pwd.hash(data.new_password)
    user.auth_version = (user.auth_version or 1) + 1
    db.commit()
    return {"success": True, "message": "Parol muvaffaqiyatli yangilandi."}
