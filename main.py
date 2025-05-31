import streamlit as st
import pandas as pd
from twilio.rest import Client
import os
import io
import sqlite3
from datetime import datetime

# Carregar variáveis de ambiente (local)
if os.getenv("TWILIO_ACCOUNT_SID") is None:
    from dotenv import load_dotenv
    load_dotenv()

# Variáveis de ambiente
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP = os.getenv("FROM_WHATSAPP")
TO_WHATSAPP = os.getenv("TO_WHATSAPP")

# Twilio client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Conexão com SQLite
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

# Função para log
def registrar_log(mensagem, sid):
    cursor.execute("INSERT INTO mensagens (mensagem, sid) VALUES (?, ?)", (mensagem, sid))
    conn.commit()

# Interface Streamlit
st.set_page_config(
    page_title="Twilio WhatsApp",
    page_icon="💬",
    layout="centered"
)

st.markdown("---")
st.subheader("📋 Histórico de mensagens enviadas")

# Exportar CSV
if st.button("⬇️ Exportar histórico como CSV"):
    try:
        cursor.execute("SELECT timestamp, mensagem, sid FROM mensagens ORDER BY timestamp DESC")
        data = cursor.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["Data", "Mensagem", "SID"])
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Clique aqui para baixar o CSV",
                data=csv,
                file_name="historico_mensagens.csv",
                mime="text/csv"
            )
        else:
            st.warning("Não há mensagens para exportar.")
    except Exception as e:
        st.error(f"Erro ao exportar CSV: {e}")

# Visualizar histórico
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
    st.error(f"Erro ao carregar histórico: {e}")

# Limpar histórico
if st.button("🗑️ Apagar todos os registros"):
    try:
        cursor.execute("DELETE FROM mensagens")
        conn.commit()
        st.success("Histórico apagado com sucesso.")
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Erro ao apagar histórico: {e}")
