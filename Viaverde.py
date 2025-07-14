import streamlit as st
import pandas as pd
import altair as alt

# 🔗 Load Excel file from GitHub
file_url = "https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx"

# Read and clean the data
df = None
try:
    df = pd.read_excel(file_url)
    st.success("✅ Arquivo carregado com sucesso!")

    # Drop unused columns
    df = df.drop(columns=['Date', 'Mês'], errors='ignore')
    st.write("📦 Colunas disponíveis:", df.columns.tolist())
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {e}")

# Proceed only if DataFrame is loaded
if df is not None:
    required_columns = ['Matricula', 'Ano', 'Month', 'Dia', 'Value']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"⚠️ Faltam colunas obrigatórias: {', '.join(missing_columns)}")
    else:
        # 🎚️ Sidebar filters
        st.sidebar.header("Filtros")

        selected_matricula = st.sidebar.selectbox("Matricula", sorted(df['Matricula'].unique()))
        selected_ano = st.sidebar.selectbox("Ano", sorted(df['Ano'].unique()))
        selected_months = st.sidebar.multiselect("Month", sorted(df['Month'].unique()), default=df['Month'].unique())
        selected_dias = st.sidebar.multiselect("Dia", sorted(df['Dia'].unique()), default=df['Dia'].unique())

        # 🔍 Filter data
        filtered_df = df[
            (df['Matricula'] == selected_matricula) &
            (df['Ano'] == selected_ano) &
            (df['Month'].isin(selected_months)) &
            (df['Dia'].isin(selected_dias))
        ]

        # 📊 Display filtered results
        st.title("📈 Via Verde Dashboard")
        st.write("✅ Dados filtrados:")
        st.dataframe(filtered_df)

        # Prepare data for chart
chart_df = (
    filtered_df[['Month', 'Value']]
    .groupby('Month')
    .sum()
    .reset_index()
    .sort_values(by='Month')
)

# Create labeled line chart
line_chart = alt.Chart(chart_df).mark_line(point=True).encode(
    x=alt.X('Month:O', title='Mês'),
    y=alt.Y('Value:Q', title='Valor Total'),
    tooltip=['Month', 'Value']
).properties(
    title='Valor Total por Mês'
)

st.altair_chart(line_chart, use_container_width=True)
