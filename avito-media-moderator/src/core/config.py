import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Название проекта для документации OpenAPI (Swagger)
    PROJECT_NAME: str = "Avito Shield: Мультимодальный Конвейер Модерации"
    
    # Пути к ONNX-моделям, которые лежат в нашей папке models/
    NSFW_MODEL_PATH: str = os.path.join("models", "nsfw_model.onnx")
    IQA_MODEL_PATH: str = os.path.join("models", "iqa_model.onnx")
    
    # --- Пороги чувствительности (Thresholds) ---
    
    # Если модель уверена в NSFW больше чем на 85% — автоматический жесткий бан
    NSFW_THRESHOLD: float = 0.85
    
    # Оценка качества фото ниже 0.4 — выдаем предупреждение пользователю переснять товар
    QUALITY_THRESHOLD: float = 0.40
    
    class Config:
        env_file = ".env"

# Инициализируем синглтон (одиночный объект) настроек для использования во всем проекте
settings = Settings()