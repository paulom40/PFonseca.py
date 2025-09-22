import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import BytesIO
import base64

# Layout mobile
st.set_page_config(layout="centered")
st.markdown("<style>div.block-container{padding-top:1rem;padding-bottom:1rem}</style>", unsafe_allow_html=True)
st.title("📱 Dashboard de Vencimentos")

# Carregar dados
url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"
df = pd.read_excel(url)

# Padronizar nomes de colunas
df.rename(columns=lambda x: x.strip(), inplace=True)

# Detectar coluna de vencimento
venc_col = next((col for col in df.columns if 'venc' in col.lower()), None)
if venc_col is None:
    st.error("❌ Nenhuma coluna de vencimento encontrada.")
    st.stop()
df[venc_col] = pd.to_datetime(df[venc_col], errors='coerce')

# Detectar coluna de Valor Pendente
valor_pendente_col = next((col for col in df.columns if 'valor pendente' in col.lower()), None)

# Detectar coluna de Entidade
entidade_col = next((col for col in df.columns if 'entidade' in col.lower()), None)

# Sidebar: filtro por comercial
with st.sidebar:
    st.header("🔍 Filtro por Comercial")
    comerciais = df['Comercial'].dropna().unique() if 'Comercial' in df.columns else []
    comercial_selecionado = st.selectbox("Selecione o comercial", comerciais)

# Filtrar dados
df = df[df['Comercial'] == comercial_selecionado]
