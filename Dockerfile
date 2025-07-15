FROM python:3.12-slim

WORKDIR /app

# PyAudio uchun kerakli tizim kutubxonalarini o‘rnatamiz
RUN apt-get update && \
    apt-get install -y gcc portaudio19-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]