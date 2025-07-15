# import whisper
# import tempfile
# import os
# import torch

# # 🔥 Modelni GPUda majburiy yuklaymiz
# model = whisper.load_model("base")  # yoki "medium"
# model = model.to("cuda")
# print("CUDA mavjud:", torch.cuda.is_available())
# print("Model qaysi device da:", next(model.parameters()).device)

# def whisper_stt(audio_bytes: bytes, lang: str = "en") -> str:
#     """
#     GPU-da ishlovchi Whisper STT
#     """
#     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
#         temp_audio.write(audio_bytes)
#         temp_audio_path = temp_audio.name

#     try:
#         result = model.transcribe(
#             temp_audio_path,
#             language=None if lang == "auto" else lang,
#             fp16=True  # <-- GPU'ni to‘liq ishga soladi
#         )
#         return result.get("text", "").strip()
#     except Exception as e:
#         return f"[Whisper xato]: {e}"
#     finally:
#         if os.path.exists(temp_audio_path):
#             os.remove(temp_audio_path)

import openai 
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()  # .env fayldan API keyni olish uchun

openai.api_key = os.getenv("OPENAI_API_KEY")  # .env ichida OPENAI_API_KEY=... bo'lishi kerak

def whisper_stt(audio_bytes: bytes, lang: str = "en") -> str:
    """
    OpenAI Whisper API orqali ovozni matnga o‘giradi
    :param audio_bytes: WAV formatdagi audio fayl baytlari
    :param lang: til kodi ('en', 'uz', 'ru' va hokazo)
    :return: transkriptsiya qilingan matn
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",  # Whisper 3 API da `whisper-1` nomi ishlatiladi
                file=audio_file,
                language=lang if lang != "auto" else None,
                response_format="text"
            )
        return transcript.strip()
    except Exception as e:
        return f"[OpenAI Whisper xato]: {e}"
    finally:
        os.remove(tmp_path)


# import tempfile
# import os
# import whisper
# import torch
# import gc

# # GPU xotirasini tozalash
# torch.cuda.empty_cache()
# gc.collect()

# # GPU bo‘lsa, undan foydalanamiz, aks holda CPU
# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# # 🟢 KICHIKROQ MODEL: large-v3 emas, medium yuklanmoqda
# model = whisper.load_model("medium", device=DEVICE)

# def whisper_stt(audio_bytes: bytes, lang: str = "en") -> str:
#     """
#     Lokal Whisper 'medium' modeli orqali audio-ni matnga o‘giradi
#     :param audio_bytes: WAV formatdagi audio fayl baytlari
#     :param lang: Til kodi ('uz', 'en', 'ru', ...)
#     :return: Transkripsiya qilingan matn
#     """
#     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
#         tmp.write(audio_bytes)
#         tmp.flush()
#         tmp_path = tmp.name

#     try:
#         result = model.transcribe(
#             tmp_path,
#             language=lang if lang != "auto" else None,
#             fp16=torch.cuda.is_available()
#         )
#         return result["text"].strip()
#     except Exception as e:
#         return f"[Whisper xato]: {e}"
#     finally:
#         os.remove(tmp_path)



# import whisper
# import tempfile, os, torch

# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# # 🟣 Load standard Whisper for EN/RU/etc.
# global_model = whisper.load_model("large-v2", device=DEVICE)

# # 🟣 Load Uzbek‑fine‑tuned Whisper separate pipeline
# from transformers import pipeline, WhisperForConditionalGeneration, WhisperProcessor
# uz_model = WhisperForConditionalGeneration.from_pretrained(
#     "totetecdev/whisper-large-v2-uzbek-100steps",
#     torch_dtype=torch.float16
# ).to(DEVICE)
# uz_proc = WhisperProcessor.from_pretrained("totetecdev/whisper-large-v2-uzbek-100steps")
# uz_pipe = pipeline("automatic-speech-recognition", model=uz_model,
#                    tokenizer=uz_proc.tokenizer, feature_extractor=uz_proc.feature_extractor,
#                    device=0, torch_dtype=torch.float16)

# def stt(audio_bytes: bytes, lang: str):
#     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
#         tmp.write(audio_bytes); tmp.flush()
#         path = tmp.name
#     try:
#         if lang == "uz":
#             return uz_pipe(path)["text"].strip()
#         else:
#             return global_model.transcribe(path, language=lang)["text"].strip()
#     finally:
#         os.remove(path)


