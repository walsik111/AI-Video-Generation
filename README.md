# AI Video Generation

Автоматизированный пайплайн генерации видеоконтента на основе открытых нейросетевых диффузионных моделей и алгоритмов композитинга. Предоставляет производительный REST API на FastAPI и веб-интерфейс для генерации роликов по текстовым промптам.

**Автор:** Дима Евгеньев ([@walsik111](https://github.com/walsik111))

---

## Стек технологий

- **FastAPI (Python)** — асинхронный серверный фреймворк для обработки задач генерации
- **Stable Diffusion (Hugging Face Diffusers)** — генерация ключевых кадров по текстовому описанию
- **PyTorch** — вычисления и инференс моделей машинного обучения
- **FFmpeg** — покадровая сборка, плавные переходы и постобработка видео
- **Tailwind CSS & JavaScript** — клиентский интерфейс отправки промптов и мониторинга задач
- **Docker & Docker Compose** — контейнеризация и воспроизводимое окружение

---

## Локальный запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/walsik111/ai-video-generation.git
cd ai-video-generation
```

### 2. Запуск через Docker Compose (рекомендуется)

```bash
docker-compose up --build
```

- API бэкенда будет доступно по адресу: [http://localhost:8000/api](http://localhost:8000/api)
- Веб-интерфейс будет доступен по адресу: [http://localhost:3000](http://localhost:3000)

### 3. Ручной запуск бэкенда

```bash
cd backend
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
