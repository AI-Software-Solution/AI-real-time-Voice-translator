import requests
from io import BytesIO
from stt.auth_tokens import token_manager
import os
from dotenv import load_dotenv
load_dotenv()
base_url=os.getenv("API_URL")

# print(base_url)

def uz_stt(audio_bytes: bytes) -> str:
    token = token_manager.get_token()
    url=base_url
    headers = {"Authorization": f"JWT {token}"}
    file_like = BytesIO(audio_bytes)
    files = {'audio': ('audio.wav', file_like, 'audio/wav')}
    response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()
    return response.text.strip()
