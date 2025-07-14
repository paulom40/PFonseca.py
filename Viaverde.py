import pandas as pd
import requests
import os
import streamlit as st

# -------------------------------
# 📥 Load Excel file from GitHub
# -------------------------------
url = "https://github.com/paulom40/PFonseca.py/raw/main/Viaverde.xlsx"

if os.path.exists("https://github.com/paulom40/PFonseca.py/raw/main/Viaverde.xlsx"):
    df = pd.read_excel("https://github.com/paulom40/PFonseca.py/raw/main/Viaverde.xlsx")
    st.success("✅ Arquivo carregado com sucesso!")
    st.write(df.head())  # Preview the first few rows
else:
    st.error("❌ Arquivo não encontrado. Verifique o caminho ou nome do arquivo.")

# Sidebar filters
st.sidebar.header("Filtros")

# Unique values
matriculas = df['Matricula'].unique()
anos = df['Ano'].unique()
meses = df['Mês'].unique()
dias = df['Dia'].unique()

# Multiselect filter boxes
selected_matriculas = st.sidebar.multiselect("Matricula", sorted(matriculas), default=matriculas)
selected_anos = st.sidebar.multiselect("Ano", sorted(anos), default=anos)
selected_meses = st.sidebar.multiselect("Mês", sorted(meses), default=meses)
selected_dias = st.sidebar.multiselect("Dia", sorted(dias), default=dias)

# Filter the dataframe
filtered_df = df[
    (df['Matricula'].isin(selected_matriculas)) &
    (df['Ano'].isin(selected_anos)) &
    (df['Mês'].isin(selected_meses)) &
    (df['Dia'].isin(selected_dias))
]

# Main dashboard
st.title("📈 Via Verde Dashboard")
st.write("Dados filtrados:")
st.dataframe(filtered_df)

# Summary statistics
st.write("📌 Resumo:")
st.write(filtered_df.describe())
