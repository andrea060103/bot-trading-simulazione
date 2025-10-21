import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title("Bot Trading Simulazione 📈 - Versione Leggera")

# -----------------------------
# Selezione asset e periodo
# -----------------------------
simbolo = st.selectbox("Simbolo asset", ["AAPL", "TSLA", "GOOG", "BTC-USD"])
periodo = st.selectbox("Periodo storico", ["1d", "5d", "1mo"])  # per 1min, max è 7d
intervallo = st.selectbox("Intervallo", ["1m", "5m", "15m", "1h", "1d"])

st.write(f"Scarico dati per {simbolo}...")

# -----------------------------
# Scarico dati da yfinance
# -----------------------------
dati = yf.download(simbolo, period=periodo, interval=intervallo, auto_adjust=True)

if dati.empty:
    st.error("Errore: nessun dato scaricato.")
else:
    # Prendiamo sempre la colonna 'Close'
    if isinstance(dati.columns, pd.MultiIndex):
        col_close = [col for col in dati.columns if col[0]=='Close'][0]
        df = dati[[col_close]].copy()
        df.columns = ['Prezzo']
    else:
        df = dati[['Close']].copy()
        df.rename(columns={'Close':'Prezzo'}, inplace=True)

    # Calcolo MA5
    df['MA5'] = df['Prezzo'].rolling(window=5).mean()

    # Generazione segnale semplice
    df['Segnale'] = 'HOLD'
    df.loc[df['Prezzo'] > df['MA5'], 'Segnale'] = 'BUY'
    df.loc[df['Prezzo'] < df['MA5'], 'Segnale'] = 'SELL'

    # Grafico semplice
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Prezzo'], mode='lines+markers', name='Prezzo', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], mode='lines', name='MA5', line=dict(color='orange')))
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Prezzo",
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Segnale ultimo intervallo disponibile
    ultimo = df.iloc[-1]
    st.subheader("Segnale ultimo intervallo")
    st.markdown(f"**Data/Ora:** {ultimo.name}")
    st.markdown(f"**Prezzo:** {ultimo['Prezzo']:.2f}")
    st.markdown(f"**MA5:** {ultimo['MA5']:.2f}" if not np.isnan(ultimo['MA5']) else "**MA5:** N/A")
    st.markdown(f"**Segnale:** {ultimo['Segnale']}")
