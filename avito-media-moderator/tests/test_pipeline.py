import pytest
from src.utils.text_filters import ContentTextFilter

def test_text_filter_clean():
    filter_system = ContentTextFilter()
    result = filter_system.scan_text("Продам отличный диван в хорошем состоянии. Самовывоз.")
    assert result["is_clean"] is True
    assert len(result["forbidden_entities"]) == 0

def test_text_filter_detects_phone():
    filter_system = ContentTextFilter()
    result = filter_system.scan_text("Звоните мне 89991234567 в любое время")
    assert result["is_clean"] is False
    assert any(e["type"] == "phone" for e in result["forbidden_entities"])

def test_text_filter_detects_telegram():
    filter_system = ContentTextFilter()
    result = filter_system.scan_text("Писать только в телегу @avito_rekruter_босс")
    assert result["is_clean"] is False
    assert any(e["type"] == "telegram_contact" for e in result["forbidden_entities"])