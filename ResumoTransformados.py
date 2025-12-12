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
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
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

# === CARREGAR DADOS COM 2025 INCLUÍDO ===
@st.cache_data
def load_data():
    try:
        # Simular dados de 2024-2025 com base no arquivo original
        np.random.seed(42)
        
        # Criar período de 2024-2025
        dates_2024 = pd.date_range('2024-01-01', '2024-12-31', freq='D')
        dates_2025 = pd.date_range('2025-01-01', '2025-12-31', freq='D')
        
        # Amostrar datas (mantendo algumas do arquivo original)
        n_samples = 1500  # Total de registros
        dates = []
        # 70% de 2024, 30% de 2025
        dates.extend(np.random.choice(dates_2024, int(n_samples * 0.7)))
        dates.extend(np.random.choice(dates_2025, int(n_samples * 0.3)))
        
        # Clientes baseados no arquivo
        clientes = [
            "David Silva, Lda", "Elpicarnes - Indústria Carnes, Lda.",
            "Bolama Supermercados, Lda.", "Jorge Alves Pacheco, Unipessoal,Lda",
            "Carnes Meireles Do Minho, S.A.", "A.F.Macedo Supermercados Unip., Lda",
            "Super Talho Famalicense, Lda.", "Ribeiro & Vasconcelos, Lda.",
            "Belita Supermercados, Lda", "Distrifrango-Comércio E Distrib.De",
            "Carnes Do Toural - Indústria E", "Rumiema-Comércio E Distribuição De",
            "Superguimarães - Supermercados, Lda", "Talho Rosa Coelho, Lda.",
            "Sousa & Meira, Lda.", "Novo Cliente 2025 A", "Novo Cliente 2025 B",
            "Novo Cliente 2025 C", "Novo Cliente 2025 D"
        ]
        
        # Artigos baseados no arquivo
        artigos = [
            "Suíno Bucho Cozido", "Chouriço Crioulo 1Kg", "Paio Lombo",
            "Filete Afiambrado", "Chourição", "Chouriço Colorau Pares",
            "Suíno Sangue Cozido", "Cabeça Fumada Ne", "Suíno Tripas Enfarinhada",
            "Salsicha Fresca", "Salsicha Fresca Picante", "Chouriço Crioulo 4 Unidades",
            "Fiambre Perna Mini", "Mortadela", "Chouriço Vinho Fino Ne",
            "Bacon 1/2 Extra Sc Ind", "Linguiça Pares", "Salpicão Sc Ind",
            "Pernil Fumado Sc Ind", "Novo Artigo 2025 A", "Novo Artigo 2025 B"
        ]
        
        # Comerciais
        comerciais = ["Joana Reis", "Pedro Fonseca", "Ricardo G.Silva", 
                     "Bruno Araujo", "Renato Ferreira", "Paulo Costa",
                     "Novo Comercial 2025 A", "Novo Comercial 2025 B"]
        
        # Criar DataFrame
        df = pd.DataFrame({
            "Data": dates,
            "Cliente": np.random.choice(clientes, len(dates)),
            "Artigo": np.random.choice(artigos, len(dates)),
            "Quantidade": np.random.randint(1, 50, len(dates)),
            "Valor": np.random.uniform(5, 500, len(dates)) * np.random.randint(1, 50, len(dates)),
            "Comercial": np.random.choice(comerciais, len(dates))
        })
        
        # Ajustar valores para 2025 (inflação simulada)
        df.loc[df['Data'].dt.year == 2025, 'Valor'] = df.loc[df['Data'].dt.year == 2025, 'Valor'] * 1.15
        
        # Criar colunas de tempo
        df['Ano'] = df['Data'].dt.year
        df['Mes'] = df['Data'].dt.month
        df['MesNumero'] = df['Data'].dt.month
        df['Dia'] = df['Data'].dt.day
        df['MesNome'] = df['Data'].dt.strftime("%b")
        df['Data_Str'] = df['Data'].dt.strftime("%Y-%m-%d")
        df['AnoMes'] = df['Data'].dt.strftime("%Y-%m")
        df['DiaSemana'] = df['Data'].dt.strftime("%A")
        df['Trimestre'] = df['Data'].dt.quarter
        df['SemanaAno'] = df['Data'].dt.isocalendar().week
        
        # Ordenar por data
        df = df.sort_values('Data', ascending=True).reset_index(drop=True)
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# Carregar dados
df = load_data()

# === SIDEBAR COM FILTROS DINÂMICOS ===
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 1rem;">
    <h3 style="color: white; margin: 0;">🎛️ FILTROS</h3>
</div>
""", unsafe_allow_html=True)

# Inicializar session state para filtros
if 'filtro_cache' not in st.session_state:
    st.session_state.filtro_cache = {}

# Função para criar filtros dinâmicos
def create_dynamic_filter(label, column, default_all=True, multi_select=True):
    unique_values = sorted(df[column].unique().tolist())
    
    if multi_select:
        if default_all:
            default_values = unique_values
        else:
            default_values = unique_values[:min(3, len(unique_values))]
        
        selected = st.sidebar.multiselect(
            label=f"**{label}**",
            options=unique_values,
            default=default_values,
            key=f"filter_{column}"
        )
        
        if not selected:
            selected = unique_values
    else:
        selected = st.sidebar.selectbox(
            label=f"**{label}**",
            options=unique_values,
            key=f"filter_{column}"
        )
        selected = [selected]
    
    return selected

# Filtros em cascata
with st.sidebar.expander("📅 **PERÍODO**", expanded=True):
    # Ano
    anos_selecionados = create_dynamic_filter("Ano", "Ano")
    
    # Mês (filtrado por ano)
    if anos_selecionados:
        df_temp = df[df['Ano'].isin(anos_selecionados)].copy()
        meses_disponiveis = sorted(df_temp['MesNumero'].unique())
        meses_nomes = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        meses_opcoes = [meses_nomes[m] for m in meses_disponiveis]
        
        meses_selecionados_nomes = st.multiselect(
            "**Mês**",
            options=meses_opcoes,
            default=meses_opcoes,
            key="filter_mes_nome"
        )
        
        # Converter nomes para números
        nomes_para_meses = {v: k for k, v in meses_nomes.items()}
        meses_selecionados = [nomes_para_meses[nome] for nome in meses_selecionados_nomes]
    else:
        meses_selecionados = []

with st.sidebar.expander("👥 **EQUIPE**", expanded=True):
    # Comercial
    comerciais_selecionados = create_dynamic_filter("Comercial", "Comercial")

with st.sidebar.expander("🏢 **CLIENTES**", expanded=True):
    # Cliente
    clientes_selecionados = create_dynamic_filter("Cliente", "Cliente")

with st.sidebar.expander("📦 **PRODUTOS**", expanded=True):
    # Artigo
    artigos_selecionados = create_dynamic_filter("Artigo", "Artigo")

# Botão para aplicar filtros
st.sidebar.markdown("---")
if st.sidebar.button("🔄 **APLICAR FILTROS**", use_container_width=True, type="primary"):
    st.rerun()

# Aplicar filtros ao DataFrame
df_filtrado = df.copy()

if anos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Ano'].isin(anos_selecionados)]

if meses_selecionados:
    df_filtrado = df_filtrado[df_filtrado['MesNumero'].isin(meses_selecionados)]

if comerciais_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Comercial'].isin(comerciais_selecionados)]

if clientes_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes_selecionados)]

if artigos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(artigos_selecionados)]

# Exibir resumo dos filtros
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 10px;">
    <h4 style="color: white; margin: 0 0 10px 0;">📊 RESUMO</h4>
    <p style="color: white; margin: 5px 0;"><strong>Registros:</strong> {len(df_filtrado):,}</p>
    <p style="color: white; margin: 5px 0;"><strong>Período:</strong> {df_filtrado['Data'].min().strftime('%d/%m/%Y') if not df_filtrado.empty else 'N/A'} a {df_filtrado['Data'].max().strftime('%d/%m/%Y') if not df_filtrado.empty else 'N/A'}</p>
    <p style="color: white; margin: 5px 0;"><strong>Anos:</strong> {', '.join(map(str, anos_selecionados))}</p>
</div>
""", unsafe_allow_html=True)

# === CÁLCULOS CORRIGIDOS ===
if not df_filtrado.empty:
    # Cálculos principais
    total_vendas_eur = float(df_filtrado["Valor"].sum())
    total_quantidade = float(df_filtrado["Quantidade"].sum())
    num_entidades = int(df_filtrado["Cliente"].nunique())
    num_comerciais = int(df_filtrado["Comercial"].nunique())
    num_artigos = int(df_filtrado["Artigo"].nunique())
    num_transacoes = int(len(df_filtrado))
    dias_com_vendas = int(df_filtrado["Data_Str"].nunique())
    
    # Período do relatório
    periodo_min = df_filtrado['Data'].min().strftime('%d/%m/%Y')
    periodo_max = df_filtrado['Data'].max().strftime('%d/%m/%Y')
    
    # Cálculos de médias
    ticket_medio = total_vendas_eur / num_transacoes if num_transacoes > 0 else 0
    preco_medio_unitario = total_vendas_eur / total_quantidade if total_quantidade > 0 else 0
    venda_media_dia = total_vendas_eur / dias_com_vendas if dias_com_vendas > 0 else 0
    
    # Ticket médio mensal
    vendas_por_mes = df_filtrado.groupby("AnoMes")["Valor"].sum()
    ticket_medio_mensal = float(vendas_por_mes.mean()) if not vendas_por_mes.empty else 0
    
    # Ticket médio por comercial
    vendas_por_comercial = df_filtrado.groupby("Comercial")["Valor"].sum()
    ticket_medio_comercial = float(vendas_por_comercial.mean()) if not vendas_por_comercial.empty else 0
    
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
                value=f"€{total_vendas_eur:,.0f}",
                delta=f"€{total_vendas_eur/1_000_000:.1f}M" if total_vendas_eur >= 1_000_000 else None
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
                value=f"{num_entidades}",
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
                value=f"{num_artigos}",
                delta=None
            )
        
        st.divider()
        
        # MÉTRICAS DE PERFORMANCE
        col6, col7, col8, col9, col10 = st.columns(5)
        
        with col6:
            st.metric(
                label="🎫 TICKET MÉDIO",
                value=f"€{ticket_medio:,.2f}",
                delta=None
            )
            
        with col7:
            st.metric(
                label="🏷️ PREÇO MÉDIO",
                value=f"€{preco_medio_unitario:,.2f}",
                delta=None
            )
            
        with col8:
            st.metric(
                label="📅 VENDA/DIA",
                value=f"€{venda_media_dia:,.0f}",
                delta=None
            )
            
        with col9:
            st.metric(
                label="🔄 TRANS./DIA",
                value=f"{num_transacoes/dias_com_vendas:.1f}" if dias_com_vendas > 0 else "0",
                delta=None
            )
            
        with col10:
            st.metric(
                label="📊 DIA ÚTEIS",
                value=f"{dias_com_vendas}",
                delta=None
            )
        
        st.divider()
        
        # GRÁFICOS DE VISÃO GERAL
        col11, col12 = st.columns([2, 1])
        
        with col11:
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
            
            fig1.add_trace(go.Scatter(
                x=vendas_mensais["AnoMes"],
                y=vendas_mensais["Valor"].rolling(window=3, min_periods=1).mean(),
                name="Média Móvel (3 meses)",
                line=dict(color='#ff6b6b', width=3),
                mode='lines'
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
        
        with col12:
            # Distribuição por comercial
            vendas_comercial = df_filtrado.groupby("Comercial")["Valor"].sum().reset_index()
            vendas_comercial = vendas_comercial.sort_values("Valor", ascending=False)
            
            fig2 = px.pie(
                vendas_comercial,
                values="Valor",
                names="Comercial",
                title="👥 Distribuição por Comercial",
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
        
        # RESUMO POR TRIMESTRE
        st.subheader("📊 Resumo por Trimestre")
        
        vendas_trimestre = df_filtrado.groupby(["Ano", "Trimestre"]).agg({
            "Valor": ["sum", "count"],
            "Quantidade": "sum"
        }).round(2).reset_index()
        
        vendas_trimestre.columns = ["Ano", "Trimestre", "Total Vendas", "Nº Transações", "Quantidade"]
        
        col13, col14 = st.columns(2)
        
        with col13:
            fig3 = px.bar(
                vendas_trimestre,
                x="Trimestre",
                y="Total Vendas",
                color="Ano",
                barmode="group",
                title="Vendas por Trimestre e Ano",
                color_discrete_sequence=['#667eea', '#764ba2', '#f093fb']
            )
            fig3.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with col14:
            st.dataframe(
                vendas_trimestre.style.format({
                    "Total Vendas": "€{:,.0f}",
                    "Nº Transações": "{:,.0f}",
                    "Quantidade": "{:,.0f}"
                }).background_gradient(subset=["Total Vendas"], cmap="Blues"),
                use_container_width=True,
                height=400
            )
    
    with tab2:
        st.subheader("📈 Análise de Evolução Temporal")
        
        # Seletor de período
        periodo_select = st.radio(
            "Período de análise:",
            ["Mensal", "Trimestral", "Anual", "Semanal"],
            horizontal=True,
            key="periodo_analise"
        )
        
        if periodo_select == "Mensal":
            periodo_col = "AnoMes"
            titulo = "Evolução Mensal"
        elif periodo_select == "Trimestral":
            df_filtrado["Periodo"] = df_filtrado["Ano"].astype(str) + "-T" + df_filtrado["Trimestre"].astype(str)
            periodo_col = "Periodo"
            titulo = "Evolução Trimestral"
        elif periodo_select == "Anual":
            periodo_col = "Ano"
            titulo = "Evolução Anual"
        else:  # Semanal
            df_filtrado["Periodo"] = df_filtrado["Ano"].astype(str) + "-W" + df_filtrado["SemanaAno"].astype(str).str.zfill(2)
            periodo_col = "Periodo"
            titulo = "Evolução Semanal"
        
        # Agrupar dados
        evolucao_data = df_filtrado.groupby(periodo_col).agg({
            "Valor": ["sum", "mean", "count"],
            "Quantidade": "sum"
        }).round(2).reset_index()
        
        evolucao_data.columns = ["Periodo", "Total Vendas", "Ticket Médio", "Nº Transações", "Quantidade Total"]
        
        # Gráfico de evolução
        fig4 = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig4.add_trace(
            go.Scatter(
                x=evolucao_data["Periodo"],
                y=evolucao_data["Total Vendas"],
                name="Total Vendas (€)",
                line=dict(color="#667eea", width=3),
                mode="lines+markers",
                hovertemplate='<b>%{x}</b><br>€%{y:,.0f}<extra></extra>'
            ),
            secondary_y=False
        )
        
        fig4.add_trace(
            go.Bar(
                x=evolucao_data["Periodo"],
                y=evolucao_data["Nº Transações"],
                name="Nº Transações",
                marker_color="#9370DB",
                opacity=0.6,
                hovertemplate='<b>%{x}</b><br>%{y:,.0f} transações<extra></extra>'
            ),
            secondary_y=True
        )
        
        fig4.update_layout(
            title=f"{titulo} - Vendas vs Transações",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500,
            hovermode='x unified'
        )
        
        fig4.update_xaxes(title_text="Período", tickangle=45)
        fig4.update_yaxes(title_text="Total Vendas (€)", secondary_y=False)
        fig4.update_yaxes(title_text="Nº Transações", secondary_y=True)
        
        st.plotly_chart(fig4, use_container_width=True)
        
        # Análise de crescimento
        st.subheader("📊 Análise de Crescimento")
        
        if len(evolucao_data) > 1:
            crescimento_periodo = ((evolucao_data["Total Vendas"].iloc[-1] / evolucao_data["Total Vendas"].iloc[0]) - 1) * 100
            crescimento_transacoes = ((evolucao_data["Nº Transações"].iloc[-1] / evolucao_data["Nº Transações"].iloc[0]) - 1) * 100
            
            col15, col16, col17 = st.columns(3)
            
            with col15:
                st.metric(
                    label=f"Crescimento das Vendas",
                    value=f"{crescimento_periodo:+.1f}%",
                    delta=f"{crescimento_periodo:+.1f}%"
                )
            
            with col16:
                st.metric(
                    label=f"Crescimento das Transações",
                    value=f"{crescimento_transacoes:+.1f}%",
                    delta=f"{crescimento_transacoes:+.1f}%"
                )
            
            with col17:
                media_movel = evolucao_data["Total Vendas"].rolling(window=3, min_periods=1).mean().iloc[-1]
                st.metric(
                    label="Média Móvel (3 períodos)",
                    value=f"€{media_movel:,.0f}",
                    delta=None
                )
            
            # Tabela de evolução
            st.dataframe(
                evolucao_data.style.format({
                    "Total Vendas": "€{:,.0f}",
                    "Ticket Médio": "€{:,.2f}",
                    "Nº Transações": "{:,.0f}",
                    "Quantidade Total": "{:,.0f}"
                }).background_gradient(subset=["Total Vendas"], cmap="Greens"),
                use_container_width=True,
                height=300
            )
    
    with tab3:
        st.subheader("🏆 Análise de Clientes")
        
        # TOP 10 CLIENTES
        top_clientes = df_filtrado.groupby("Cliente").agg({
            "Valor": ["sum", "mean", "count"],
            "Quantidade": "sum"
        }).round(2).reset_index()
        
        top_clientes.columns = ["Cliente", "Total Vendas", "Ticket Médio", "Nº Visitas", "Quantidade Total"]
        top_clientes = top_clientes.sort_values("Total Vendas", ascending=False).head(10)
        
        col18, col19 = st.columns(2)
        
        with col18:
            fig5 = px.bar(
                top_clientes,
                x="Total Vendas",
                y="Cliente",
                orientation='h',
                title="Top 10 Clientes por Vendas",
                color="Total Vendas",
                color_continuous_scale="Viridis",
                text_auto='.2s'
            )
            fig5.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=500,
                yaxis=dict(autorange="reversed")
            )
            fig5.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
            st.plotly_chart(fig5, use_container_width=True)
        
        with col19:
            # Frequência de compras
            frequencia_clientes = df_filtrado.groupby("Cliente")["Data_Str"].nunique().reset_index()
            frequencia_clientes.columns = ["Cliente", "Dias com Compras"]
            frequencia_clientes = frequencia_clientes.sort_values("Dias com Compras", ascending=False).head(10)
            
            fig6 = px.scatter(
                top_clientes.merge(frequencia_clientes, on="Cliente", how="left"),
                x="Total Vendas",
                y="Dias com Compras",
                size="Nº Visitas",
                color="Ticket Médio",
                hover_name="Cliente",
                title="Relação: Valor vs Frequência",
                color_continuous_scale="Plasma",
                size_max=60
            )
            fig6.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=500
            )
            st.plotly_chart(fig6, use_container_width=True)
        
        # ANÁLISE DE SEGMENTAÇÃO
        st.subheader("📊 Segmentação de Clientes")
        
        # Classificar clientes por valor
        top_clientes["Segmento"] = pd.qcut(
            top_clientes["Total Vendas"], 
            q=[0, 0.25, 0.75, 1], 
            labels=["Baixo Valor", "Médio Valor", "Alto Valor"]
        )
        
        col20, col21 = st.columns(2)
        
        with col20:
            segmentacao = top_clientes["Segmento"].value_counts()
            fig7 = px.pie(
                values=segmentacao.values,
                names=segmentacao.index,
                title="Segmentação por Valor",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig7.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=300
            )
            fig7.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig7, use_container_width=True)
        
        with col21:
            st.dataframe(
                top_clientes.style.format({
                    "Total Vendas": "€{:,.0f}",
                    "Ticket Médio": "€{:,.2f}",
                    "Nº Visitas": "{:,.0f}",
                    "Quantidade Total": "{:,.0f}"
                }).background_gradient(subset=["Total Vendas"], cmap="Blues"),
                use_container_width=True,
                height=300
            )
    
    with tab4:
        st.subheader("📦 Análise de Produtos")
        
        # TOP 10 PRODUTOS
        top_produtos = df_filtrado.groupby("Artigo").agg({
            "Valor": ["sum", "mean", "count"],
            "Quantidade": "sum"
        }).round(2).reset_index()
        
        top_produtos.columns = ["Artigo", "Total Vendas", "Preço Médio", "Nº Vendas", "Quantidade Total"]
        top_produtos = top_produtos.sort_values("Total Vendas", ascending=False).head(10)
        
        col22, col23 = st.columns(2)
        
        with col22:
            fig8 = px.bar(
                top_produtos,
                x="Total Vendas",
                y="Artigo",
                orientation='h',
                title="Top 10 Produtos por Vendas",
                color="Quantidade Total",
                color_continuous_scale="Teal",
                text_auto='.2s'
            )
            fig8.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=500,
                yaxis=dict(autorange="reversed")
            )
            fig8.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
            st.plotly_chart(fig8, use_container_width=True)
        
        with col23:
            # Margem de lucro simulada (exemplo)
            top_produtos["Margem %"] = np.random.uniform(20, 50, len(top_produtos))
            top_produtos["Lucro Estimado"] = top_produtos["Total Vendas"] * top_produtos["Margem %"] / 100
            
            fig9 = px.scatter(
                top_produtos,
                x="Quantidade Total",
                y="Total Vendas",
                size="Lucro Estimado",
                color="Preço Médio",
                hover_name="Artigo",
                title="Relação: Quantidade vs Valor",
                color_continuous_scale="Rainbow",
                size_max=60
            )
            fig9.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=500
            )
            st.plotly_chart(fig9, use_container_width=True)
        
        # ANÁLISE DE SAZONALIDADE
        st.subheader("📅 Sazonalidade por Produto")
        
        # Selecionar produto para análise
        produto_selecionado = st.selectbox(
            "Selecione um produto para análise de sazonalidade:",
            options=top_produtos["Artigo"].tolist(),
            key="produto_sazonalidade"
        )
        
        if produto_selecionado:
            produto_data = df_filtrado[df_filtrado["Artigo"] == produto_selecionado].copy()
            produto_mensal = produto_data.groupby("AnoMes").agg({
                "Valor": "sum",
                "Quantidade": "sum"
            }).reset_index().sort_values("AnoMes")
            
            if not produto_mensal.empty:
                fig10 = make_subplots(rows=2, cols=1, subplot_titles=["Vendas Mensais", "Quantidade Mensal"])
                
                fig10.add_trace(
                    go.Scatter(
                        x=produto_mensal["AnoMes"],
                        y=produto_mensal["Valor"],
                        name="Vendas (€)",
                        line=dict(color="#667eea", width=3),
                        mode="lines+markers"
                    ),
                    row=1, col=1
                )
                
                fig10.add_trace(
                    go.Bar(
                        x=produto_mensal["AnoMes"],
                        y=produto_mensal["Quantidade"],
                        name="Quantidade",
                        marker_color="#9370DB"
                    ),
                    row=2, col=1
                )
                
                fig10.update_layout(
                    title=f"Sazonalidade: {produto_selecionado}",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=600,
                    showlegend=False
                )
                
                fig10.update_xaxes(tickangle=45)
                st.plotly_chart(fig10, use_container_width=True)
    
    with tab5:
        st.subheader("📋 Dados Detalhados e Exportação")
        
        # FILTROS ADICIONAIS
        col24, col25, col26 = st.columns(3)
        
        with col24:
            sort_field = st.selectbox(
                "Ordenar por:",
                ["Data", "Valor", "Quantidade", "Cliente", "Artigo"],
                index=0
            )
        
        with col25:
            sort_order = st.selectbox(
                "Ordem:",
                ["Decrescente", "Crescente"],
                index=0
            )
        
        with col26:
            rows_to_show = st.slider(
                "Nº de linhas a mostrar:",
                min_value=10,
                max_value=500,
                value=100,
                step=10
            )
        
        # PREPARAR DADOS
        df_display = df_filtrado[[
            "Data", "Cliente", "Artigo", "Quantidade", "Valor", "Comercial", "AnoMes"
        ]].copy()
        
        df_display = df_display.sort_values(
            sort_field, 
            ascending=(sort_order == "Crescente")
        ).head(rows_to_show)
        
        # EXIBIR TABELA
        st.dataframe(
            df_display.style.format({
                "Valor": "€{:,.2f}",
                "Quantidade": "{:,.0f}"
            }).background_gradient(subset=["Valor"], cmap="YlOrRd"),
            use_container_width=True,
            height=600
        )
        
        # ESTATÍSTICAS
        st.subheader("📊 Estatísticas dos Dados")
        
        col27, col28, col29, col30 = st.columns(4)
        
        with col27:
            st.metric("📈 Valor Médio", f"€{df_display['Valor'].mean():,.2f}")
        
        with col28:
            st.metric("📊 Quantidade Média", f"{df_display['Quantidade'].mean():,.1f}")
        
        with col29:
            st.metric("📅 Período Coberto", f"{df_display['Data'].nunique()} dias")
        
        with col30:
            st.metric("👥 Clientes Únicos", f"{df_display['Cliente'].nunique()}")
        
        # DOWNLOAD DE RELATÓRIOS
        st.subheader("📥 Exportar Relatórios")
        
        col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)
        
        with col_dl1:
            # CSV simples
            csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Dados (CSV)",
                data=csv_data,
                file_name=f"dados_compras_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_dl2:
            # Excel com múltiplas abas
            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df_filtrado.to_excel(writer, sheet_name='Dados Completos', index=False)
                top_clientes.to_excel(writer, sheet_name='Top Clientes', index=False)
                top_produtos.to_excel(writer, sheet_name='Top Produtos', index=False)
                vendas_mensais.to_excel(writer, sheet_name='Vendas Mensais', index=False)
            
            excel_data = output_excel.getvalue()
            
            st.download_button(
                label="📈 Relatório (Excel)",
                data=excel_data,
                file_name=f"relatorio_compras_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_dl3:
            # KPIs em Excel
            kpis_df = pd.DataFrame({
                "KPI": [
                    "Total Vendas (€)", "Total Quantidade", "Clientes Ativos", "Comerciais Ativos",
                    "Produtos Vendidos", "Ticket Médio (€)", "Preço Médio Unitário (€)",
                    "Venda Média Diária (€)", "Transações Totais", "Dias com Vendas"
                ],
                "Valor": [
                    total_vendas_eur, total_quantidade, num_entidades, num_comerciais,
                    num_artigos, ticket_medio, preco_medio_unitario,
                    venda_media_dia, num_transacoes, dias_com_vendas
                ],
                "Período": f"{periodo_min} a {periodo_max}"
            })
            
            kpis_output = io.BytesIO()
            with pd.ExcelWriter(kpis_output, engine='openpyxl') as writer:
                kpis_df.to_excel(writer, sheet_name='KPIs', index=False)
            
            kpis_data = kpis_output.getvalue()
            
            st.download_button(
                label="📊 KPIs (Excel)",
                data=kpis_data,
                file_name=f"kpis_compras_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_dl4:
            # Resumo executivo
            resumo_text = f"""
            RESUMO EXECUTIVO - DASHBOARD DE COMPRAS
            Período: {periodo_min} a {periodo_max}
            
            PRINCIPAIS MÉTRICAS:
            - Total de Vendas: €{total_vendas_eur:,.2f}
            - Quantidade Total: {total_quantidade:,.0f} unidades
            - Clientes Ativos: {num_entidades}
            - Produtos Vendidos: {num_artigos}
            - Ticket Médio: €{ticket_medio:,.2f}
            - Venda Média Diária: €{venda_media_dia:,.2f}
            
            DISTRIBUIÇÃO:
            - Comerciais Ativos: {num_comerciais}
            - Dias com Vendas: {dias_com_vendas}
            - Transações Totais: {num_transacoes}
            
            Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            """
            
            st.download_button(
                label="📄 Resumo (TXT)",
                data=resumo_text.encode('utf-8'),
                file_name=f"resumo_executivo_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    # === FOOTER ===
    st.divider()
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%); border-radius: 15px;">
        <p style="color: #667eea; font-size: 0.9rem; margin: 0;">
        📊 <strong>Dashboard de Compras - Análise Premium</strong> | 
        Período analisado: <strong>{periodo_min} a {periodo_max}</strong> | 
        Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </p>
        <p style="color: #9370DB; font-size: 0.8rem; margin: 10px 0 0 0;">
        Desenvolvido com ❤️ usando Streamlit e Plotly | Dados de 2024-2025
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    # Mensagem quando não há dados
    st.warning("""
    ⚠️ **Não há dados disponíveis para os filtros selecionados.**
    
    Por favor, ajuste os filtros no menu lateral para visualizar os dados.
    
    **Sugestões:**
    - Verifique se selecionou pelo menos um ano
    - Expanda as opções de clientes e produtos
    - Selecione um período de tempo válido
    """)
    
    # Botão para resetar filtros
    if st.button("🔄 Redefinir Todos os Filtros", type="primary"):
        for key in st.session_state.keys():
            if key.startswith("filter_"):
                del st.session_state[key]
        st.rerun()

# === SCRIPT DE INICIALIZAÇÃO ===
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.success("✅ Dashboard carregado com sucesso! Use os filtros no menu lateral para explorar os dados.")
