# Backend Dockerfile (multi-stage)
# Stage 1: builder (install dependencies)
FROM python:3.10-slim as builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y git build-essential ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Stage 2: runtime
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y ffmpeg libgl1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY backend /app
ENV WORK_DIR=/data
VOLUME ["/data"]
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Optional GPU notes:
# To build a GPU-enabled image, base on a CUDA image and install pytorch with CUDA support.
# This file keeps the default CPU-only setup for broad compatibility.
