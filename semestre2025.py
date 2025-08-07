import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px

# Title
st.title("Relatório Interativo - 1º Semestre 2025")

@st.cache_data(ttl=3600)
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/1Semestre2025.xlsx"
    response = requests.get(url)
    df = pd.read_excel(BytesIO(response.content), sheet_name="Dados")
    return df

try:
    df = load_data()
    st.success("✅ Dados carregados com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {e}")
    st.stop()

# Sidebar filters
st.sidebar.header("Filtros")

ano_selecionado = st.sidebar.multiselect("Ano", sorted(df['Ano'].dropna().unique()), default=sorted(df['Ano'].dropna().unique()))
mes_selecionado = st.sidebar.multiselect("Mês", sorted(df['Mês'].dropna().unique()), default=sorted(df['Mês'].dropna().unique()))
artigo_selecionado = st.sidebar.multiselect("Artigo", sorted(df['Artigo'].dropna().unique()), default=sorted(df['Artigo'].dropna().unique()))
comercial_selecionado = st.sidebar.selectbox("Comercial", sorted(df['Comercial'].dropna().unique()))
cliente_selecionado = st.sidebar.selectbox("Cliente", sorted(df['Cliente'].dropna().unique()))

# Apply filters
df_filtrado = df[
    (df['Ano'].isin(ano_selecionado)) &
    (df['Mês'].isin(mes_selecionado)) &
    (df['Artigo'].isin(artigo_selecionado)) &
    (df['Comercial'] == comercial_selecionado) &
    (df['Cliente'] == cliente_selecionado)
]

# Show filtered data
st.subheader("📊 Tabela de Dados Filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# Summary
st.subheader("📌 Resumo")
st.write(f"Total de Registros: {len(df_filtrado)}")
if 'Valor' in df_filtrado.columns:
    st.write(f"Valor Total: €{df_filtrado['Valor'].sum():,.2f}")

# Bar chart: Valor por Mês
if 'Valor' in df_filtrado.columns and 'Mês' in df_filtrado.columns:
    st.subheader("📈 Valor por Mês")
    chart_data = df_filtrado.groupby('Mês')['Valor'].sum().reset_index()
    fig_bar = px.bar(chart_data, x='Mês', y='Valor', title="Valor por Mês")
    st.plotly_chart(fig_bar, use_container_width=True)

# Line Chart 1: Artigo vs Kgs (default)
if 'Artigo' in df_filtrado.columns and 'Kgs' in df_filtrado.columns:
    st.subheader("📉 Linha: Artigo vs Kgs (Padrão)")
    line_data = df_filtrado.groupby('Artigo')['Kgs'].sum().reset_index()
    fig_line1 = px.line(line_data, x='Artigo', y='Kgs', markers=True, title="Artigo vs Kgs")
    st.plotly_chart(fig_line1, use_container_width=True)

    # Line Chart 2: Artigo vs Kgs with red labels
    st.subheader("📉 Linha: Artigo vs Kgs (Etiquetas Vermelhas)")
    fig_line2 = px.line(line_data, x='Artigo', y='Kgs', markers=True, title="Artigo vs Kgs")
    fig_line2.update_layout(
        xaxis_title="Artigo",
        yaxis_title="Kgs",
        font=dict(color="red"),
        xaxis=dict(tickfont=dict(color='red'), titlefont=dict(color='red')),
        yaxis=dict(tickfont=dict(color='red'), titlefont=dict(color='red')),
        title_font=dict(color='red')
    )
    st.plotly_chart(fig_line2, use_container_width=True)

# Download filtered data as Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Filtrado')
    processed_data = output.getvalue()
    return processed_data

excel_data = to_excel(df_filtrado)

st.download_button(
    label="📥 Baixar Dados Filtrados como Excel",
    data=excel_data,
    file_name="dados_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
