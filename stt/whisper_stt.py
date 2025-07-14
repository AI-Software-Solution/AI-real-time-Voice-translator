import whisper
import tempfile
import os
import torch

# 🔥 Modelni GPUda majburiy yuklaymiz
model = whisper.load_model("base")  # yoki "medium"
model = model.to("cuda")
print("CUDA mavjud:", torch.cuda.is_available())
print("Model qaysi device da:", next(model.parameters()).device)

def whisper_stt(audio_bytes: bytes, lang: str = "en") -> str:
    """
    GPU-da ishlovchi Whisper STT
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name

    try:
        result = model.transcribe(
            temp_audio_path,
            language=None if lang == "auto" else lang,
            fp16=True  # <-- GPU'ni to‘liq ishga soladi
        )
        return result.get("text", "").strip()
    except Exception as e:
        return f"[Whisper xato]: {e}"
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
