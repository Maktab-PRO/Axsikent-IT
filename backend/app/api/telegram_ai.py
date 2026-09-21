from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import verify_token
from app.models.student import Student
from app.models.ai_telegram_submission import AITelegramSubmission
from app.db import get_db
from openai import OpenAI
import httpx
import json
import base64
import hashlib
import hmac
import time


router = APIRouter(prefix="/telegram", tags=["Telegram AI"])
security = HTTPBearer()


async def send_telegram_message(chat_id: str, text: str):
    if not settings.TELEGRAM_BOT_TOKEN:
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=15) as client:
        await client.post(url, json={
            "chat_id": chat_id,
            "text": text
        })


def create_student_link_code(student_id: int) -> str:
    expires = int(time.time()) + 900
    payload = f"{student_id}:{expires}"
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()[:24]
    raw = f"{payload}:{signature}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def verify_student_link_code(code: str):
    try:
        padded = code + "=" * (-len(code) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")
        student_id_text, expires_text, signature = raw.split(":", 2)
        payload = f"{student_id_text}:{expires_text}"

        expected = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()[:24]

        if not hmac.compare_digest(signature, expected):
            return None

        if int(expires_text) < int(time.time()):
            return None

        return int(student_id_text)
    except Exception:
        return None


@router.get("/connect")
async def create_telegram_connect_link(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    student_id = verify_token(credentials.credentials)

    if not student_id:
        raise HTTPException(status_code=401, detail="Token noto'g'ri yoki muddati tugagan")

    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=503, detail="Telegram bot hali sozlanmagan")

    token = create_student_link_code(student.id)

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url)
        data = response.json()

    if not data.get("ok") or not (data.get("result") or {}).get("username"):
        raise HTTPException(status_code=503, detail="Telegram bot ma'lumotlarini olishda xatolik")

    username = data["result"]["username"]

    return {
        "connected": bool(student.telegram_chat_id),
        "bot_username": username,
        "connect_url": f"https://t.me/{username}?start={token}"
    }


@router.get("/status")
async def telegram_status():
    if not settings.TELEGRAM_BOT_TOKEN:
        return {"configured": False, "message": "TELEGRAM_BOT_TOKEN topilmadi"}
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getWebhookInfo"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url)
        data = response.json()
    return {
        "configured": True,
        "telegram_ok": data.get("ok", False),
        "webhook_url": (data.get("result") or {}).get("url", ""),
        "pending_updates": (data.get("result") or {}).get("pending_update_count", 0),
        "last_error": (data.get("result") or {}).get("last_error_message"),
    }


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    if settings.TELEGRAM_WEBHOOK_SECRET:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != settings.TELEGRAM_WEBHOOK_SECRET:
            raise HTTPException(status_code=403, detail="Webhook secret noto'g'ri")

    update = await request.json()
    message = update.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id or not text:
        return {"ok": True}

    if text.startswith("/start"):
        parts = text.split(maxsplit=1)

        if len(parts) == 2:
            student_id = verify_student_link_code(parts[1].strip())

            if student_id:
                student = db.query(Student).filter(Student.id == student_id).first()

                if student:
                    student.telegram_chat_id = str(chat_id)
                    db.commit()

                    await send_telegram_message(
                        str(chat_id),
                        "✅ Telegram muvaffaqiyatli ulandi!\n\n"
                        f"👨‍🎓 O‘quvchi: {student.full_name}\n"
                        "🤖 Endi AKHSIKENT AI (Ustoz AI) orqali "
                        "uy vazifalaringizni tekshirishingiz mumkin.\n\n"
                        "Format:\n"
                        "TOPSHIRIQ: ...\n"
                        "JAVOB: ..."
                    )
                    return {"ok": True}

        await send_telegram_message(
            str(chat_id),
            "🤖 AKHSIKENT AI (Ustoz AI)\n\n"
            "Uy vazifangizni tekshirish uchun yuboring.\n"
            "Format:\n"
            "TOPSHIRIQ: ...\n"
            "JAVOB: ...\n\n"
            "AI sizga xatolar, foiz va tavsiyani beradi."
        )
        return {"ok": True}

    if not settings.OPENAI_API_KEY:
        await send_telegram_message(str(chat_id), "⚠️ OpenAI API kaliti hali serverga ulanmagan.")
        return {"ok": True}

    if "JAVOB:" not in text.upper():
        await send_telegram_message(
            str(chat_id),
            "Iltimos shu formatda yuboring:\n\nTOPSHIRIQ: ...\nJAVOB: ..."
        )
        return {"ok": True}

    upper = text.upper()
    idx = upper.find("JAVOB:")
    task = text[:idx].replace("TOPSHIRIQ:", "", 1).strip()
    answer = text[idx + len("JAVOB:"):].strip()

    if not task or not answer:
        await send_telegram_message(str(chat_id), "Topshiriq va javobni to'liq yuboring.")
        return {"ok": True}

    student = db.query(Student).filter(Student.telegram_chat_id == str(chat_id)).first()
    if not student:
        await send_telegram_message(str(chat_id), "Avval Student paneldagi AKHSIKENT AI bo‘limidan Telegramni ulang.")
        return {"ok": True}

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = f"""
Siz AKHSIKENT AI (Ustoz AI), Axsikent IT uchun uy vazifa tekshiruvchi ustozsiz.

TOPSHIRIQ:
{task}

O'QUVCHI JAVOBI:
{answer}

JSON qaytaring:
{{"score":0,"passed":false,"mistakes":[],"explanation":"","recommendation":""}}

score 0-100. 80 va yuqori passed=true.
""".strip()

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Siz aniq va adolatli AI o'qituvchisiz. Faqat JSON qaytaring."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)

        score = max(0, min(100, int(result.get("score", 0))))
        mistakes = result.get("mistakes") or []

        ai_submission = AITelegramSubmission(
            student_id=student.id,
            telegram_chat_id=str(chat_id),
            task=task,
            answer=answer,
            score=score,
            passed="true" if score >= 80 else "false",
            mistakes=json.dumps(mistakes, ensure_ascii=False),
            explanation=str(result.get("explanation", "")),
            recommendation=str(result.get("recommendation", "")),
            status="checked",
            checked_at=__import__("datetime").datetime.utcnow()
        )
        db.add(ai_submission)
        db.commit()
        mistakes_text = "\n".join(f"• {item}" for item in mistakes) or "Xato topilmadi."

        reply = (
            "🤖 AKHSIKENT AI — NATIJA\n\n"
            f"📊 Baho: {score}%\n"
            f"{'✅ Keyingi dars ochiladi' if score >= 80 else '🔒 Keyingi dars ochilmaydi'}\n\n"
            f"❌ Xatolar:\n{mistakes_text}\n\n"
            f"💡 Izoh: {result.get('explanation', '')}\n"
            f"🎯 Tavsiya: {result.get('recommendation', '')}"
        )
        await send_telegram_message(str(chat_id), reply)

    except Exception as exc:
        await send_telegram_message(str(chat_id), f"❌ AI tekshiruvda xatolik: {exc}")

    return {"ok": True}
