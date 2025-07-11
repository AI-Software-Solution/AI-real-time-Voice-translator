import streamlit as st
import sounddevice as sd
import soundfile as sf
import tempfile
import asyncio
import websockets
import base64
import json

st.title("🎙️ Real-Time Voice Translator")

source_lang = st.selectbox("🎧 Manba tili (source)", ["uz", "en", "ru"])
target_lang = st.selectbox("🔊 Maqsad tili (target)", ["uz", "en", "ru"])

if st.button("🎤 Gapirishni boshlash"):
    duration = 5
    fs = 16000
    st.info("⏺ Gapiring...")

    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        sf.write(temp.name, recording, fs)
        temp.seek(0)
        wav_bytes = temp.read()

    audio_b64 = base64.b64encode(wav_bytes).decode("utf-8")

    async def process_translation():
        # --- 1. STT ---
        async with websockets.connect("ws://localhost:8001/ws/stt") as ws_stt:
            await ws_stt.send(json.dumps({"lang": source_lang, "audio": audio_b64}))
            stt_response = await ws_stt.recv()
            stt_data = json.loads(stt_response)

        if "error" in stt_data:
            st.error(f"❌ STT xato: {stt_data['error']}")
            return

        original_text = stt_data.get("text", "")
        st.subheader("📝 Tan olingan matn:")
        st.write(original_text)

        # --- 2. Translate ---
        async with websockets.connect("ws://localhost:8001/ws/translate") as ws_translate:
            await ws_translate.send(json.dumps({
                "text": original_text,
                "source": source_lang,
                "target": target_lang
            }))
            tr_response = await ws_translate.recv()
            tr_data = json.loads(tr_response)

        if "error" in tr_data:
            st.error(f"❌ Tarjima xato: {tr_data['error']}")
            return

        translated_text = tr_data.get("translation", "")
        st.subheader("🌍 Tarjima:")
        st.write(translated_text)

        # --- 3. TTS ---
        async with websockets.connect("ws://localhost:8001/ws/tts") as ws_tts:
            await ws_tts.send(json.dumps({
                "text": translated_text,
                "lang": target_lang
            }))
            tts_response = await ws_tts.recv()
            tts_data = json.loads(tts_response)

        if "error" in tts_data:
            st.error(f"❌ TTS xato: {tts_data['error']}")
            return

        audio_b64_out = tts_data.get("audio", "")
        audio_bytes = base64.b64decode(audio_b64_out)

        st.subheader("🔊 Ovoz natijasi:")
        st.audio(audio_bytes, format="audio/wav")

    asyncio.run(process_translation())
