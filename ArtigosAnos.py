import streamlit as st
import pandas as pd
import io

# 🖼️ Logo
st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=100)

# 📂 Load Excel data from GitHub
excel_url = 'https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx'
df = pd.read_excel(excel_url, sheet_name='Resumo', engine='openpyxl')

# 🧼 Clean column names
df.columns = df.columns.str.strip().str.upper()

# 🔧 Ensure 'ANO' is numeric
df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce').astype('Int64')

# 🔍 Detect quantity column
quantity_candidates = ['QUANTIDADE', 'QTD', 'TOTAL', 'VALOR']
quantity_col = next((col for col in df.columns if col in quantity_candidates), None)

if quantity_col:

    # 🎛️ Sidebar filters
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

    anos_target = [2023, 2024, 2025]
    anos_disponiveis = df['ANO'].dropna().unique().tolist()
    anos_filtrados = [ano for ano in anos_target if ano in anos_disponiveis]

    selected_ano = st.sidebar.multiselect(
        "Ano (Comparar)",
        options=anos_filtrados,
        default=anos_filtrados
    )

    # 🔍 Apply filters
    filtered_df = df[
        (df['PRODUTO'].isin(selected_produto)) &
        (df['MÊS'].isin(selected_mes)) &
        (df['ANO'].isin(selected_ano))
    ]

    # 📋 Show filtered data
    st.write("### 📋 Dados Filtrados")
    st.dataframe(filtered_df)

    # 📥 Download button for filtered data
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Filtrado')

    st.download_button(
        label="📥 Baixar dados filtrados em Excel",
        data=excel_buffer.getvalue(),
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 📈 Prepare chart
    chart_df = filtered_df[filtered_df['ANO'].isin(selected_ano)]
    pivot_data = chart_df.groupby(['MÊS', 'ANO'])[quantity_col].sum().reset_index()
    pivot_table = pivot_data.pivot(index='MÊS', columns='ANO', values=quantity_col).fillna(0)

    # 📊 Render chart
    st.write("### 📈 Comparação de Quantidades: 2023 vs 2024 vs 2025")
    st.line_chart(pivot_table)

else:
    st.warning("🛑 Nenhuma coluna de quantidade foi encontrada.")
