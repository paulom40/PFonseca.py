import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# Title
st.title("📈 Relatório Interativo - KPIs do 1º Semestre 2025")

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
comercial_selecionado = st.sidebar.multiselect("Comercial", sorted(df['Comercial'].dropna().unique()), default=sorted(df['Comercial'].dropna().unique()))
cliente_selecionado = st.sidebar.multiselect("Cliente", sorted(df['Cliente'].dropna().unique()), default=sorted(df['Cliente'].dropna().unique()))

# Apply filters
df_filtrado = df[
    (df['Ano'].isin(ano_selecionado)) &
    (df['Mês'].isin(mes_selecionado)) &
    (df['Artigo'].isin(artigo_selecionado)) &
    (df['Comercial'].isin(comercial_selecionado)) &
    (df['Cliente'].isin(cliente_selecionado))
]

# Show filtered data
st.subheader("📊 Tabela de Dados Filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# Summary
st.subheader("📌 Resumo")
st.write(f"Total de Registros: {len(df_filtrado)}")
if 'Valor' in df_filtrado.columns:
    st.write(f"Valor Total: €{df_filtrado['Valor'].sum():,.2f}")

# KPIs by Mês
st.header("📌 KPIs Mensais")

for mes in sorted(df_filtrado['Mês'].dropna().unique()):
    st.subheader(f"📅 Mês: {mes}")

    df_mes = df_filtrado[df_filtrado['Mês'] == mes]

    # Top 5 Artigos
    if 'Artigo' in df_mes.columns and 'Kgs' in df_mes.columns:
        top_artigos = df_mes.groupby('Artigo')['Kgs'].sum().sort_values(ascending=False).head(5)
        st.markdown("**Top 5 Artigos (por Kgs):**")
        st.dataframe(top_artigos.reset_index(), use_container_width=True)

    # Top 5 Clientes
    if 'Cliente' in df_mes.columns and 'Kgs' in df_mes.columns:
        top_clientes = df_mes.groupby('Cliente')['Kgs'].sum().sort_values(ascending=False).head(5)
        st.markdown("**Top 5 Clientes (por Kgs):**")
        st.dataframe(top_clientes.reset_index(), use_container_width=True)

    # Top 5 Comerciais
    if 'Comercial' in df_mes.columns and 'Kgs' in df_mes.columns:
        top_comerciais = df_mes.groupby('Comercial')['Kgs'].sum().sort_values(ascending=False).head(3)
        st.markdown("**Top 5 Comerciais (por Kgs):**")
        st.dataframe(top_comerciais.reset_index(), use_container_width=True)

    # Top 5 Artigos by Categoria
    if 'Categoria' in df_mes.columns and 'Artigo' in df_mes.columns and 'Kgs' in df_mes.columns:
        st.markdown("**Top 5 Artigos por Categoria (por Kgs):**")
        categorias = df_mes['Categoria'].dropna().unique()
        for cat in categorias:
            df_cat = df_mes[df_mes['Categoria'] == cat]
            top_art_cat = df_cat.groupby('Artigo')['Kgs'].sum().sort_values(ascending=False).head(5)
            st.markdown(f"🔹 Categoria: {cat}")
            st.dataframe(top_art_cat.reset_index(), use_container_width=True)

# Excel download
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
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
