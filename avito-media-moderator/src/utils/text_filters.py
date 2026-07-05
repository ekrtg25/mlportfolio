import re
from typing import List, Dict, Any

class ContentTextFilter:
    def __init__(self):
        # 1. Паттерн для поиска номеров телефонов (различные форматы: +7, 8, с дефисами и скобками)
        self.phone_pattern = re.compile(
            r'(?:\+?7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}'
        )
        
        # 2. Паттерн для поиска веб-ссылок (http, https, www или просто доменные зоны .ru/.com)
        self.link_pattern = re.compile(
            r'(https?://[^\s]+|(?:www\.)?[a-zA-Z0-9.-]+\.(?:ru|com|net|org|io)[^\s]*)'
        )
        
        # 3. Паттерн для поиска Telegram-контактов (@username или t.me/...)
        self.telegram_pattern = re.compile(
            r'(@[a-zA-Z0-9_]{5,32}|t\.me/[a-zA-Z0-9_]{5,32})'
        )

    def scan_text(self, text: str) -> Dict[str, Any]:
        """
        Сканирует текст и возвращает список найденных нарушений.
        """
        # Приводим к нижнему регистру для стабильности поиска
        clean_text = text.lower()
        
        found_phones = self.phone_pattern.findall(text) # Ищем в оригинальном регистре
        found_links = self.link_pattern.findall(clean_text)
        found_tg = self.telegram_pattern.findall(clean_text)
        
        forbidden_entities = []
        if found_phones:
            forbidden_entities.append({"type": "phone", "matches": found_phones})
        if found_links:
            forbidden_entities.append({"type": "forbidden_link", "matches": found_links})
        if found_tg:
            forbidden_entities.append({"type": "telegram_contact", "matches": found_tg})
            
        is_clean = len(forbidden_entities) == 0
        
        return {
            "is_clean": is_clean,
            "forbidden_entities": forbidden_entities,
            "extracted_text": text
        }