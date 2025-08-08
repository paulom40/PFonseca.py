import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# Fetch data from URL
url = "https://github.com/paulom40/PFonseca.py/raw/main/1semestrePM.xlsx"
@st.cache_data
def load_data():
    return pd.read_excel(url)

df = load_data()

# Sidebar filters
st.sidebar.header("Filtros")
ano_options = sorted(df['Ano'].unique())
selected_ano = st.sidebar.multiselect("Ano", ano_options, default=ano_options)

mes_options = sorted(df['Mês'].unique())
selected_mes = st.sidebar.multiselect("Mês", mes_options, default=mes_options)

artigo_options = sorted(df['Artigo'].unique())
selected_artigo = st.sidebar.multiselect("Artigo", artigo_options, default=artigo_options)

# Filter data
filtered_df = df[
    (df['Ano'].isin(selected_ano)) &
    (df['Mês'].isin(selected_mes)) &
    (df['Artigo'].isin(selected_artigo))
]

# KPIs
st.header("KPIs")
col1, col2, col3 = st.columns(3)

avg_pm = filtered_df['PM'].mean() if not filtered_df.empty else 0
avg_quantidade = filtered_df['Quantidade'].mean() if not filtered_df.empty else 0
avg_valor_liquido = filtered_df['Valor Liquido'].mean() if not filtered_df.empty else 0

with col1:
    st.metric("Média PM", f"{avg_pm:.2f}")
with col2:
    st.metric("Média Quantidade", f"{avg_quantidade:.2f}")
with col3:
    st.metric("Média Valor Liquido", f"{avg_valor_liquido:.2f}")

# Display filtered data
st.header("Dados Filtrados")
st.dataframe(filtered_df)
