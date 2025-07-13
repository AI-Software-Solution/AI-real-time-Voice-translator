# stt/ru_stt.py
import torch
from io import BytesIO

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model, decoder, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_stt',
    device=device
)

(read_batch, split_into_batches, read_audio, prepare_model_input) = utils

def ru_stt(audio_bytes: bytes) -> str:
    try:
        # ❌ sampling_rate ni olib tashladik
        audio = read_audio(BytesIO(audio_bytes))
        batch = prepare_model_input([audio], device=device)
        output = model(batch)
        text = decoder(output[0].cpu())
        return text.strip()
    except Exception as e:
        return f"[Silero STT xato]: {e}"
