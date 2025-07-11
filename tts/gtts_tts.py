from gtts import gTTS
import tempfile

def gtts_tts(text: str, lang: str) -> bytes:
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        with open(f.name, "rb") as audio_file:
            return audio_file.read()

