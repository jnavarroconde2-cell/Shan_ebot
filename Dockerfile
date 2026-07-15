FROM python:3.11-slim

# Instalar ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Carpeta de trabajo
WORKDIR /app

# Copiar archivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .

# Comando para iniciar
CMD ["python", "bot.py"]
