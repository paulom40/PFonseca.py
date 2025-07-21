import streamlit as st
import pandas as pd

st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=100)

# 📂 Excel file from GitHub (use RAW .xlsx URL)
excel_url = 'https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx'

# 📄 Load data from 'Resumo' worksheet
df = pd.read_excel(excel_url, sheet_name='Resumo', engine='openpyxl')

# 🧼 Normalize column names
df.columns = df.columns.str.strip().str.upper()

# ✅ Display column names for debugging (optional)
# st.write("🔍 Available columns:", df.columns.tolist())

# 🧠 Try to detect the quantity column automatically
quantity_candidates = ['QUANTIDADE', 'QTD', 'TOTAL', 'VALOR']
quantity_col = next((col for col in df.columns if col in quantity_candidates), None)

# ✅ Proceed only if quantity column is found
if quantity_col:

    # 🧭 Sidebar Filters
    st.sidebar.header("🔎 Filtros")

    selected_produto = st.sidebar.multiselect(
        "Produto",
        options=df['PRODUTO'].dropna().unique(),
        default=df['PRODUTO'].dropna().unique()
    )

    selected_mes = st.sidebar.multiselect(
        "Mês",
        options=df['MÊS'].dropna().unique(),
        default=df['MÊS'].dropna().unique()
    )

    # 🎯 Filter only the years you're interested in
ano_opcoes = [ano for ano in [2023, 2024, 2025] if ano in df['ANO'].dropna().unique()]

selected_ano = st.sidebar.multiselect(
    "Ano (Comparar)",
    options=ano_opcoes,
    default=ano_opcoes
)


    # 🧮 Filter the dataset
    filtered_df = df[
        (df['PRODUTO'].isin(selected_produto)) &
        (df['MÊS'].isin(selected_mes)) &
        (df['ANO'].isin(selected_ano))
    ]

    # 📋 Show filtered data
    st.write("### 📋 Dados Filtrados")
    st.dataframe(filtered_df)

    # 📈 Prepare chart data
    years_to_compare = [2023, 2024, 2025]
    chart_df = filtered_df[filtered_df['ANO'].isin(years_to_compare)]

    # 📊 Group and pivot for multi-year comparison
    pivot_data = chart_df.groupby(['MÊS', 'ANO'])[quantity_col].sum().reset_index()
    pivot_table = pivot_data.pivot(index='MÊS', columns='ANO', values=quantity_col).fillna(0)

    # 🖼️ Draw multi-line comparison chart
    st.write("### 📈 Comparação de Quantidades: 2023 vs 2024 vs 2025")
    st.line_chart(pivot_table)

else:
    st.warning("🛑 Nenhuma coluna de quantidade foi encontrada.")
