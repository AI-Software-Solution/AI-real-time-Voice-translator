import edge_tts

async def tts_edge(text: str, lang: str = "uz-UZ-SardorNeural") -> bytes:
    communicate = edge_tts.Communicate(text, voice=lang)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data


# Sinov uchun:
# audio = asyncio.run(uz_tts("Salom, dunyo!"))
# with open("output.mp3", "wb") as f: f.write(audio)

