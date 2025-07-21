import streamlit as st
import pandas as pd

# 🖼️ Logo
st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=100)

# 📂 Excel file from GitHub
excel_url = 'https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx'

# 📄 Load data
df = pd.read_excel(excel_url, sheet_name='Resumo', engine='openpyxl')

# 🧼 Normalize columns
df.columns = df.columns.str.strip().str.upper()

# 🔧 Sanitize 'ANO' column
df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce').astype('Int64')

# 🧠 Detect quantity column
quantity_candidates = ['QUANTIDADE', 'QTD', 'TOTAL', 'VALOR']
quantity_col = next((col for col in df.columns if col in quantity_candidates), None)

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

    # 🎯 Filter only 2023–2025
    anos_para_comparar = [2023, 2024, 2025]
    anos_disponiveis = df['ANO'].dropna().unique().tolist()
    anos_filtrados = [ano for ano in anos_para_comparar if ano in anos_disponiveis]

    selected_ano = st.sidebar.multiselect(
        "Ano (Comparar)",
        options=anos_filtrados,
        default=anos_filtrados
    )

    # 🧮 Filter the dataset
    filtered_df = df[
        (df['PRODUTO'].isin(selected_produto)) &
        (df['MÊS'].isin(selected_mes)) &
        (df['ANO'].isin(selected_ano))
    ]

    # 🔍 Diagnostic output
    st.write("📌 Anos encontrados nos dados filtrados:", filtered_df['ANO'].unique())

    # 📋 Show filtered data
    st.write("### 📋 Dados Filtrados")
    st.dataframe(filtered_df)

    # 📊 Chart Data
    chart_df = filtered_df[filtered_df['ANO'].isin(selected_ano)]

    pivot_data = chart_df.groupby(['MÊS', 'ANO'])[quantity_col].sum().reset_index()
    pivot_table = pivot_data.pivot(index='MÊS', columns='ANO', values=quantity_col).fillna(0)

    # 🖼️ Line Chart
    st.write("### 📈 Comparação de Quantidades: 2023 vs 2024 vs 2025")
    st.line_chart(pivot_table)

else:
    st.warning("🛑 Nenhuma coluna de quantidade foi encontrada.")
