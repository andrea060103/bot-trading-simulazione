import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------------------
# Interfaccia semplice
# ---------------------------------
st.title("Bot Trading Simulazione 📈")

simbolo = st.selectbox("Simbolo asset", ["AAPL", "TSLA", "GOOG", "BTC-USD"])
periodo = st.selectbox("Periodo storico", ["1mo", "3mo", "6mo"])
intervallo = st.selectbox("Intervallo", ["1d", "1wk"])

# ---------------------------------
# Scarico dati
# ---------------------------------
st.write(f"Scarico dati per {simbolo}...")
dati = yf.download(simbolo, period=periodo, interval=intervallo)

if dati.empty:
    st.error("Errore: nessun dato scaricato.")
else:
    df = pd.DataFrame(dati['Close'])
    df.rename(columns={'Close':'Prezzo'}, inplace=True)

    # Media mobile 5 giorni
    df['MA5'] = df['Prezzo'].rolling(window=5).mean()

    # Segnali BUY / SELL / HOLD
    df['Segnale'] = 'HOLD'
    df.loc[df['Prezzo'] > df['MA5'], 'Segnale'] = 'BUY'
    df.loc[df['Prezzo'] < df['MA5'], 'Segnale'] = 'SELL'

    # Funzione per colorare i segnali
    def color_segnale(val):
        if val == 'BUY':
            return 'background-color: lightgreen'
        elif val == 'SELL':
            return 'background-color: lightcoral'
        else:
            return ''

    # Mostra solo le colonne principali
    st.subheader("Tabella dei segnali")
    st.dataframe(df[['Prezzo','MA5','Segnale']].style.applymap(color_segnale, subset=['Segnale']))

    # ---------------------------------
    # Grafico interattivo con Plotly
    # ---------------------------------
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

    # ---------------------------------
    # Seleziona giorno per segnale specifico
    # ---------------------------------
    st.subheader("Seleziona un giorno per vedere il segnale")
    giorno_scelto = st.selectbox("Scegli la data", df.index)

    prezzo_giorno = df.loc[giorno_scelto, 'Prezzo']
    ma5_giorno = df.loc[giorno_scelto, 'MA5']
    segnale_giorno = df.loc[giorno_scelto, 'Segnale']

    st.markdown(f"**Data:** {giorno_scelto.date()}")
    st.markdown(f"**Prezzo:** {prezzo_giorno:.2f}")
    st.markdown(f"**MA5:** {ma5_giorno:.2f}" if not np.isnan(ma5_giorno) else "**MA5:** N/A")
    st.markdown(f"**Segnale:** {segnale_giorno}")
