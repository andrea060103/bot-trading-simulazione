import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.title("Bot Trading Crypto Simulazione 🪙 (Aggiornamento al secondo)")

# Aggiornamento automatico ogni 1 secondo
st_autorefresh(interval=1000, key="bot_refresh")

# -----------------------------
# CONFIGURAZIONE BOT
# -----------------------------
simbolo = st.selectbox("Simbolo crypto", ["BTC-USD", "ETH-USD", "BNB-USD"])
saldo_iniziale = st.number_input("Saldo iniziale ($)", value=1000.0)
st.write(f"Saldo di partenza: ${saldo_iniziale:.2f}")

# Percentuale da investire per ogni operazione
percentuale_base = 0.05  # 5% del saldo
percentuale_massima = 0.2 # 20% nelle operazioni più sicure

# -----------------------------
# FUNZIONI DI SUPPORTO
# -----------------------------
def calcola_segnali(df):
    df['MA5'] = df['Prezzo'].rolling(window=5).mean()
    df['Segnale'] = 'HOLD'
    df.loc[df['Prezzo'] > df['MA5'], 'Segnale'] = 'BUY'
    df.loc[df['Prezzo'] < df['MA5'], 'Segnale'] = 'SELL'
    return df

def color_segnale(val):
    if val == 'BUY':
        return 'background-color: lightgreen'
    elif val == 'SELL':
        return 'background-color: lightcoral'
    else:
        return ''

# -----------------------------
# SCARICO DATI MINUTO
# -----------------------------
dati = yf.download(simbolo, period="1d", interval="1m", auto_adjust=True, progress=False)

if dati.empty:
    st.warning("Errore: nessun dato disponibile al momento.")
else:
    # Gestione MultiIndex o normale
    if isinstance(dati.columns, pd.MultiIndex):
        df = dati['Close'][simbolo].to_frame()
    else:
        df = dati['Close'].to_frame()
    df.columns = ['Prezzo']

    df = calcola_segnali(df)
    df['Cumulativo_%'] = 0.0

    # Simulazione saldo e operazioni
    saldo = saldo_iniziale
    operazioni = []

    for i in range(len(df)):
        segnale = df['Segnale'].iloc[i]
        prezzo = df['Prezzo'].iloc[i]

        if segnale == 'BUY':
            invest = saldo * percentuale_base
            saldo -= invest
            guadagno = invest * 0.001  # ipotetico guadagno 0.1%
            saldo += invest + guadagno
            operazioni.append(f"BUY ${invest:.2f} a ${prezzo:.2f} => nuovo saldo ${saldo:.2f}")

        elif segnale == 'SELL':
            invest = saldo * percentuale_base
            saldo -= invest
            perdita = invest * 0.001  # ipotetica perdita 0.1%
            saldo += invest - perdita
            operazioni.append(f"SELL ${invest:.2f} a ${prezzo:.2f} => nuovo saldo ${saldo:.2f}")

        df['Cumulativo_%'].iloc[i] = (saldo - saldo_iniziale) / saldo_iniziale * 100

    # -----------------------------
    # VISUALIZZAZIONE
    # -----------------------------
    st.subheader("Tabella segnali recenti")
    st.dataframe(df.tail(20).style.applymap(color_segnale, subset=['Segnale']))

    st.subheader("Grafico Prezzo vs MA5")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Prezzo'], mode='lines', name='Prezzo', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], mode='lines', name='MA5', line=dict(color='orange')))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"Saldo attuale: ${saldo:.2f}")
    st.markdown("**Ultime operazioni:**")
    for op in operazioni[-5:]:
        st.markdown(op)

    st.subheader(f"Guadagno/Perdita cumulativa: {df['Cumulativo_%'].iloc[-1]:.2f}%")
