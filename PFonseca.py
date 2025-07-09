import pandas as pd
import requests
from io import BytesIO
import streamlit as st

# -------------------------------
# 📥 Load Excel file from GitHub
# -------------------------------
url = "https://github.com/paulom40/PFonseca.py/raw/main/Venc_040725.xlsx"

try:
    response = requests.get(url)
    response.raise_for_status()
    df = pd.read_excel(BytesIO(response.content), sheet_name="PFonseca2")
    st.success("📥 Dados carregados com sucesso!")
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# -------------------------------
# 🧹 Clean and prepare data
# -------------------------------
df.columns = df.columns.str.strip()
df["Entidade"] = df["Entidade"].astype(str).str.strip()
df["Dias"] = pd.to_numeric(df["Dias"], errors="coerce")
df = df.dropna(subset=["Dias"])
df["Dias"] = df["Dias"].astype(int)
df["Data Venc."] = pd.to_datetime(df["Data Venc."], errors="coerce", dayfirst=True)

# -------------------------------
# 🎛️ Sidebar: Filters
# -------------------------------
st.sidebar.header("🔎 Filtros")

# Cliente selector
entidades_unicas = sorted(df["Entidade"].dropna().unique())
entidade_selecionada = st.sidebar.selectbox("Selecione o Cliente:", entidades_unicas)

# Dias slider
st.sidebar.markdown("### ⏳ Filtro por Dias até Vencimento")
dias_min, dias_max = st.sidebar.slider(
    "Selecione o intervalo de Dias:",
    min_value=1,
    max_value=180,
    value=(1, 180),
    step=1
)

# -------------------------------
# 🔍 Apply filters
# -------------------------------
df_cliente = df[df["Entidade"] == entidade_selecionada]
df_filtrado = df_cliente[(df_cliente["Dias"] >= dias_min) & (df_cliente["Dias"] <= dias_max)]

# -------------------------------
# 📊 Display results
# -------------------------------
st.title("📊 Vencimentos PFonseca")
st.markdown(f"Exibindo resultados para **{entidade_selecionada}** com **{dias_min}–{dias_max} dias** até vencimento.")

st.dataframe(df_filtrado, use_container_width=True)

# Optional summary
st.metric("Total de Registros", len(df_filtrado))
if not df_filtrado.empty:
    st.metric("Dias Médios", round(df_filtrado["Dias"].mean(), 1))
