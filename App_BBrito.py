import pandas as pd
import requests
from io import BytesIO
import streamlit as st

# ---------------------------------------
# 📥 Load Excel file from GitHub
# ---------------------------------------
@st.cache_data(ttl=3600)
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/BBrito.xlsx"
    response = requests.get(url)
    df = pd.read_excel(BytesIO(response.content), sheet_name="BBrito")
    return df

try:
    df = load_data()
    st.success("✅ Dados carregados com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {e}")
    st.stop()

# ---------------------------------------
# 📅 Data Cleaning
# ---------------------------------------
st.write("📅 Última atualização: 08/08/2025")

df.columns = df.columns.str.strip()
df["Entidade"] = df["Entidade"].astype(str).str.strip()
df["Dias"] = pd.to_numeric(df["Dias"], errors="coerce")
df = df.dropna(subset=["Dias"])
df["Dias"] = df["Dias"].astype(int)
df["Valor Pendente"] = pd.to_numeric(df["Valor Pendente"], errors="coerce")
df["Data Venc."] = pd.to_datetime(df["Data Venc."], errors="coerce").dt.date

# ---------------------------------------
# 🎛️ Sidebar Filters
# ---------------------------------------
st.sidebar.header("🔎 Filtros")
entidades_unicas = sorted(df["Entidade"].dropna().unique())
entidade_selecionada = st.sidebar.selectbox("Cliente:", entidades_unicas)

dias_min, dias_max = st.sidebar.slider(
    "Intervalo de Dias até Vencimento:",
    min_value=-30,
    max_value=180,
    value=(1, 180),
    step=1
)

# ---------------------------------------
# 🔍 Filter and Display
# ---------------------------------------
df_cliente = df[df["Entidade"] == entidade_selecionada]
df_filtrado = df_cliente[(df_cliente["Dias"] >= dias_min) & (df_cliente["Dias"] <= dias_max)]

st.title("📊 Vencimentos Bruno Brito")
st.markdown(f"**Cliente:** {entidade_selecionada} | **Intervalo de dias:** {dias_min}–{dias_max}")

cols_exibir = ["Documento", "Data Venc.", "Dias", "Valor Pendente"]
st.dataframe(df_filtrado[cols_exibir], use_container_width=True)

# 📈 Summary Metrics
col1, col2, col3 = st.columns(3)
col1.metric("🔢 Total", len(df_filtrado))
col2.metric("📆 Média Dias", f"{df_filtrado['Dias'].mean():.1f}" if len(df_filtrado) > 0 else "0")
col3.metric("💰 Total €", f"€ {df_filtrado['Valor Pendente'].sum():,.2f}")

# ---------------------------------------
# 📉 Registros Próximos (–20 a –1 Dias)
# ---------------------------------------
st.subheader("📉 Vencimentos nos próximos 20 dias")
df_a_vencer = df_cliente[(df_cliente["Dias"] >= -20) & (df_cliente["Dias"] <= -1)]

st.dataframe(df_a_vencer[cols_exibir], use_container_width=True)

col1, col2, col3 = st.columns(3)
col1.metric("🔴 Total A Vencer", len(df_a_vencer))
col2.metric("🕒 Média Dias", f"{df_a_vencer['Dias'].mean():.1f}" if len(df_a_vencer) > 0 else "0")
col3.metric("💸 Valor Total", f"€ {df_a_vencer['Valor Pendente'].sum():,.2f}")
