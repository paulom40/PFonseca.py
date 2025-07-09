import pandas as pd
import requests
from io import BytesIO
import streamlit as st

# Load Excel file
url = "https://github.com/paulom40/PFonseca.py/raw/main/Venc_040725.xlsx"
response = requests.get(url)
df = pd.read_excel(BytesIO(response.content), sheet_name="PFonseca2")

# Clean columns
df.columns = df.columns.str.strip()
df["Entidade"] = df["Entidade"].astype(str).str.strip()
df["Dias"] = pd.to_numeric(df["Dias"], errors="coerce")
df = df.dropna(subset=["Dias"])
df["Dias"] = df["Dias"].astype(int)
df["Data Venc."] = pd.to_datetime(df["Data Venc."], errors="coerce", dayfirst=True)

# Sidebar: Cliente selector only
entidades_unicas = sorted(df["Entidade"].dropna().unique())
entidade_selecionada = st.sidebar.selectbox("Selecione o Cliente:", entidades_unicas)

# Filter by selected client
df_cliente = df[df["Entidade"] == entidade_selecionada]

# Display
st.subheader(f"📄 Dados para {entidade_selecionada}")
st.dataframe(df_cliente)
