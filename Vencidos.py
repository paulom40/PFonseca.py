import pandas as pd
import requests
from io import BytesIO
import streamlit as st

st.set_page_config(layout="wide")


# -------------------------------
# 📥 Load Excel file from GitHub
# -------------------------------
url = "https://github.com/paulom40/PFonseca.py/raw/main/VVencidos.xlsx"

try:
    response = requests.get(url)
    response.raise_for_status()

    df = pd.read_excel(BytesIO(response.content), sheet_name="VVencidos")
    # 🛠️ Parse dates safely, skipping invalid entries
    df["Data Venc."] = pd.to_datetime(df["Data Venc."], origin='1899-12-30', unit='D', errors="coerce")



    st.success("📥 Dados carregados com sucesso!")

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

st.write("📅 Ultima etualização: 17/07/2025 ás 13:30")

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

# Comercial selector
Comercial_unicos = sorted(df["Comercial"].dropna().unique())
Comercial_selecionado = st.sidebar.selectbox("Selecione o Comercial:", Comercial_unicos)

# Dias slider
st.sidebar.markdown("### ⏳ Filtro por Dias até Vencimento")
dias_min, dias_max = st.sidebar.slider(
    "Selecione o intervalo de Dias:",
    min_value=1,
    max_value=360,
    value=(1, 360),
    step=1
)

# -------------------------------
# 🔍 Apply filters
# -------------------------------
df_filtrado = df[
    (df["Comercial"] == Comercial_selecionado) &
    (df["Dias"] >= dias_min) &
    (df["Dias"] <= dias_max)
]

# -------------------------------
# 📊 Display results
# -------------------------------
st.title("📊 Vencimentos Comerciais")
st.markdown(f"Exibindo resultados para **{Comercial_selecionado}** com **{dias_min}–{dias_max} dias** até vencimento.")

st.dataframe(df_filtrado, use_container_width=True)

# -------------------------------
# 📈 Summary metrics
# -------------------------------
total_registros = len(df_filtrado)
media_dias = df_filtrado["Dias"].mean() if total_registros > 0 else 0
valor_total = df_filtrado["Valor Pendente"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("📌 Total de Registros", total_registros)
col2.metric("📆 Dias Médios", f"{media_dias:.1f}")
col3.metric("💰 Valor Pendente Total", f"€ {valor_total:,.2f}")
