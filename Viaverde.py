import streamlit as st
import pandas as pd
import os

# 📁 File path
file_path = "https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx"

# 🧮 Attempt to load the file safely
df = None
try:
    if os.path.exists("https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx"):
        df = pd.read_excel("https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx")
        # Optional: Preview column names
        st.success("✅ Arquivo carregado com sucesso!")
        st.write("🔍 Colunas disponíveis:", df.columns.tolist())

        # Remove 'Date' and 'Mês' columns if they exist
        df = df.drop(columns=['Date', 'Mês'], errors='ignore')
    else:
        st.error(f"❌ Arquivo não encontrado: {file_path}")
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {e}")

# 🚦 Continue only if data is loaded
if df is not None:
    # Confirm required columns exist
    required_columns = ['Matricula', 'Ano', 'Month', 'Dia']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"❌ As seguintes colunas estão faltando: {', '.join(missing_columns)}")
    else:
        # 🎛️ Sidebar Filters
        st.sidebar.header("Filtros")

        selected_matriculas = st.sidebar.multiselect("Matricula", sorted(df['Matricula'].unique()), default=df['Matricula'].unique())
        selected_anos = st.sidebar.multiselect("Ano", sorted(df['Ano'].unique()), default=df['Ano'].unique())
        selected_meses = st.sidebar.multiselect("Month", sorted(df['Month'].unique()), default=df['Month'].unique())
        selected_dias = st.sidebar.multiselect("Dia", sorted(df['Dia'].unique()), default=df['Dia'].unique())

        # 🎯 Apply filters
        filtered_df = df[
            df['Matricula'].isin(selected_matriculas) &
            df['Ano'].isin(selected_anos) &
            df['Month'].isin(selected_meses) &
            df['Dia'].isin(selected_dias)
        ]

        # 🧩 Main Dashboard Display
        st.title("📈 Via Verde Dashboard")
        st.write("✅ Dados filtrados:")
        st.dataframe(filtered_df)

        st.write("📌 Resumo estatístico:")
        st.write(filtered_df.describe())

