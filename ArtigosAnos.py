import streamlit as st
import pandas as pd



# 🖼️ Logo
st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=100)

# 📂 Excel file from GitHub (use RAW .xlsx URL)
excel_url = 'https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx'

# 📄 Load data from 'Resumo' worksheet
df = pd.read_excel(excel_url, sheet_name='Resumo', engine='openpyxl')

# 🧼 Normalize column names
df.columns = df.columns.str.strip().str.upper()

# 🧠 Detect quantity column
quantity_candidates = ['QUANTIDADE', 'QTD', 'TOTAL', 'VALOR']
quantity_col = next((col for col in df.columns if col in quantity_candidates), None)

# 🔧 Sanitize 'ANO' column
df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce').astype('Int64')

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

    # 🎯 Restrict to 2023–2025
    anos_disponiveis = df['ANO'].dropna().unique()
    anos_para_comparar = [ano for ano in [2023, 2024, 2025] if ano in anos_disponiveis]

    selected_ano = st.sidebar.multiselect(
        "Ano (Comparar)",
        options=anos_para_comparar,
        default=anos_para_comparar
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

# ⬇️ Optional Excel download
import io
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name='Filtrado')

st.download_button(
    label="📥 Download dados filtrados em Excel",
    data=excel_buffer.getvalue(),
    file_name="dados_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 📈 Prepare chart data
chart_df = filtered_df[filtered_df['ANO'].isin(anos_para_comparar)]



    # 📈 Prepare chart data
    chart_df = filtered_df[filtered_df['ANO'].isin(anos_para_comparar)]

    # 📊 Group and pivot for comparison
    pivot_data = chart_df.groupby(['MÊS', 'ANO'])[quantity_col].sum().reset_index()
    pivot_table = pivot_data.pivot(index='MÊS', columns='ANO', values=quantity_col).fillna(0)

    # 🖼️ Draw chart
    st.write("### 📈 Comparação de Quantidades: 2023 vs 2024 vs 2025")
    st.line_chart(pivot_table)

else:
    st.warning("🛑 Nenhuma coluna de quantidade foi encontrada.")


