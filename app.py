import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title("Bot Trading Simulazione 📈")

simbolo = st.selectbox("Simbolo asset", ["AAPL", "TSLA", "GOOG", "BTC-USD"])
periodo = st.selectbox("Periodo storico", ["1mo", "3mo", "6mo"])
intervallo = st.selectbox("Intervallo", ["1d", "1wk"])

st.write(f"Scarico dati per {simbolo}...")
dati = yf.download(simbolo, period=periodo, interval=intervallo, auto_adjust=True)

if dati.empty:
    st.error("Errore: nessun dato scaricato.")
else:
    # Se MultiIndex, prendiamo la colonna 'Close' giusta
    if isinstance(dati.columns, pd.MultiIndex):
        # Prendiamo sempre la colonna Close
        col_close = [col for col in dati.columns if col[0]=='Close'][0]
        df = dati[[col_close]].copy()
        df.columns = ['Prezzo']
    else:
        # Se colonna semplice
        df = dati[['Close']].copy()
        df.rename(columns={'Close':'Prezzo'}, inplace=True)

    df['MA5'] = df['Prezzo'].rolling(window=5).mean()

    df['Segnale'] = 'HOLD'
    df.loc[df['Prezzo'] > df['MA5'], 'Segnale'] = 'BUY'
    df.loc[df['Prezzo'] < df['MA5'], 'Segnale'] = 'SELL'

    # Reset index per Streamlit selectbox
    df_reset = df.reset_index()
    df_reset['Data_str'] = df_reset['Date'].dt.strftime('%Y-%m-%d')

    st.subheader("Tabella dei segnali")
    def color_segnale(val):
        if val == 'BUY':
            return 'background-color: lightgreen'
        elif val == 'SELL':
            return 'background-color: lightcoral'
        else:
            return ''
    st.dataframe(df_reset[['Data_str','Prezzo','MA5','Segnale']].style.applymap(color_segnale, subset=['Segnale']))

    st.subheader("Grafico Prezzo vs MA5")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_reset['Date'], y=df_reset['Prezzo'], mode='lines+markers', name='Prezzo', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df_reset['Date'], y=df_reset['MA5'], mode='lines', name='MA5', line=dict(color='orange')))
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Prezzo",
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Seleziona un giorno per vedere il segnale")
    giorno_scelto = st.selectbox("Scegli la data", df_reset['Data_str'])

    riga = df_reset[df_reset['Data_str'] == giorno_scelto].iloc[0]
    st.markdown(f"**Data:** {riga['Data_str']}")
    st.markdown(f"**Prezzo:** {riga['Prezzo']:.2f}")
    st.markdown(f"**MA5:** {riga['MA5']:.2f}" if not np.isnan(riga['MA5']) else "**MA5:** N/A")
    st.markdown(f"**Segnale:** {riga['Segnale']}")
