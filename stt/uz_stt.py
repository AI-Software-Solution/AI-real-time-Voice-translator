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

import openai
import os
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def uz_stt(audio_bytes: bytes, lang: str = "uz") -> str:
    try:
        # audio_bytes ni filega o‘xshatamiz
        audio_file = BytesIO(audio_bytes)
        audio_file.name = "audio.wav"

        # OpenAI Whisper API chaqiruvi
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            # language=lang,  # Masalan: "uz", "en", "ru"
            response_format="text"
        )
        return transcript.strip()
    except Exception as e:
        return f"[Whisper xato]: {e}"


