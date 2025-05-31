import streamlit as st
import pandas as pd
from twilio.rest import Client
import os
import sqlite3

# Carregar do .env local apenas se não estiver rodando no Streamlit Cloud
if os.getenv("TWILIO_ACCOUNT_SID") is None:
    from dotenv import load_dotenv
    load_dotenv()

# Variáveis de ambiente seguras
ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
FROM_WHATSAPP = st.secrets["FROM_WHATSAPP"]
TO_WHATSAPP = st.secrets["TO_WHATSAPP"]

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Banco SQLite
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

# Layout do app
st.set_page_config(page_title="Twilio WhatsApp", page_icon="💬", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #f5f5f5;
    }
    .stTextArea>div>textarea {
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

if os.path.exists("logo.png"):
    st.image("logo.png", width=200)

st.title("💬 Envio de Mensagens via WhatsApp com Twilio")

# Tabs
aba1, aba2, aba3 = st.tabs(["📨 Enviar", "📋 Histórico", "📎 Exportar"])

with aba1:
    mensagem = st.text_area("Digite sua mensagem aqui:")
    if st.button("📤 Enviar via WhatsApp"):
        if not mensagem.strip():
            st.warning("Por favor, digite uma mensagem antes de enviar.")
        else:
            try:
                msg = client.messages.create(
                    body=mensagem,
                    from_=f"whatsapp:{FROM_WHATSAPP}",
                    to=f"whatsapp:{TO_WHATSAPP}"
                )
                st.success(f"Mensagem enviada! SID: {msg.sid}")
                registrar_log(mensagem, msg.sid)
            except Exception as e:
                st.error(f"Erro ao enviar: {e}")

with aba2:
    st.subheader("📜 Histórico de Mensagens")
    cursor.execute("SELECT timestamp, mensagem, sid FROM mensagens ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            st.markdown(f"🕒 **{row[0]}**  \n📤 `{row[1]}`  \n🆔 SID: `{row[2]}`")
            st.markdown("---")
    else:
        st.info("Nenhuma mensagem registrada ainda.")

    if st.button("🗑️ Limpar histórico"):
        cursor.execute("DELETE FROM mensagens")
        conn.commit()
        st.success("Histórico apagado.")
        st.experimental_rerun()

with aba3:
    st.subheader("📁 Exportar Histórico")
    cursor.execute("SELECT timestamp, mensagem, sid FROM mensagens ORDER BY timestamp DESC")
    data = cursor.fetchall()
    if data:
        df = pd.DataFrame(data, columns=["Data", "Mensagem", "SID"])
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar CSV", data=csv, file_name="mensagens.csv", mime="text/csv")
    else:
        st.warning("Nenhum dado para exportar.")
