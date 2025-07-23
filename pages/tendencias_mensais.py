import streamlit as st
import pandas as pd
import altair as alt

# 📄 Page setup
st.set_page_config(page_title="Tendências Mensais", layout="wide")
st.title("📆 Tendências Mensais")

# 📁 Load Data
excel_url = 'https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx'
df = pd.read_excel(excel_url, sheet_name='Resumo', engine='openpyxl')
df.columns = df.columns.str.strip().str.upper()

# 📅 Ensure month order
ordered_months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
df['MÊS'] = pd.Categorical(df['MÊS'], categories=ordered_months, ordered=True)

# 🎛️ Sidebar Filters
st.sidebar.header("Filtros")
produtos = st.sidebar.multiselect("Selecionar Produto", df['PRODUTO'].dropna().unique())
anos = st.sidebar.multiselect("Selecionar Ano", sorted(df['ANO'].dropna().unique()))

filtered_df = df[
    (df['PRODUTO'].isin(produtos)) &
    (df['ANO'].isin(anos))
]

if not filtered_df.empty:
    # 📈 Quantity Trend Chart
    if 'KGS' in filtered_df.columns:
        qty_chart_data = filtered_df.groupby(['MÊS', 'ANO'])['KGS'].sum().reset_index()

        qty_chart = alt.Chart(qty_chart_data).mark_line(point=True).encode(
            x='MÊS:N', y='KGS:Q', color='ANO:N', tooltip=['MÊS', 'ANO', 'KGS']
        ).properties(
            title='📦 Quantidades por Mês',
            width=800, height=400
        )

        st.altair_chart(qty_chart, use_container_width=True)

    # 💸 Price Trend Chart
    if 'PM' in filtered_df.columns:
        price_chart_data = filtered_df.groupby(['MÊS', 'ANO'])['PM'].mean().reset_index()

        price_chart = alt.Chart(price_chart_data).mark_bar().encode(
            x='MÊS:N', y='PM:Q', color='ANO:N', tooltip=['MÊS', 'ANO', 'PM']
        ).properties(
            title='💰 Preço Médio por Mês',
            width=800, height=400
        )

        st.altair_chart(price_chart, use_container_width=True)
else:
    st.info("🔍 Selecione pelo menos um produto e ano com dados disponíveis.")
