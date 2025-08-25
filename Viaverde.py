import streamlit as st
import pandas as pd
import altair as alt

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


# 📂 Load Excel file from GitHub
file_url = "https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx"

# 🔷 Header layout
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://github.com/paulom40/PFonseca.py/raw/main/Bracar.png", width=100)
with col2:
    st.title("Via Verde Dashboard")

# 📊 Load and validate data
try:
    df = pd.read_excel(file_url)
    df = df.drop(columns=['Mês'], errors='ignore')
    st.success("✅ Dados carregados com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {e}")
    st.stop()

required_cols = ['Matricula', 'Date', 'Ano', 'Month', 'Dia', 'Value']
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"⚠️ Faltam colunas: {', '.join(missing_cols)}")
    st.stop()

# 🗓️ Normalize month names
month_mapping = {
    'janeiro': 'Janeiro', 'fevereiro': 'Fevereiro', 'março': 'Março', 'abril': 'Abril',
    'maio': 'Maio', 'junho': 'Junho', 'julho': 'Julho', 'agosto': 'Agosto',
    'setembro': 'Setembro', 'outubro': 'Outubro', 'novembro': 'Novembro', 'dezembro': 'Dezembro'
}
df['Month'] = df['Month'].str.lower().map(month_mapping).fillna(df['Month'])

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

st.write("✅ Dados filtrados:")
st.dataframe(filtered_df)

# 📈 First chart: Total value by month
month_order = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

chart_df = (
    filtered_df[['Month', 'Value']]
    .groupby('Month')
    .sum()
    .reset_index()
)

line_chart = alt.Chart(chart_df).mark_line(point=True).encode(
    x=alt.X('Month:O', title='Mês', sort=month_order, axis=alt.Axis(labelFontWeight='bold', titleFontWeight='bold')),
    y=alt.Y('Value:Q', title='Valor Total', axis=alt.Axis(labelFontWeight='bold', titleFontWeight='bold')),
    tooltip=['Month', 'Value']
)

line_labels = alt.Chart(chart_df).mark_text(
    align='center', baseline='bottom', fontWeight='bold', color='red', dy=-5
).encode(
    x=alt.X('Month:O', sort=month_order),
    y='Value:Q',
    text='Value:Q'
)

st.altair_chart((line_chart + line_labels).properties(title='Valor Total por Mês'), use_container_width=True)

# 📅 Weekend data (sábado e domingo)
weekend_df = filtered_df[filtered_df['Dia'].isin(['sábado', 'domingo'])]

st.write("✅ Dados para sábado e domingo:")
if weekend_df.empty:
    st.warning("⚠️ Nenhum dado para sábado ou domingo.")
else:
    st.dataframe(weekend_df)

weekend_chart_df = (
    weekend_df[['Month', 'Value']]
    .groupby('Month')
    .sum()
    .reset_index()
)

weekend_line = alt.Chart(weekend_chart_df).mark_line(point=True).encode(
    x=alt.X('Month:O', title='Mês', sort=month_order, axis=alt.Axis(labelFontWeight='bold', titleFontWeight='bold')),
    y=alt.Y('Value:Q', title='Valor Total (sábado e domingo)', axis=alt.Axis(labelFontWeight='bold', titleFontWeight='bold')),
    tooltip=['Month', 'Value']
)

weekend_labels = alt.Chart(weekend_chart_df).mark_text(
    align='center', baseline='bottom', fontWeight='bold', color='blue', dy=-5
).encode(
    x=alt.X('Month:O', sort=month_order),
    y='Value:Q',
    text='Value:Q'
)

st.altair_chart((weekend_line + weekend_labels).properties(title='Valor Total por Mês (sábado e domingo)'), use_container_width=True)
