import hashlib
import secrets
from datetime import datetime, timezone, timedelta

import httpx

from app.core.config import settings


SENDER_ID = "AkhsikentIT"
OTP_TTL_MINUTES = 5
RESEND_COOLDOWN_SECONDS = 60
MAX_VERIFY_ATTEMPTS = 5


def normalize_phone(phone: str) -> str:
    value = (phone or "").strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if value.startswith("+"):
        value = value[1:]
    if not value.isdigit() or len(value) != 12 or not value.startswith("998"):
        raise ValueError("Telefon raqam 998XXXXXXXXX ko‘rinishida bo‘lishi kerak")
    return value


def _otp_hash(code: str) -> str:
    return hashlib.sha256(f"{settings.SECRET_KEY}:{code}".encode()).hexdigest()


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def send_sms(phone: str, message: str) -> bool:
    if not settings.SMS_API_USERNAME or not settings.SMS_API_PASSWORD:
        return False

    url = settings.SMS_API_URL.rstrip("/") + "/broker-api/send" if settings.SMS_API_URL.rstrip("/").endswith("smsxabar.uz") else settings.SMS_API_URL.rstrip("/")
    payload = {
        "messages": [{
            "recipient": normalize_phone(phone),
            "message-id": secrets.token_hex(12),
            "sms": {
                "originator": settings.SMS_SENDER_ID or SENDER_ID,
                "ttl": "300",
                "content": {"text": message},
            },
        }]
    }

    try:
        response = httpx.post(
            url,
            json=payload,
            auth=(settings.SMS_API_USERNAME, settings.SMS_API_PASSWORD),
            headers={"Content-Type": "application/json"},
            timeout=15.0,
        )
        response.raise_for_status()
        return True
    except Exception:
        return False


def create_and_send_otp(db, phone: str, purpose: str, message_prefix: str) -> tuple[bool, int]:
    from app.models.sms_verification import SmsVerification

    normalized = normalize_phone(phone)
    now = datetime.now(timezone.utc)
    active = (
        db.query(SmsVerification)
        .filter(
            SmsVerification.phone == normalized,
            SmsVerification.purpose == purpose,
            SmsVerification.used_at.is_(None),
            SmsVerification.expires_at > now,
        )
        .order_by(SmsVerification.id.desc())
        .first()
    )
    if active and active.last_sent_at:
        elapsed = (now - active.last_sent_at).total_seconds()
        if elapsed < RESEND_COOLDOWN_SECONDS:
            return False, int(RESEND_COOLDOWN_SECONDS - elapsed)

    code = generate_otp()
    record = SmsVerification(
        phone=normalized,
        purpose=purpose,
        code_hash=_otp_hash(code),
        expires_at=now + timedelta(minutes=OTP_TTL_MINUTES),
        attempts=0,
        last_sent_at=now,
    )
    db.add(record)
    db.commit()

    sent = send_sms(normalized, f"{message_prefix}: {code}. Kod 5 daqiqa amal qiladi.")
    if not sent:
        db.delete(record)
        db.commit()
        return False, 0
    return True, 0


def verify_otp(db, phone: str, purpose: str, code: str) -> bool:
    from app.models.sms_verification import SmsVerification

    normalized = normalize_phone(phone)
    now = datetime.now(timezone.utc)
    record = (
        db.query(SmsVerification)
        .filter(
            SmsVerification.phone == normalized,
            SmsVerification.purpose == purpose,
            SmsVerification.used_at.is_(None),
            SmsVerification.expires_at > now,
        )
        .order_by(SmsVerification.id.desc())
        .first()
    )
    if not record or record.attempts >= MAX_VERIFY_ATTEMPTS:
        return False
    record.attempts += 1
    if secrets.compare_digest(record.code_hash, _otp_hash(code.strip())):
        record.used_at = now
        db.commit()
        return True
    db.commit()
    return False
