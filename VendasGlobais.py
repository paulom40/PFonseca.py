import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import requests
import xlsxwriter

# Load Excel from GitHub
@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    response = requests.get(url)
    xls = pd.ExcelFile(BytesIO(response.content))
    df = pd.read_excel(xls, sheet_name=0)
    return df

df = load_data()

# Parse and clean
df['Data'] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
df['Ano'] = df['Data'].dt.year
df['Mes'] = df['Data'].dt.month
df = df.dropna(subset=['Data', 'Qtd.', 'Cliente', 'Artigo'])

# Tabs
tab1, tab2 = st.tabs(["📊 Year-over-Year Comparison", "🔎 Artigo & Cliente Filter"])

# -------------------- TAB 1 --------------------
with tab1:
    st.title("📊 Year-over-Year Comparison")

    # Sidebar filters
    with st.sidebar:
        st.markdown("### 🔍 Filters")
        selected_month = st.selectbox("Select Month", sorted(df['Mes'].unique()), key="month1")
        clientes = st.multiselect("Filter by Cliente", sorted(df['Cliente'].unique()), key="cliente1")
        artigos = st.multiselect("Filter by Artigo", sorted(df['Artigo'].unique()), key="artigo1")

    # Apply filters
    df_filtered = df[df['Mes'] == selected_month]
    if clientes:
        df_filtered = df_filtered[df_filtered['Cliente'].isin(clientes)]
    if artigos:
        df_filtered = df_filtered[df_filtered['Artigo'].isin(artigos)]

    # Compare current vs last year
    current_year = df_filtered['Ano'].max()
    last_year = current_year - 1
    df_compare = df_filtered[df_filtered['Ano'].isin([last_year, current_year])]

    grouped = df_compare.groupby(['Cliente', 'Artigo', 'Ano'])['Qtd.'].sum().reset_index()
    pivoted = grouped.pivot_table(index=['Cliente', 'Artigo'], columns='Ano', values='Qtd.', fill_value=0).reset_index()
    pivoted['Diferença'] = pivoted.get(current_year, 0) - pivoted.get(last_year, 0)

    # Color-coded display
    def highlight_diff(val):
        if val > 0:
            return 'background-color: #d4f4dd'
        elif val < 0:
            return 'background-color: #fddddd'
        return ''

    styled_df = pivoted.style.applymap(highlight_diff, subset=['Diferença'])

    st.subheader(f"Month: {selected_month} | {last_year} vs {current_year}")
    st.dataframe(styled_df, use_container_width=True)

    # Export to Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Comparativo')
            workbook = writer.book
            worksheet = writer.sheets['Comparativo']
            diff_col = df.columns.get_loc('Diferença')
            format_pos = workbook.add_format({'bg_color': '#d4f4dd'})
            format_neg = workbook.add_format({'bg_color': '#fddddd'})
            worksheet.conditional_format(1, diff_col, len(df), diff_col, {
                'type': 'cell',
                'criteria': '>',
                'value': 0,
                'format': format_pos
            })
            worksheet.conditional_format(1, diff_col, len(df), diff_col, {
                'type': 'cell',
                'criteria': '<',
                'value': 0,
                'format': format_neg
            })
        return output.getvalue()

    excel_data = to_excel(pivoted)
    st.download_button("📥 Export to Excel", data=excel_data, file_name="Comparativo_YoY.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# -------------------- TAB 2 --------------------
with tab2:
    st.subheader("🔎 Filter by Artigo, Cliente, and Month")

    selected_month2 = st.selectbox("Select Month", sorted(df['Mes'].unique()), key="month2")
    selected_cliente2 = st.multiselect("Select Cliente", sorted(df['Cliente'].unique()), key="cliente2")
    selected_artigo2 = st.multiselect("Select Artigo", sorted(df['Artigo'].unique()), key="artigo2")

    df_tab2 = df[df['Mes'] == selected_month2]
    if selected_cliente2:
        df_tab2 = df_tab2[df_tab2['Cliente'].isin(selected_cliente2)]
    if selected_artigo2:
        df_tab2 = df_tab2[df_tab2['Artigo'].isin(selected_artigo2)]

    st.write(f"Showing results for Month {selected_month2}")
    st.dataframe(df_tab2[['Data', 'Cliente', 'Artigo', 'Qtd.']], use_container_width=True)

    # Totals by Cliente
    st.markdown("### 📌 Totals by Cliente")
    cliente_totals = df_tab2.groupby('Cliente')['Qtd.'].sum().reset_index().sort_values(by='Qtd.', ascending=False)
    st.dataframe(cliente_totals, use_container_width=True)

    # Totals by Artigo
    st.markdown("### 📌 Totals by Artigo")
    artigo_totals = df_tab2.groupby('Artigo')['Qtd.'].sum().reset_index().sort_values(by='Qtd.', ascending=False)
    st.dataframe(artigo_totals, use_container_width=True)

    # Bar chart
    st.markdown("### 📊 Artigo Sales Chart")
    st.bar_chart(artigo_totals.set_index('Artigo'))
