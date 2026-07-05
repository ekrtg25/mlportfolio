import streamlit as st
import asyncio
from PIL import Image
import io
from src.core.pipeline import ModerationPipeline

# Настраиваем конфигурацию страницы Streamlit
st.set_page_config(
    page_title="Avito Shield Demo",
    page_icon="🛡️",
    layout="wide"
)

# Инициализируем пайплайн модерации и кэшируем его, чтобы не создавать заново при каждом клике
@st.cache_resource
def get_pipeline():
    return ModerationPipeline()

pipeline = get_pipeline()

st.title("🛡️ Avito Shield: Автоматическая Модерация Медиаконтента")
st.caption("Прототип интеллектуального конвейера фильтрации NSFW, оценки качества (IQA) и анализа скрытого текста (OCR)")

st.write("---")

# Разделяем интерфейс на две колонки: левая для загрузки, правая для результатов
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📥 Загрузка изображения")
    uploaded_file = st.file_uploader(
        "Выберите фотографию объявления (JPG, JPEG, PNG)...", 
        type=["jpg", "jpeg", "png"]
    )
    
    if uploaded_file is not None:
        # Отображаем загруженную картинку пользователю
        image = Image.open(uploaded_file)
        st.image(image, caption="Исходное изображение", use_container_width=True)
        
        # Конвертируем загруженный файл в байты для передачи в пайплайн
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format if image.format else "JPEG")
        image_bytes = img_byte_arr.getvalue()

with col2:
    st.header("📊 Вердикт системы")
    
    if uploaded_file is not None:
        with st.spinner("Анализ изображения каскадными моделями..."):
            # Так как Streamlit синхронный, а наш пайплайн асинхронный, запускаем его через event loop
            result = asyncio.run(pipeline.moderate_image(image_bytes))
            
        # 1. Визуализируем статус проверки с помощью цветных плашек
        status = result["status"]
        if status == "passed":
            st.success("✅ ОБЪЯВЛЕНИЕ ДОПУЩЕНО К ПУБЛИКАЦИИ")
        elif status == "warning":
            st.warning("⚠️ ВНИМАНИЕ: Требуется оптимизация контента")
        else:
            st.error("🚨 ОБЪЯВЛЕНИЕ ЗАБЛОКИРОВАНО")
            
        # Выводим текстовую причину вердикта, если она есть
        if result["verdict_reason"]:
            st.info(f"**Причина:** {result['verdict_reason']}")
            
        st.write("---")
        
        # 2. Выводим технические метрики скорости выполнения
        st.subheader("⏱️ Производительность инференса")
        st.metric(
            label="Общее время обработки (Latency)", 
            value=f"{result['metrics']['total_latency_ms']} мс"
        )
        
        # 3. Выводим детальный разбор по компонентам
        st.subheader("🔍 Результаты глубокого анализа")
        
        details = result["moderation_details"]
        
        # Показываем распознанный текст
        st.text_area(
            label="Текст, обнаруженный на картинке (EasyOCR):", 
            value=details["extracted_text"] if details["extracted_text"] else "[Текст не обнаружен]", 
            disabled=True
        )
        
        # Отображаем найденные скрытые сущности (телефоны, ссылки и т.д.)
        if details["forbidden_entities_found"]:
            st.error("❌ Обнаружены запрещенные контакты/ссылки:")
            for entity in details["forbidden_entities_found"]:
                st.write(f"• **Тип:** `{entity['type']}` — **Найдено:** `{entity['matches']}`")
        else:
            st.success("🟢 Скрытых контактов и внешних ссылок не обнаружено")
            
        # Выводим сырые вероятности моделей
        with st.expander("Посмотреть сырые выходы нейросетей"):
            st.json(result["metrics"])
            
    else:
        st.info("Загрузите изображение в левой панели, чтобы увидеть детальный лог разбора конвейера.")