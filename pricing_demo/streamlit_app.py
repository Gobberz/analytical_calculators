# streamlit_app.py
import sys
import os
from pathlib import Path
import streamlit as st

# Добавляем корневую директорию проекта в sys.path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Настройка страницы
st.set_page_config(
    page_title="Система расчета цен конкурентов",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Проверяем наличие основных модулей
try:
    from src.streamlit_app.main import main
    
    # Запускаем основное приложение
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    st.error(f"Ошибка импорта модулей: {e}")
    st.info("Убедитесь, что все файлы проекта загружены в репозиторий")
    
    # Показываем демо-версию
    st.title("🏗️ Система расчета цен конкурентов")
    st.subheader("Демо-версия")
    
    st.markdown("""
    ### 📊 Основные возможности:
    - **Анализ конкурентных цен** - мониторинг цен по товарам и ритейлерам
    - **Автоматический расчет цен** - применение правил ценообразования
    - **Интерактивные дашборды** - визуализация данных и метрик
    - **Экспорт данных** - выгрузка в различных форматах
    - **Двухуровневый доступ** - интерфейсы для пользователей и аналитиков
    
    ### 🚀 Статус развертывания:
    Приложение находится в процессе настройки. Полная версия будет доступна после загрузки всех компонентов.
    """)
    
    # Показываем структуру проекта
    with st.expander("📁 Структура проекта"):
        st.code("""
        competitor_pricing_app_v2/
        ├── src/
        │   ├── data_processing/
        │   │   ├── data_loader.py
        │   │   ├── pricing_engine.py
        │   │   └── pipeline.py
        │   └── streamlit_app/
        │       ├── main.py
        │       ├── auth.py
        │       ├── visualizations.py
        │       └── analytics.py
        ├── data/
        │   ├── raw/
        │   ├── processed/
        │   └── archive/
        ├── config/
        ├── docs/
        └── requirements.txt
        """)
    
    # Демо-данные
    import pandas as pd
    import numpy as np
    import plotly.express as px
    
    st.subheader("📈 Демо-визуализация")
    
    # Генерируем демо-данные
    np.random.seed(42)
    demo_data = pd.DataFrame({
        'Товар': [f'SKU_{i:03d}' for i in range(1, 21)],
        'Наша_цена': np.random.uniform(50, 200, 20),
        'Конкурент_1': np.random.uniform(45, 210, 20),
        'Конкурент_2': np.random.uniform(40, 220, 20),
        'Рекомендуемая_цена': np.random.uniform(48, 205, 20),
        'Категория': np.random.choice(['Молочные', 'Хлеб', 'Мясо', 'Овощи'], 20)
    })
    
    # График сравнения цен
    fig = px.scatter(
        demo_data, 
        x='Наша_цена', 
        y='Рекомендуемая_цена',
        color='Категория',
        title='Сравнение текущих и рекомендуемых цен',
        labels={'Наша_цена': 'Текущая цена', 'Рекомендуемая_цена': 'Рекомендуемая цена'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Таблица данных
    st.subheader("📋 Демо-данные")
    st.dataframe(demo_data, use_container_width=True)
    
    st.info("💡 Это демо-версия. Полная функциональность будет доступна после настройки всех компонентов.")
