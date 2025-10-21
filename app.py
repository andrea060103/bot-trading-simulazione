import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title("Bot Trading Crypto 📈")

# -----------------------------
# SELEZIONE CRYPTO E INTERVALLO
# -----------------------------
crypto = st.selectbox("Seleziona crypto", ["BTC-USD", "ETH-USD", "BNB-USD"])
intervallo = "1m"  # intervallo a 1 minuto
periodo = "1d"     # ultimi 1 giorno

st.write(f"Scarico dati per {crypto}...")
dati = yf.download(crypto, period=periodo, interval=intervallo, auto_adjust=True)

if dati.empty:
    st.error("Errore: nessun dato scaricato.")
else:
    # Gestione MultiIndex (tipica per yfinance con crypto e intervalli brevi)
    if isinstance(dati.columns, pd.MultiIndex):
        df = dati['Close'][crypto].to_frame()
    else:
        df = dati['Close'].to_frame()
    df.rename(columns={'Close':'Prezzo'}, inplace=True)

    # -----------------------------
    # CALCOLO MEDIA MOBILE
    # -----------------------------
    df['MA5'] = df['Prezzo'].rolling(window=5).mean()

    # -----------------------------
    # GENERAZIONE SEGNALI
    # -----------------------------
    df['Segnale'] = 'HOLD'
    df.loc[df['Prezzo'] > df['MA5'], 'Segnale'] = 'BUY'
    df.loc[df['Prezzo'] < df['MA5'], 'Segnale'] = 'SELL'

    def color_segnale(val):
        if val == 'BUY':
            return 'background-color: lightgreen'
        elif val == 'SELL':
            return 'background-color: lightcoral'
        else:
            return ''

    # -----------------------------
    # TABELLA SEGNALI
    # -----------------------------
    st.subheader("Tabella dei segnali")
    st.dataframe(df[['Prezzo','MA5','Segnale']].style.applymap(color_segnale, subset=['Segnale']))

    # -----------------------------
    # GRAFICO Prezzo vs MA5
    # -----------------------------
    st.subheader("Grafico Prezzo vs MA5")
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

    # -----------------------------
    # SEGNALI ULTIMO MINUTO
    # -----------------------------
    st.subheader("Ultimo segnale")
    ultimo = df.iloc[-1]
    st.markdown(f"**Data:** {ultimo.name}")
    st.markdown(f"**Prezzo:** {ultimo['Prezzo']:.2f}")
    st.markdown(f"**MA5:** {ultimo['MA5']:.2f}" if not np.isnan(ultimo['MA5']) else "**MA5:** N/A")
    st.markdown(f"**Segnale:** {ultimo['Segnale']}")
