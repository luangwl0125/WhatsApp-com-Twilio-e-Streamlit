import streamlit as st
from twilio.rest import Client
import os

if os.getenv("TWILIO_ACCOUNT_SID") is None:
    from dotenv import load_dotenv
    load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP = os.getenv("FROM_WHATSAPP")
TO_WHATSAPP = os.getenv("TO_WHATSAPP")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

st.set_page_config(
    page_title="Twilio WhatsApp",
    page_icon="💬",
    layout="centered"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #f7f7f7;
    }
    .css-18e3th9 {
        padding-top: 3rem;
    }
    .stTextArea>div>textarea {
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Envio de Mensagens via WhatsApp com Twilio")
mensagem = st.text_area("Digite a mensagem que deseja enviar:")

if st.button("Enviar Mensagem"):
    try:
        msg = client.messages.create(
            body=mensagem,
            from_=f"whatsapp:{FROM_WHATSAPP}",
            to=f"whatsapp:{TO_WHATSAPP}"
        )
        st.success(f"Mensagem enviada com sucesso! SID: {msg.sid}")
    except Exception as e:
        st.error(f"Erro ao enviar mensagem: {e}")
