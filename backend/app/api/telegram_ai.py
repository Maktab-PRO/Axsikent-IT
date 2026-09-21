from fastapi import APIRouter, Request, HTTPException
from app.core.config import settings
from openai import OpenAI
import httpx
import json


router = APIRouter(prefix="/telegram", tags=["Telegram AI"])


async def send_telegram_message(chat_id: str, text: str):
    if not settings.TELEGRAM_BOT_TOKEN:
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=15) as client:
        await client.post(url, json={
            "chat_id": chat_id,
            "text": text
        })


@router.post("/webhook")
async def telegram_webhook(request: Request):
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
