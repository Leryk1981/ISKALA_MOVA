# ISKALA RAG System
FROM python:3.11-slim

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    nano \
    vim \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Створення користувача
RUN useradd --create-home --shell /bin/bash app && \
    usermod -aG sudo app && \
    echo "app ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Створення робочої директорії
WORKDIR /app

# Копіювання файлів залежностей
COPY requirements.txt .

# Встановлення Python залежностей
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду RAG системи
COPY . .

# Створення необхідних директорій
RUN mkdir -p /app/vector_store /app/capsules /app/uploads && \
    chown -R app:app /app && \
    chmod -R 755 /app

# Переключення на користувача app
USER app

# Відкриття порту
EXPOSE 8002

# Команда запуску
CMD ["python", "api.py"] 