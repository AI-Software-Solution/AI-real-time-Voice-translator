from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from stt.uz_stt import uz_stt
from stt.whisper_stt import whisper_stt
from translator.translator import translate_text
from tts.uz_tts import uz_tts
from tts.gtts_tts import gtts_tts
import base64
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# --- STT (Ovozdan matnga) ---
@app.websocket("/ws/stt")
async def websocket_stt(websocket: WebSocket):
    await websocket.accept()
    logging.info("🟢 STT WebSocket ulanmoqda...")
    try:
        while True:
            data = await websocket.receive_json()
            lang = data.get("lang")  # ❌ default yo‘q
            audio_b64 = data.get("audio", "")

            if not lang:
                await websocket.send_json({"error": "Til (lang) belgilanmagan"})
                continue

            if not audio_b64:
                await websocket.send_json({"error": "Audio fayl topilmadi"})
                continue

            try:
                audio_bytes = base64.b64decode(audio_b64)
                text = uz_stt(audio_bytes) if lang == "uz" else whisper_stt(audio_bytes, lang)

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
            text = data.get("text", "")
            source = data.get("source", "")
            target = data.get("target", "")

            if not text.strip():
                await websocket.send_json({"error": "Bo'sh matn kiritildi"})
                continue

            try:
                translated = translate_text(text, source, target)

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
            text = data.get("text", "")
            lang = data.get("lang", "")

            if not text.strip():
                await websocket.send_json({"error": "Bo‘sh matn yuborildi"})
                continue

            try:
                audio_bytes = uz_tts(text) if lang == "uz" else gtts_tts(text, lang)
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                await websocket.send_json({"audio": audio_b64})
            except Exception as e:
                logging.exception("❌ TTS xatosi")
                await websocket.send_json({"error": f"TTS xato: {str(e)}"})

    except WebSocketDisconnect:
        logging.warning("🔌 TTS WebSocket uzildi")
