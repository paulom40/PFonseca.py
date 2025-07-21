import streamlit as st
import pandas as pd

# 📂 Excel file from GitHub (use RAW .xlsx URL)
excel_url = 'https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx'

# 📄 Load data from 'Resumo' worksheet
df = pd.read_excel(excel_url, sheet_name='Resumo', engine='openpyxl')

# 🧼 Normalize column names
df.columns = df.columns.str.strip().str.upper()

# 🪪 Show available columns for debugging (optional)
# st.write("🔍 Available columns:", df.columns.tolist())

# 🧠 Try to detect the quantity column automatically
quantity_candidates = ['QUANTIDADE', 'QTD', 'TOTAL', 'VALOR']
quantity_col = next((col for col in df.columns if col in quantity_candidates), None)

# ✅ Proceed only if quantity column is found
if quantity_col:

    # 🧭 Sidebar Filters
    st.sidebar.header("🔎 Filtros")
    selected_produto = st.sidebar.multiselect(
        "Produto", options=df['PRODUTO'].dropna().unique(), default=df['PRODUTO'].dropna().unique()
    )
    selected_mes = st.sidebar.multiselect(
        "Mês", options=df['MÊS'].dropna().unique(), default=df['MÊS'].dropna().unique()
    )
    selected_ano = st.sidebar.multiselect(
        "Ano", options=df['ANO'].dropna().unique(), default=df['ANO'].dropna().unique()
    )

    # 🧮 Filter the dataset
    filtered_df = df[
        df['PRODUTO'].isin(selected_produto) &
        df['MÊS'].isin(selected_mes) &
        df['ANO'].isin(selected_ano)
    ]

    # 📋 Show filtered data
    st.write("### 📋 Dados Filtrados")
    st.dataframe(filtered_df)

    # 📈 Prepare chart data
    chart_data = (
        filtered_df.groupby(['ANO', 'MÊS'])[quantity_col]
        .sum()
        .reset_index()
    )
    chart_data['LABEL'] = chart_data['ANO'].astype(str) + '-' + chart_data['MÊS'].astype(str)

    # 🖼️ Draw chart
    st.write("### 📈 Gráfico de Linhas")
    st.line_chart(chart_data.set_index('LABEL')[quantity_col])

else:
    st.error("🚫 Nenhuma coluna de quantidade encontrada. Verifique os nomes na folha 'Resumo'.")
