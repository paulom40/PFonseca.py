import pandas as pd
import requests
from io import BytesIO
import streamlit as st

# -------------------------------
# 📥 Load Excel file from GitHub
# -------------------------------
url = "https://github.com/paulom40/PFonseca.py/raw/main/PCosta.xlsx"

st.set_page_config(page_title="Vencimentos Paulo Costa", layout="centered")

st.title("📊 Vencimentos Paulo Costa")
st.caption("📅 Última atualização: 07/08/2025")

with st.spinner("Carregando dados..."):
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), sheet_name="PCosta")
        df["Data Venc."] = pd.to_datetime(df["Data Venc."], errors="coerce").dt.date
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
df["Valor Pendente"] = pd.to_numeric(df["Valor Pendente"], errors="coerce")

# -------------------------------
# 🎛️ Sidebar: Filters
# -------------------------------
st.sidebar.header("🔎 Filtros")

entidades = sorted(df["Entidade"].dropna().unique())
cliente = st.sidebar.selectbox("Cliente:", entidades)

dias_min, dias_max = st.sidebar.slider(
    "Dias até vencimento:",
    min_value=1,
    max_value=180,
    value=(1, 180),
    step=1
)

# -------------------------------
# 🔍 Apply filters
# -------------------------------
df_cliente = df[df["Entidade"] == cliente]
df_filtrado = df_cliente[(df_cliente["Dias"] >= dias_min) & (df_cliente["Dias"] <= dias_max)]
df_a_vencer = df_cliente[(df_cliente["Dias"] >= -20) & (df_cliente["Dias"] <= -1)]

cols_exibir = ["Entidade", "Documento", "Data Venc.", "Dias", "Valor Pendente"]

# -------------------------------
# 📊 Filtered Results
# -------------------------------
with st.expander("📋 Resultados Filtrados", expanded=True):
    st.markdown(f"**Cliente:** {cliente}  \n**Intervalo de Dias:** {dias_min}–{dias_max}")
    st.dataframe(df_filtrado[cols_exibir], use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("📌 Registros", len(df_filtrado))
    col2.metric("📆 Média Dias", f"{df_filtrado['Dias'].mean():.1f}" if len(df_filtrado) > 0 else "0")
    col3.metric("💰 Valor Total", f"€ {df_filtrado['Valor Pendente'].sum():,.2f}")

# -------------------------------
# 📉 Próximos a Vencer
# -------------------------------
with st.expander("📉 Por Vencer (Próximos 20 Dias)", expanded=False):
    st.dataframe(df_a_vencer[cols_exibir], use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 Registros", len(df_a_vencer))
    col2.metric("🕒 Média Dias", f"{df_a_vencer['Dias'].mean():.1f}" if len(df_a_vencer) > 0 else "0")
    col3.metric("💸 Valor Total", f"€ {df_a_vencer['Valor Pendente'].sum():,.2f}")
