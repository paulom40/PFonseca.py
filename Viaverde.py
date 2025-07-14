import streamlit as st
import pandas as pd

# 🔗 Load Excel file from GitHub
file_url = "https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx"

df = None
try:
    df = pd.read_excel(file_url)
    st.success("✅ Arquivo carregado com sucesso!")

    # Remove unused columns if needed
    df = df.drop(columns=['Date', 'Mês'], errors='ignore')
    st.write("📦 Colunas disponíveis:", df.columns.tolist())
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {e}")

# ⛳ Proceed if loaded successfully
if df is not None:
    required = ['Matricula', 'Ano', 'Month', 'Dia']
    missing = [col for col in required if col not in df.columns]

    if missing:
        st.error(f"⚠️ Faltam colunas obrigatórias: {', '.join(missing)}")
    else:
        # 🎚️ Sidebar filters
        st.sidebar.header("Filtros")
        selected_matricula = st.sidebar.selectbox("Matricula", sorted(df['Matricula'].unique()))   
        selected_anos = st.sidebar.selectbox("Ano", sorted(df['Ano'].unique()))
        selected_anos = st.sidebar.multiselect("Ano", sorted(df['Ano'].unique()), default=df['Ano'].unique())
        selected_months = st.sidebar.multiselect("Month", sorted(df['Month'].unique()), default=df['Month'].unique())
        selected_dias = st.sidebar.multiselect("Dia", sorted(df['Dia'].unique()), default=df['Dia'].unique())

        # 🔍 Apply filters
        filtered_df = df[
        (df['Matricula'] == selected_matricula) &
        (df['Ano'] == selected_ano)) &
        (df['Month'].isin(selected_months)) &
        (df['Dia'].isin(selected_dias))
]

        # 📈 Dashboard output
        st.title("📊 Via Verde Dashboard")
        st.write("✅ Dados filtrados:")
        st.dataframe(filtered_df)

     # 🎨 Line chart: Month vs. Value
st.write("📊 Valor por Mês")

# Make sure the necessary columns are present
if 'Month' in filtered_df.columns and 'Value' in filtered_df.columns:
    chart_data = filtered_df[['Month', 'Value']].groupby('Month').sum().sort_index()
    st.line_chart(chart_data)
else:
    st.warning("⚠️ As colunas 'Month' e 'Value' são necessárias para o gráfico.")
