import whisper
import tempfile
import os

# Modelni bir marta yuklab qo'yamiz
model = whisper.load_model("large")  # yoki "base", "medium", "large"

def whisper_stt(audio_bytes: bytes, lang: str = "en") -> str:
    """
    audio_bytes -> Whisper STT model orqali matn qaytaradi.
    :param audio_bytes: WAV formatdagi audio baytlar
    :param lang: til kodi (masalan, 'en', 'ru', 'de') yoki 'auto'
    :return: transkriptsiya qilingan matn
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name

    try:
        result = model.transcribe(temp_audio_path, language=None if lang == "auto" else lang)
        return result.get("text", "").strip()
    except Exception as e:
        return f"[Whisper xato]: {e}"
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
