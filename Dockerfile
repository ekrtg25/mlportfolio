# Изучаем официальный легковесный образ Python
FROM python:3.12-slim

# Устанавливаем системные зависимости для работы OpenCV и графики в Linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем библиотеки без кэширования для уменьшения размера образа
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем все исходники проекта в контейнер
COPY . .

# Открываем порты для FastAPI (8000) и Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# По умолчанию запускаем наше интерактивное UI демо
CMD ["streamlit", "run", "app_demo.py", "--server.port=8501", "--server.address=0.0.0.0"]