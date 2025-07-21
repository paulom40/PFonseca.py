import streamlit as st
import pandas as pd

# 📂 URL of the raw Excel file from GitHub
excel_url = 'https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx'
# 📄 Load and normalize worksheet columns
df = pd.read_excel(excel_url, sheet_name='Resumo', engine='openpyxl')
df.columns = df.columns.str.strip().str.upper()  # Clean column names

# 🪟 Sidebar filters
st.sidebar.header("🔎 Filtros")
selected_produto = st.sidebar.multiselect("Produto", options=df['PRODUTO'].dropna().unique(), default=df['PRODUTO'].dropna().unique())
selected_mes = st.sidebar.multiselect("Mês", options=df['MÊS'].dropna().unique(), default=df['MÊS'].dropna().unique())
selected_ano = st.sidebar.multiselect("Ano", options=df['ANO'].dropna().unique(), default=df['ANO'].dropna().unique())

# 🧮 Filter the data
filtered_df = df[
    (df['PRODUTO'].isin(selected_produto)) &
    (df['MÊS'].isin(selected_mes)) &
    (df['ANO'].isin(selected_ano))
]

# 📊 Display filtered data
st.write("### 📋 Dados Filtrados")
st.dataframe(filtered_df)

# 📈 Create line chart
chart_data = filtered_df.groupby(['ANO', 'MÊS'])['QUANTIDADE'].sum().reset_index()
chart_data['LABEL'] = chart_data['ANO'].astype(str) + '-' + chart_data['MÊS'].astype(str)

st.write("### 📈 Gráfico de Linhas")
st.line_chart(chart_data.set_index('LABEL')['QUANTIDADE'])
