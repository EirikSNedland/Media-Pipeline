FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install runtime codecs, extraction binaries, and Tesseract layout dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    mkvtoolnix \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-nor \
    tesseract-ocr-deu \
    tesseract-ocr-fra \
    tesseract-ocr-spa \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install the native Python subtitle coordinator layers
RUN pip install --no-cache-dir pgsrip babelfish

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]