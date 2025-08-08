import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# 🔧 Page configuration
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# 🏷️ Title
st.title("📊 Sales Data Analysis Dashboard")

# 📥 Load and clean data
@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/1semestrePM.xlsx"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("❌ Failed to load data from URL")
        return pd.DataFrame()

    df = pd.read_excel(BytesIO(response.content))

    # 🧼 Clean column names
    df.columns = df.columns.str.strip()

    # 📅 Convert 'Data' to datetime
    if "Data" in df.columns:
        df = df.rename(columns={"Data": "Date"})
        df["Date"] = pd.to_numeric(df["Date"], errors="coerce")
        df["Date"] = df["Date"].apply(
            lambda x: pd.to_datetime("1899-12-30") + pd.Timedelta(days=x)
            if pd.notnull(x) and 1 <= x <= 73048 else pd.NaT
        )
        df["Week"] = df["Date"].dt.isocalendar().week

    # 🔢 Convert numeric columns
    for col in ["Quantidade", "PM", "V_Líquido"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 🧹 Drop rows missing key fields
    df = df.dropna(subset=["Quantidade", "PM", "Mês", "Ano", "Artigo"])

    return df

# 📊 Load data
df = load_data()

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

# 📈 KPIs
st.header("📈 Key Performance Indicators")
col1, col2, col3 = st.columns(3)

avg_pm = filtered_df["PM"].mean()
avg_qty_month = filtered_df.groupby("Mês")["Quantidade"].mean().mean()
avg_qty_week = filtered_df.groupby("Week")["Quantidade"].mean().mean()

col1.metric("Average PM", f"{avg_pm:.2f}")
col2.metric("Average Quantidade by Month", f"{avg_qty_month:.2f}")
col3.metric("Average Quantidade by Week", f"{avg_qty_week:.2f}")

# 📦 Quantidade por Mês
st.subheader("📦 Quantidade por Mês")
st.bar_chart(filtered_df.groupby("Mês")["Quantidade"].sum())

# 💰 V Líquido por Mês
st.subheader("💰 V Líquido por Mês")
st.line_chart(filtered_df.groupby("Mês")["V_Líquido"].mean())

# 📋 Dados Filtrados
st.subheader("📋 Dados Filtrados")
st.dataframe(filtered_df, use_container_width=True)
