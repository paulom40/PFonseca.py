import streamlit as st
import pandas as pd

# Load Excel file from GitHub
url = "https://github.com/paulom40/PFonseca.py/raw/main/1semestrePM.xlsx"
df = pd.read_excel(url)

# Sidebar filters
st.sidebar.title("🎛️ Filtros")
selected_years = st.sidebar.multiselect("Ano", df['Ano'].unique(), default=df['Ano'].unique())
selected_months = st.sidebar.multiselect("Mês", df['Mês'].unique(), default=df['Mês'].unique())
selected_artigos = st.sidebar.multiselect("Artigo", df['Artigo'].unique(), default=df['Artigo'].unique())

# Apply filters
filtered_df = df[
    df['Ano'].isin(selected_years) &
    df['Mês'].isin(selected_months) &
    df['Artigo'].isin(selected_artigos)
]

# KPIs
total_pm = filtered_df['PM'].sum()
avg_quantidade_by_month = filtered_df.groupby('Mês')['Quantidade'].mean().sort_index()
avg_vliquido_by_month = filtered_df.groupby('Mês')['V Liquido'].mean().sort_index()

# Main dashboard
st.title("📊 Indicadores de Desempenho")

st.metric(label="Total PM", value=f"{total_pm:,.2f}")

st.subheader("📦 Média de Quantidade por Mês")
st.dataframe(avg_quantidade_by_month)

st.subheader("💰 Média de V Liquido por Mês")
st.dataframe(avg_vliquido_by_month)
