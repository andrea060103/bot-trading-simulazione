# pip install streamlit yfinance pandas numpy

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.title("Bot Trading Simulazione 📈")

simbolo = st.text_input("Simbolo asset", "AAPL")
giorni = st.selectbox("Periodo storico", ["1mo", "3mo", "6mo"], index=1)
intervallo = st.selectbox("Intervallo", ["1d", "1h"], index=0)

if st.button("Scarica dati e genera segnali"):
    dati = yf.download(simbolo, period=giorni, interval=intervallo, auto_adjust=False)
    
    if isinstance(dati.columns, pd.MultiIndex):
        df = dati['Close'].copy()
        df.columns = ['Prezzo']
    else:
        df = dati[['Close']].copy()
        df.columns = ['Prezzo']

    df['MA5'] = df['Prezzo'].rolling(5).mean()
    
    # RSI
    delta = df['Prezzo'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    window = 14
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = df['Prezzo'].ewm(span=12, adjust=False).mean()
    ema26 = df['Prezzo'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    df['Segnale'] = 'HOLD'
    for i in range(1, len(df)):
        prezzo = df['Prezzo'].iloc[i]
        ma5 = df['MA5'].iloc[i]
        macd = df['MACD'].iloc[i]
        signal = df['Signal'].iloc[i]
        rsi = df['RSI'].iloc[i]
        if prezzo > ma5 and macd > signal and rsi < 70:
            df['Segnale'].iloc[i] = 'BUY'
        elif prezzo < ma5 or macd < signal or rsi > 70:
            df['Segnale'].iloc[i] = 'SELL'
    
    # Mostra tabella
    st.dataframe(df.style.apply(lambda x: ['background-color: lightgreen' if v=='BUY' else 'lightcoral' if v=='SELL' else '' for v in x], subset=['Segnale']))
