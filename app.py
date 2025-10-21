import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

st.title("Bot Trading Crypto Live 📈")

# Selezione crypto e intervallo
simbolo = st.selectbox("Simbolo crypto", ["BTC-USD", "ETH-USD", "BNB-USD"])
intervallo = "1m"  # 1 minuto per dati intraday

# Placeholder per aggiornamento live
placeholder = st.empty()

# Loop infinito con refresh ogni minuto
while True:
    # Scarico ultimi 60 minuti
    dati = yf.download(simbolo, period="1d", interval=intervallo, auto_adjust=True)

    if dati.empty:
        placeholder.error("Errore: nessun dato scaricato.")
    else:
        df = dati['Close'].to_frame()
        df.rename(columns={'Close':'Prezzo'}, inplace=True)

        # Media mobile 5 minuti
        df['MA5'] = df['Prezzo'].rolling(window=5).mean()

        # Generazione segnali
        df['Segnale'] = 'HOLD'
        df.loc[df['Prezzo'] > df['MA5'], 'Segnale'] = 'BUY'
        df.loc[df['Prezzo'] < df['MA5'], 'Segnale'] = 'SELL'

        # Funzione colori per Streamlit
        def color_segnale(val):
            if val == 'BUY':
                return 'background-color: lightgreen'
            elif val == 'SELL':
                return 'background-color: lightcoral'
            else:
                return ''

        with placeholder.container():
            st.subheader(f"Ultimi segnali per {simbolo}")
            st.dataframe(df[['Prezzo','MA5','Segnale']].style.applymap(color_segnale, subset=['Segnale']))

            # Grafico
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Prezzo'], mode='lines+markers', name='Prezzo', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], mode='lines', name='MA5', line=dict(color='orange')))
            fig.update_layout(
                xaxis_title="Ora",
                yaxis_title="Prezzo",
                margin=dict(l=20, r=20, t=40, b=20),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

            # Mostro ultimo segnale
            ultimo = df.iloc[-1]
            st.markdown(f"**Ultimo segnale ({ultimo.name}):** {ultimo['Segnale']}  |  Prezzo: {ultimo['Prezzo']:.2f}  |  MA5: {ultimo['MA5']:.2f}" if not np.isnan(ultimo['MA5']) else f"**Ultimo segnale ({ultimo.name}):** {ultimo['Segnale']}  |  Prezzo: {ultimo['Prezzo']:.2f}  |  MA5: N/A")

    # Aggiorna ogni minuto
    time.sleep(60)
