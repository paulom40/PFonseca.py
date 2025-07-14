import streamlit as st
import pandas as pd

# URL to your GitHub raw file
file_url = "https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx"

# Load the Excel file directly from GitHub
df = None
try:
    df = pd.read_excel(file_url)
    st.success("✅ Arquivo carregado com sucesso!")

    # Remove unnecessary columns
    df = df.drop(columns=['Date', 'Mês'], errors='ignore')

    # Display columns for confirmation
    st.write("📦 Colunas após limpeza:", df.columns.tolist())
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {e}")

# Proceed only if data is loaded
if df is not None:
    required_columns = ['Matricula', 'Ano', 'Month', 'Dia']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"⚠️ Faltam colunas obrigatórias: {', '.join(missing_columns)}")
    else:
        st.sidebar.header("Filtros")

        selected_matriculas = st.sidebar.multiselect("Matricula", sorted(df['Matricula'].unique()), default=df['Matricula'].unique())
        selected_anos = st.sidebar.multiselect("Ano", sorted(df['Ano'].unique()), default=df['Ano'].unique())
        selected_months = st.sidebar.multiselect("Month", sorted(df['Month'].unique()), default=df['Month'].unique())
        selected_dias = st.sidebar.multiselect("Dia", sorted(df['Dia'].unique()), default=df['Dia'].unique())

        filtered_df = df[
            df['Matricula'].isin(selected_matriculas) &
            df['Ano'].isin(selected_anos) &
            df['Month'].isin(selected_months) &
            df['Dia'].isin(selected_dias)
        ]

        st.title("📈 Via Verde Dashboard")
        st.write("✅ Dados filtrados:")
        st.dataframe(filtered_df)

        st.write("📌 Resumo estatístico:")
        st.write(filtered_df.describe())
