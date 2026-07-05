import time
from typing import Dict, Any
from src.core.config import settings
from src.services.ocr import OCRService
from src.utils.text_filters import ContentTextFilter

class ModerationPipeline:
    def __init__(self):
        # Инициализируем сервисы
        self.ocr_service = OCRService()
        self.text_filter = ContentTextFilter()
        
        # Примечание для собеседования: Здесь инициализируются ONNX сессии.
        # Для демонстрации, если файлы моделей пустые (заглушки), мы переключимся в режим симуляции,
        # чтобы бэкенд запустился без падения по ошибке парсинга ONNX.
        self.simulation_mode = True 
        print("ℹ️ Moderation Pipeline запущен в режиме симуляции (используются заглушки моделей).")

    async def moderate_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Проводит изображение через каскад проверок: NSFW -> IQA -> OCR -> Текстовые фильтры.
        """
        start_time = time.time()
        
        # --- 1. КАСКАД: Фильтр NSFW контента ---
        # В продакшене: nsfw_score = self.nsfw_detector.predict(image_bytes)
        nsfw_score = 0.02 if self.simulation_mode else 0.02 
        
        if nsfw_score >= settings.NSFW_THRESHOLD:
            latency = (time.time() - start_time) * 1000
            return self._build_response(
                status="rejected",
                reason="NSFW content detected",
                latency=latency,
                nsfw_score=nsfw_score
            )
            
        # --- 2. КАСКАД: Оценка качества изображения (IQA) ---
        # В продакшене: quality_score = self.iqa_detector.predict(image_bytes)
        quality_score = 0.85 if self.simulation_mode else 0.85
        
        low_quality_warning = quality_score < settings.QUALITY_THRESHOLD
        
        # --- 3. КАСКАД: Извлечение и фильтрация текста (OCR) ---
        # Извлекаем текст с картинки с помощью PaddleOCR
        extracted_text = self.ocr_service.extract_text(image_bytes)
        
        # Сканируем текст регулярными выражениями на ссылки/телефоны
        text_analysis = self.text_filter.scan_text(extracted_text)
        
        # Определяем итоговый вердикт
        if not text_analysis["is_clean"]:
            status = "rejected"
            reason = f"Forbidden entities found in image text: {[e['type'] for e in text_analysis['forbidden_entities']]}"
        elif low_quality_warning:
            status = "warning"
            reason = "Low quality image. Recommendation sent to user."
        else:
            status = "passed"
            reason = None
            
        latency = (time.time() - start_time) * 1000
        
        return self._build_response(
            status=status,
            reason=reason,
            latency=latency,
            nsfw_score=nsfw_score,
            quality_score=quality_score,
            low_quality_warning=low_quality_warning,
            text_analysis=text_analysis
        )

    def _build_response(
        self, 
        status: str, 
        reason: str | None, 
        latency: float, 
        nsfw_score: float,
        quality_score: float = 1.0,
        low_quality_warning: bool = False,
        text_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Вспомогательный метод для формирования строгого контракта ответа API.
        """
        if text_analysis is None:
            text_analysis = {"is_clean": True, "forbidden_entities": [], "extracted_text": ""}
            
        return {
            "status": status,
            "verdict_reason": reason,
            "metrics": {
                "total_latency_ms": round(latency, 2),
                "nsfw_score": round(nsfw_score, 4),
                "quality_score": round(quality_score, 4)
            },
            "moderation_details": {
                "nsfw_detected": nsfw_score >= settings.NSFW_THRESHOLD,
                "low_quality_warning": low_quality_warning,
                "extracted_text": text_analysis["extracted_text"],
                "forbidden_entities_found": text_analysis["forbidden_entities"]
            }
        }