from fastapi import FastAPI, UploadFile, File, HTTPException, status
from src.core.config import settings
from src.core.pipeline.py_or_imported_module import ModerationPipeline  # Импортируем наш пайплайн

# Подменяем импорт, чтобы путь был чистым относительно корня src
from src.core.pipeline import ModerationPipeline

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Высокопроизводительный асинхронный конвейер для автоматической фильтрации NSFW контента, IQA и текста на изображениях.",
    version="1.0.0"
)

# Инициализируем пайплайн при старте сервера
pipeline = ModerationPipeline()

@app.get("/", tags=["Healthcheck"])
async def root():
    """
    Эндпоинт проверки работоспособности сервиса (Liveness Probe).
    """
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

@app.post(
    "/moderate", 
    status_code=status.HTTP_200_OK,
    tags=["Moderation"],
    summary="Проверить изображение на нарушения",
    description="Принимает файл изображения, прогоняет через каскад моделей и возвращает вердикт."
)
async def moderate_image(file: UploadFile = File(...)):
    # 1. Валидация формата файла
    allowed_extensions = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый формат файла. Разрешены только: {allowed_extensions}"
        )
        
    try:
        # 2. Асинхронно вычитываем байты изображения напрямую в оперативную память
        image_bytes = await file.read()
        
        # 3. Передаем байты в наш каскадный пайплайн модерации
        result = await pipeline.moderate_image(image_bytes)
        
        return result
        
    except Exception as e:
        # В случае непредвиденного сбоя возвращаем 500 ошибку
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера при обработке медиа: {str(e)}"
        )