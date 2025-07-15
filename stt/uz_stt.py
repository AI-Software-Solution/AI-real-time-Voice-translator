# import requests
# from io import BytesIO
# from stt.auth_tokens import token_manager
# import os
# from dotenv import load_dotenv
# load_dotenv()
# base_url=os.getenv("API_URL")

# # print(base_url)

# def uz_stt(audio_bytes: bytes) -> str:
#     token = token_manager.get_token()
#     url=base_url
#     headers = {"Authorization": f"JWT {token}"}
#     file_like = BytesIO(audio_bytes)
#     files = {'audio': ('audio.wav', file_like, 'audio/wav')}
#     response = requests.post(url, headers=headers, files=files)
#     response.raise_for_status()
#     return response.text.strip()

# import openai
# import os
# from dotenv import load_dotenv
# from io import BytesIO

# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

# def uz_stt(audio_bytes: bytes, lang: str = "uz") -> str:
#     try:
#         # audio_bytes ni filega o‘xshatamiz
#         audio_file = BytesIO(audio_bytes)
#         audio_file.name = "audio.wav"

#         # OpenAI Whisper API chaqiruvi
#         transcript = openai.Audio.transcribe(
#             model="whisper-1",
#             file=audio_file,
#             # language=lang,  # Masalan: "uz", "en", "ru"
#             response_format="text"
#         )
#         return transcript.strip()
#     except Exception as e:
#         return f"[Whisper xato]: {e}"


import os
import zipfile
import requests
from tqdm import tqdm
from io import BytesIO
from vosk import Model, KaldiRecognizer
import json
import wave
import tempfile

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-uz-0.22.zip"
MODEL_DIR = "vosk-model-small-uz-0.22"

# --- 1. Modelni yuklab olish va ochish ---
def download_and_extract_model(url: str, target_dir: str):
    if os.path.exists(target_dir):
        print(f"[✅] Model allaqachon mavjud: {target_dir}")
        return
    print("[⬇️] Model yuklanmoqda...")
    response = requests.get(url, stream=True)
    total = int(response.headers.get('content-length', 0))
    zip_bytes = BytesIO()
    with tqdm(total=total, unit='B', unit_scale=True, desc="Yuklab olish") as pbar:
        for data in response.iter_content(chunk_size=1024):
            zip_bytes.write(data)
            pbar.update(len(data))
    zip_bytes.seek(0)
    print("[📦] Model zipdan chiqarilmoqda...")
    with zipfile.ZipFile(zip_bytes) as zip_ref:
        zip_ref.extractall()  # joriy papkaga chiqaramiz
    print(f"[✅] Model tayyor: {target_dir}")

# --- 2. STT funksiyasi ---
def uz_stt(audio_bytes: bytes) -> str:
    model = Model(MODEL_DIR)
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        wf = wave.open(tmp_path, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            wf.close()
            os.remove(tmp_path)
            return "[VOSK xato]: Audio format noto‘g‘ri. Mono PCM 16-bit bo‘lishi kerak."

        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)

        final_text = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                final_text += result.get("text", "") + " "
        result = json.loads(rec.FinalResult())
        final_text += result.get("text", "")
        wf.close()
        os.remove(tmp_path)
        return final_text.strip()

    except Exception as e:
        return f"[VOSK xato]: {e}"

# --- 3. Modelni yuklab olish ---
download_and_extract_model(MODEL_URL, MODEL_DIR)

# --- 4. Sinab ko‘rish ---
# with open("audio_uzbek.wav", "rb") as f:
#     text = uz_stt(f.read())
#     print("Natija:", text)

