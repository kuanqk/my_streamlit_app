import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Настройка страницы
st.set_page_config(page_title="Financial Tickers", layout="wide")

# Заголовок
st.title("📈 Financial Market Dashboard")

@st.cache_data(ttl=300)  # Кэширование на 5 минут
def get_real_data(ticker, period="7d", interval="1h"):
    """Получает реальные данные через yfinance с OHLC для свечей"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        
        if df.empty:
            return None
            
        df = df.reset_index()
        
        # Определяем имя колонки с датой
        date_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
        
        # Переименовываем колонки для единообразия
        df = df.rename(columns={
            date_col: 'date', 
            'Close': 'price',
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low'
        })
        
        # Возвращаем все OHLC данные для свечного графика
        return df[['date', 'Open', 'High', 'Low', 'price']]
    except Exception as e:
        st.error(f"Ошибка при получении данных для {ticker}: {str(e)}")
        return None

def create_financial_chart(df, ticker_name, current_price, change_pct, change_abs, currency="USD"):
    """Создает график в стиле финансовых тикеров - точная копия профессиональных терминалов"""
    
    if df is None or df.empty:
        # Создаем пустой график с сообщением об ошибке
        fig = go.Figure()
        fig.add_annotation(
            text="Данные недоступны",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color='#999')
        )
        fig.update_layout(height=250, margin=dict(l=10, r=60, t=10, b=30))
        return fig
    
    # Определяем цвет на основе изменения (как на TradingView)
    color = '#E53935' if change_pct < 0 else '#26A69A'
    
    fig = go.Figure()
    
    # Создаем свечной график (candlestick chart)
    # Для имитации свечей на основе линейных данных
    if 'Open' in df.columns and 'High' in df.columns and 'Low' in df.columns:
        # Если есть OHLC данные - используем настоящие свечи
        fig.add_trace(go.Candlestick(
            x=df['date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['price'],
            increasing_line_color='#26A69A',
            decreasing_line_color='#E53935',
            increasing_fillcolor='#26A69A',
            decreasing_fillcolor='#E53935',
            line=dict(width=1),
            name=ticker_name
        ))
    else:
        # Если только цена закрытия - рисуем линию в стиле TradingView
        colors = []
        for i in range(1, len(df)):
            if df['price'].iloc[i] >= df['price'].iloc[i-1]:
                colors.append('#26A69A')
            else:
                colors.append('#E53935')
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['price'],
            mode='lines',
            line=dict(color=color, width=1.5),
            fill='tonexty',
            fillcolor=f'rgba(229, 57, 53, 0.05)' if change_pct < 0 else 'rgba(38, 166, 154, 0.05)',
            hovertemplate='%{y:,.2f}<extra></extra>',
            name=ticker_name
        ))
    
    # Добавляем текст с названием тикера в центре (крупно и полупрозрачно)
    fig.add_annotation(
        text=ticker_name,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=48, color='rgba(100, 100, 100, 0.15)', family='Arial Black', weight='bold'),
        xanchor='center',
        yanchor='middle'
    )
    
    # Добавляем метку с ценой справа (как на скриншоте)
    price_text = f"<b>{currency}</b><br><b>{current_price:,.1f}</b><br><b>{change_pct:+.2f}%</b><br><b>{change_abs:+,.2f}</b>"
    
    fig.add_annotation(
        text=price_text,
        xref="paper", yref="paper",
        x=0.98, y=0.08,
        showarrow=False,
        font=dict(size=10, color='white', family='Arial'),
        bgcolor=color,
        borderpad=6,
        xanchor='right',
        yanchor='bottom',
        align='center'
    )
    
    # Настройка осей (минималистичный стиль как на профессиональных терминалах)
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200, 200, 200, 0.2)',
        showticklabels=True,
        tickfont=dict(size=9, color='#888'),
        tickformat='%d',
        title='',
        zeroline=False
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200, 200, 200, 0.2)',
        showticklabels=True,
        tickfont=dict(size=9, color='#888'),
        title='',
        side='right',
        tickformat=',.0f',
        zeroline=False
    )
    
    fig.update_layout(
        height=280,
        margin=dict(l=5, r=80, t=15, b=35),
        plot_bgcolor='#FAFAFA',
        paper_bgcolor='white',
        hovermode='x unified',
        showlegend=False,
        xaxis=dict(fixedrange=False),
        yaxis=dict(fixedrange=False),
        dragmode='pan'
    )
    
    return fig

# Настройки в сайдбаре
with st.sidebar:
    st.header("⚙️ Настройки")
    
    period = st.selectbox(
        "Период",
        options=["1d", "5d", "7d", "1mo", "3mo"],
        index=2,
        help="Выберите период отображения данных"
    )
    
    interval_map = {
        "1d": "5m",
        "5d": "30m",
        "7d": "1h",
        "1mo": "1d",
        "3mo": "1d"
    }
    interval = interval_map[period]
    
    auto_refresh = st.checkbox("Авто-обновление", value=False)
    if auto_refresh:
        refresh_rate = st.slider("Обновление (сек)", 30, 300, 60)
        st.empty()
    
    st.markdown("---")
    
    st.header("📊 О приложении")
    st.markdown("""
    ### Реальные финансовые данные
    
    Данные загружаются через **yfinance API**:
    - **SP500** (^GSPC) - S&P 500 Index
    - **BTC-USD** - Bitcoin to USD
    - **GC=F** - Gold Futures
    
    Обновление каждые 5 минут (кэш).
    """)

# Конфигурация тикеров
tickers_config = {
    "SP500": {"symbol": "^GSPC", "name": "SP500", "currency": "USD"},
    "BTC": {"symbol": "BTC-USD", "name": "BTC", "currency": "USD"},
    "GOLD": {"symbol": "GC=F", "name": "ЗОЛОТО", "currency": "USD"}
}

# Создаем три колонки для графиков
cols = st.columns(3)

for idx, (key, config) in enumerate(tickers_config.items()):
    with cols[idx]:
        # Получаем данные
        data = get_real_data(config["symbol"], period=period, interval=interval)
        
        if data is not None and not data.empty:
            current_price = data['price'].iloc[-1]
            prev_price = data['price'].iloc[0]
            change_abs = current_price - prev_price
            change_pct = (change_abs / prev_price) * 100
            
            fig = create_financial_chart(
                data,
                config["name"],
                current_price,
                change_pct,
                change_abs,
                config["currency"]
            )
            st.plotly_chart(fig, use_container_width=True, key=key)
        else:
            st.error(f"Не удалось загрузить данные для {config['name']}")

# Добавляем информацию о последнем обновлении
st.markdown("---")
col_left, col_right = st.columns([3, 1])

with col_left:
    st.caption(f"Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col_right:
    if st.button("🔄 Обновить данные"):
        st.cache_data.clear()
        st.rerun()

# Авто-обновление
if auto_refresh:
    import time
    time.sleep(refresh_rate)
    st.rerun()

# Дополнительная информация
with st.expander("ℹ️ Дополнительная информация"):
    st.markdown(f"""
    - **Период отображения**: {period}
    - **Интервал данных**: {interval}
    - **Источник**: Yahoo Finance API
    - **Кэширование**: 5 минут
    
    ### Как использовать:
    1. Выберите период в боковой панели
    2. Наведите на график для просмотра точных значений
    3. Используйте кнопку "Обновить данные" для принудительной загрузки
    """)
