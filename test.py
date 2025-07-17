import asyncio
import websockets
import json
import queue
import base64
from io import BytesIO
import pygame
import pyaudio
import wave
import struct

# Инициализация
pygame.mixer.init()
message_queue = queue.Queue()

# Параметры аудио (должны совпадать с ожидаемыми сервером)
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # 16kHz - стандартная частота для распознавания речи
CHUNK = 1024
RECORD_SECONDS = 5

audio = pyaudio.PyAudio()

def create_wav_header(sample_rate, bit_depth, channels, data_length):
    """Создает WAV-заголовок для raw аудио данных"""
    byte_rate = sample_rate * channels * bit_depth // 8
    block_align = channels * bit_depth // 8
    
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + data_length,
        b'WAVE',
        b'fmt ',
        16,
        1,  # PCM format
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bit_depth,
        b'data',
        data_length
    )
    return header

async def record_and_recognize():
    """Записывает аудио в WAV формате и отправляет на сервер"""
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                       rate=RATE, input=True,
                       frames_per_buffer=CHUNK)
    
    print("\nГоворите сейчас... (скажите 'стоп' для выхода)")
    
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    
    # Создаем WAV файл в памяти
    with BytesIO() as wav_buffer:
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(audio.get_sample_size(FORMAT))
            wav_file.setframerate(RATE)
            wav_file.writeframes(b''.join(frames))
        
        # Получаем WAV данные
        wav_buffer.seek(0)
        wav_data = wav_buffer.read()
    
    # Кодируем в base64
    audio_b64 = base64.b64encode(wav_data).decode('utf-8')
    
    # Отправляем на сервер STT
    async with websockets.connect("wss://fastapi.ilmiy1.uz/ws/stt") as ws:
        await ws.send(json.dumps({
            "lang": "en",
            "audio": audio_b64
        }))
        response = await ws.recv()
        text = json.loads(response).get("text", "")
        
        if text.lower() == "стоп":
            message_queue.put(None)
        elif text:
            print(f"Распознано: {text}")
            message_queue.put(text)

async def play_audio(audio_base64):
    """Воспроизведение аудио из base64"""
    try:
        audio_data = base64.b64decode(audio_base64)
        audio_file = BytesIO(audio_data)
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
            
    except Exception as e:
        print(f"Ошибка воспроизведения: {e}")

async def translate_and_speak(text):
    """Перевод и озвучка текста"""
    # Перевод
    async with websockets.connect("wss://fastapi.ilmiy1.uz/ws/translate") as ws:
        await ws.send(json.dumps({
            "text": text,
            "source": "en",
            "target": "uz"
        }))
        translated = json.loads(await ws.recv()).get("translation", "")
        print(f"Перевод: {translated}")
    
    # Озвучка
    if translated:
        async with websockets.connect("wss://fastapi.ilmiy1.uz/ws/tts") as ws:
            await ws.send(json.dumps({
                "text": translated,
                "lang": "uz"
            }))
            audio_data = json.loads(await ws.recv()).get("audio", "")
            if audio_data:
                await play_audio(audio_data.split(",")[-1] if "," in audio_data else audio_data)
    

async def main():
    """Основной цикл"""
    while True:
        # Записываем и распознаем речь
        await record_and_recognize()
        
        # Обрабатываем распознанный текст
        if not message_queue.empty():
            text = message_queue.get()
            if text is None:  # Сигнал завершения
                break
            await translate_and_speak(text)

if __name__ == "__main__":
    print("Голосовой переводчик запущен. Скажите 'стоп' для выхода.")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПрограмма завершена")
    finally:
        audio.terminate()
        pygame.mixer.quit()
