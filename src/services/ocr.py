import numpy as np
import cv2
import easyocr

class OCRService:
    def __init__(self):
        # Инициализируем EasyOCR для русского (ru) и английского (en) языков.
        # gpu=False использует процессор, что на M3 Pro работает стабильно и быстро.
        self.reader = easyocr.Reader(['ru', 'en'], gpu=False)

    def extract_text(self, image_bytes: bytes) -> str:
        """
        Принимает байты изображения, распознает текст через EasyOCR и возвращает его единой строкой.
        """
        try:
            # Декодируем байты в NumPy массив для OpenCV
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return ""
            
            # Запускаем чтение текста. detail=0 означает, что нам нужен только чистый текст
            # без координат рамок (bounding boxes), что экономит память.
            result = self.reader.readtext(img, detail=0)
            
            # Соединяем распознанные строчки в единый текст
            return " ".join(result)
            
        except Exception as e:
            print(f"Error during EasyOCR processing: {e}")
            return ""