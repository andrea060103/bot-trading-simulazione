import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

st.title("Bot Trading Simulazione in tempo reale ⏱️")

# -----------------------------
# SELEZIONE ASSET
# -----------------------------
simbolo = st.selectbox("Simbolo crypto", ["BTC-USD", "ETH-USD"])
saldo_iniziale = st.number_input("Saldo iniziale (USD)", value=1000.0, step=100.0)

# Contenitore Streamlit per aggiornamento dinamico
placeholder_tabella = st.empty()
placeholder_grafico = st.empty()
placeholder_ultimo = st.empty()

saldo = saldo_iniziale

# Loop infinito (fino a chiusura app)
while True:
    dati = yf.download(simbolo, period="1d", interval="1m", auto_adjust=True)
    if dati.empty:
        st.warning("Nessun dato disponibile al momento...")
        time.sleep(60)
        continue

    df = dati['Close'].to_frame()
    df.columns = ['Prezzo']
    df['MA5'] = df['Prezzo'].rolling(window=5).mean()
    df['Segnale'] = 'HOLD'
    df.loc[df['Prezzo'] > df['MA5'], 'Segnale'] = 'BUY'
    df.loc[df['Prezzo'] < df['MA5'], 'Segnale'] = 'SELL'
    df['Percentuale'] = np.where(df['Segnale']=='HOLD', 0, np.random.randint(10,51))
    df['Saldo'] = saldo

    # Calcolo saldo aggiornato
    for i in range(1, len(df)):
        segnale = df['Segnale'].iloc[i]
        pct = df['Percentuale'].iloc[i] / 100
        prezzo_corrente = df['Prezzo'].iloc[i]
        prezzo_precedente = df['Prezzo'].iloc[i-1]

        if segnale == 'BUY':
            delta = (prezzo_corrente - prezzo_precedente) * pct
            saldo += delta
        elif segnale == 'SELL':
            delta = (prezzo_precedente - prezzo_corrente) * pct
            saldo += delta
        df['Saldo'].iloc[i] = saldo

    # Colorazione segnali
    def color_segnale(val):
        if val == 'BUY':
            return 'background-color: lightgreen'
        elif val == 'SELL':
            return 'background-color: lightcoral'
        else:
            return ''

    # Aggiorna tabella
    placeholder_tabella.dataframe(df[['Prezzo','MA5','Segnale','Percentuale','Saldo']].style.applymap(color_segnale, subset=['Segnale']))

    # Aggiorna grafico
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Prezzo'], mode='lines+markers', name='Prezzo', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], mode='lines', name='MA5', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=df['Saldo'], mode='lines', name='Saldo', line=dict(color='purple')))
    fig.update_layout(xaxis_title="Data", yaxis_title="Prezzo / Saldo", height=400)
    placeholder_grafico.plotly_chart(fig, use_container_width=True)

    # Mostra ultimo segnale
    ultimo = df.iloc[-1]
    placeholder_ultimo.markdown(f"**Ultimo segnale** - Data: {ultimo.name}")
    placeholder_ultimo.markdown(f"Prezzo: {ultimo['Prezzo']:.2f} USD | MA5: {ultimo['MA5']:.2f} | Segnale: {ultimo['Segnale']} | Percentuale: {ultimo['Percentuale']}% | Saldo: {ultimo['Saldo']:.2f} USD")

    # Aspetta 60 secondi prima di aggiornare
    time.sleep(60)
