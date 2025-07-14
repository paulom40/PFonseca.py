import streamlit as st
import pandas as pd
import altair as alt

# 📂 File URL
file_url = "https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx"

# 🚀 Load data
try:
    df = pd.read_excel(file_url)
    df = df.drop(columns=['Date', 'Mês'], errors='ignore')
    st.success("✅ Dados carregados com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {e}")
    st.stop()

# ✅ Required columns check
required_cols = ['Matricula', 'Ano', 'Month', 'Dia', 'Value']
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"⚠️ Faltam colunas: {', '.join(missing_cols)}")
    st.stop()

# 🎛️ Sidebar filters
st.sidebar.header("Filtros")
selected_matricula = st.sidebar.selectbox("Matricula", sorted(df['Matricula'].unique()))
selected_ano = st.sidebar.selectbox("Ano", sorted(df['Ano'].unique()))
selected_months = st.sidebar.multiselect("Month", sorted(df['Month'].unique()), default=df['Month'].unique())
selected_dias = st.sidebar.multiselect("Dia", sorted(df['Dia'].unique()), default=df['Dia'].unique())

# 🔍 Apply filters
filtered_df = df[
    (df['Matricula'] == selected_matricula) &
    (df['Ano'] == selected_ano) &
    (df['Month'].isin(selected_months)) &
    (df['Dia'].isin(selected_dias))
]

# 📊 Dashboard display
st.title("📈 Via Verde Dashboard")
st.write("✅ Dados filtrados:")
st.dataframe(filtered_df)

chart_df = (
    filtered_df[['Month', 'Value']]
    .groupby('Month')
    .sum()
    .reset_index()
    .sort_values(by='Month')
)

chart = alt.Chart(chart_df).mark_line(point=True).encode(
    x=alt.X('Month:O', title='Mês', axis=alt.Axis(labelFontWeight='bold', titleFontWeight='bold')),
    y=alt.Y('Value:Q', title='Valor Total', axis=alt.Axis(labelFontWeight='bold', titleFontWeight='bold')),
    tooltip=['Month', 'Value']
).properties(
    title='Valor Total por Mês',
    width='container'
)

st.altair_chart(chart, use_container_width=True)
