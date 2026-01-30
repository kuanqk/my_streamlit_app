import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Настройка страницы
st.set_page_config(page_title="Financial Tickers", layout="wide")

# Заголовок
st.title("📈 Financial Market Dashboard")

# Функция для генерации данных (замените на реальные данные из API)
def generate_sample_data(days=7, start_price=100, volatility=0.02):
    """Генерирует примерные данные для графика"""
    dates = pd.date_range(end=datetime.now(), periods=days*24, freq='H')
    prices = [start_price]
    
    for _ in range(len(dates)-1):
        change = np.random.normal(0, volatility)
        prices.append(prices[-1] * (1 + change))
    
    # Создаем резкое падение в последний день
    last_day_idx = int(len(prices) * 0.85)
    drop_factor = 0.95  # 5% падение
    prices[last_day_idx:] = [p * drop_factor for p in prices[last_day_idx:]]
    
    return pd.DataFrame({
        'date': dates,
        'price': prices
    })

# Функция для создания графика
def create_financial_chart(df, ticker_name, current_price, change_pct, change_abs, currency="USD"):
    """Создает график в стиле финансовых тикеров"""
    
    # Определяем цвет на основе изменения
    color = '#EF5350' if change_pct < 0 else '#26A69A'
    
    fig = go.Figure()
    
    # Добавляем линию графика
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['price'],
        mode='lines',
        line=dict(color=color, width=2),
        fill='tonexty',
        fillcolor=f'rgba(239, 83, 80, 0.1)' if change_pct < 0 else 'rgba(38, 166, 154, 0.1)',
        hovertemplate='%{y:.2f}<extra></extra>'
    ))
    
    # Добавляем текст с названием тикера
    fig.add_annotation(
        text=ticker_name,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=32, color='rgba(128, 128, 128, 0.3)', family='Arial Black'),
        xanchor='center',
        yanchor='middle'
    )
    
    # Добавляем метку с текущей ценой и изменением
    fig.add_annotation(
        text=f"{currency}<br>{current_price:,.2f}<br><span style='color:{color}'>{change_pct:+.2f}%<br>{change_abs:+,.2f}</span>",
        xref="paper", yref="paper",
        x=0.95, y=0.15,
        showarrow=False,
        font=dict(size=11, color='white'),
        bgcolor=color,
        borderpad=8,
        xanchor='right',
        yanchor='bottom',
        align='right'
    )
    
    # Настройка осей и фона
    fig.update_xaxes(
        showgrid=False,
        showticklabels=True,
        tickformat='%d',
        title='',
        color='#666'
    )
    
    fig.update_yaxes(
        showgrid=False,
        showticklabels=True,
        title='',
        side='right',
        color='#666'
    )
    
    fig.update_layout(
        height=250,
        margin=dict(l=10, r=60, t=10, b=30),
        plot_bgcolor='#f5f5f5',
        paper_bgcolor='white',
        hovermode='x unified',
        showlegend=False,
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True)
    )
    
    return fig

# Создаем три колонки для графиков
col1, col2, col3 = st.columns(3)

# S&P 500
with col1:
    sp500_data = generate_sample_data(days=7, start_price=7000, volatility=0.015)
    current_sp500 = sp500_data['price'].iloc[-1]
    prev_sp500 = sp500_data['price'].iloc[-25]  # ~1 день назад
    change_sp500 = current_sp500 - prev_sp500
    change_pct_sp500 = (change_sp500 / prev_sp500) * 100
    
    fig_sp500 = create_financial_chart(
        sp500_data, 
        "SP500", 
        current_sp500, 
        change_pct_sp500, 
        change_sp500,
        "USD"
    )
    st.plotly_chart(fig_sp500, use_container_width=True, key="sp500")

# Bitcoin
with col2:
    btc_data = generate_sample_data(days=7, start_price=88000, volatility=0.025)
    current_btc = btc_data['price'].iloc[-1]
    prev_btc = btc_data['price'].iloc[-25]
    change_btc = current_btc - prev_btc
    change_pct_btc = (change_btc / prev_btc) * 100
    
    fig_btc = create_financial_chart(
        btc_data, 
        "BTC", 
        current_btc, 
        change_pct_btc, 
        change_btc,
        "USD"
    )
    st.plotly_chart(fig_btc, use_container_width=True, key="btc")

# Золото
with col3:
    gold_data = generate_sample_data(days=7, start_price=2800, volatility=0.01)
    current_gold = gold_data['price'].iloc[-1]
    prev_gold = gold_data['price'].iloc[-25]
    change_gold = current_gold - prev_gold
    change_pct_gold = (change_gold / prev_gold) * 100
    
    fig_gold = create_financial_chart(
        gold_data, 
        "ЗОЛОТО", 
        current_gold, 
        change_pct_gold, 
        change_gold,
        "USD"
    )
    st.plotly_chart(fig_gold, use_container_width=True, key="gold")

# Добавляем информацию о последнем обновлении
st.markdown("---")
st.caption(f"Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Инструкция по запуску в сайдбаре
with st.sidebar:
    st.header("📊 О приложении")
    st.markdown("""
    ### Финансовые графики
    
    Это приложение визуализирует финансовые тикеры:
    - **SP500** - индекс S&P 500
    - **BTC** - Bitcoin
    - **ЗОЛОТО** - Gold
    
    #### Для реальных данных:
    Замените функцию `generate_sample_data()` на API:
    - **yfinance** для акций и индексов
    - **ccxt** для криптовалют
    - **Alpha Vantage** для различных активов
    
    #### Установка зависимостей:
    ```bash
    pip install streamlit plotly pandas numpy
    ```
    
    #### Запуск:
    ```bash
    streamlit run finance_charts_app.py
    ```
    """)
    
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit & Plotly")
