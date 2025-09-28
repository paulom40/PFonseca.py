import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import requests
from datetime import datetime
import xlsxwriter

# Meses em português
meses_pt = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def obter_numero_mes(nome_mes):
    if not isinstance(nome_mes, str):
        return None
    nome_mes = nome_mes.strip().lower()
    for k, v in meses_pt.items():
        nome_mes_ref = v.lower()
        if nome_mes == nome_mes_ref or nome_mes.startswith(nome_mes_ref[:3]):
            return k
    return None

@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    response = requests.get(url)
    xls = pd.ExcelFile(BytesIO(response.content))
    df = pd.read_excel(xls, sheet_name=0)
    df.columns = df.columns.str.strip()

    if 'Mês' not in df.columns:
        st.error("❌ A coluna 'Mês' não foi encontrada no ficheiro.")
        st.stop()

    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df = df.dropna(subset=['Mês'])
    df['Mês'] = df['Mês'].astype(int)

    if 'Data' not in df.columns:
        df['Data'] = pd.to_datetime(dict(year=df['Ano'], month=df['Mês'], day=1), errors='coerce')

    df = df.dropna(subset=['Data', 'Qtd.', 'Cliente', 'Artigo'])
    return df

df = load_data()

tab1, tab2 = st.tabs(["📊 Comparativo Ano a Ano", "🔎 Filtro por Artigo e Cliente"])

# -------------------- TAB 1 --------------------
with tab1:
    st.title("📊 Comparativo Ano a Ano")

    with st.sidebar:
        st.markdown("### 🔍 Filtros")
        meses_disponiveis = sorted(df['Mês'].dropna().unique())
        nomes_meses = [meses_pt.get(int(m), f"Mês {m}") for m in meses_disponiveis]

        if nomes_meses:
            mes_selecionado_label = st.selectbox("Selecionar Mês", nomes_meses, key="month1")
            mes_selecionado = obter_numero_mes(mes_selecionado_label)
            if mes_selecionado is None:
                st.error(f"❌ Mês '{mes_selecionado_label}' não reconhecido.")
                st.stop()
            else:
                st.success(f"✅ Mês reconhecido: {mes_selecionado_label} → {mes_selecionado}")
        else:
            st.warning("⚠️ Nenhum mês disponível nos dados.")
            st.stop()

        clientes = st.multiselect("Filtrar por Cliente", sorted(df['Cliente'].unique()), key="cliente1")
        artigos = st.multiselect("Filtrar por Artigo", sorted(df['Artigo'].unique()), key="artigo1")

    df_filtrado = df[df['Mês'] == mes_selecionado]
    if clientes:
        df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes)]
    if artigos:
        df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(artigos)]

    ano_atual = df_filtrado['Ano'].max()
    ano_passado = ano_atual - 1
    df_comparativo = df_filtrado[df_filtrado['Ano'].isin([ano_passado, ano_atual])]

    agrupado = df_comparativo.groupby(['Cliente', 'Artigo', 'Ano'])['Qtd.'].sum().reset_index()
    tabela = agrupado.pivot_table(index=['Cliente', 'Artigo'], columns='Ano', values='Qtd.', fill_value=0).reset_index()
    tabela['Diferença'] = tabela.get(ano_atual, 0) - tabela.get(ano_passado, 0)

    st.subheader(f"Mês: {mes_selecionado_label} | {ano_passado} vs {ano_atual}")
    st.dataframe(tabela, use_container_width=True)

    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Comparativo')
        return output.getvalue()

    excel_data = to_excel(tabela)
    st.download_button("📥 Exportar Comparativo para Excel", data=excel_data, file_name="Comparativo_YoY.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# -------------------- TAB 2 --------------------
with tab2:
    st.subheader("🔎 Filtro por Artigo, Cliente e Mês")

    meses_disponiveis2 = sorted(df['Mês'].dropna().unique())
    nomes_meses2 = [meses_pt.get(int(m), f"Mês {m}") for m in meses_disponiveis2]

    if nomes_meses2:
        mes_label2 = st.selectbox("Selecionar Mês", nomes_meses2, key="month2")
        mes2 = obter_numero_mes(mes_label2)
        if mes2 is None:
            st.error(f"❌ Mês '{mes_label2}' não reconhecido.")
            st.stop()
        else:
            st.success(f"✅ Mês reconhecido: {mes_label2} → {mes2}")
    else:
        st.warning("⚠️ Nenhum mês disponível nos dados.")
        st.stop()

    cliente2 = st.multiselect("Selecionar Cliente", sorted(df['Cliente'].unique()), key="cliente2")
    artigo2 = st.multiselect("Selecionar Artigo", sorted(df['Artigo'].unique()), key="artigo2")

    df_tab2 = df[df['Mês'] == mes2]
    if cliente2:
        df_tab2 = df_tab2[df_tab2['Cliente'].isin(cliente2)]
    if artigo2:
        df_tab2 = df_tab2[df_tab2['Artigo'].isin(artigo2)]

    st.write(f"Resultados para o mês de {mes_label2}")
    st.dataframe(df_tab2[['Data', 'Cliente', 'Artigo', 'Qtd.']], use_container_width=True)

    st.markdown("### 📌 Totais por Cliente")
    totais_cliente = df_tab2.groupby('Cliente')['Qtd.'].sum().reset_index().sort_values(by='Qtd.', ascending=False)
    st.dataframe(totais_cliente, use_container_width=True)

    st.markdown("### 📌 Totais por Artigo")
    totais_artigo = df_tab2.groupby('Artigo')['Qtd.'].sum().reset_index().sort_values(by='Qtd.', ascending=False)
    st.dataframe(totais_artigo, use_container_width=True)

    st.markdown("### 📊 Gráfico de Vendas por Artigo")
    st.bar_chart(totais_artigo.set_index('Artigo'))

    def exportar_excel_completo(dados_df, cliente_df, artigo_df, nome_mes, mes_num):
        output = BytesIO()
        logo_url = "https://github.com/paulom40/PFonseca.py/raw/main/Bracar.png"
        logo_data = requests.get(logo_url).content

        variacoes = dados_df.groupby(['Cliente', 'Artigo', 'Mês'])['Qtd.'].sum().reset_index()
        variacoes_pivot = variacoes.pivot_table(index=['Cliente', 'Artigo'], columns='Mês', values='Qtd.', fill_value=0).reset_index()

        if 'Comercial' in dados_df.columns:
            variacoes_comercial = dados_df.groupby(['Comercial', 'Cliente', 'Mês'])['Qtd.'].sum().reset_index()
            variacoes_comercial_pivot = variacoes_comercial.pivot_table(index=['Comercial', 'Cliente'], columns='Mês', values='Qtd.', fill_value=0).reset_index()
        else:
            variacoes_comercial_pivot = pd.DataFrame({'Aviso': ['Coluna "Comercial" não encontrada nos dados.']})

        mes_anterior = mes_num - 1 if mes_num > 1 else 12
        todos_clientes = sorted(df['Cliente'].unique())
        clientes_ativos = sorted(df[df['Mês'] == mes_anterior]['Cliente'].unique())
