import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title("Bot Trading Simulazione 📈")

# -----------------------------
# SELEZIONE ASSET E INTERVALLO
# -----------------------------
simbolo = st.selectbox("Simbolo asset", ["BTC-USD", "ETH-USD", "AAPL", "TSLA"])
periodo = st.selectbox("Periodo storico", ["1d", "5d"])  # dati recenti
intervallo = st.selectbox("Intervallo", ["1m", "5m"])    # al minuto

st.write(f"Scarico dati per {simbolo}...")
dati = yf.download(simbolo, period=periodo, interval=intervallo, auto_adjust=True)

if dati.empty:
    st.error("Errore: nessun dato scaricato.")
else:
    # -----------------------------
    # SISTEMA COLONNA 'Prezzo' SICURO
    # -----------------------------
    if isinstance(dati.columns, pd.MultiIndex):
        if 'Close' in dati.columns.get_level_values(0):
            df = dati['Close'].copy()
        else:
            df = dati.iloc[:, [0]].copy()
    else:
        if 'Close' in dati.columns:
            df = dati['Close'].to_frame()
        else:
            df = dati.iloc[:, [0]].copy()
    
    df.columns = ['Prezzo']

    # -----------------------------
    # MEDIA MOBILE 5 PERIODI
    # -----------------------------
    df['MA5'] = df['Prezzo'].rolling(window=5).mean()

    # -----------------------------
    # GENERAZIONE SEGNALI
    # -----------------------------
    df['Segnale'] = 'HOLD'
    df.loc[df['Prezzo'] > df['MA5'], 'Segnale'] = 'BUY'
    df.loc[df['Prezzo'] < df['MA5'], 'Segnale'] = 'SELL'

    # -----------------------------
    # PERCENTUALE IPOTETICA DI OPERAZIONE
    # -----------------------------
    df['Percentuale'] = np.where(df['Segnale']=='HOLD', 0, np.random.randint(10, 51))

    # -----------------------------
    # SIMULAZIONE SALDO
    # -----------------------------
    saldo_iniziale = 1000  # saldo iniziale in USD
    saldo = saldo_iniziale
    df['Saldo'] = saldo  # colonna saldo

    for i in range(1, len(df)):
        segnale = df['Segnale'].iloc[i]
        pct = df['Percentuale'].iloc[i] / 100
        prezzo_corrente = df['Prezzo'].iloc[i]
        prezzo_precedente = df['Prezzo'].iloc[i-1]

        if segnale == 'BUY':
            # guadagno ipotetico: se prezzo sale dopo il segnale
            delta = (prezzo_corrente - prezzo_precedente) * pct
            saldo += delta
        elif segnale == 'SELL':
            # guadagno ipotetico: se prezzo scende dopo il segnale
            delta = (prezzo_precedente - prezzo_corrente) * pct
            saldo += delta
        # HOLD non cambia saldo
        df['Saldo'].iloc[i] = saldo

    # -----------------------------
    # FUNZIONE COLORAZIONE
    # -----------------------------
    def color_segnale(val):
        if val == 'BUY':
            return 'background-color: lightgreen'
        elif val == 'SELL':
            return 'background-color: lightcoral'
        else:
            return ''

    # -----------------------------
    # MOSTRA DATI
    # -----------------------------
    st.subheader("Tabella dei segnali")
    st.dataframe(df[['Prezzo','MA5','Segnale','Percentuale','Saldo']].style.applymap(color_segnale, subset=['Segnale']))

    st.subheader("Grafico Prezzo vs MA5")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Prezzo'], mode='lines+markers', name='Prezzo', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], mode='lines', name='MA5', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=df['Saldo'], mode='lines', name='Saldo', line=dict(color='purple')))
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Prezzo / Saldo",
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Ultimo segnale disponibile")
    ultimo = df.iloc[-1]
    st.markdown(f"**Data:** {ultimo.name}")
    st.markdown(f"**Prezzo:** {ultimo['Prezzo']:.2f}")
    st.markdown(f"**MA5:** {ultimo['MA5']:.2f}" if not np.isnan(ultimo['MA5']) else "**MA5:** N/A")
    st.markdown(f"**Segnale:** {ultimo['Segnale']}")
    st.markdown(f"**Percentuale operazione:** {ultimo['Percentuale']}%")
    st.markdown(f"**Saldo simulato:** {ultimo['Saldo']:.2f} USD")
