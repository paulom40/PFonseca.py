# dashboard_pro.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import requests
import warnings
warnings.filterwarnings("ignore")

# =============================================
# CONFIG & ESTILO
# =============================================
st.set_page_config(page_title="BI Pro", layout="wide", page_icon="📊")
st.markdown("""
<style>
    .main {background:#f8fafc; padding:2rem}
    h1 {color:#1e293b; font-size:2.6rem; font-weight:800; text-align:center}
    [data-testid="stSidebar"] {background:linear-gradient(#4f46e5,#7c3aed); border-radius:0 20px 20px 0; padding:2rem}
    .stSelectbox > div > div {background:white !important; border:2px solid #e2e8f0 !important; border-radius:12px !important}
    .stSelectbox span, .stSelectbox input {color:#1e293b !important}
    [data-testid="metric-container"] {background:white; border-radius:16px; padding:1.5rem; box-shadow:0 6px 25px rgba(0,0,0,0.1)}
    .plotly-graph-div {border-radius:18px; overflow:hidden; box-shadow:0 8px 30px rgba(0,0,0,0.12)}
    .filter-section {background:white; padding:1rem; border-radius:12px; margin-bottom:1rem; border:1px solid #e2e8f0}
</style>
""", unsafe_allow_html=True)

# =============================================
# CARREGAMENTO SIMPLIFICADO
# =============================================
month_map = {'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,
             'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}

@st.cache_data(ttl=3600)
def load_data():
    try:
        url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        df = pd.read_excel(BytesIO(response.content))
        st.info(f"📥 Dados carregados: {len(df)} registros")
        
        # Padronizar colunas
        df.columns = [col.strip().lower() for col in df.columns]
        column_mapping = {
            'mês': 'mes', 'qtd.': 'qtd', 'v. líquido': 'v_liquido',
            'v.líquido': 'v_liquido', 'v_líquido': 'v_liquido'
        }
        df.rename(columns=column_mapping, inplace=True)
        
        # Converter dados
        if 'mes' in df.columns:
            df['mes'] = df['mes'].astype(str).str.strip().str.lower()
            df['mes_num'] = df['mes'].map(month_map)
            df['mes_nome'] = df['mes']
        
        if 'ano' in df.columns:
            df['ano'] = pd.to_numeric(df['ano'], errors='coerce').fillna(2024).astype(int)
        
        # Converter quantidades e valores
        for col in ['qtd', 'v_liquido']:
            if col in df.columns:
                df[col] = df[col].astype(str)
                df[col] = df[col].str.replace(r'[^\d,\.\-]', '', regex=True)
                df[col] = df[col].str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Limpeza
        df = df[(df['qtd'].notna()) & (df['v_liquido'].notna()) & (df['cliente'].notna())].copy()
        
        st.success("🎉 Dados carregados com sucesso!")
        return df

    except Exception as e:
        st.error(f"❌ Erro no carregamento: {str(e)}")
        return pd.DataFrame()

# Carregar dados
with st.spinner('📥 Carregando dados...'):
    df = load_data()

if df.empty: 
    st.error("Não foi possível carregar os dados.")
    st.stop()

# =============================================
# INICIALIZAR SESSION STATE
# =============================================
def initialize_session_state():
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            'ano': "Todos",
            'comercial': "Todos", 
            'cliente': "Todos",
            'categoria': "Todas"
        }
    if 'data_filtered' not in st.session_state:
        st.session_state.data_filtered = df

initialize_session_state()

# =============================================
# FUNÇÕES PARA FILTROS DINÂMICOS
# =============================================
def get_available_options(base_data, current_filters):
    """Retorna opções disponíveis baseadas nos filtros atuais"""
    temp_data = base_data.copy()
    
    # Aplicar filtros sequencialmente
    if current_filters['ano'] != "Todos":
        temp_data = temp_data[temp_data['ano'] == current_filters['ano']]
    
    if current_filters['comercial'] != "Todos":
        temp_data = temp_data[temp_data['comercial'] == current_filters['comercial']]
    
    if current_filters['cliente'] != "Todos":
        temp_data = temp_data[temp_data['cliente'] == current_filters['cliente']]
    
    if current_filters['categoria'] != "Todas" and 'categoria' in temp_data.columns:
        temp_data = temp_data[temp_data['categoria'] == current_filters['categoria']]
    
    return {
        'anos': ["Todos"] + sorted(temp_data['ano'].unique().tolist()),
        'comerciais': ["Todos"] + sorted(temp_data['comercial'].unique().tolist()),
        'clientes': ["Todos"] + sorted(temp_data['cliente'].unique().tolist()),
        'categorias': ["Todas"] + sorted(temp_data.get('categoria', pd.Series()).dropna().unique().tolist())
    }

def apply_filters(data, filters):
    """Aplica filtros aos dados"""
    filtered_data = data.copy()
    
    if filters['ano'] != "Todos":
        filtered_data = filtered_data[filtered_data['ano'] == filters['ano']]
    
    if filters['comercial'] != "Todos":
        filtered_data = filtered_data[filtered_data['comercial'] == filters['comercial']]
    
    if filters['cliente'] != "Todos":
        filtered_data = filtered_data[filtered_data['cliente'] == filters['cliente']]
    
    if filters['categoria'] != "Todas" and 'categoria' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['categoria'] == filters['categoria']]
    
    return filtered_data

# =============================================
# SIDEBAR COM FILTROS
# =============================================
with st.sidebar:
    st.markdown("<h2 style='color:white'>BI Pro</h2>", unsafe_allow_html=True)
    
    # Navegação
    page = st.radio("Navegação", [
        "Visão Geral", "KPIs", "Comparação", "Clientes", "Análise Detalhada"
    ])
    
    st.markdown("---")
    st.markdown("### 🔧 Filtros")
    
    # Obter opções disponíveis baseadas nos filtros atuais
    available_options = get_available_options(df, st.session_state.filters)
    
    # Filtro de Ano
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    novo_ano = st.selectbox(
        "📅 Ano",
        options=available_options['anos'],
        index=available_options['anos'].index(st.session_state.filters['ano']) 
        if st.session_state.filters['ano'] in available_options['anos'] else 0,
        key='ano_selectbox'
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Atualizar filtro de ano se mudou
    if novo_ano != st.session_state.filters['ano']:
        st.session_state.filters['ano'] = novo_ano
        st.session_state.filters['comercial'] = "Todos"
        st.session_state.filters['cliente'] = "Todos"
        st.rerun()
    
    # Recalcular opções após possível mudança no ano
    available_options = get_available_options(df, st.session_state.filters)
    
    # Filtro de Comercial
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    novo_comercial = st.selectbox(
        "👨‍💼 Comercial", 
        options=available_options['comerciais'],
        index=available_options['comerciais'].index(st.session_state.filters['comercial']) 
        if st.session_state.filters['comercial'] in available_options['comerciais'] else 0,
        key='comercial_selectbox'
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Atualizar filtro de comercial se mudou
    if novo_comercial != st.session_state.filters['comercial']:
        st.session_state.filters['comercial'] = novo_comercial
        st.session_state.filters['cliente'] = "Todos"
        st.rerun()
    
    # Recalcular opções após possível mudança no comercial
    available_options = get_available_options(df, st.session_state.filters)
    
    # Filtro de Cliente
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    novo_cliente = st.selectbox(
        "🏢 Cliente",
        options=available_options['clientes'],
        index=available_options['clientes'].index(st.session_state.filters['cliente']) 
        if st.session_state.filters['cliente'] in available_options['clientes'] else 0,
        key='cliente_selectbox'
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Atualizar filtro de cliente se mudou
    if novo_cliente != st.session_state.filters['cliente']:
        st.session_state.filters['cliente'] = novo_cliente
        st.rerun()
    
    # Recalcular opções após possível mudança no cliente
    available_options = get_available_options(df, st.session_state.filters)
    
    # Filtro de Categoria (se existir)
    if 'categoria' in df.columns:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        nova_categoria = st.selectbox(
            "📦 Categoria",
            options=available_options['categorias'],
            index=available_options['categorias'].index(st.session_state.filters['categoria']) 
            if st.session_state.filters['categoria'] in available_options['categorias'] else 0,
            key='categoria_selectbox'
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if nova_categoria != st.session_state.filters['categoria']:
            st.session_state.filters['categoria'] = nova_categoria
            st.rerun()
    
    # Botão para limpar filtros
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    if st.button("🔄 Limpar Todos os Filtros", use_container_width=True, key='clear_filters'):
        st.session_state.filters = {
            'ano': "Todos",
            'comercial': "Todos", 
            'cliente': "Todos",
            'categoria': "Todas"
        }
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# APLICAR FILTROS AOS DADOS
# =============================================
# Aplicar filtros atuais (isso roda a cada renderização)
data_filtrada = apply_filters(df, st.session_state.filters)

# =============================================
# FUNÇÕES DE FORMATAÇÃO
# =============================================
def formatar_numero_europeu(numero, casas_decimais=2):
    if pd.isna(numero) or numero == 0:
        return "0" if casas_decimais == 0 else "0,00"
    try:
        if casas_decimais == 0:
            formatted = f"{numero:,.0f}"
        else:
            formatted = f"{numero:,.{casas_decimais}f}"
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0" if casas_decimais == 0 else "0,00"

def fmt_valor(x): return f"€ {formatar_numero_europeu(x, 2)}"
def fmt_quantidade(x): 
    return f"{formatar_numero_europeu(x, 0)}" if pd.notna(x) and x == int(x) else f"{formatar_numero_europeu(x, 2)}"
def fmt_percentual(x): return f"{x:.2f}%".replace(".", ",") if not pd.isna(x) and not np.isinf(x) else "0,00%"

# =============================================
# PÁGINAS PRINCIPAIS
# =============================================
if page == "Visão Geral":
    st.markdown("<h1>📊 Visão Geral</h1>", unsafe_allow_html=True)
    
    # Mostrar filtros ativos
    filtros_ativos = []
    for key, value in st.session_state.filters.items():
        if value != "Todos" and value != "Todas":
            filtros_ativos.append(f"{key}: {value}")
    
    if filtros_ativos:
        st.info(f"🔍 **Filtros ativos:** {', '.join(filtros_ativos)}")
    
    # Métricas principais
    total_qtd = data_filtrada['qtd'].sum()
    total_valor = data_filtrada['v_liquido'].sum()
    total_clientes = data_filtrada['cliente'].nunique()
    total_comerciais = data_filtrada['comercial'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Quantidade Total", fmt_quantidade(total_qtd), "kg")
    with col2: st.metric("Valor Total", fmt_valor(total_valor))
    with col3: st.metric("Total de Clientes", f"{total_clientes:,}")
    with col4: st.metric("Comerciais Ativos", f"{total_comerciais:,}")
    
    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        if not data_filtrada.empty:
            vendas_comercial = data_filtrada.groupby('comercial')['v_liquido'].sum().nlargest(10)
            if not vendas_comercial.empty:
                fig = px.bar(vendas_comercial, title="Top Comerciais por Valor")
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not data_filtrada.empty:
            vendas_cliente = data_filtrada.groupby('cliente')['v_liquido'].sum().nlargest(10)
            if not vendas_cliente.empty:
                fig = px.bar(vendas_cliente, title="Top Clientes por Valor")
                st.plotly_chart(fig, use_container_width=True)

elif page == "KPIs":
    st.markdown("<h1>📈 KPIs e Métricas</h1>", unsafe_allow_html=True)
    
    if not data_filtrada.empty:
        total_vendas = data_filtrada['v_liquido'].sum()
        media_venda = data_filtrada['v_liquido'].mean()
        ticket_medio = total_vendas / len(data_filtrada) if len(data_filtrada) > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Total de Vendas", fmt_valor(total_vendas))
        with col2: st.metric("Média por Venda", fmt_valor(media_venda))
        with col3: st.metric("Ticket Médio", fmt_valor(ticket_medio))

elif page == "Comparação":
    st.markdown("<h1>📊 Comparação</h1>", unsafe_allow_html=True)
    
    anos_disponiveis = sorted(data_filtrada['ano'].unique())
    
    if len(anos_disponiveis) >= 2:
        col1, col2 = st.columns(2)
        with col1: ano1 = st.selectbox("Ano 1", anos_disponiveis, key="ano1")
        with col2: 
            outros_anos = [a for a in anos_disponiveis if a != ano1]
            ano2 = st.selectbox("Ano 2", outros_anos if outros_anos else anos_disponiveis, key="ano2")
        
        # Dados para comparação
        dados_ano1 = apply_filters(df, {**st.session_state.filters, 'ano': ano1})
        dados_ano2 = apply_filters(df, {**st.session_state.filters, 'ano': ano2})
        
        # Métricas
        qtd_ano1, qtd_ano2 = dados_ano1['qtd'].sum(), dados_ano2['qtd'].sum()
        valor_ano1, valor_ano2 = dados_ano1['v_liquido'].sum(), dados_ano2['v_liquido'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric(f"Qtd {ano1}", fmt_quantidade(qtd_ano1))
        with col2: st.metric(f"Qtd {ano2}", fmt_quantidade(qtd_ano2))
        with col3: st.metric(f"Valor {ano1}", fmt_valor(valor_ano1))
        with col4: st.metric(f"Valor {ano2}", fmt_valor(valor_ano2))

elif page == "Clientes":
    st.markdown("<h1>👥 Análise de Clientes</h1>", unsafe_allow_html=True)
    
    if not data_filtrada.empty:
        analise_clientes = data_filtrada.groupby('cliente').agg({
            'v_liquido': ['sum', 'count', 'mean'],
            'qtd': 'sum'
        }).round(2)
        analise_clientes.columns = ['Total Vendas', 'Nº Transações', 'Ticket Médio', 'Quantidade Total']
        analise_clientes = analise_clientes.sort_values('Total Vendas', ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            top_clientes = analise_clientes.head(10)
            fig = px.bar(top_clientes, y=top_clientes.index, x='Total Vendas', 
                        title="Top 10 Clientes por Valor", orientation='h')
            st.plotly_chart(fig, use_container_width=True)

elif page == "Análise Detalhada":
    st.markdown("<h1>🔍 Análise Detalhada</h1>", unsafe_allow_html=True)
    
    if not data_filtrada.empty:
        st.subheader("📈 Estatísticas")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Valor:**")
            st.write(f"- Média: {fmt_valor(data_filtrada['v_liquido'].mean())}")
            st.write(f"- Máximo: {fmt_valor(data_filtrada['v_liquido'].max())}")
        with col2:
            st.write("**Quantidade:**")
            st.write(f"- Média: {fmt_quantidade(data_filtrada['qtd'].mean())}")
            st.write(f"- Máximo: {fmt_quantidade(data_filtrada['qtd'].max())}")

# =============================================
# RESUMO NO SIDEBAR
# =============================================
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📈 Resumo")
    
    qtd_total = data_filtrada['qtd'].sum()
    valor_total = data_filtrada['v_liquido'].sum()
    
    st.markdown(f"**Período:** {data_filtrada['ano'].min()}-{data_filtrada['ano'].max()}")
    st.markdown(f"**Valor:** {fmt_valor(valor_total)}")
    st.markdown(f"**Quantidade:** {fmt_quantidade(qtd_total)}")
    st.markdown(f"**Clientes:** {data_filtrada['cliente'].nunique():,}")
    st.markdown(f"**Registros:** {len(data_filtrada):,}")

st.sidebar.markdown("---")
st.sidebar.markdown("🔄 *Filtros dinâmicos ativos*")
