import streamlit as st
import pandas as pd

# URL of the raw Excel file on GitHub
excel_url = 'https://raw.githubusercontent.com/yourusername/yourrepo/main/Artigos_totais%20ANOS.xlsx'

# Load the Excel file (specific worksheet: "Resumo")
df = pd.read_excel(excel_url, sheet_name='Resumo', engine='openpyxl')

# Sidebar filters
st.sidebar.header("🔎 Filters")
selected_produto = st.sidebar.multiselect("Produto", options=df['Produto'].unique(), default=df['Produto'].unique())
selected_mes = st.sidebar.multiselect("Mês", options=df['Mês'].unique(), default=df['Mês'].unique())
selected_ano = st.sidebar.multiselect("Ano", options=df['Ano'].unique(), default=df['Ano'].unique())

# Filter data
filtered_df = df[
    (df['Produto'].isin(selected_produto)) &
    (df['Mês'].isin(selected_mes)) &
    (df['Ano'].isin(selected_ano))
]

# Display filtered data in a table
st.write("### 📋 Filtered Data")
st.dataframe(filtered_df)

# Line chart
st.write("### 📈 Line Chart")
chart_data = filtered_df.groupby(['Ano', 'Mês'])['Quantidade'].sum().reset_index()

# Create a label for X-axis
chart_data['Label'] = chart_data['Ano'].astype(str) + '-' + chart_data['Mês'].astype(str)

st.line_chart(chart_data.set_index('Label')['Quantidade'])
