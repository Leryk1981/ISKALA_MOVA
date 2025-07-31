FROM python:3.11-slim

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y \
git \
curl \
&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копіювання залежностей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду
COPY . .

# Створення користувача
RUN useradd --create-home --shell /bin/bash app && \
chown -R app:app /app

USER app

EXPOSE 8080

CMD ["python", "main.py"]
