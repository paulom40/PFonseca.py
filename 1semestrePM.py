import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import BytesIO

# 🔧 Page configuration
st.set_page_config(page_title="📊 Sales Dashboard", layout="wide")

# 🏷️ Title
st.title("📊 1º Semestre PM - Sales Data Dashboard")

# 📥 Load and clean data
@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/1semestrePM.xlsx"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("❌ Failed to load data from URL")
        return pd.DataFrame()

    df = pd.read_excel(BytesIO(response.content))
    df.columns = df.columns.str.strip()

    # 📅 Convert 'Date' column
    if "Date" in df.columns:
        df["Date"] = pd.to_numeric(df["Date"], errors="coerce")
        df["Date"] = df["Date"].apply(
            lambda x: pd.to_datetime("1899-12-30") + pd.Timedelta(days=x)
            if pd.notnull(x) and isinstance(x, (int, float)) and 0 <= x <= 2958465
            else pd.NaT
        )
    else:
        st.warning("⚠️ 'Date' column not found.")

    # 🔢 Convert numeric columns
    for col in ["Quantidade", "PM", "Valor liquido"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            st.warning(f"⚠️ Column '{col}' not found.")

    # 🧹 Drop rows missing key fields
    df.dropna(subset=["Quantidade", "PM", "Mês", "Ano", "Artigo"], inplace=True)

    return df

# 📊 Load data
with st.spinner("Loading data..."):
    df = load_data()
if df.empty:
    st.stop()

# 🎛️ Sidebar filters
st.sidebar.header("🎛️ Filtros")
selected_anos = st.sidebar.multiselect("Ano", sorted(df["Ano"].unique()), default=sorted(df["Ano"].unique()))
selected_meses = st.sidebar.multiselect("Mês", sorted(df["Mês"].unique()), default=sorted(df["Mês"].unique()))
selected_artigos = st.sidebar.multiselect("Artigo", sorted(df["Artigo"].unique()), default=sorted(df["Artigo"].unique()))

# 🔍 Apply filters
filtered_df = df[
    df["Ano"].isin(selected_anos) &
    df["Mês"].isin(selected_meses) &
    df["Artigo"].isin(selected_artigos)
]

if filtered_df.empty:
    st.warning("⚠️ No matching data for selected filters.")
    st.stop()

# 📅 Sort months chronologically
month_order = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
filtered_df["Mês"] = pd.Categorical(filtered_df["Mês"], categories=month_order, ordered=True)

# 📈 KPIs
st.header("📈 Indicadores de Desempenho")
col1, col2, col3 = st.columns(3)

avg_pm = filtered_df["PM"].mean()
avg_qty_month = filtered_df.groupby("Mês")["Quantidade"].mean().mean()
avg_vliquido_by_month = filtered_df.groupby("Mês")["Valor liquido"].mean().mean()

col1.metric("PM Médio", f"{avg_pm:.2f}")
col2.metric("Quantidade Média por Mês", f"{avg_qty_month:.2f}")
col3.metric("Valor Líquido Médio por Mês", f"{avg_vliquido_by_month:.2f}")

# 📦 Quantidade por Mês
st.subheader("📦 Quantidade Total por Mês")
st.bar_chart(filtered_df.groupby("Mês")["Quantidade"].sum())

# 💰 Valor Líquido por Mês
st.subheader("💰 Valor Líquido Médio por Mês")
st.line_chart(filtered_df.groupby("Mês")["Valor liquido"].mean())

# 📋 Dados Filtrados
st.subheader("📋 Dados Filtrados")
st.dataframe(filtered_df, use_container_width=True)

# 📥 Download CSV
st.download_button(
    label="📥 Baixar dados filtrados como CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="dados_filtrados.csv",
    mime="text/csv"
)

# 🧼 Footer
st.markdown("---")
st.markdown("Feito com ❤️ por Paulojt")
