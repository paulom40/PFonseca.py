import pandas as pd
import requests
from io import BytesIO
import streamlit as st

# ✅ Correct raw file URL from GitHub
url = "https://github.com/paulom40/PFonseca.py/raw/main/Venc_040725.xlsx"

# 📥 Download and load Excel file
try:
    response = requests.get(url)
    response.raise_for_status()  # Raise error if download fails

    # Load Excel sheet into DataFrame
    df = pd.read_excel(BytesIO(response.content), sheet_name="PFonseca2")
    st.success("Dados carregados com sucesso!")
except requests.exceptions.HTTPError as e:
    st.error(f"Erro HTTP ao carregar o arquivo: {e}")
    st.stop()
except Exception as e:
    st.error(f"Erro inesperado: {e}")
    st.stop()

# 🧹 Clean and prepare data
df.columns = df.columns.str.strip()
df["Dias"] = pd.to_numeric(df["Dias"], errors="coerce")
df = df.dropna(subset=["Dias"])
df["Dias"] = df["Dias"].astype(int)
df["Data Venc."] = pd.to_datetime(df["Data Venc."], errors="coerce", dayfirst=True)
df["Mês"] = df["Mês"].astype(str).str.lower().str.strip()

# 📋 Show full table (optional)
st.subheader("📊 Tabela Completa")
st.dataframe(df)

# 🧭 Sidebar Filters
st.sidebar.header("🔎 Filtros")

# 🧼 Clean the 'Entidade' column
df["Entidade"] = df["Entidade"].astype(str).str.strip()

# 📋 Get sorted, unique list of clients
entidades_unicas = sorted(df["Entidade"].dropna().unique())

# 🎯 Sidebar selector for client
entidade_selecionada = st.sidebar.selectbox(
    "Selecione o Cliente:",
    options=entidades_unicas
)

# 🔍 Filter the DataFrame
df_cliente = df[df["Entidade"] == entidade_selecionada]


# Mês selector
meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", 
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
mes_selecionado = st.sidebar.selectbox("Selecione o Mês:", [m.capitalize() for m in meses])
mes_selecionado = mes_selecionado.lower().strip()

# 🔍 Filter by client
df_cliente = df[df["Entidade"] == Entidade]

# 🔍 Filter by month
df_mes = df_cliente[df_cliente["Mês"] == mes_selecionado]

# 📄 Show filtered results
st.subheader(f"📄 Dados para {Entidade} no mês de {mes_selecionado.capitalize()}")
st.dataframe(df_mes)
