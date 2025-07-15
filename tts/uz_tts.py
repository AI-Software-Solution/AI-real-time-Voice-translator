import edge_tts
import asyncio

async def uz_tts(text: str) -> bytes:
    communicate = edge_tts.Communicate(text, voice="uz-UZ-SardorNeural")
    audio_fp = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_fp += chunk["data"]
    return audio_fp

# Sinov uchun:
# audio = asyncio.run(uz_tts("Salom, dunyo!"))
# with open("output.mp3", "wb") as f: f.write(audio)

