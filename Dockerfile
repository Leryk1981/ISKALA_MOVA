# ISKALA Core - Объединенная версия
FROM python:3.11-slim

# Системные зависимости
RUN apt-get update && apt-get install -y \
    git curl wget nano vim sudo \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя
RUN useradd --create-home --shell /bin/bash app && \
    usermod -aG sudo app && \
    echo "app ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .

# Установка Python пакетов
RUN pip install --no-cache-dir -r requirements.txt

# Дополнительные пакеты для OpenAPI Tool Server
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    requests \
    pydantic

# Копирование всех модулей
COPY src/ ./src/
COPY data/ ./data/
COPY state/ ./state/
COPY trees/ ./trees/
COPY vault/ ./vault/
COPY rag_system/ ./rag_system/
COPY shield/ ./shield/
COPY translation/ ./translation/
COPY tool_api/ ./tool_api/
COPY universal_api_connector/ ./universal_api_connector/

# Копирование OpenAPI Tool Server
COPY iskala_openapi_server.py ./

# Создание директорий
RUN mkdir -p /app/workspace /app/state/logs /app/vector_db /app/adapters /app/data/capsules /app/logs && \
    chown -R app:app /app && \
    chmod -R 755 /app

USER app

EXPOSE 8001 8081 8082 8002 8003

# Запуск объединенного сервиса (по умолчанию)
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"] 