import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import matplotlib.pyplot as plt

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
    chart_data = df_filtrado.groupby('Mês')['Valor'].sum().sort_index()
    st.bar_chart(chart_data)

# Line Chart 1: Artigo vs Kgs (default)
if 'Artigo' in df_filtrado.columns and 'Kgs' in df_filtrado.columns:
    st.subheader("📉 Linha: Artigo vs Kgs (Padrão)")
    line_data = df_filtrado.groupby('Artigo')['Kgs'].sum().sort_index()
    st.line_chart(line_data)

# Line Chart 2: Artigo vs Kgs with red labels
    st.subheader("📉 Linha: Artigo vs Kgs (Etiquetas Vermelhas)")
    fig, ax = plt.subplots()
    ax.plot(line_data.index, line_data.values, marker='o', color='blue')
    ax.set_xlabel("Artigo", color='red')
    ax.set_ylabel("Kgs", color='red')
    ax.tick_params(axis='x', colors='red')
    ax.tick_params(axis='y', colors='red')
    ax.set_title("Artigo vs Kgs", color='red')
    plt.xticks(rotation=45)
    st.pyplot(fig)

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
