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

# Dias slider
st.sidebar.markdown("### ⏳ Filtro por Dias até Vencimento")
dias_min, dias_max = st.sidebar.slider(
    "Selecione o intervalo de Dias:",
    min_value=1,
    max_value=180,
    value=(1, 180),
    step=1
)

# Date range filter
st.sidebar.markdown("### 📅 Filtro por Intervalo de Data de Vencimento")
data_inicio = st.sidebar.date_input("Data Inicial", value=df["Data Venc."].min())
data_fim = st.sidebar.date_input("Data Final", value=df["Data Venc."].max())

# Checkbox for overdue filter
usar_filtro_atrasado = st.sidebar.checkbox("📉 Mostrar apenas atrasados nos últimos 7 dias (-7 a -1)")

# -------------------------------
# 🔍 Apply filters
# -------------------------------
df_cliente = df[df["Entidade"] == entidade_selecionada]

# Filter main dataset
if usar_filtro_atrasado:
    df_filtrado = df_cliente[
        (df_cliente["Dias"] >= -7) &
        (df_cliente["Dias"] <= -1) &
        (df_cliente["Data Venc."] >= data_inicio) &
        (df_cliente["Data Venc."] <= data_fim)
    ]
else:
    df_filtrado = df_cliente[
        (df_cliente["Dias"] >= dias_min) &
        (df_cliente["Dias"] <= dias_max) &
        (df_cliente["Data Venc."] >= data_inicio) &
        (df_cliente["Data Venc."] <= data_fim)
    ]

# -------------------------------
# 📊 Display filtered table
# -------------------------------
st.title("📊 Vencimentos Bruno Brito")

if usar_filtro_atrasado:
    st.markdown(
        f"Exibindo resultados **atrasados nos últimos 7 dias (-7 a -1)** para **{entidade_selecionada}** com vencimentos entre **{data_inicio}** e **{data_fim}**."
    )
else:
    st.markdown(
        f"Exibindo resultados para **{entidade_selecionada}** com **{dias_min}–{dias_max} dias** até vencimento "
        f"e vencimentos entre **{data_inicio}** e **{data_fim}**."
    )

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

# -------------------------------
# 🧾 Overdue Table: Dias between -7 and -1
# -------------------------------
df_atrasado = df_cliente[
    (df_cliente["Dias"] >= -7) &
    (df_cliente["Dias"] <= -1) &
    (df_cliente["Data Venc."] >= data_inicio) &
    (df_cliente["Data Venc."] <= data_fim)
]

st.subheader("📉 Registros Atrasados nos Últimos 7 Dias")
st.dataframe(df_atrasado, use_container_width=True)

# Metrics for overdue
total_registros_atrasado = len(df_atrasado)
media_dias_atrasado = df_atrasado["Dias"].mean() if total_registros_atrasado > 0 else 0
valor_total_atrasado = df_atrasado["Valor Pendente"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("🔴 Total Atrasados", total_registros_atrasado)
col2.metric("🕒 Média Dias", f"{media_dias_atrasado:.1f}")
col3.metric("💸 Valor Atrasado Total", f"€ {valor_total_atrasado:,.2f}")
