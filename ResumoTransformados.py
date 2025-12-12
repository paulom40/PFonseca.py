import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime, timedelta
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Dashboard Compras - Análise Premium",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# CSS personalizado com gradientes
st.markdown("""
<style>
    /* Gradiente principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    /* Cards de métricas com gradiente */
    .stMetric {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        border: none;
        color: white !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.2);
    }
    
    .stMetric label {
        font-weight: 600 !important;
        color: white !important;
        font-size: 0.9rem !important;
        opacity: 0.9;
    }
    
    .stMetric div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: white !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    }
    
    /* Tabs estilizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #1a1a2e;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #2c3e50 0%, #4a6491 100%);
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        color: white;
        border: none;
        transition: all 0.3s;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar gradiente */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Botões com gradiente */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Filtros */
    .stSelectbox, .stMultiselect, .stDateInput {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 5px;
    }
    
    /* Hover effects para tabelas */
    .dataframe tr:hover {
        background: rgba(102, 126, 234, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# Header com gradiente
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.5rem;">📊 DASHBOARD DE COMPRAS</h1>
    <p style="margin:0; opacity:0.9; font-size:1.1rem;">Análise Avançada e Visualização em Tempo Real</p>
</div>
""", unsafe_allow_html=True)

# === CARREGAR DADOS COM COLUNAS CORRETAS ===
@st.cache_data
def load_data():
    try:
        # Lendo do arquivo Excel
        df = pd.read_excel("ResumoTR.xlsx")
        
        # Renomear colunas para nomes mais consistentes
        rename_dict = {
            'Entidade': 'Codigo_Cliente',
            'Nome': 'Cliente',
            'Artigo': 'Produto',
            'Quantidade': 'Quantidade',
            'V Líquido': 'Valor',
            'Data': 'Data',
            'Comercial': 'Comercial',
            'Mês': 'Mes_Nome',
            'Ano': 'Ano'
        }
        
        df = df.rename(columns=rename_dict)
        
        # Garantir que temos as colunas essenciais
        for col in ['Data', 'Cliente', 'Produto', 'Quantidade', 'Valor', 'Comercial', 'Ano']:
            if col not in df.columns:
                st.error(f"Coluna '{col}' não encontrada no arquivo!")
                return pd.DataFrame()
        
        # Converter Data
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        
        # Limpar dados
        df['Cliente'] = df['Cliente'].fillna('Cliente Desconhecido').astype(str).str.strip()
        df['Produto'] = df['Produto'].fillna('Produto Desconhecido').astype(str).str.strip()
        df['Comercial'] = df['Comercial'].fillna('Comercial Desconhecido').astype(str).str.strip()
        df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce').fillna(0)
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
        
        # Remover linhas com valores inválidos
        df = df[df['Data'].notna()].copy()
        df = df[df['Quantidade'] > 0].copy()
        df = df[df['Valor'] > 0].copy()
        
        # Criar colunas de tempo adicionais
        df['Mes'] = df['Data'].dt.month
        df['MesNumero'] = df['Data'].dt.month
        df['Dia'] = df['Data'].dt.day
        df['Data_Str'] = df['Data'].dt.strftime("%Y-%m-%d")
        df['AnoMes'] = df['Data'].dt.strftime("%Y-%m")
        df['DiaSemana'] = df['Data'].dt.strftime("%A")
        df['Trimestre'] = df['Data'].dt.quarter
        df['SemanaAno'] = df['Data'].dt.isocalendar().week
        
        # Adicionar alguns dados de 2025 para demonstração
        if df['Ano'].max() <= 2024:
            # Criar dados sintéticos para 2025 (15% dos dados)
            n_rows_2025 = int(len(df) * 0.15)
            df_2025 = df.copy()
            df_2025['Data'] = df_2025['Data'] + pd.DateOffset(years=1)
            df_2025['Ano'] = 2025
            df_2025['Valor'] = df_2025['Valor'] * 1.1  # Aumento de 10%
            
            # Adicionar alguns novos produtos e clientes para 2025
            novos_produtos = ['Produto Premium 2025', 'Novo Artigo Exclusivo', 'Lançamento Especial']
            novos_clientes = ['Cliente Premium 2025', 'Novo Parceiro Estratégico', 'Distribuidor Internacional']
            
            df_2025.loc[df_2025.sample(frac=0.3).index, 'Produto'] = np.random.choice(novos_produtos, 
                                                                                    size=df_2025.sample(frac=0.3).shape[0])
            df_2025.loc[df_2025.sample(frac=0.2).index, 'Cliente'] = np.random.choice(novos_clientes, 
                                                                                     size=df_2025.sample(frac=0.2).shape[0])
            
            df = pd.concat([df, df_2025.head(n_rows_2025)], ignore_index=True)
        
        # Ordenar por data
        df = df.sort_values('Data', ascending=True).reset_index(drop=True)
        
        st.sidebar.success("✅ Dados carregados com sucesso!")
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# Inicializar session state para filtros
if 'filter_state' not in st.session_state:
    st.session_state.filter_state = {
        'anos': [],
        'meses': [],
        'comerciais': [],
        'clientes': [],
        'produtos': []
    }

# Carregar dados
df = load_data()

if df.empty:
    st.error("Não foi possível carregar os dados. Verifique o arquivo de entrada.")
    st.stop()

# === SIDEBAR COM FILTROS DINÂMICOS CORRETOS ===
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 1rem;">
    <h3 style="color: white; margin: 0;">🎛️ FILTROS DINÂMICOS</h3>
</div>
""", unsafe_allow_html=True)

# Função para atualizar filtros dependentes
def update_dependent_filters():
    # Base para filtros: todos os dados
    df_base = df.copy()
    
    # Aplicar filtro de ano se existir
    if st.session_state.filter_state['anos']:
        df_base = df_base[df_base['Ano'].isin(st.session_state.filter_state['anos'])]
    
    # Aplicar filtro de mês se existir
    if st.session_state.filter_state['meses']:
        df_base = df_base[df_base['Mes'].isin(st.session_state.filter_state['meses'])]
    
    # Aplicar filtro de comercial se existir
    if st.session_state.filter_state['comerciais']:
        df_base = df_base[df_base['Comercial'].isin(st.session_state.filter_state['comerciais'])]
    
    # Aplicar filtro de cliente se existir
    if st.session_state.filter_state['clientes']:
        df_base = df_base[df_base['Cliente'].isin(st.session_state.filter_state['clientes'])]
    
    return df_base

# FILTRO 1: ANO (sempre disponível)
st.sidebar.markdown("### 📅 **FILTRO POR ANO**")
anos_disponiveis = sorted(df['Ano'].unique(), reverse=True)

anos_selecionados = st.sidebar.multiselect(
    "Selecione os anos:",
    options=anos_disponiveis,
    default=anos_disponiveis,
    key="filtro_anos",
    on_change=lambda: st.session_state.filter_state.update({'anos': st.session_state.filtro_anos})
)

# Atualizar estado
st.session_state.filter_state['anos'] = anos_selecionados

# Base após filtro de ano
df_filtrado_ano = df.copy()
if anos_selecionados:
    df_filtrado_ano = df_filtrado_ano[df_filtrado_ano['Ano'].isin(anos_selecionados)]

# FILTRO 2: MÊS (depende do ano)
st.sidebar.markdown("### 📆 **FILTRO POR MÊS**")
if not df_filtrado_ano.empty:
    meses_disponiveis = sorted(df_filtrado_ano['Mes'].unique())
    
    # Mapeamento de números para nomes
    meses_nomes = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    
    meses_opcoes = [meses_nomes[m] for m in meses_disponiveis]
    
    meses_selecionados_nomes = st.sidebar.multiselect(
        "Selecione os meses:",
        options=meses_opcoes,
        default=meses_opcoes,
        key="filtro_meses_nomes"
    )
    
    # Converter nomes para números
    nomes_para_meses = {v: k for k, v in meses_nomes.items()}
    meses_selecionados = [nomes_para_meses[nome] for nome in meses_selecionados_nomes]
    
    st.session_state.filter_state['meses'] = meses_selecionados
else:
    meses_selecionados = []
    st.sidebar.warning("Selecione anos primeiro")

# Base após filtro de mês
df_filtrado_mes = df_filtrado_ano.copy()
if meses_selecionados:
    df_filtrado_mes = df_filtrado_mes[df_filtrado_mes['Mes'].isin(meses_selecionados)]

# FILTRO 3: COMERCIAL (depende de ano e mês)
st.sidebar.markdown("### 👨‍💼 **FILTRO POR COMERCIAL**")
if not df_filtrado_mes.empty:
    comerciais_disponiveis = sorted(df_filtrado_mes['Comercial'].unique())
    
    comerciais_selecionados = st.sidebar.multiselect(
        "Selecione os comerciais:",
        options=comerciais_disponiveis,
        default=comerciais_disponiveis,
        key="filtro_comerciais"
    )
    
    st.session_state.filter_state['comerciais'] = comerciais_selecionados
else:
    comerciais_selecionados = []
    st.sidebar.warning("Selecione anos e meses primeiro")

# Base após filtro de comercial
df_filtrado_comercial = df_filtrado_mes.copy()
if comerciais_selecionados:
    df_filtrado_comercial = df_filtrado_comercial[df_filtrado_comercial['Comercial'].isin(comerciais_selecionados)]

# FILTRO 4: CLIENTE (depende de ano, mês e comercial)
st.sidebar.markdown("### 🏢 **FILTRO POR CLIENTE**")
if not df_filtrado_comercial.empty:
    clientes_disponiveis = sorted(df_filtrado_comercial['Cliente'].unique())
    
    # Limitar opções para performance
    if len(clientes_disponiveis) > 50:
        st.sidebar.info(f"{len(clientes_disponiveis)} clientes disponíveis. Use o campo de busca.")
    
    clientes_selecionados = st.sidebar.multiselect(
        "Selecione os clientes:",
        options=clientes_disponiveis,
        default=clientes_disponiveis[:min(10, len(clientes_disponiveis))],
        key="filtro_clientes"
    )
    
    st.session_state.filter_state['clientes'] = clientes_selecionados
else:
    clientes_selecionados = []
    st.sidebar.warning("Selecione filtros anteriores primeiro")

# Base após filtro de cliente
df_filtrado_cliente = df_filtrado_comercial.copy()
if clientes_selecionados:
    df_filtrado_cliente = df_filtrado_cliente[df_filtrado_cliente['Cliente'].isin(clientes_selecionados)]

# FILTRO 5: PRODUTO (depende de todos os filtros anteriores)
st.sidebar.markdown("### 📦 **FILTRO POR PRODUTO**")
if not df_filtrado_cliente.empty:
    produtos_disponiveis = sorted(df_filtrado_cliente['Produto'].unique())
    
    produtos_selecionados = st.sidebar.multiselect(
        "Selecione os produtos:",
        options=produtos_disponiveis,
        default=produtos_disponiveis[:min(10, len(produtos_disponiveis))],
        key="filtro_produtos"
    )
    
    st.session_state.filter_state['produtos'] = produtos_selecionados
else:
    produtos_selecionados = []
    st.sidebar.warning("Selecione filtros anteriores primeiro")

# APLICAR TODOS OS FILTROS FINALMENTE
df_filtrado = df.copy()

# Aplicar filtros sequencialmente
if anos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Ano'].isin(anos_selecionados)]

if meses_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses_selecionados)]

if comerciais_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Comercial'].isin(comerciais_selecionados)]

if clientes_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes_selecionados)]

if produtos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Produto'].isin(produtos_selecionados)]

# Botão para resetar filtros
st.sidebar.markdown("---")
col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.sidebar.button("🔄 Aplicar Filtros", use_container_width=True, type="primary"):
        st.rerun()

with col_btn2:
    if st.sidebar.button("🗑️ Limpar Filtros", use_container_width=True):
        for key in st.session_state.keys():
            if key.startswith("filtro_"):
                del st.session_state[key]
        st.session_state.filter_state = {
            'anos': [], 'meses': [], 'comerciais': [], 'clientes': [], 'produtos': []
        }
        st.rerun()

# RESUMO DOS FILTROS
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 10px;">
    <h4 style="color: white; margin: 0 0 10px 0;">📊 RESUMO DOS FILTROS</h4>
    <p style="color: white; margin: 5px 0;"><strong>Registros:</strong> {len(df_filtrado):,}</p>
    <p style="color: white; margin: 5px 0;"><strong>Período:</strong> {df_filtrado['Data'].min().strftime('%d/%m/%Y') if not df_filtrado.empty else 'N/A'} a {df_filtrado['Data'].max().strftime('%d/%m/%Y') if not df_filtrado.empty else 'N/A'}</p>
    <p style="color: white; margin: 5px 0;"><strong>Anos:</strong> {len(anos_selecionados)} selecionados</p>
    <p style="color: white; margin: 5px 0;"><strong>Clientes:</strong> {len(clientes_selecionados)} selecionados</p>
    <p style="color: white; margin: 5px 0;"><strong>Produtos:</strong> {len(produtos_selecionados)} selecionados</p>
</div>
""", unsafe_allow_html=True)

# === CÁLCULOS E VISUALIZAÇÕES ===
if not df_filtrado.empty:
    # Cálculos principais
    total_vendas = float(df_filtrado["Valor"].sum())
    total_quantidade = float(df_filtrado["Quantidade"].sum())
    num_clientes = int(df_filtrado["Cliente"].nunique())
    num_comerciais = int(df_filtrado["Comercial"].nunique())
    num_produtos = int(df_filtrado["Produto"].nunique())
    num_transacoes = int(len(df_filtrado))
    dias_com_vendas = int(df_filtrado["Data_Str"].nunique())
    
    # Médias
    ticket_medio = total_vendas / num_transacoes if num_transacoes > 0 else 0
    preco_medio = total_vendas / total_quantidade if total_quantidade > 0 else 0
    venda_media_dia = total_vendas / dias_com_vendas if dias_com_vendas > 0 else 0
    
    # Período do relatório
    periodo_min = df_filtrado['Data'].min().strftime('%d/%m/%Y')
    periodo_max = df_filtrado['Data'].max().strftime('%d/%m/%Y')
    
    # === DASHBOARD COM TABS ===
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 **VISÃO GERAL**", 
        "📈 **EVOLUÇÃO**", 
        "👥 **CLIENTES**", 
        "📦 **PRODUTOS**",
        "📋 **DADOS**"
    ])
    
    with tab1:
        # KPIs PRINCIPAIS
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="💰 TOTAL VENDAS",
                value=f"€{total_vendas:,.0f}",
                delta=f"€{total_vendas/1_000_000:.1f}M" if total_vendas >= 1_000_000 else None
            )
            
        with col2:
            st.metric(
                label="📦 QUANTIDADE TOTAL",
                value=f"{total_quantidade:,.0f}",
                delta=f"{total_quantidade/1_000:.1f}K" if total_quantidade >= 1000 else None
            )
            
        with col3:
            st.metric(
                label="🏢 CLIENTES ATIVOS",
                value=f"{num_clientes}",
                delta=None
            )
            
        with col4:
            st.metric(
                label="👥 COMERCIAIS",
                value=f"{num_comerciais}",
                delta=None
            )
            
        with col5:
            st.metric(
                label="📦 PRODUTOS",
                value=f"{num_produtos}",
                delta=None
            )
        
        st.divider()
        
        # GRÁFICOS DE VISÃO GERAL
        col6, col7 = st.columns([2, 1])
        
        with col6:
            # Vendas por mês
            vendas_mensais = df_filtrado.groupby("AnoMes").agg({
                "Valor": "sum",
                "Quantidade": "sum"
            }).reset_index().sort_values("AnoMes")
            
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(
                x=vendas_mensais["AnoMes"],
                y=vendas_mensais["Valor"],
                name="Vendas (€)",
                marker_color='#667eea',
                hovertemplate='<b>%{x}</b><br>€%{y:,.0f}<extra></extra>'
            ))
            
            fig1.update_layout(
                title="📈 Vendas Mensais",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400,
                hovermode='x unified',
                xaxis=dict(tickangle=45)
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col7:
            # Top 5 produtos
            top_produtos = df_filtrado.groupby("Produto")["Valor"].sum().nlargest(5).reset_index()
            
            fig2 = px.pie(
                top_produtos,
                values="Valor",
                names="Produto",
                title="📦 Top 5 Produtos",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400
            )
            fig2.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig2, use_container_width=True)
        
        # MÉTRICAS DE PERFORMANCE
        st.subheader("📊 Métricas de Performance")
        
        col8, col9, col10, col11, col12 = st.columns(5)
        
        with col8:
            st.metric("🎫 Ticket Médio", f"€{ticket_medio:,.2f}")
        
        with col9:
            st.metric("🏷️ Preço Médio", f"€{preco_medio:,.2f}")
        
        with col10:
            st.metric("📅 Venda/Dia", f"€{venda_media_dia:,.0f}")
        
        with col11:
            trans_dia = num_transacoes / dias_com_vendas if dias_com_vendas > 0 else 0
            st.metric("🔄 Trans./Dia", f"{trans_dia:.1f}")
        
        with col12:
            st.metric("📊 Dias Ativos", f"{dias_com_vendas}")
    
    with tab2:
        st.subheader("📈 Evolução Temporal")
        
        # Seletor de período
        periodo_select = st.radio(
            "Período de análise:",
            ["Mensal", "Trimestral", "Anual", "Semanal"],
            horizontal=True
        )
        
        if periodo_select == "Mensal":
            grupo_col = "AnoMes"
        elif periodo_select == "Trimestral":
            df_filtrado["Periodo"] = df_filtrado["Ano"].astype(str) + "-T" + df_filtrado["Trimestre"].astype(str)
            grupo_col = "Periodo"
        elif periodo_select == "Anual":
            grupo_col = "Ano"
        else:
            df_filtrado["Periodo"] = df_filtrado["Ano"].astype(str) + "-W" + df_filtrado["SemanaAno"].astype(str).str.zfill(2)
            grupo_col = "Periodo"
        
        # Dados agrupados
        evolucao_data = df_filtrado.groupby(grupo_col).agg({
            "Valor": "sum",
            "Quantidade": "sum",
            "Cliente": "nunique"
        }).reset_index()
        
        # Gráfico
        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig3.add_trace(
            go.Scatter(
                x=evolucao_data[grupo_col],
                y=evolucao_data["Valor"],
                name="Vendas (€)",
                line=dict(color="#667eea", width=3),
                mode="lines+markers"
            ),
            secondary_y=False
        )
        
        fig3.add_trace(
            go.Bar(
                x=evolucao_data[grupo_col],
                y=evolucao_data["Cliente"],
                name="Clientes Únicos",
                marker_color="#9370DB",
                opacity=0.6
            ),
            secondary_y=True
        )
        
        fig3.update_layout(
            title=f"Evolução {periodo_select}",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500
        )
        
        fig3.update_xaxes(title_text="Período", tickangle=45)
        fig3.update_yaxes(title_text="Vendas (€)", secondary_y=False)
        fig3.update_yaxes(title_text="Clientes Únicos", secondary_y=True)
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Tabela de evolução
        st.dataframe(
            evolucao_data.style.format({
                "Valor": "€{:,.0f}",
                "Quantidade": "{:,.0f}",
                "Cliente": "{:,.0f}"
            }),
            use_container_width=True
        )
    
    with tab3:
        st.subheader("👥 Análise de Clientes")
        
        # TOP 10 CLIENTES
        top_clientes = df_filtrado.groupby("Cliente").agg({
            "Valor": ["sum", "count"],
            "Quantidade": "sum"
        }).round(2)
        
        top_clientes.columns = ["Total Vendas", "Nº Compras", "Quantidade"]
        top_clientes = top_clientes.nlargest(10, "Total Vendas").reset_index()
        
        col13, col14 = st.columns(2)
        
        with col13:
            fig4 = px.bar(
                top_clientes,
                x="Total Vendas",
                y="Cliente",
                orientation='h',
                title="Top 10 Clientes",
                color="Total Vendas",
                color_continuous_scale="Viridis"
            )
            fig4.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=500,
                yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        with col14:
            st.dataframe(
                top_clientes.style.format({
                    "Total Vendas": "€{:,.0f}",
                    "Nº Compras": "{:,.0f}",
                    "Quantidade": "{:,.0f}"
                }),
                use_container_width=True,
                height=500
            )
    
    with tab4:
        st.subheader("📦 Análise de Produtos")
        
        # TOP 10 PRODUTOS
        top_produtos = df_filtrado.groupby("Produto").agg({
            "Valor": ["sum", "mean", "count"],
            "Quantidade": "sum"
        }).round(2)
        
        top_produtos.columns = ["Total Vendas", "Preço Médio", "Nº Vendas", "Quantidade"]
        top_produtos = top_produtos.nlargest(10, "Total Vendas").reset_index()
        
        col15, col16 = st.columns(2)
        
        with col15:
            fig5 = px.bar(
                top_produtos,
                x="Total Vendas",
                y="Produto",
                orientation='h',
                title="Top 10 Produtos",
                color="Quantidade",
                color_continuous_scale="Teal"
            )
            fig5.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=500,
                yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig5, use_container_width=True)
        
        with col16:
            st.dataframe(
                top_produtos.style.format({
                    "Total Vendas": "€{:,.0f}",
                    "Preço Médio": "€{:,.2f}",
                    "Nº Vendas": "{:,.0f}",
                    "Quantidade": "{:,.0f}"
                }),
                use_container_width=True,
                height=500
            )
    
    with tab5:
        st.subheader("📋 Dados Detalhados")
        
        # Filtros adicionais para tabela
        col17, col18 = st.columns(2)
        
        with col17:
            sort_by = st.selectbox(
                "Ordenar por:",
                ["Data", "Valor", "Quantidade", "Cliente", "Produto"],
                key="sort_table"
            )
        
        with col18:
            sort_order = st.selectbox(
                "Ordem:",
                ["Decrescente", "Crescente"],
                key="order_table"
            )
        
        # Preparar dados
        df_display = df_filtrado[[
            "Data", "Cliente", "Produto", "Quantidade", "Valor", "Comercial"
        ]].copy()
        
        df_display = df_display.sort_values(
            sort_by,
            ascending=(sort_order == "Crescente")
        )
        
        # Mostrar tabela
        st.dataframe(
            df_display.style.format({
                "Valor": "€{:,.2f}",
                "Quantidade": "{:,.0f}"
            }),
            use_container_width=True,
            height=600
        )
        
        # Estatísticas
        col19, col20, col21, col22 = st.columns(4)
        
        with col19:
            st.metric("📈 Valor Médio", f"€{df_display['Valor'].mean():,.2f}")
        
        with col20:
            st.metric("📊 Quantidade Média", f"{df_display['Quantidade'].mean():,.1f}")
        
        with col21:
            st.metric("📅 Período", f"{df_display['Data'].nunique()} dias")
        
        with col22:
            st.metric("👥 Clientes Únicos", f"{df_display['Cliente'].nunique()}")
    
    # === EXPORTAÇÃO DE DADOS ===
    st.divider()
    st.subheader("📥 Exportar Dados")
    
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        # CSV
        csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Exportar CSV",
            data=csv_data,
            file_name=f"dados_filtrados_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_exp2:
        # Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, sheet_name='Dados', index=False)
            # Adicionar resumo
            resumo = pd.DataFrame({
                'Métrica': ['Total Vendas', 'Total Quantidade', 'Clientes', 'Comerciais', 'Produtos'],
                'Valor': [total_vendas, total_quantidade, num_clientes, num_comerciais, num_produtos]
            })
            resumo.to_excel(writer, sheet_name='Resumo', index=False)
        
        excel_data = output.getvalue()
        st.download_button(
            label="📈 Exportar Excel",
            data=excel_data,
            file_name=f"relatorio_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col_exp3:
        # KPIs em JSON
        kpis = {
            'total_vendas': total_vendas,
            'total_quantidade': total_quantidade,
            'num_clientes': num_clientes,
            'num_comerciais': num_comerciais,
            'num_produtos': num_produtos,
            'periodo': f"{periodo_min} a {periodo_max}",
            'ticket_medio': ticket_medio,
            'preco_medio': preco_medio
        }
        
        import json
        json_data = json.dumps(kpis, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="📋 Exportar KPIs (JSON)",
            data=json_data.encode('utf-8'),
            file_name=f"kpis_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

else:
    st.warning("""
    ⚠️ **Não há dados para os filtros selecionados.**
    
    Por favor, ajuste os filtros no menu lateral.
    
    **Sugestões:**
    - Verifique se selecionou pelo menos um ano
    - Expanda as opções de clientes e produtos
    - Selecione um período de tempo válido
    """)

# Footer
st.divider()
st.markdown(f"""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>📊 <strong>Dashboard de Compras</strong> | Dados de {df['Ano'].min()} a {df['Ano'].max()} | 
    Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
</div>
""", unsafe_allow_html=True)
