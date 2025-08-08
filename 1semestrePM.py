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

    # 📅 Convert 'Date' to datetime (optional, removed 'Week' dependency)
    if "Date" in df.columns:
        # Debugging: Show first few raw Date values
        st.write("First few raw Date values:", df["Date"].head().tolist())
        # Convert to numeric, coerce invalid values to NaN
        df["Date"] = pd.to_numeric(df["Date"], errors="coerce")
        # Debugging: Show first few numeric Date values
        st.write("First few numeric Date values:", df["Date"].head().tolist())
        # Convert to datetime, cap out-of-bounds values
        df["Date"] = df["Date"].apply(
            lambda x: pd.NaT if pd.isna(x) or (not isinstance(x, (int, float)) or x < 0 or x > 2958465)
            else pd.to_datetime("1899-12-30") + pd.Timedelta(days=x)
        )
        # Debugging: Show first few converted Date values
        st.write("First few converted Date values:", df["Date"].head().tolist())
    else:
        st.warning("⚠️ 'Date' column not found in dataset.")

    # 🔢 Convert numeric columns
    for col in ["Quantidade", "PM", "Valor liquido"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            st.warning(f"⚠️ Column '{col}' not found in dataset.")

    # 🧹 Drop rows missing key fields
    df = df.dropna(subset=["Quantidade", "PM", "Mês", "Ano", "Artigo"])

    # Debugging: Show column names
    st.write("Loaded DataFrame columns:", df.columns.tolist())

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
avg_vliquido_by_month = filtered_df.groupby("Mês")["Valor liquido"].mean().mean()

col1.metric("Average PM", f"{avg_pm:.2f}")
col2.metric("Average Quantidade by Month", f"{avg_qty_month:.2f}")
col3.metric("Average Valor Liquido by Month", f"{avg_vliquido_by_month:.2f}")

# 📦 Quantidade por Mês
st.subheader("📦 Quantidade por Mês")
st.bar_chart(filtered_df.groupby("Mês")["Quantidade"].sum())

# 💰 Valor Liquido por Mês
st.subheader("💰 Valor Liquido por Mês")
st.line_chart(filtered_df.groupby("Mês")["Valor liquido"].mean())

# 📋 Dados Filtrados
st.subheader("📋 Dados Filtrados")
st.dataframe(filtered_df, use_container_width=True)
