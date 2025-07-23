import streamlit as st
import pandas as pd
import io
import altair as alt

st.set_page_config(layout="wide")
st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=100)

# 📂 Load data
excel_url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx"
df = pd.read_excel(excel_url, sheet_name="Resumo", engine="openpyxl")

# 🧼 Clean and normalize data
df.columns = df.columns.str.strip().str.upper()
df['MES'] = df['MÊS'].str.capitalize().str.strip()
df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce').astype('Int64')
df['KGS'] = pd.to_numeric(df['KGS'], errors='coerce')
df['PM'] = pd.to_numeric(df['PM'], errors='coerce')

# 🎛️ Sidebar filters
st.sidebar.header("🔎 Filtros")
produtos = df['PRODUTO'].dropna().unique()
meses = df['MES'].dropna().unique()
anos = sorted(df['ANO'].dropna().unique())

selected_produto = st.sidebar.multiselect("Produto", options=produtos, default=produtos)
selected_mes = st.sidebar.multiselect("Mês", options=meses, default=meses)
selected_ano = st.sidebar.multiselect("Ano", options=anos, default=anos)

# 🔍 Filter data
filtered_df = df[
    (df['PRODUTO'].isin(selected_produto)) &
    (df['MES'].isin(selected_mes)) &
    (df['ANO'].isin(selected_ano))
].copy()

# 📋 Show filtered data
st.write("### 📋 Dados Filtrados")
st.dataframe(filtered_df)

# 🔢 Indicadores
st.write("### 🔢 Indicadores")
if not filtered_df.empty:
    total_kgs = filtered_df['KGS'].sum()
    st.metric("📦 Quantidade Total (KGS)", f"{total_kgs:,.2f}")

    if 'PM' in filtered_df.columns:
        avg_price = filtered_df['PM'].mean()
        st.metric("💰 Preço Médio", f"€{avg_price:,.2f}")
else:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")

# 📥 Download Excel
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name='Filtrado')

st.download_button(
    label="📥 Baixar dados filtrados em Excel",
    data=excel_buffer.getvalue(),
    file_name="dados_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 📈 Line chart for KGS
ordered_months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
chart_df = filtered_df[filtered_df['KGS'].notnull()].copy()
chart_df['MES'] = pd.Categorical(chart_df['MES'], categories=ordered_months, ordered=True)

if not chart_df.empty:
    pivot_data = chart_df.groupby(['MES', 'ANO'])['KGS'].sum().reset_index()

    line_chart = alt.Chart(pivot_data).mark_line(point=True).encode(
        x=alt.X('MES:N', title='Mês', sort=ordered_months),
        y=alt.Y('KGS:Q', title='Quantidade (KGS)'),
        color=alt.Color('ANO:N', title='Ano'),
        tooltip=['MES', 'ANO', 'KGS']
    ).properties(
        title='📈 Evolução de Quantidades por Mês (KGS)',
        width=700,
        height=400
    )

    labels = alt.Chart(pivot_data).mark_text(
    align='center',
    baseline='bottom',
    dy=-5,
    fontSize=11,
    font='Arial',
    color='white'  # 👈 Add this line to make labels white
).encode(
    x='MES:N',
    y='KGS:Q',
    detail='ANO:N',
    text=alt.Text('KGS:Q', format=".0f")
)


    st.altair_chart(line_chart + labels, use_container_width=True)
else:
    st.info("ℹ️ Não há dados de KGS válidos para gerar o gráfico.")

# 💸 Bar chart for PM
if 'PM' in filtered_df.columns and filtered_df['PM'].notnull().any():
    pm_data = filtered_df[filtered_df['PM'].notnull()].copy()
    pm_data['MES'] = pd.Categorical(pm_data['MES'], categories=ordered_months, ordered=True)

    bar_chart = alt.Chart(pm_data.groupby(['MES', 'ANO'])['PM'].mean().reset_index()).mark_bar().encode(
        x=alt.X('MES:N', title='Mês', sort=ordered_months),
        y=alt.Y('PM:Q', title='Preço Médio'),
        color=alt.Color('ANO:N', title='Ano'),
        tooltip=['ANO', 'MES', 'PM']
    ).properties(
        title='💸 Evolução do Preço Médio por Mês',
        width=700,
        height=400
    )

    st.altair_chart(bar_chart, use_container_width=True)
else:
    st.info("ℹ️ Não há dados de PM válidos para gerar o gráfico.")
