import sqlite3

import streamlit as st
import pandas as pd
import numpy as np
import requests


def upload_ticker_info_from_db(ticker):
    conn = sqlite3.connect('data_ticker_summary.sqlite')
    data_ticker = pd.read_sql_query(f'SELECT * FROM {ticker}', conn)
    conn.close()
    return data_ticker


def upload_data_ticker_from_db(ticker):
    conn = sqlite3.connect('data_ticker_history.sqlite')
    data_ticker = pd.read_sql_query(f'SELECT * FROM {ticker}', conn)
    conn.close()

    return data_ticker


def moving_average(ticker):

    df = upload_data_ticker_from_db(ticker)

    df = df[['Date', 'Close']]
    df.set_index('Date', inplace=True)
    ma_day = [10, 20, 30]

    for ma in ma_day:
        column_name = "MA for %s days" % (str(ma))
        df[column_name] = df['Close'].rolling(window=ma, center=False).mean()

    return df[['Close', 'MA for 10 days', 'MA for 20 days', 'MA for 30 days']]


def moving_average_display(ticker):
    data = upload_data_ticker_from_db(ticker)
    interval_30_days = data[::30]
    interval_t = interval_30_days.expanding(min_periods=1, center=None, axis=0, method="single").mean()
    ticker_cma = interval_t['Close'].to_frame()
    ticker_cma['Date'] = interval_30_days.get('Date')
    ticker_cma['CMA30'] = ticker_cma['Close'].expanding().mean()

    ticker_cma.set_index('Date', inplace=True)
    ticker_cma = ticker_cma.reindex(index=ticker_cma.index[::-1])
    return ticker_cma


def rsi(ticker, periods=14):
    df = upload_data_ticker_from_db(ticker)

    close_delta = df['Close'].diff()

    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)

    ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()

    rsi = 100 - (100 / (1 + (ma_up / ma_down)))

    rsi = (pd.concat([df['Date'], rsi, pd.DataFrame([20] * 1746), pd.DataFrame([80] * 1746)], axis=1)[14:])[::-1]
    rsi.set_index('Date', inplace=True)

    rsi = rsi.set_axis(['Close', 'Уровень 20', 'Уровень 80'], axis=1, inplace=False)
    return rsi


def volume(ticker):
    df = upload_data_ticker_from_db(ticker)
    data = pd.concat([df['Date'], df['Volume']], axis=1)
    data.set_index('Date', inplace=True)

    return data


def component(ticker, index, props):
    flag = False

    with st.container():

        col1, col2, col3 = st.columns(3)
        with col1:
            st.text(index + 1)
        with col2:
            st.text(ticker)
        with col3:
            if st.button("↓", key=index): flag = True

    if flag:
        st.text("Общая информация")
        st.write(props)
        st.text("Полосы Боллинджера")
        st.line_chart(moving_average(ticker))
        st.text("Индекс относительной силы(RSI)")
        st.line_chart(rsi(ticker))
        st.text("Изменение объема торгов:")
        st.line_chart(volume(ticker))

    st.markdown(
        """
    <style>
        [data-testid="column"] {
            margin:0px auto;
        } 
        [data-testid="stHorizontalBlock"] {
            display:flex;
            justify-content: space-between;
            width:600px;
        }
         [data-testid="stHorizontalBlock"] {
            display:flex;
            justify-content: space-between;
            width:600px;
            margin-left:10%;
        }
       
        .css-1r6slb0{
            display:flex;
            justify-content: top;
            align-items:top;
            width:10px;
                 
        }
        .css-183lzff{
            margin-top:10px;
        }

        input{
           width:500px;
        }
    
        [data-testid="stButton"] {
            display:flex;
            justify-content: center;
            align-items:center;
            display:none;
        } 
    </style>
    """,
        unsafe_allow_html=True,
    )


tickers = ['AI', 'GNS', 'O', 'JNJ', 'XELA', 'VZ', 'KO', 'NIO', 'BRK.B', 'PFE', 'MPW', 'V', 'F', 'MO', 'ZIM', 'TSM',
           'BABA', 'EPD', 'CVX', 'MMM', 'UNH', 'CRM', 'ABBV', 'HD', 'T', 'SI', 'AMZN', 'TSLA', 'AAPL', 'KALA', 'MSFT',
           'HUBC', 'NVDA', 'MULN', 'GOOG', 'COST', 'TRKA', 'GOOGL', 'BFRG', 'INTC', 'AVGO', 'GNLX', 'META', 'AMD',
           'PEP', 'PYPL', 'RUM', 'AGNC', 'VERU', 'ZS']
local_tickers = ['AMZN', 'TSLA', 'AAPL', 'KALA', 'MSFT', 'HUBC', 'NVDA', 'MULN', 'GOOG', 'COST']

st.title('Анализ финансовых данных компаний')

col1, col2 = st.columns(2)
with col1:
    input_ticker = st.text_input("Найти компанию по тикеру:", "")
with col2:
    st.title("")
    if st.button("Искать"): local_tickers = [x for x in tickers if input_ticker.title().upper() in x]

if len(input_ticker) != 0:
    for x in tickers:
        print(x, input_ticker.title())
    local_tickers = [x for x in tickers if input_ticker.title().upper() in x]

for i in range(len(local_tickers)):
    component(
        local_tickers[i],
        i,
        upload_ticker_info_from_db(local_tickers[i])
    )
