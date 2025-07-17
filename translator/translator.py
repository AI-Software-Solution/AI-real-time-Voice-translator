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
import logging
from googletrans import Translator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

LANG_MAP = {
    "uz": "Uzbek",
    "ko": "Korean",
    "en": "English",
    "ru": "Russian",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "es": "Spanish",
    "pt": "Portuguese",
}

def translate(text: str, source_lang: str, target_lang: str) -> str:
    if not text.strip():
        logger.error("Translation failed: Input text is empty")
        raise ValueError("Matn bo‘sh bo‘lishi mumkin emas")

    source_lang = source_lang.lower()
    target_lang = target_lang.lower()
    source_lang_name = LANG_MAP.get(source_lang, source_lang)
    target_lang_name = LANG_MAP.get(target_lang, target_lang)

    prompt = (
        f"Translate the following text from {source_lang_name} to {target_lang_name}. "
        f"Return only the translated text, without any explanation:\n\n{text}"
    )

    try:
        if not openai.api_key:
            logger.error("OPENAI_API_KEY is not set")
            raise ValueError("OPENAI_API_KEY sozlanmagan")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000,
        )
        translated_text = response["choices"][0]["message"]["content"].strip()
        logger.info(f"OpenAI translated '{text}' from {source_lang_name} to {target_lang_name}: {translated_text}")
        return translated_text
    except Exception as e:
        logger.warning(f"OpenAI translation failed: {str(e)}, trying Google Translate")
        try:
            translator = Translator()
            result = translator.translate(text, src=source_lang, dest=target_lang)
            translated_text = result.text
            logger.info(f"Google translated '{text}' from {source_lang_name} to {target_lang_name}: {translated_text}")
            return translated_text
        except Exception as g_e:
            logger.error(f"Google Translate error: {str(g_e)}")
            raise Exception(f"[Tarjima xatosi]: OpenAI: {str(e)}, Google: {str(g_e)}")
