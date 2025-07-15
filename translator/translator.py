# from deep_translator import GoogleTranslator

# def translate_text(text: str, source: str, target: str) -> str:
#     try:
#         translated = GoogleTranslator(source=source, target=target).translate(text)
#         return translated
#     except Exception as e:
#         return f"[Tarjima xato]: {e}"


import openai
import os 
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def translate(text: str, source_lang: str, target_lang: str) -> str:
    prompt = (
        f"Please translate the following text from {source_lang} to {target_lang}, "
        f"and only return the translated text, without explanation:\n\n{text}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[GPT tarjima xato]: {e}"
