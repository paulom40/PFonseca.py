import streamlit as st
import pandas as pd
import os

# -------------------------------
# 📥 Load Excel file from GitHub
# -------------------------------
url = "https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx"
# File path
file_path = "https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx"

# Attempt to load the file
df = None
try:
    if os.path.exists("https://github.com/paulom40/PFonseca.py/raw/main/Viaverde.xlsx"):
        df = pd.read_excel("https://github.com/paulom40/PFonseca.py/raw/main/Viaverde.xlsx")
        st.success("✅ Arquivo carregado com sucesso!")
        st.write("🔍 Colunas disponíveis:", df.columns.tolist())
    else:
        st.error("❌ Arquivo não encontrado: " + file_path)
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {e}")

# Only proceed if df is loaded correctly
if df is not None:
    # Check required columns
    required_cols = ['Matricula', 'Ano', 'Mês', 'Dia']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"❌ Colunas faltando no arquivo: {', '.join(missing_cols)}")
    else:
        # Sidebar filters
        st.sidebar.header("Filtros")
        selected_matriculas = st.sidebar.multiselect("Matricula", sorted(df['Matricula'].unique()), default=df['Matricula'].unique())
        selected_anos = st.sidebar.multiselect("Ano", sorted(df['Ano'].unique()), default=df['Ano'].unique())
        selected_meses = st.sidebar.multiselect("Mês", sorted(df['Mês'].unique()), default=df['Mês'].unique())
        selected_dias = st.sidebar.multiselect("Dia", sorted(df['Dia'].unique()), default=df['Dia'].unique())

        # Filtered data
        filtered_df = df[
            df['Matricula'].isin(selected_matriculas) &
            df['Ano'].isin(selected_anos) &
            df['Mês'].isin(selected_meses) &
            df['Dia'].isin(selected_dias)
        ]

        # Display results
        st.title("📈 Via Verde Dashboard")
        st.write("Dados filtrados:")
        st.dataframe(filtered_df)

        st.write("📌 Resumo:")
        st.write(filtered_df.describe())
