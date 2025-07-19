import pandas as pd
import requests
from io import BytesIO
import streamlit as st

# -------------------------------
# 📥 Load Excel file from GitHub
# -------------------------------
url = "https://github.com/paulom40/PFonseca.py/raw/main/BBrito.xlsx"

try:
    response = requests.get(url)
    response.raise_for_status()

    df = pd.read_excel(BytesIO(response.content), sheet_name="BBrito")
    df["Data Venc."] = pd.to_datetime(df["Data Venc."], errors="coerce").dt.date

    st.success("📥 Dados carregados com sucesso!")

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

st.write("📅 Last Update 18/07/2025")

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

# Cliente selector
entidades_unicas = sorted(df["Entidade"].dropna().unique())
entidade_selecionada = st.sidebar.selectbox("Selecione o Cliente:", entidades_unicas)

# -------------------------------
# 🔍 Apply Dias filter (-7 to -1)
# -------------------------------
df_cliente = df[df["Entidade"] == entidade_selecionada]
df_filtrado = df_cliente[(df_cliente["Dias"] >= -7) & (df_cliente["Dias"] <= -1)]

# -------------------------------
# 📊 Display results
# -------------------------------
st.title("📉 Vencimentos Atrasados - Últimos 7 Dias")
st.markdown(
    f"Exibindo resultados para **{entidade_selecionada}** com vencimentos **atrasados entre -7 e -1 dias**."
)

st.dataframe(df_filtrado, use_container_width=True)

# -------------------------------
# 📈 Summary metrics
# -------------------------------
total_registros = len(df_filtrado)
media_dias = df_filtrado["Dias"].mean() if total_registros > 0 else 0
valor_total = df_filtrado["Valor Pendente"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("🔴 Total Atrasados", total_registros)
col2.metric("🕒 Média Dias", f"{media_dias:.1f}")
col3.metric("💸 Valor Pendente Total", f"€ {valor_total:,.2f}")
