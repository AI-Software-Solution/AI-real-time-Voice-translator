from deep_translator import GoogleTranslator

def translate_text(text: str, source: str, target: str) -> str:
    try:
        translated = GoogleTranslator(source=source, target=target).translate(text)
        return translated
    except Exception as e:
        return f"[Tarjima xato]: {e}"
