import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Настройка страницы
st.set_page_config(page_title="Trading Terminal", layout="wide", page_icon="📊")

# Заголовок в профессиональном стиле
st.markdown("# 📊 Professional Trading Terminal")
st.markdown("---")

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
            'Low': 'Low',
            'Volume': 'Volume'
        })
        
        # Возвращаем все OHLC данные для свечного графика
        return df[['date', 'Open', 'High', 'Low', 'price', 'Volume']]
    except Exception as e:
        st.error(f"Ошибка при получении данных для {ticker}: {str(e)}")
        return None

def create_professional_chart(df, ticker_name, current_price, change_pct, change_abs, currency="USD", 
                              chart_type="Candlestick (Японские свечи)", show_volume=True, show_ma=False, 
                              ma_period_1=20, ma_period_2=50):
    """Создает профессиональный график как в TradingView с правильными свечами"""
    
    if df is None or df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Данные недоступны",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color='#999')
        )
        fig.update_layout(height=350, margin=dict(l=10, r=80, t=10, b=30))
        return fig
    
    # Определяем цвет (профессиональная палитра TradingView)
    color = '#E53935' if change_pct < 0 else '#26A69A'
    
    # Создаем subplot для графика и объема
    if show_volume and 'Volume' in df.columns:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=('', '')
        )
        volume_row = 2
        price_row = 1
    else:
        fig = go.Figure()
        volume_row = None
        price_row = None
    
    # Проверяем наличие OHLC данных
    has_ohlc = all(col in df.columns for col in ['Open', 'High', 'Low', 'price'])
    
    # Выбираем тип графика
    if chart_type == "Candlestick (Японские свечи)" and has_ohlc:
        # Свечной график
        trace = go.Candlestick(
            x=df['date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['price'],
            increasing_line_color='#26A69A',
            increasing_fillcolor='#26A69A',
            decreasing_line_color='#E53935',
            decreasing_fillcolor='#E53935',
            line=dict(width=1),
            whiskerwidth=0.8,
            name=ticker_name,
            showlegend=False,
            hoverinfo='x+y'
        )
    elif chart_type == "Bar Chart (Столбцовый)" and has_ohlc:
        # OHLC Bar Chart
        trace = go.Ohlc(
            x=df['date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['price'],
            increasing_line_color='#26A69A',
            decreasing_line_color='#E53935',
            line=dict(width=1),
            name=ticker_name,
            showlegend=False
        )
    else:
        # Линейный график (по умолчанию или если нет OHLC)
        trace = go.Scatter(
            x=df['date'],
            y=df['price'],
            mode='lines',
            line=dict(color=color, width=2),
            fill='tonexty',
            fillcolor=f'rgba(229, 57, 53, 0.05)' if change_pct < 0 else 'rgba(38, 166, 154, 0.05)',
            hovertemplate='%{y:,.2f}<extra></extra>',
            name=ticker_name,
            showlegend=False
        )
    
    # Добавляем основной график
    if volume_row:
        fig.add_trace(trace, row=price_row, col=1)
    else:
        fig.add_trace(trace)
    
    # Добавляем скользящие средние (Moving Averages)
    if show_ma and len(df) > max(ma_period_1, ma_period_2):
        # MA 1
        df[f'MA{ma_period_1}'] = df['price'].rolling(window=ma_period_1).mean()
        ma1_trace = go.Scatter(
            x=df['date'],
            y=df[f'MA{ma_period_1}'],
            mode='lines',
            line=dict(color='#2196F3', width=1.5),
            name=f'MA{ma_period_1}',
            showlegend=True,
            hovertemplate=f'MA{ma_period_1}: %{{y:,.2f}}<extra></extra>'
        )
        
        # MA 2
        df[f'MA{ma_period_2}'] = df['price'].rolling(window=ma_period_2).mean()
        ma2_trace = go.Scatter(
            x=df['date'],
            y=df[f'MA{ma_period_2}'],
            mode='lines',
            line=dict(color='#FF9800', width=1.5),
            name=f'MA{ma_period_2}',
            showlegend=True,
            hovertemplate=f'MA{ma_period_2}: %{{y:,.2f}}<extra></extra>'
        )
        
        if volume_row:
            fig.add_trace(ma1_trace, row=price_row, col=1)
            fig.add_trace(ma2_trace, row=price_row, col=1)
        else:
            fig.add_trace(ma1_trace)
            fig.add_trace(ma2_trace)
    
    # Добавляем объем торгов (если включен)
    if show_volume and 'Volume' in df.columns and has_ohlc and volume_row:
        # Определяем цвета для объёма на основе направления свечи
        colors_volume = []
        for i in range(len(df)):
            if pd.notna(df['Open'].iloc[i]) and pd.notna(df['price'].iloc[i]):
                if df['price'].iloc[i] >= df['Open'].iloc[i]:
                    colors_volume.append('#26A69A')
                else:
                    colors_volume.append('#E53935')
            else:
                colors_volume.append('#888888')
        
        fig.add_trace(
            go.Bar(
                x=df['date'],
                y=df['Volume'],
                marker_color=colors_volume,
                name='Volume',
                showlegend=False,
                opacity=0.5,
                hovertemplate='Volume: %{y:,.0f}<extra></extra>'
            ),
            row=volume_row, col=1
        )
    
    # Добавляем название тикера крупным водяным знаком
    fig.add_annotation(
        text=ticker_name,
        xref="paper", yref="paper",
        x=0.5, y=0.4,
        showarrow=False,
        font=dict(size=60, color='rgba(100, 100, 100, 0.08)', family='Arial Black', weight='bold'),
        xanchor='center',
        yanchor='middle'
    )
    
    # Добавляем метку с ценой (профессиональный стиль)
    price_text = f"<b>{currency}</b><br><b style='font-size:12px'>{current_price:,.1f}</b><br><b>{change_pct:+.2f}%</b><br><b>{change_abs:+,.1f}</b>"
    
    fig.add_annotation(
        text=price_text,
        xref="paper", yref="paper",
        x=0.98, y=0.92,
        showarrow=False,
        font=dict(size=10, color='white', family='Arial'),
        bgcolor=color,
        borderpad=8,
        xanchor='right',
        yanchor='top',
        align='center'
    )
    
    # Настройка осей (минималистичный профессиональный стиль)
    if volume_row:
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200, 200, 200, 0.15)',
            showticklabels=True,
            tickfont=dict(size=9, color='#888'),
            tickformat='%d %b',
            zeroline=False,
            row=volume_row, col=1
        )
        
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200, 200, 200, 0.15)',
            showticklabels=False,
            zeroline=False,
            row=price_row, col=1
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200, 200, 200, 0.15)',
            showticklabels=True,
            tickfont=dict(size=9, color='#888'),
            side='right',
            tickformat=',.0f',
            zeroline=False,
            row=price_row, col=1
        )
        
        fig.update_yaxes(
            showgrid=False,
            showticklabels=True,
            tickfont=dict(size=8, color='#888'),
            side='right',
            zeroline=False,
            row=volume_row, col=1
        )
    else:
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200, 200, 200, 0.15)',
            showticklabels=True,
            tickfont=dict(size=9, color='#888'),
            tickformat='%d %b',
            zeroline=False
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200, 200, 200, 0.15)',
            showticklabels=True,
            tickfont=dict(size=9, color='#888'),
            side='right',
            tickformat=',.0f',
            zeroline=False
        )
    
    fig.update_layout(
        height=400,
        margin=dict(l=5, r=80, t=10, b=35),
        plot_bgcolor='#FAFAFA',
        paper_bgcolor='white',
        hovermode='x unified',
        xaxis_rangeslider_visible=False,
        dragmode='pan',
        showlegend=show_ma,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ) if show_ma else None
    )
    
    return fig

# Настройки в сайдбаре
with st.sidebar:
    st.header("⚙️ Настройки терминала")
    
    # Режим отображения
    view_mode = st.radio(
        "📺 Режим отображения",
        options=["Множественный вид", "Одиночный график"],
        index=0,
        help="Выберите как отображать графики"
    )
    
    st.markdown("---")
    
    # Тип графика
    st.subheader("📊 Тип графика")
    chart_type = st.selectbox(
        "Выберите тип",
        options=["Candlestick (Японские свечи)", "Line Chart (Линейный)", "Bar Chart (Столбцовый)"],
        index=0,
        help="Тип отображения ценового графика"
    )
    
    # Дополнительные индикаторы
    show_volume = st.checkbox("📦 Volume (Объём торгов)", value=True)
    show_ma = st.checkbox("〰️ Moving Averages (Скользящие средние)", value=False)
    
    if show_ma:
        col_ma1, col_ma2 = st.columns(2)
        with col_ma1:
            ma_period_1 = st.number_input("MA 1", min_value=5, max_value=200, value=20, step=5)
        with col_ma2:
            ma_period_2 = st.number_input("MA 2", min_value=5, max_value=200, value=50, step=5)
    
    st.markdown("---")
    
    # Выбор периода
    period = st.selectbox(
        "📅 Период",
        options=["1d", "5d", "1mo", "3mo", "6mo", "1y"],
        index=2,
        help="Выберите временной период"
    )
    
    interval_map = {
        "1d": "5m",
        "5d": "15m",
        "1mo": "1h",
        "3mo": "1d",
        "6mo": "1d",
        "1y": "1wk"
    }
    interval = interval_map[period]
    
    st.markdown("---")
    
    # Предустановленные тикеры
    st.subheader("📈 Популярные тикеры")
    
    preset_tickers = {
        "^GSPC": {"name": "S&P 500", "currency": "USD", "default": True},
        "BTC-USD": {"name": "Bitcoin", "currency": "USD", "default": True},
        "GC=F": {"name": "Gold", "currency": "USD", "default": True},
        "^DJI": {"name": "Dow Jones", "currency": "USD", "default": False},
        "^IXIC": {"name": "NASDAQ", "currency": "USD", "default": False},
        "ETH-USD": {"name": "Ethereum", "currency": "USD", "default": False},
        "CL=F": {"name": "Crude Oil", "currency": "USD", "default": False},
        "AAPL": {"name": "Apple", "currency": "USD", "default": False},
        "TSLA": {"name": "Tesla", "currency": "USD", "default": False},
        "EURUSD=X": {"name": "EUR/USD", "currency": "", "default": False},
    }
    
    selected_presets = []
    for symbol, info in preset_tickers.items():
        if st.checkbox(info["name"], value=info["default"], key=f"preset_{symbol}"):
            selected_presets.append({
                "symbol": symbol,
                "name": info["name"],
                "currency": info["currency"]
            })
    
    st.markdown("---")
    
    # Кастомные тикеры
    st.subheader("➕ Добавить свой тикер")
    
    custom_ticker = st.text_input(
        "Символ тикера",
        placeholder="Например: MSFT, GOOGL, ^RUT",
        help="Введите символ тикера из Yahoo Finance"
    )
    
    custom_name = st.text_input(
        "Название (опционально)",
        placeholder="Microsoft",
        help="Краткое название для отображения"
    )
    
    custom_currency = st.text_input(
        "Валюта",
        value="USD",
        help="Валюта тикера"
    )
    
    if st.button("Добавить тикер", use_container_width=True):
        if custom_ticker:
            # Проверяем, существует ли тикер
            test_data = get_real_data(custom_ticker, period="1d", interval="5m")
            if test_data is not None and not test_data.empty:
                selected_presets.append({
                    "symbol": custom_ticker.upper(),
                    "name": custom_name if custom_name else custom_ticker.upper(),
                    "currency": custom_currency
                })
                st.success(f"✅ Тикер {custom_ticker.upper()} добавлен!")
            else:
                st.error(f"❌ Тикер {custom_ticker} не найден в Yahoo Finance")
        else:
            st.warning("⚠️ Введите символ тикера")
    
    st.markdown("---")
    
    # Одиночный режим - выбор конкретного тикера
    if view_mode == "Одиночный график" and selected_presets:
        selected_single = st.selectbox(
            "Выберите тикер",
            options=range(len(selected_presets)),
            format_func=lambda x: f"{selected_presets[x]['name']} ({selected_presets[x]['symbol']})"
        )
    
    st.markdown("---")
    
    # Авто-обновление
    auto_refresh = st.checkbox("🔄 Авто-обновление", value=False)
    if auto_refresh:
        refresh_rate = st.slider("Интервал (сек)", 30, 300, 60)
    
    st.markdown("---")
    st.caption("**Professional Trading Terminal**")
    st.caption(f"Data: Yahoo Finance")
    st.caption(f"Update: Every 5 min")

# Отображение графиков
if not selected_presets:
    st.warning("⚠️ Выберите хотя бы один тикер из списка или добавьте свой")
else:
    # Режим одиночного графика
    if view_mode == "Одиночный график":
        config = selected_presets[selected_single]
        
        st.subheader(f"📊 {config['name']} ({config['symbol']})")
        
        # Получаем данные
        with st.spinner(f"Загрузка данных {config['name']}..."):
            data = get_real_data(config["symbol"], period=period, interval=interval)
        
        if data is not None and not data.empty:
            current_price = data['price'].iloc[-1]
            prev_price = data['price'].iloc[0]
            change_abs = current_price - prev_price
            change_pct = (change_abs / prev_price) * 100
            
            # Создаем и показываем график
            fig = create_professional_chart(
                data,
                config["name"],
                current_price,
                change_pct,
                change_abs,
                config["currency"],
                chart_type=chart_type,
                show_volume=show_volume,
                show_ma=show_ma,
                ma_period_1=ma_period_1 if show_ma else 20,
                ma_period_2=ma_period_2 if show_ma else 50
            )
            st.plotly_chart(fig, use_container_width=True, key=f"single_{config['symbol']}")
            
            # Расширенная статистика для одиночного режима
            st.markdown("### 📊 Статистика")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("💰 Текущая цена", f"{current_price:,.2f}")
            with col2:
                st.metric("📈 High", f"{data['High'].max():,.2f}")
            with col3:
                st.metric("📉 Low", f"{data['Low'].min():,.2f}")
            with col4:
                st.metric("📊 Среднее", f"{data['price'].mean():,.2f}")
            with col5:
                if 'Volume' in data.columns:
                    st.metric("📦 Объём", f"{data['Volume'].sum()/1e9:.2f}B")
                else:
                    st.metric("📦 Объём", "N/A")
        else:
            st.error(f"❌ Не удалось загрузить данные для {config['name']}")
    
    # Режим множественного отображения
    else:
        cols = st.columns(min(len(selected_presets), 3))
        
        for idx, config in enumerate(selected_presets):
            col_idx = idx % 3
            
            with cols[col_idx]:
                # Получаем данные
                with st.spinner(f"Загрузка {config['name']}..."):
                    data = get_real_data(config["symbol"], period=period, interval=interval)
                
                if data is not None and not data.empty:
                    current_price = data['price'].iloc[-1]
                    prev_price = data['price'].iloc[0]
                    change_abs = current_price - prev_price
                    change_pct = (change_abs / prev_price) * 100
                    
                    # Создаем и показываем график
                    fig = create_professional_chart(
                        data,
                        config["name"],
                        current_price,
                        change_pct,
                        change_abs,
                        config["currency"],
                        chart_type=chart_type,
                        show_volume=show_volume,
                        show_ma=show_ma,
                        ma_period_1=ma_period_1 if show_ma else 20,
                        ma_period_2=ma_period_2 if show_ma else 50
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"multi_{config['symbol']}")
                    
                    # Компактная статистика
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("High", f"{data['High'].max():,.1f}")
                    with col_b:
                        st.metric("Low", f"{data['Low'].min():,.1f}")
                    with col_c:
                        st.metric("Avg", f"{data['price'].mean():,.1f}")
                else:
                    st.error(f"❌ {config['name']}")

# Футер
st.markdown("---")
col_left, col_right = st.columns([3, 1])

with col_left:
    st.caption(f"⏰ Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col_right:
    if st.button("🔄 Обновить", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Авто-обновление
if auto_refresh:
    import time
    time.sleep(refresh_rate)
    st.rerun()

# Информация о рынке
with st.expander("ℹ️ Информация о рынке"):
    st.markdown(f"""
    ### Параметры отображения
    - **Период**: {period}
    - **Интервал**: {interval}
    - **Источник данных**: Yahoo Finance API
    - **Кэширование**: 5 минут
    
    ### Легенда графиков
    - 🟢 **Зелёный** - рост цены
    - 🔴 **Красный** - падение цены
    - **Свечи** - OHLC данные (Open, High, Low, Close)
    - **Столбцы внизу** - объём торгов
    
    ### Управление
    - Наведите курсор для просмотра точных значений
    - Используйте колёсико мыши для масштабирования
    - Перетаскивайте график для навигации
    """)
