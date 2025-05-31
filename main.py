import streamlit as st
import pandas as pd
from twilio.rest import Client
import os
import io
import sqlite3
from datetime import datetime

# Carrega variáveis do .env local, se não vierem do ambiente (ex: Streamlit Cloud)
if os.getenv("TWILIO_ACCOUNT_SID") is None:
    from dotenv import load_dotenv
    load_dotenv()

# Variáveis
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP = os.getenv("FROM_WHATSAPP")
TO_WHATSAPP = os.getenv("TO_WHATSAPP")
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Banco de dados SQLite
conn = sqlite3.connect("mensagens.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS mensagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mensagem TEXT,
    sid TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def registrar_log(mensagem, sid):
    cursor.execute("INSERT INTO mensagens (mensagem, sid) VALUES (?, ?)", (mensagem, sid))
    conn.commit()

# Tema e layout
st.set_page_config(page_title="Twilio WhatsApp", page_icon="💬", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #f5f5f5;
    }
    .css-18e3th9 {
        padding-top: 2rem;
    }
    .stTextArea>div>textarea {
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# Logotipo
if os.path.exists("logo.png"):
    st.image("logo.png", width=200)

st.title("💬 Envio de Mensagens via WhatsApp com Twilio")
col1, col2 = st.columns([4, 1])
with col1:
    mensagem = st.text_area("Digite a mensagem:")
with col2:
    if st.button("📤 Enviar"):
        try:
            msg = client.messages.create(
                body=mensagem,
                from_=f"whatsapp:{FROM_WHATSAPP}",
                to=f"whatsapp:{TO_WHATSAPP}"
            )
            st.success(f"Mensagem enviada! SID: {msg.sid}")
            registrar_log(mensagem, msg.sid)
        except Exception as e:
            st.error(f"Erro: {e}")

st.markdown("---")
st.subheader("📋 Histórico de mensagens enviadas")

if st.button("⬇️ Exportar como CSV"):
    try:
        cursor.execute("SELECT timestamp, mensagem, sid FROM mensagens ORDER BY timestamp DESC")
        data = cursor.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["Data", "Mensagem", "SID"])
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Clique aqui para baixar", data=csv, file_name="historico_mensagens.csv", mime="text/csv")
        else:
            st.warning("Nenhuma mensagem registrada.")
    except Exception as e:
        st.error(f"Erro: {e}")

try:
    cursor.execute("SELECT timestamp, mensagem, sid FROM mensagens ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            st.markdown(f"🕒 **{row[0]}**  \n📤 `{row[1]}`  \n🆔 SID: `{row[2]}`")
            st.markdown("---")
    else:
        st.info("Nenhuma mensagem registrada ainda.")
except Exception as e:
    st.error(f"Erro: {e}")

if st.button("🗑️ Apagar histórico"):
    try:
        cursor.execute("DELETE FROM mensagens")
        conn.commit()
        st.success("Histórico apagado.")
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Erro: {e}")
