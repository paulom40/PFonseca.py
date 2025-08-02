import streamlit as st
import pandas as pd
import altair as alt

# 📂 File URL
file_url = "https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx"

# Create top layout
col1, col2 = st.columns([1, 5])  # Adjust width ratio as needed

with col1:
    st.image("https://github.com/paulom40/PFonseca.py/raw/main/Bracar.png", width=100)  # Local file or URL

with col2:
    st.title("Via Verde Dashboard")

# 🚀 Load data
try:
    df = pd.read_excel(file_url)
    df = df.drop(columns=['Mês'], errors='ignore')
    st.success("✅ Dados carregados com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {e}")
    st.stop()

# ✅ Required columns check
required_cols = ['Matricula', 'Date', 'Ano', 'Month', 'Dia', 'Value']
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
st.write("✅ Dados filtrados:")
st.dataframe(filtered_df)

# Prepare data for first line chart
chart_df = (
    filtered_df[['Month', 'Value']]
    .groupby('Month')
    .sum()
    .reset_index()
)

# Define month order in Portuguese
month_order = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

# First line chart with bold axis labels and ordered months
line = alt.Chart(chart_df).mark_line(point=True).encode(
    x=alt.X('Month:O', title='Mês', sort=month_order, axis=alt.Axis(labelFontWeight='bold', titleFontWeight='bold')),
    y=alt.Y('Value:Q', title='Valor Total', axis=alt.Axis(labelFontWeight='bold', titleFontWeight='bold')),
    tooltip=['Month', 'Value']
)

# Add text labels at each point
labels = alt.Chart(chart_df).mark_text(
    align='center',
    baseline='bottom',
    fontWeight='bold',
    color='red',
    dy=-5  # shift upward for clarity
).encode(
    x=alt.X('Month:O', sort=month_order),
    y='Value:Q',
    text='Value:Q'
)

# Combine both charts
chart = line + labels

# Render first line chart
st.altair_chart(chart.properties(title='Valor Total por Mês'), use_container_width=True)

# Filter data for Sábado and Domingo
weekend_df = filtered_df[filtered_df['Dia'].isin(['Sábado', 'Domingo'])]

# Display table for Sábado and Domingo
st.write("✅ Dados para Sábado e Domingo:")
st.dataframe(weekend_df)

# Prepare data for second line chart (Sábado and Domingo)
weekend_chart_df = (
    weekend_df[['Month', 'Value']]
    .groupby('Month')
    .sum()
    .reset_index()
)

# Debug: Display weekend_chart_df to verify Month values
st.write("✅ Dados para o segundo gráfico (sábado e domingo):")
st.dataframe(weekend_chart_df)

# Second line chart for Sábado and Domingo
weekend_line = alt.Chart(weekend_chart_df).mark_line(point=True).encode(
    x=alt.X('Month:O', title='Mês', sort=month_order, axis=alt.Axis(labelFontWeight='bold', titleFontWeight='bold')),
    y=alt.Y('Value:Q', title='Valor Total (Sábado e Domingo)', axis=alt.Axis(labelFontWeight='bold', titleFontWeight='bold')),
    tooltip=['Month', 'Value']
)

# Add text labels for second chart
weekend_labels = alt.Chart(weekend_chart_df).mark_text(
    align='center',
    baseline='bottom',
    fontWeight='bold',
    color='blue',  # Changed to blue for distinction
    dy=-5  # shift upward for clarity
).encode(
    x=alt.X('Month:O', sort=month_order),
    y='Value:Q',
    text='Value:Q'
)

# Combine second chart
weekend_chart = weekend_line + weekend_labels

# Render second line chart
st.altair_chart(weekend_chart.properties(title='Valor Total por Mês (Sábado e Domingo)'), use_container_width=True)
