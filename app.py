import streamlit as st
import sounddevice as sd
import soundfile as sf
import tempfile
import asyncio
import websockets
import base64
import json

# Tillar ro‘yxati: {To‘liq nom: ISO kodi}
languages = {
    "🇺🇿 Uzbek": "uz",
    "🇺🇸 English": "en",
    "🇷🇺 Russian": "ru",
    "🇫🇷 French": "fr",
    "🇩🇪 German": "de",
    "🇨🇳 Chinese": "zh",
    "🇯🇵 Japanese": "ja",
    "🇰🇷 Korean": "ko",
    "🇪🇸 Spanish": "es",
    "🇵🇹 Portuguese": "pt",
    "🇲🇳 Mongolian": "mn"
}

st.title("🎙️ Real-Time Voice Translator")

# Foydalanuvchiga to‘liq nomni ko‘rsatamiz
source_lang_name = st.selectbox("🎧 Manba tili (Source Language)", list(languages.keys()))
target_lang_name = st.selectbox("🔊 Maqsad tili (Target Language)", list(languages.keys()))

# Qisqartma kodlarni olish
source_lang = languages[source_lang_name]
target_lang = languages[target_lang_name]

# Gapirish tugmasi
if st.button("🎤 Gapirishni boshlash"):
    duration = 5  # sekund
    fs = 16000    # audio chastota
    st.info("⏺ Gapiring...")

    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        sf.write(temp.name, recording, fs)
        temp.seek(0)
        wav_bytes = temp.read()

    audio_b64 = base64.b64encode(wav_bytes).decode("utf-8")

    async def process_translation():
        try:
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

        except Exception as e:
            st.error(f"❌ Aloqa xatosi: {e}")

        

    asyncio.run(process_translation())
st.markdown("---")
st.header("📤 Matndan tarjima va ovoz")

with st.form("translate_text_form"):
    input_text = st.text_area("✍️ Matnni kiriting", "")
    source_text_lang_name = st.selectbox("Manba tili", list(languages.keys()), index=0, key="source_text")
    target_text_lang_name = st.selectbox("Maqsad tili", list(languages.keys()), index=1, key="target_text")
    submitted = st.form_submit_button("Tarjima va ovoz chiqarish")

if submitted:
    source_text_lang = languages[source_text_lang_name]
    target_text_lang = languages[target_text_lang_name]

    with st.spinner("⏳ Tarjima qilinmoqda va ovozga aylantirilmoqda..."):
        try:
            import requests

            response = requests.post(
                "http://localhost:8001/translate-tts",  # API endpoint
                json={
                    "text": input_text,
                    "source": source_text_lang,
                    "target": target_text_lang
                },
                timeout=10
            )

            if response.status_code != 200:
                st.error(f"❌ Xatolik: {response.json().get('detail')}")
            else:
                result = response.json()
                st.subheader("🌍 Tarjima:")
                st.write(result["translation"])

                audio_data = base64.b64decode(result["audio"])
                st.subheader("🔊 Ovoz:")
                st.audio(audio_data, format="audio/wav")

        except Exception as e:
            st.error(f"❌ So‘rov xatosi: {e}")
