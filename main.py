from fastapi import FastAPI, WebSocket, WebSocketDisconnect,HTTPException
from stt.uz_stt import uz_stt
from stt.whisper_stt import whisper_stt
from translator.translator import translate
from tts.uz_tts import uz_tts
from tts.gtts_tts import gtts_tts
import base64
import logging
from pydantic import BaseModel

# Qo‘llab-quvvatlanadigan tillar
SUPPORTED_LANGS = {
    "uz": "🇺🇿 Uzbek",
    "en": "🇺🇸 English",
    "ru": "🇷🇺 Russian",
    "fr": "🇫🇷 French",
    "de": "🇩🇪 German",
    "zh": "🇨🇳 Chinese",
    "ja": "🇯🇵 Japanese",
    "ko": "🇰🇷 Korean",
    "es": "🇪🇸 Spanish",
    "pt": "🇵🇹 Portuguese",
    "mn": "🇲🇳 Mongolian"
}

app = FastAPI()
logging.basicConfig(level=logging.INFO)

class TranslateTTSRequest(BaseModel):
    text: str
    source: str
    target: str

# --- STT (Ovozdan matnga) ---
@app.websocket("/ws/stt")
async def websocket_stt(websocket: WebSocket):
    await websocket.accept()
    logging.info("🟢 STT WebSocket ulanmoqda...")
    try:
        while True:
            data = await websocket.receive_json()
            lang = data.get("lang")
            audio_b64 = data.get("audio", "")

            if not lang or lang not in SUPPORTED_LANGS:
                await websocket.send_json({"error": f"Til (lang='{lang}') qo‘llab-quvvatlanmaydi"})
                continue

            if not audio_b64:
                await websocket.send_json({"error": "Audio fayl topilmadi"})
                continue

            try:
                audio_bytes = base64.b64decode(audio_b64)
                text = uz_stt(audio_bytes) if lang == "uz" else whisper_stt(audio_bytes, lang)
# 
                if not text.strip():
                    await websocket.send_json({"error": "Matn topilmadi"})
                    continue

                await websocket.send_json({"text": text})
            except Exception as e:
                logging.exception("❌ STT xatosi")
                await websocket.send_json({"error": f"STT xato: {str(e)}"})

    except WebSocketDisconnect:
        logging.warning("🔌 STT WebSocket uzildi")


# --- Tarjimon (Matndan matnga) ---
@app.websocket("/ws/translate")
async def websocket_translate(websocket: WebSocket):
    await websocket.accept()
    logging.info("🟢 Translate WebSocket ulanmoqda...")
    try:
        while True:
            data = await websocket.receive_json()
            text = data.get("text", "").strip()
            source = data.get("source", "")
            target = data.get("target", "")

            if not text:
                await websocket.send_json({"error": "Bo‘sh matn kiritildi"})
                continue

            if source not in SUPPORTED_LANGS or target not in SUPPORTED_LANGS:
                await websocket.send_json({"error": "Til kodi noto‘g‘ri yoki qo‘llab-quvvatlanmaydi"})
                continue

            try:
                translated = translate(text, source, target)

                if not translated.strip():
                    await websocket.send_json({"error": "Tarjima natijasi bo‘sh"})
                    continue

                await websocket.send_json({"translation": translated})
            except Exception as e:
                logging.exception("❌ Tarjima xatosi")
                await websocket.send_json({"error": f"Tarjima xato: {str(e)}"})

    except WebSocketDisconnect:
        logging.warning("🔌 Translate WebSocket uzildi")


# --- TTS (Matndan ovozga) ---
@app.websocket("/ws/tts")
async def websocket_tts(websocket: WebSocket):
    await websocket.accept()
    logging.info("🟢 TTS WebSocket ulanmoqda...")
    try:
        while True:
            data = await websocket.receive_json()
            text = data.get("text", "").strip()
            lang = data.get("lang", "")

            if not text:
                await websocket.send_json({"error": "Bo‘sh matn yuborildi"})
                continue

            if lang not in SUPPORTED_LANGS:
                await websocket.send_json({"error": f"TTS uchun til '{lang}' qo‘llab-quvvatlanmaydi"})
                continue

            try:
                if lang == "uz":
                    audio_bytes = await uz_tts(text)
                else:
                    audio_bytes = await gtts_tts(text, lang)
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                await websocket.send_json({"audio": audio_b64})
            except Exception as e:
                logging.exception("❌ TTS xatosi")
                await websocket.send_json({"error": f"TTS xato: {str(e)}"})

    except WebSocketDisconnect:
        logging.warning("🔌 TTS WebSocket uzildi")

@app.post("/translate-tts")
async def translate_and_tts(req: TranslateTTSRequest):
    if req.source not in SUPPORTED_LANGS or req.target not in SUPPORTED_LANGS:
        raise HTTPException(status_code=400, detail="Til kodi noto‘g‘ri yoki qo‘llab-quvvatlanmaydi")

    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Bo‘sh matn yuborildi")

    try:
        # Tarjima
        translated = translate(req.text, req.source, req.target)

        if not translated.strip():
            raise HTTPException(status_code=500, detail="Tarjima natijasi bo‘sh")

        # TTS: O'zbek tili uchun uz_tts, boshqa tillar uchun gtts_tts
        if req.target == "uz":
            audio_bytes = await uz_tts(translated)
        else:
            audio_bytes = await gtts_tts(translated, req.target)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        return {
            "translation": translated,
            "audio": audio_b64
        }
    except Exception as e:
        logging.exception("❌ Xatolik")
        raise HTTPException(status_code=500, detail=f"Xatolik: {str(e)}")