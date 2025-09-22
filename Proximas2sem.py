import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import BytesIO
import base64

# Layout mobile
st.set_page_config(layout="centered")
st.markdown("<style>div.block-container{padding-top:1rem;padding-bottom:1rem}</style>", unsafe_allow_html=True)
st.title("📱 Dashboard de Vencimentos")

# Carregar dados
url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"
df = pd.read_excel(url)

# Padronizar nomes de colunas
df.rename(columns=lambda x: x.strip(), inplace=True)

# Detectar colunas principais
venc_col = next((col for col in df.columns if 'venc' in col.lower()), None)
valor_pendente_col = next((col for col in df.columns if 'valor pendente' in col.lower()), None)
entidade_col = next((col for col in df.columns if 'entidade' in col.lower()), None)
cliente_col = next((col for col in df.columns if 'cliente' in col.lower()), None)
valor_col = next((col for col in df.columns if 'valor' in col.lower() and 'pendente' not in col.lower()), None)

# Validar coluna de vencimento
if venc_col is None:
    st.error("❌ Nenhuma coluna de vencimento encontrada.")
    st.stop()
df[venc_col] = pd.to_datetime(df[venc_col], errors='coerce')

# Sidebar: filtro por comercial com opção "Todos"
with st.sidebar:
    st.header("🔍 Filtro por Comercial")
    comerciais = df['Comercial'].dropna().unique() if 'Comercial' in df.columns else []
    comercial_selecionado = st.selectbox("Selecione o comercial", ["Todos"] + list(comerciais))

# Aplicar filtro se necessário
if comercial_selecionado != "Todos":
    df = df[df['Comercial'] == comercial_selecionado]

# Verificar se há dados após o filtro
if df.empty:
    st.warning(f"⚠️ Nenhum dado encontrado para o comercial '{comercial_selecionado}'.")
    st.stop()

# Detectar datas futuras
datas_validas = df[venc_col].dropna().dt.date
datas_futuras = datas_validas[datas_validas >= datetime.today().date()]
base_date = datas_futuras.min() if not datas_futuras.empty else datas_validas.min()

# Intervalos dinâmicos
week1_start = base_date
week1_end = week1_start + timedelta(days=6)
week2_start = week1_end + timedelta(days=1)
week2_end = week2_start + timedelta(days=6)

# Filtro por semana
df_week1 = df[(df[venc_col].dt.date >= week1_start) & (df[venc_col].dt.date <= week1_end)]
df_week2 = df[(df[venc_col].dt.date >= week2_start) & (df[venc_col].dt.date <= week2_end)]

# Cartão fixo com intervalos
st.markdown(f"""
<style>
.fixed-card {{
    position: sticky;
    top: 0;
    z-index: 999;
    background-color: #f0f8ff;
    padding: 1rem;
    border-radius: 8px;
    border-left: 5px solid #4682B4;
    margin-bottom: 1rem;
}}
</style>
<div class="fixed-card">
    <h4 style="margin-top:0">📅 Intervalos com base nos dados disponíveis</h4>
    <ul style="padding-left:1rem">
        <li><strong>🗓 Semana 1:</strong> {week1_start.strftime('%d/%m/%Y')} → {week1_end.strftime('%d/%m/%Y')}</li>
        <li><strong>🗓 Semana 2:</strong> {week2_start.strftime('%d/%m/%Y')} → {week2_end.strftime('%d/%m/%Y')}</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Função para exportar gráfico
def export_figure(fig, filename):
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">📥 Baixar gráfico como imagem</a>'
    st.markdown(href, unsafe_allow_html=True)

# Abas
tab1, tab2 = st.tabs(["📋 Resumo", "📊 Gráficos"])

# 📋 RESUMO
with tab1:
    st.subheader("Totais por Cliente (Top 5 + Outros)")
    if cliente_col and valor_col:
        resumo_week1 = df_week1.groupby(cliente_col)[valor_col].sum().rename('Semana 1')
        resumo_week2 = df_week2.groupby(cliente_col)[valor_col].sum().rename('Semana 2')
        resumo_total = pd.concat([resumo_week1, resumo_week2], axis=1).fillna(0)
        resumo_total['Total'] = resumo_total['Semana 1'] + resumo_total['Semana 2']
        resumo_total = resumo_total.sort_values(by='Total', ascending=False)

        # Agrupar os menores como "Outros"
        top_n = 5
        top_clientes = resumo_total.head(top_n)
        outros = resumo_total.iloc[top_n:].sum()
        if outros['Total'] > 0:
            outros_df = pd.DataFrame({
                'Semana 1': [outros['Semana 1']],
                'Semana 2': [outros['Semana 2']],
                'Total': [outros['Total']]
            }, index=['Outros'])
            resumo_total = pd.concat([top_clientes, outros_df])

        st.dataframe(resumo_total.style.format({
            'Semana 1': '€ {:,.2f}',
            'Semana 2': '€ {:,.2f}',
            'Total': '€ {:,.2f}'
        }), use_container_width=True)
    else:
        st.info("ℹ️ Dados insuficientes para gerar a tabela resumo.")

    st.subheader("📋 Valor Pendente por Comercial")
    if valor_pendente_col and 'Comercial' in df.columns:
        resumo_pendente = df.groupby('Comercial')[valor_pendente_col].sum().sort_values(ascending=False)
        st.dataframe(resumo_pendente.reset_index().style.format({valor_pendente_col: '€ {:,.2f}'}), use_container_width=True)

    st.subheader("📋 Valor Pendente por Entidade — Semana 1")
    if entidade_col and valor_pendente_col and not df_week1.empty:
        resumo_entidade_sem1 = df_week1.groupby(entidade_col)[valor_pendente_col].sum().sort_values(ascending=False)
        st.dataframe(resumo_entidade_sem1.reset_index().style.format({valor_pendente_col: '€ {:,.2f}'}), use_container_width=True)

    st.subheader("📋 Valor Pendente por Entidade — Semana 2")
    if entidade_col and valor_pendente_col and not df_week2.empty:
        resumo_entidade_sem2 = df_week2.groupby(entidade_col)[valor_pendente_col].sum().sort_values(ascending=False)
        st.dataframe(resumo_entidade_sem2.reset_index().style.format({valor_pendente_col: '€ {:,.2f}'}), use_container_width=True)

# 📊 GRÁFICOS
with tab2:
    st.subheader("Visualização por Cliente")
    chart_type = st.radio("Tipo de gráfico:", ["Barra comparativa", "Pizza total"], horizontal=True)
    df_combined = pd.concat([df_week1, df_week2])

    if cliente_col and valor_col:
        if chart_type == "Barra comparativa":
            df_week1_chart = df_week1.groupby(cliente_col)[valor_col].sum().rename('Semana 1')
            df_week2_chart = df_week2.groupby(cliente_col)[valor_col].sum().rename('Semana 2')
            chart_df = pd.concat([df_week1_chart, df_week2_chart], axis=1).fillna(0)
            chart_df['Total'] = chart_df['Semana 1'] + chart_df['Semana 2']
            chart_df = chart_df.sort_values(by='Total', ascending=False).drop(columns='Total')

            # Agrupar menores como "Outros"
            top_n = 5
            top_chart = chart_df.head(top_n)
            outros = chart_df.iloc[top_n:].sum()
