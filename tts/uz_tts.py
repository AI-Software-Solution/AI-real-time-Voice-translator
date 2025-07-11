import requests
from stt.auth_tokens import token_manager
import os 
from dotenv import load_dotenv
load_dotenv()
base_url=os.getenv("tts_url")


def uz_tts(text: str) -> bytes:
    token = token_manager.get_token()
    url = ""
    headers = {"Authorization": f"JWT {token}"}
    data = {"text": text, "version": "1"}
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.content