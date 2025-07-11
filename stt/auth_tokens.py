import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()
user=os.getenv("user")
password=os.getenv("password")
token_url=os.getenv("API_TOKEN_URL")
# print(f"{user}>>{password}")

class TokenManager:
    def __init__(self):
        self.token = None
        self.expiry = 0  # timestamp

    def get_token(self):
        if self.token is None or time.time() > self.expiry:
            print("🔄 Getting new token...")
            url = token_url
            data = {"username":user, "password":password}
            response = requests.post(url, data=data)
            response.raise_for_status()
            json_data = response.json()
            self.token = json_data["access"]
            self.expiry = time.time() + 540  # 9 minut ishlatamiz xavfsizlik uchun
        return self.token

token_manager = TokenManager()
