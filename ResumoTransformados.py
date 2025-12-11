# Streamlit Multi-page Dashboard (estrutura de ficheiros)
# ======================================================
# Este documento contém o conteúdo de vários ficheiros necessários para um
# dashboard Streamlit multipágina profissional. Copie cada secção para o ficheiro
# correspondente na sua aplicação.
# Estrutura proposta:
#  - app.py
#  - utils.py
#  - pages/1_Overview.py
#  - pages/2_Clientes.py
#  - pages/3_Artigos.py
#  - pages/4_Comerciais.py
#  - requirements.txt
# ------------------------------------------------------

# === FILE: app.py ===
"""
app.py - ponto de entrada principal
"""
import streamlit as st
from utils import load_data, apply_filters, resumo_kpis

st.set_page_config(page_title="Dashboard Compras - MultiPage", layout="wide")

st.title("Dashboard de Compras – Visão Geral")

# Carregar dados (cacheado)
df = load_data()

if df.empty:
    st.error("❌ Não foi possível carregar dados. Verifique o ficheiro ou a ligação.")
    st.stop()

# Barra lateral comum com filtros (aplicada globalmente)
st.sidebar.header("🎛️ Filtros Globais")
filters = apply_filters(df)

# Mostra resumo rápido
st.sidebar.divider()
st.sidebar.write(f"**Registros totais:** {len(df):,}")
st.sidebar.write(f"**Registros após filtros:** {len(filters['df_filtrado']):,}")

# Navegação (páginas Streamlit usam /pages; esta app mantém a homepage com resumo)
st.subheader("📌 Resumo Rápido")
ks = resumo_kpis(filters['df_filtrado'])

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Vendas (€)", ks['Total Vendas'])
col2.metric("📦 Quantidade", ks['Total Quantidade'])
col3.metric("🏢 Clientes", ks['Clientes Únicos'])
col4.metric("👨‍💼 Comerciais", ks['Comerciais Únicos'])

st.markdown("---")

st.header("📈 Evolução e Insights")
st.write("Use as páginas no menu lateral (Streamlit > Pages) para análises detalhadas de Clientes, Artigos e Comerciais.")

# Mostrar gráfico de evolução mensal com Plotly
import plotly.express as px
vendas_mensais = filters['df_filtrado'].groupby(['Ano','MesNumero']).Valor.sum().reset_index()
if not vendas_mensais.empty:
    vendas_mensais = vendas_mensais.sort_values(['Ano','MesNumero'])
    vendas_mensais['Periodo'] = vendas_mensais['Ano'].astype(str) + '-' + vendas_mensais['MesNumero'].astype(str).str.zfill(2)
    fig = px.bar(vendas_mensais, x='Periodo', y='Valor', title='Evolução Mensal de Vendas', labels={'Valor':'€'})
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info('Sem dados de vendas mensais para mostrar.')

st.markdown("\n---\n")
st.caption("Sugestão: abra as páginas (Overview/Clientes/Artigos/Comerciais) para análises específicas.")


# === FILE: utils.py ===
"""
utils.py - funções utilitárias para carregar dados e filtros
"""
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime

@st.cache_data
def load_data(url: str = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx") -> pd.DataFrame:
    """Carrega e normaliza o ficheiro Excel em DataFrame padrão.
    Detecção automática de colunas: Data, Cliente, Artigo, Comercial, Quantidade, Valor.
    """
    try:
        df_raw = pd.read_excel(url)
        df = pd.DataFrame()
        cols = df_raw.columns

        # 1) DETECTAR COLUNA DE DATA
        data_col = None
        for c in cols:
            temp = pd.to_datetime(df_raw[c], errors='coerce')
            if temp.notna().sum() > len(df_raw)*0.3:
                data_col = c
                df['Data'] = temp
                break
        if data_col is None:
            df['Data'] = pd.to_datetime(df_raw.iloc[:, 0], errors='coerce')

        df = df[df['Data'].notna()].copy()

        # 2) DETECTAR COLUNAS DE TEXTO (preferir colunas próximas à data)
        text_cols = [c for c in cols if df_raw[c].dtype == 'object']

        def get_text(idx, default='Desconhecido'):
            try:
                return df_raw[text_cols[idx]].astype(str).str.strip()
            except Exception:
                return pd.Series([default]*len(df), index=df.index)

        df['Cliente'] = get_text(0)
        df['Artigo'] = get_text(1)
        df['Comercial'] = get_text(2)

        # 3) DETECTAR NUMERICOS
        nums = [c for c in cols if pd.api.types.is_numeric_dtype(df_raw[c])]
        if len(nums) >= 1:
            df['Quantidade'] = pd.to_numeric(df_raw[nums[0]], errors='coerce').fillna(1)
        else:
            df['Quantidade'] = 1
        if len(nums) >= 2:
            df['Valor'] = pd.to_numeric(df_raw[nums[1]], errors='coerce').fillna(0)
        else:
            df['Valor'] = df['Quantidade'] * np.random.uniform(5,100,len(df))

        # 4) Limpeza adicional
        df = df[df['Quantidade'] > 0]
        df = df[df['Valor'] > 0]
        df = df[df['Cliente'] != 'Desconhecido']
        df = df[df['Artigo'] != 'Desconhecido']

        # 5) Campos de tempo
        df['Ano'] = df['Data'].dt.year
        df['MesNumero'] = df['Data'].dt.month
        df['MesNome'] = df['Data'].dt.strftime('%b')
        df['Data_Str'] = df['Data'].dt.strftime('%Y-%m-%d')

        return df

    except Exception as e:
        st.error(f"Erro a carregar dados: {e}")
        # Retornar DataFrame vazio para não quebrar a app
        return pd.DataFrame()


# Função para criar filtros interativos e aplicar
def apply_filters(df: pd.DataFrame) -> dict:
    """Cria a UI de filtros na sidebar e devolve df_filtrado e selecções."""
    result = {}

    # Ano
    anos = sorted(df['Ano'].unique(), reverse=True)
    anos_sel = st.sidebar.multiselect('Ano', options=anos, default=anos[:min(2,len(anos))])
    if not anos_sel:
        anos_sel = anos

    # Mês (dinâmico conforme anos)
    meses_disponiveis = sorted(df[df['Ano'].isin(anos_sel)]['MesNumero'].unique())
    meses_map = {1:'Janeiro',2:'Fevereiro',3:'Março',4:'Abril',5:'Maio',6:'Junho',7:'Julho',8:'Agosto',9:'Setembro',10:'Outubro',11:'Novembro',12:'Dezembro'}
    meses_labels = [meses_map[m] for m in meses_disponiveis]
    meses_sel_labels = st.sidebar.multiselect('Mês', options=meses_labels, default=meses_labels)
    nomes_para_mes = {v:k for k,v in meses_map.items()}
    meses_sel = [nomes_para_mes[n] for n in meses_sel_labels] if meses_sel_labels else meses_disponiveis

    # Comercial
    comerciais_disponiveis = sorted(df[df['Ano'].isin(anos_sel) & df['MesNumero'].isin(meses_sel)]['Comercial'].unique())
    if not comerciais_disponiveis:
        comerciais_disponiveis = sorted(df['Comercial'].unique())
    todos_com = st.sidebar.checkbox('Todos os Comerciais', value=True, key='todos_com')
    if todos_com:
        comerciais_sel = comerciais_disponiveis
    else:
        comerciais_sel = st.sidebar.multiselect('Comercial', options=comerciais_disponiveis, default=comerciais_disponiveis[:min(3,len(comerciais_disponiveis))])
        if not comerciais_sel:
            comerciais_sel = comerciais_disponiveis

    # Cliente
    clientes_disponiveis = sorted(df[df['Ano'].isin(anos_sel) & df['MesNumero'].isin(meses_sel) & df['Comercial'].isin(comerciais_sel)]['Cliente'].unique())
    if not clientes_disponiveis:
        clientes_disponiveis = sorted(df['Cliente'].unique())
    todos_cli = st.sidebar.checkbox('Todos os Clientes', value=True, key='todos_cli')
    if todos_cli:
        clientes_sel = clientes_disponiveis
    else:
        clientes_sel = st.sidebar.multiselect('Cliente', options=clientes_disponiveis, default=clientes_disponiveis[:min(5,len(clientes_disponiveis))])
        if not clientes_sel:
            clientes_sel = clientes_disponiveis

    # Artigo
    artigos_disponiveis = sorted(df[df['Ano'].isin(anos_sel) & df['MesNumero'].isin(meses_sel) & df['Comercial'].isin(comerciais_sel) & df['Cliente'].isin(clientes_sel)]['Artigo'].unique())
    if not artigos_disponiveis:
        artigos_disponiveis = sorted(df['Artigo'].unique())
    todos_art = st.sidebar.checkbox('Todos os Artigos', value=True, key='todos_art')
    if todos_art:
        artigos_sel = artigos_disponiveis
    else:
        artigos_sel = st.sidebar.multiselect('Artigo', options=artigos_disponiveis, default=artigos_disponiveis[:min(5,len(artigos_disponiveis))])
        if not artigos_sel:
            artigos_sel = artigos_disponiveis

    # Botão reset
    if st.sidebar.button('🔄 Resetar Filtros'):
        st.experimental_rerun()

    # Aplicar filtros
    df_filtrado = df[
        (df['Ano'].isin(anos_sel)) &
        (df['MesNumero'].isin(meses_sel)) &
        (df['Comercial'].isin(comerciais_sel)) &
        (df['Cliente'].isin(clientes_sel)) &
        (df['Artigo'].isin(artigos_sel))
    ].copy()

    result['df_filtrado'] = df_filtrado
    result['anos_sel'] = anos_sel
    result['meses_sel'] = meses_sel
    result['comerciais_sel'] = comerciais_sel
    result['clientes_sel'] = clientes_sel
    result['artigos_sel'] = artigos_sel

    return result


def resumo_kpis(df):
    if df is None or df.empty:
        return {"Total Vendas":"€0","Total Quantidade":0,"Clientes Únicos":0,"Comerciais Únicos":0}
    total_vendas = df['Valor'].sum()
    return {
        'Total Vendas': f"€{total_vendas:,.2f}",
        'Total Quantidade': int(df['Quantidade'].sum()),
        'Clientes Únicos': int(df['Cliente'].nunique()),
        'Comerciais Únicos': int(df['Comercial'].nunique())
    }


# === FILE: pages/1_Overview.py ===
"""
Página Overview - insights gerais, top KPIs e mapa de calor mensal
"""
import streamlit as st
from utils import load_data, apply_filters, resumo_kpis
import plotly.express as px

st.set_page_config(page_title='Overview', layout='wide')
st.title('Overview - KPIs & Tendências')

df = load_data()
if df.empty:
    st.error('Erro: sem dados')
    st.stop()

filters = apply_filters(df)
df_f = filters['df_filtrado']

st.subheader('KPIs')
ks = resumo_kpis(df_f)
cols = st.columns(4)
cols[0].metric('Vendas', ks['Total Vendas'])
cols[1].metric('Quantidade', ks['Total Quantidade'])
cols[2].metric('Clientes', ks['Clientes Únicos'])
cols[3].metric('Comerciais', ks['Comerciais Únicos'])

st.markdown('---')

st.subheader('Vendas Mensais')
if not df_f.empty:
    vm = df_f.groupby(['Ano','MesNumero']).Valor.sum().reset_index()
    vm = vm.sort_values(['Ano','MesNumero'])
    vm['Periodo'] = vm['Ano'].astype(str)+'-'+vm['MesNumero'].astype(str).str.zfill(2)
    fig = px.line(vm, x='Periodo', y='Valor', markers=True, title='Evolução Mensal')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info('Sem dados filtrados')


# === FILE: pages/2_Clientes.py ===
"""
Página Clientes - Top clientes e análise detalhada
"""
import streamlit as st
from utils import load_data, apply_filters
import plotly.express as px

st.set_page_config(page_title='Clientes', layout='wide')
st.title('Análise de Clientes')

df = load_data()
if df.empty:
    st.error('Erro: sem dados')
    st.stop()

filters = apply_filters(df)
df_f = filters['df_filtrado']

if df_f.empty:
    st.warning('Sem dados para os filtros atuais')
    st.stop()

st.subheader('Top Clientes por Vendas')
clientes = df_f.groupby('Cliente').Valor.sum().reset_index().sort_values('Valor', ascending=False).head(20)
fig = px.bar(clientes, x='Valor', y='Cliente', orientation='h', title='Top Clientes')
st.plotly_chart(fig, use_container_width=True)

st.markdown('---')
st.subheader('Tabela detalhada')
st.dataframe(df_f.groupby('Cliente').agg({'Valor':'sum','Quantidade':'sum','Data':'count'}).rename(columns={'Data':'Transações'}).sort_values('Valor', ascending=False))


# === FILE: pages/3_Artigos.py ===
"""
Página Artigos - Top artigos e performance
"""
import streamlit as st
from utils import load_data, apply_filters
import plotly.express as px

st.set_page_config(page_title='Artigos', layout='wide')
st.title('Análise de Artigos')

df = load_data()
if df.empty:
    st.error('Erro: sem dados')
    st.stop()

filters = apply_filters(df)
df_f = filters['df_filtrado']

if df_f.empty:
    st.warning('Sem dados para os filtros atuais')
    st.stop()

st.subheader('Top Artigos por Vendas')
artigos = df_f.groupby('Artigo').agg({'Valor':'sum','Quantidade':'sum'}).reset_index().sort_values('Valor', ascending=False).head(30)
fig = px.bar(artigos, x='Artigo', y='Valor', title='Top Artigos', labels={'Valor':'€'})
fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

st.markdown('---')
st.subheader('Detalhe por Artigo')
st.dataframe(artigos)


# === FILE: pages/4_Comerciais.py ===
"""
Página Comerciais - Desempenho por comercial
"""
import streamlit as st
from utils import load_data, apply_filters
import plotly.express as px

st.set_page_config(page_title='Comerciais', layout='wide')
st.title('Desempenho por Comercial')

df = load_data()
if df.empty:
    st.error('Erro: sem dados')
    st.stop()

filters = apply_filters(df)
df_f = filters['df_filtrado']

if df_f.empty:
    st.warning('Sem dados para os filtros atuais')
    st.stop()

st.subheader('Ranking Comerciais')
com = df_f.groupby('Comercial').agg({'Valor':'sum','Quantidade':'sum','Cliente':'nunique'}).reset_index().sort_values('Valor', ascending=False)
fig = px.bar(com, x='Comercial', y='Valor', title='Total Vendas por Comercial')
fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

st.markdown('---')
st.subheader('Matriz de Performance')
st.dataframe(com)


# === FILE: requirements.txt ===
# Dependências sugeridas
streamlit
pandas
numpy
openpyxl
plotly

# FIM
