# bot_crypto_simulazione.py
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Bot Crypto Trading Simulazione", layout="wide")
st.title("Bot Crypto Trading Simulazione 📈")

# -----------------------------
# PARAMETRI UTENTE
# -----------------------------
crypto = st.selectbox("Seleziona crypto", ["BTC-USD", "ETH-USD", "BNB-USD"])
periodo = st.selectbox("Periodo storico", ["1d", "5d"])
intervallo = "1m"  # intervallo al minuto

saldo_iniziale = st.number_input("Saldo iniziale (USD)", value=1000.0, step=50.0)

# -----------------------------
# SCARICO DATI
# -----------------------------
st.write(f"Scarico dati per {crypto}...")
dati = yf.download(crypto, period=periodo, interval=intervallo, auto_adjust=True)

if dati.empty:
    st.error("Errore: nessun dato scaricato.")
else:
    # Prendiamo solo la chiusura aggiustata
    if isinstance(dati.columns, pd.MultiIndex):
        df = dati['Close'].copy().to_frame()
    else:
        df = dati['Close'].to_frame()

    df.rename(columns={'Close':'Prezzo'}, inplace=True)
    df['MA5'] = df['Prezzo'].rolling(window=5).mean()

    # -----------------------------
    # GENERAZIONE SEGNALI
    # -----------------------------
    df['Segnale'] = 'HOLD'
    df.loc[df['Prezzo'] > df['MA5'], 'Segnale'] = 'BUY'
    df.loc[df['Prezzo'] < df['MA5'], 'Segnale'] = 'SELL'

    # -----------------------------
    # SIMULAZIONE PORTAFOGLIO
    # -----------------------------
    max_rischio_per_operazione = 0.2
    frazione_massima = 0.5
    frazione_minima = 0.1

    saldo_usd = saldo_iniziale
    posizione_crypto = 0.0
    portafoglio_valore = []

    for i in range(len(df)):
        prezzo = df['Prezzo'].iloc[i]
        ma5 = df['MA5'].iloc[i]
        segnale = df['Segnale'].iloc[i]

        # Forza segnale
        if pd.isna(ma5):
            forza = 0
        else:
            forza = (prezzo - ma5) / ma5

        # Frazione da investire
        if forza > 0.02:
            frazione_investimento = frazione_massima
        elif forza > 0:
            frazione_investimento = frazione_minima
        else:
            frazione_investimento = 0

        # BUY
        if segnale == 'BUY' and saldo_usd > 0:
            importo_investire = min(saldo_usd * frazione_investimento, saldo_usd * max_rischio_per_operazione)
            posizione_crypto += importo_investire / prezzo
            saldo_usd -= importo_investire

        # SELL
        elif segnale == 'SELL' and posizione_crypto > 0:
            saldo_usd += posizione_crypto * prezzo
            posizione_crypto = 0

        # Valore portafoglio totale
        portafoglio_valore.append(saldo_usd + posizione_crypto * prezzo)

    df['Portafoglio'] = portafoglio_valore
    df['Profit%'] = ((df['Portafoglio'] - saldo_iniziale) / saldo_iniziale) * 100

    # -----------------------------
    # VISUALIZZAZIONE
    # -----------------------------
    def color_segnale(val):
        if val == 'BUY':
            return 'background-color: lightgreen'
        elif val == 'SELL':
            return 'background-color: lightcoral'
        else:
            return ''

    st.subheader("Tabella dei segnali")
    st.dataframe(df[['Prezzo','MA5','Segnale','Portafoglio','Profit%']].style.applymap(color_segnale, subset=['Segnale']))

    st.subheader("Grafico Prezzo, MA5 e Portafoglio")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Prezzo'], mode='lines', name='Prezzo', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], mode='lines', name='MA5', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=df['Portafoglio'], mode='lines', name='Valore Portafoglio', line=dict(color='green')))
    fig.update_layout(xaxis_title="Data", yaxis_title="USD", height=500, margin=dict(l=20,r=20,t=40,b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Ultimo segnale")
    ultimo = df.iloc[-1]
    st.markdown(f"**Data:** {ultimo.name}")
    st.markdown(f"**Prezzo:** {ultimo['Prezzo']:.2f}")
    st.markdown(f"**Segnale:** {ultimo['Segnale']}")
    st.markdown(f"**Valore portafoglio:** {ultimo['Portafoglio']:.2f} USD")
    st.markdown(f"**Profitto:** {ultimo['Profit%']:.2f} %")
