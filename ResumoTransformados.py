import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas - ResumoTR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adicionar CSS customizado
def add_custom_css():
    st.markdown("""
    <style>
    .main > div {
        padding-top: 1rem;
    }
    
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    
    /* Estilo para multiselects */
    .stMultiSelect [data-baseweb=tag] {
        background-color: #e3f2fd;
        color: #1f77b4;
        font-weight: 500;
    }
    
    .stMultiSelect div[data-baseweb="select"] > div {
        border-color: #1f77b4;
    }
    
    /* Cards para KPIs */
    .kpi-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    
    /* Botões */
    .stButton button {
        border-radius: 6px;
        font-weight: 600;
    }
    
    .stButton button[kind="primary"] {
        background-color: #1f77b4;
    }
    
    .stButton button[kind="secondary"] {
        background-color: #6c757d;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Função para carregar dados
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('ResumoTR.xlsx')
        
        # Renomear colunas para facilitar acesso
        column_mapping = {
            'Nome': 'Entidade_Nome',
            'V Líquido': 'V_Liquido',
            'PM': 'Preco_Medio'
        }
        
        # Renomear colunas que existem
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Garantir que as colunas de data sejam datetime
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            # Remover registros com data inválida
            df = df[df['Data'].notna()]
            
            # Extrair informações temporais
            df['Ano'] = df['Data'].dt.year
            df['Mes_Num'] = df['Data'].dt.month
            df['Mes_Nome'] = df['Data'].dt.strftime('%B')
            df['Dia'] = df['Data'].dt.day
            df['Dia_Semana'] = df['Data'].dt.day_name()
        
        # Converter colunas numéricas
        numeric_cols = ['Quantidade', 'V_Liquido', 'Preco_Medio']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(0)
        
        # Verificar e criar colunas padrão se necessário
        if 'Comercial' not in df.columns:
            df['Comercial'] = 'Não Informado'
        
        # Mapear meses para português
        mes_pt_en = {
            'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
            'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
            'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
            'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
        }
        
        if 'Mes_Nome' in df.columns:
            df['Mes_PT'] = df['Mes_Nome'].map(mes_pt_en)
            df['Mes_PT'] = df['Mes_PT'].fillna(df['Mes_Nome'])
        
        return df
    
    except FileNotFoundError:
        st.error("❌ Arquivo 'ResumoTR.xlsx' não encontrado!")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return None

# Função para criar filtros multiselect
def create_multiselect_filters(df):
    """Cria todos os filtros multiselect"""
    
    filtros = {}
    
    # Filtro de Ano (Multiselect)
    if 'Ano' in df.columns:
        anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
        anos_selecionados = st.multiselect(
            "**📅 Ano**",
            options=anos_disponiveis,
            default=anos_disponiveis if len(anos_disponiveis) <= 3 else anos_disponiveis[:3],
            help="Selecione um ou mais anos"
        )
        filtros['anos'] = anos_selecionados if anos_selecionados else anos_disponiveis
    
    # Filtro de Mês (Multiselect)
    if 'Mes_PT' in df.columns:
        meses_disponiveis = sorted(df['Mes_PT'].dropna().unique(), 
                                  key=lambda x: list(mes_pt_en.values()).index(x) if x in mes_pt_en.values() else 13)
        meses_selecionados = st.multiselect(
            "**📆 Mês**",
            options=meses_disponiveis,
            default=meses_disponiveis,
            help="Selecione um ou mais meses"
        )
        filtros['meses'] = meses_selecionados if meses_selecionados else meses_disponiveis
    
    # Filtro de Comercial (Multiselect)
    if 'Comercial' in df.columns:
        comerciais_disponiveis = sorted(df['Comercial'].dropna().unique())
        comerciais_selecionados = st.multiselect(
            "**👨‍💼 Comercial**",
            options=comerciais_disponiveis,
            default=comerciais_disponiveis,
            help="Selecione um ou mais comerciais"
        )
        filtros['comerciais'] = comerciais_selecionados if comerciais_selecionados else comerciais_disponiveis
    
    # Filtro de Entidade (Multiselect com pesquisa)
    if 'Entidade_Nome' in df.columns:
        entidades_disponiveis = sorted(df['Entidade_Nome'].dropna().astype(str).unique())
        entidades_selecionadas = st.multiselect(
            "**🏢 Entidade (Nome)**",
            options=entidades_disponiveis,
            default=[],
            help="Selecione uma ou mais entidades (deixe vazio para todas)"
        )
        filtros['entidades'] = entidades_selecionadas
    
    # Filtro de Artigo (Multiselect com pesquisa)
    if 'Artigo' in df.columns:
        artigos_disponiveis = sorted(df['Artigo'].dropna().astype(str).unique())
        artigos_selecionados = st.multiselect(
            "**🛒 Artigo**",
            options=artigos_disponiveis,
            default=[],
            help="Selecione um ou mais artigos (deixe vazio para todos)"
        )
        filtros['artigos'] = artigos_selecionados
    
    return filtros

# Dicionário de meses (português-inglês)
mes_pt_en = {
    'Janeiro': 'January', 'Fevereiro': 'February', 'Março': 'March',
    'Abril': 'April', 'Maio': 'May', 'Junho': 'June',
    'Julho': 'July', 'Agosto': 'August', 'Setembro': 'September',
    'Outubro': 'October', 'Novembro': 'November', 'Dezembro': 'December'
}

# Função para aplicar filtros
def apply_filters(df, filtros):
    """Aplica todos os filtros ao DataFrame"""
    
    df_filtrado = df.copy()
    
    try:
        # Filtro de Ano
        if 'anos' in filtros and filtros['anos']:
            df_filtrado = df_filtrado[df_filtrado['Ano'].isin(filtros['anos'])]
        
        # Filtro de Mês
        if 'meses' in filtros and filtros['meses']:
            df_filtrado = df_filtrado[df_filtrado['Mes_PT'].isin(filtros['meses'])]
        
        # Filtro de Comercial
        if 'comerciais' in filtros and filtros['comerciais']:
            df_filtrado = df_filtrado[df_filtrado['Comercial'].isin(filtros['comerciais'])]
        
        # Filtro de Entidade
        if 'entidades' in filtros and filtros['entidades']:
            df_filtrado = df_filtrado[df_filtrado['Entidade_Nome'].isin(filtros['entidades'])]
        
        # Filtro de Artigo
        if 'artigos' in filtros and filtros['artigos']:
            df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(filtros['artigos'])]
    
    except Exception as e:
        st.error(f"❌ Erro ao aplicar filtros: {str(e)}")
        return df
    
    return df_filtrado

# Função principal
def main():
    add_custom_css()
    
    # Título e descrição
    st.title("📊 Dashboard de Análise de Vendas - ResumoTR")
    st.markdown("---")
    
    # Carregar dados
    with st.spinner('Carregando dados...'):
        df = load_data()
    
    if df is None or df.empty:
        st.error("❌ Não foi possível carregar os dados.")
        return
    
    # Sidebar - Filtros Multiselect
    with st.sidebar:
        st.header("⚙️ Filtros Dinâmicos")
        st.markdown("📍 **Selecione múltiplos valores em cada filtro**")
        
        # Criar filtros multiselect
        filtros = create_multiselect_filters(df)
        
        # Controles adicionais
        st.markdown("---")
        st.subheader("🎛️ Controles")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Resetar Todos", use_container_width=True, type="secondary"):
                st.rerun()
        with col2:
            if st.button("✅ Aplicar Filtros", use_container_width=True, type="primary"):
                st.rerun()
        
        # Mostrar resumo dos filtros ativos
        st.markdown("---")
        st.subheader("📊 Filtros Ativos")
        
        filtros_ativos = []
        if 'anos' in filtros:
            anos_texto = ', '.join(map(str, filtros['anos'])) if len(filtros['anos']) <= 3 else f"{len(filtros['anos'])} anos"
            filtros_ativos.append(f"**Anos:** {anos_texto}")
        
        if 'meses' in filtros:
            meses_texto = ', '.join(filtros['meses']) if len(filtros['meses']) <= 3 else f"{len(filtros['meses'])} meses"
            filtros_ativos.append(f"**Meses:** {meses_texto}")
        
        if 'comerciais' in filtros:
            comerciais_texto = f"{len(filtros['comerciais'])} comerciais"
            filtros_ativos.append(f"**Comerciais:** {comerciais_texto}")
        
        if 'entidades' in filtros and filtros['entidades']:
            entidades_texto = f"{len(filtros['entidades'])} entidades"
            filtros_ativos.append(f"**Entidades:** {entidades_texto}")
        
        if 'artigos' in filtros and filtros['artigos']:
            artigos_texto = f"{len(filtros['artigos'])} artigos"
            filtros_ativos.append(f"**Artigos:** {artigos_texto}")
        
        for filtro in filtros_ativos:
            st.markdown(f"• {filtro}")
    
    # Aplicar filtros
    df_filtrado = apply_filters(df, filtros)
    
    # Mostrar estatísticas dos filtros
    with st.sidebar:
        st.markdown("---")
        st.subheader("📈 Estatísticas Filtradas")
        
        total_registros = len(df_filtrado)
        total_vendas = df_filtrado['V_Liquido'].sum() if 'V_Liquido' in df_filtrado.columns else 0
        total_quantidade = df_filtrado['Quantidade'].sum() if 'Quantidade' in df_filtrado.columns else 0
        
        st.success(f"""
        **Registros:** {total_registros:,}
        **Vendas:** €{total_vendas:,.2f}
        **Quantidade:** {total_quantidade:,.0f}
        """)
        
        # Indicador de % dos dados
        if len(df) > 0:
            percentual = (len(df_filtrado) / len(df)) * 100
            st.progress(percentual / 100, text=f"Mostrando {percentual:.1f}% dos dados")
    
    # Seção de KPIs
    st.header("📈 KPIs Principais")
    
    # Criar colunas para os KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_vendas = df_filtrado['V_Liquido'].sum() if 'V_Liquido' in df_filtrado.columns else 0
        st.metric(
            label="💰 Total Vendas Líquidas",
            value=f"€{total_vendas:,.2f}",
            delta=None
        )
    
    with col2:
        total_quantidade = df_filtrado['Quantidade'].sum() if 'Quantidade' in df_filtrado.columns else 0
        st.metric(
            label="📦 Quantidade Total",
            value=f"{total_quantidade:,.0f}",
            delta=None
        )
    
    with col3:
        num_entidades = df_filtrado['Entidade_Nome'].nunique() if 'Entidade_Nome' in df_filtrado.columns else 0
        ticket_medio = total_vendas / num_entidades if num_entidades > 0 else 0
        st.metric(
            label="👥 Ticket Médio/Entidade",
            value=f"€{ticket_medio:,.2f}",
            delta=None
        )
    
    with col4:
        num_comerciais = df_filtrado['Comercial'].nunique() if 'Comercial' in df_filtrado.columns else 0
        st.metric(
            label="👨‍💼 Comerciais Ativos",
            value=num_comerciais,
            delta=None
        )
    
    # KPIs adicionais
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        num_artigos = df_filtrado['Artigo'].nunique() if 'Artigo' in df_filtrado.columns else 0
        st.metric(
            label="🛒 Artigos Vendidos",
            value=num_artigos,
            delta=None
        )
    
    with col6:
        preco_medio = df_filtrado['V_Liquido'].sum() / total_quantidade if total_quantidade > 0 else 0
        st.metric(
            label="🏷️ Preço Médio Unitário",
            value=f"€{preco_medio:,.2f}",
            delta=None
        )
    
    with col7:
        # Venda média por transação
        venda_media_transacao = total_vendas / len(df_filtrado) if len(df_filtrado) > 0 else 0
        st.metric(
            label="💳 Venda Média/Transação",
            value=f"€{venda_media_transacao:,.2f}",
            delta=None
        )
    
    with col8:
        # Quantidade média por transação
        qtd_media_transacao = total_quantidade / len(df_filtrado) if len(df_filtrado) > 0 else 0
        st.metric(
            label="📊 Quantidade Média/Transação",
            value=f"{qtd_media_transacao:,.1f}",
            delta=None
        )
    
    st.markdown("---")
    
    # Gráficos e Análises em Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral", 
        "👥 Por Entidade", 
        "🛒 Por Artigo", 
        "👨‍💼 Por Comercial",
        "📈 Tendências"
    ])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição por Mês (com todos os meses selecionados)
            if 'Mes_PT' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
                vendas_por_mes = df_filtrado.groupby('Mes_PT')['V_Liquido'].sum().reset_index()
                
                # Ordenar por ordem cronológica
                ordem_meses = list(mes_pt_en.keys())
                vendas_por_mes['Mes_Ordem'] = vendas_por_mes['Mes_PT'].apply(
                    lambda x: ordem_meses.index(x) if x in ordem_meses else 99
                )
                vendas_por_mes = vendas_por_mes.sort_values('Mes_Ordem')
                
                fig = px.bar(
                    vendas_por_mes,
                    x='Mes_PT',
                    y='V_Liquido',
                    title='📅 Vendas por Mês',
                    color='V_Liquido',
                    color_continuous_scale='Blues',
                    text_auto='.2s'
                )
                fig.update_layout(
                    xaxis_title="Mês",
                    yaxis_title="Vendas Líquidas (€)",
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distribuição por Dia da Semana
            if 'Dia_Semana' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
                dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                dias_pt = {
                    'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
                    'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado',
                    'Sunday': 'Domingo'
                }
                
                vendas_por_dia = df_filtrado.copy()
                vendas_por_dia['Dia_PT'] = vendas_por_dia['Dia_Semana'].map(dias_pt)
                vendas_por_dia = vendas_por_dia.groupby('Dia_Semana')['V_Liquido'].sum().reset_index()
                
                # Ordenar
                vendas_por_dia['Dia_Ordem'] = vendas_por_dia['Dia_Semana'].apply(
                    lambda x: dias_ordem.index(x) if x in dias_ordem else 99
                )
                vendas_por_dia = vendas_por_dia.sort_values('Dia_Ordem')
                vendas_por_dia['Dia_PT'] = vendas_por_dia['Dia_Semana'].map(dias_pt)
                
                fig = px.line(
                    vendas_por_dia,
                    x='Dia_PT',
                    y='V_Liquido',
                    title='📆 Vendas por Dia da Semana',
                    markers=True,
                    line_shape='spline'
                )
                fig.update_layout(
                    xaxis_title="Dia da Semana",
                    yaxis_title="Vendas Líquidas (€)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 15 Entidades por Vendas
            if 'Entidade_Nome' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
                top_entidades = df_filtrado.groupby('Entidade_Nome').agg({
                    'V_Liquido': 'sum',
                    'Quantidade': 'sum',
                    'Data': 'count'
                }).reset_index()
                top_entidades = top_entidades.sort_values('V_Liquido', ascending=False).head(15)
                top_entidades.columns = ['Entidade', 'Total Vendas (€)', 'Quantidade Total', 'Nº Compras']
                
                # Formatar para exibição
                top_entidades_display = top_entidades.copy()
                top_entidades_display['Total Vendas (€)'] = top_entidades_display['Total Vendas (€)'].apply(
                    lambda x: f"€{x:,.2f}"
                )
                
                st.subheader("🏆 Top 15 Entidades por Vendas")
                st.dataframe(
                    top_entidades_display,
                    use_container_width=True,
                    height=400
                )
        
        with col2:
            # Gráfico de pizza para distribuição de vendas por entidade (Top 10)
            if 'Entidade_Nome' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
                top_10_entidades = df_filtrado.groupby('Entidade_Nome')['V_Liquido'].sum().reset_index()
                top_10_entidades = top_10_entidades.sort_values('V_Liquido', ascending=False).head(10)
                
                # Calcular "Outros"
                outros_vendas = df_filtrado['V_Liquido'].sum() - top_10_entidades['V_Liquido'].sum()
                
                if outros_vendas > 0:
                    outros_row = pd.DataFrame({
                        'Entidade_Nome': ['Outras Entidades'],
                        'V_Liquido': [outros_vendas]
                    })
                    top_10_entidades = pd.concat([top_10_entidades, outros_row])
                
                fig = px.pie(
                    top_10_entidades,
                    values='V_Liquido',
                    names='Entidade_Nome',
                    title='🍰 Distribuição de Vendas por Entidade (Top 10 + Outros)',
                    hole=0.3
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 15 Artigos por Quantidade
            if 'Artigo' in df_filtrado.columns and 'Quantidade' in df_filtrado.columns:
                top_artigos_qtd = df_filtrado.groupby('Artigo').agg({
                    'Quantidade': 'sum',
                    'V_Liquido': 'sum',
                    'Preco_Medio': 'mean'
                }).reset_index()
                top_artigos_qtd = top_artigos_qtd.sort_values('Quantidade', ascending=False).head(15)
                
                fig = px.bar(
                    top_artigos_qtd,
                    x='Artigo',
                    y='Quantidade',
                    title='📦 Top 15 Artigos por Quantidade Vendida',
                    color='V_Liquido',
                    color_continuous_scale='Viridis',
                    hover_data=['V_Liquido', 'Preco_Medio'],
                    text_auto=',.0f'
                )
                fig.update_layout(
                    xaxis_title="Artigo",
                    yaxis_title="Quantidade Vendida",
                    xaxis_tickangle=45,
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top 15 Artigos por Valor
            if 'Artigo' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
                top_artigos_valor = df_filtrado.groupby('Artigo').agg({
                    'V_Liquido': 'sum',
                    'Quantidade': 'sum',
                    'Preco_Medio': 'mean'
                }).reset_index()
                top_artigos_valor = top_artigos_valor.sort_values('V_Liquido', ascending=False).head(15)
                
                fig = px.bar(
                    top_artigos_valor,
                    x='Artigo',
                    y='V_Liquido',
                    title='💰 Top 15 Artigos por Valor de Vendas',
                    color='Preco_Medio',
                    color_continuous_scale='Reds',
                    hover_data=['Quantidade', 'Preco_Medio'],
                    text_auto='.2s'
                )
                fig.update_layout(
                    xaxis_title="Artigo",
                    yaxis_title="Valor de Vendas (€)",
                    xaxis_tickangle=45,
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            # Performance por Comercial (Ranking)
            if 'Comercial' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
                performance_comercial = df_filtrado.groupby('Comercial').agg({
                    'V_Liquido': 'sum',
                    'Quantidade': 'sum',
                    'Entidade_Nome': 'nunique',
                    'Data': 'count'
                }).reset_index()
                
                performance_comercial = performance_comercial.sort_values('V_Liquido', ascending=False)
                performance_comercial.columns = ['Comercial', 'Total Vendas (€)', 'Quantidade', 'Clientes Únicos', 'Nº Transações']
                
                # Calcular métricas adicionais
                performance_comercial['Venda Média'] = performance_comercial['Total Vendas (€)'] / performance_comercial['Nº Transações']
                performance_comercial['Clientes/Transação'] = performance_comercial['Clientes Únicos'] / performance_comercial['Nº Transações']
                
                # Formatar para exibição
                perf_display = performance_comercial.copy()
                perf_display['Total Vendas (€)'] = perf_display['Total Vendas (€)'].apply(lambda x: f"€{x:,.2f}")
                perf_display['Venda Média'] = perf_display['Venda Média'].apply(lambda x: f"€{x:,.2f}")
                perf_display['Clientes/Transação'] = perf_display['Clientes/Transação'].apply(lambda x: f"{x:.2f}")
                
                st.subheader("🏆 Ranking de Comerciais")
                st.dataframe(
                    perf_display,
                    use_container_width=True,
                    height=400
                )
        
        with col2:
            # Gráfico de dispersão: Vendas vs Clientes por Comercial
            if 'Comercial' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
                scatter_data = df_filtrado.groupby('Comercial').agg({
                    'V_Liquido': 'sum',
                    'Entidade_Nome': 'nunique',
                    'Quantidade': 'sum'
                }).reset_index()
                
                fig = px.scatter(
                    scatter_data,
                    x='Entidade_Nome',
                    y='V_Liquido',
                    size='Quantidade',
                    color='Comercial',
                    hover_name='Comercial',
                    title='🎯 Vendas vs Clientes por Comercial',
                    size_max=40,
                    labels={
                        'Entidade_Nome': 'Nº de Clientes Únicos',
                        'V_Liquido': 'Total Vendas (€)'
                    }
                )
                fig.update_layout(
                    height=500,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        # Análise temporal detalhada
        if 'Data' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
            # Agrupar por dia
            df_filtrado['Data_Dia'] = df_filtrado['Data'].dt.date
            vendas_diarias = df_filtrado.groupby('Data_Dia').agg({
                'V_Liquido': 'sum',
                'Quantidade': 'sum',
                'Entidade_Nome': 'nunique',
                'Artigo': 'nunique'
            }).reset_index()
            
            # Criar gráfico com 4 eixos Y
            fig = go.Figure()
            
            # Linha para vendas (eixo Y1)
            fig.add_trace(go.Scatter(
                x=vendas_diarias['Data_Dia'],
                y=vendas_diarias['V_Liquido'],
                mode='lines+markers',
                name='Vendas Líquidas (€)',
                line=dict(color='blue', width=2),
                yaxis='y1'
            ))
            
            # Barras para quantidade (eixo Y2)
            fig.add_trace(go.Bar(
                x=vendas_diarias['Data_Dia'],
                y=vendas_diarias['Quantidade'],
                name='Quantidade Vendida',
                marker_color='lightblue',
                opacity=0.6,
                yaxis='y2'
            ))
            
            # Linha para clientes únicos (eixo Y3)
            fig.add_trace(go.Scatter(
                x=vendas_diarias['Data_Dia'],
                y=vendas_diarias['Entidade_Nome'],
                mode='lines',
                name='Clientes Únicos',
                line=dict(color='green', width=2, dash='dash'),
                yaxis='y3'
            ))
            
            # Linha para artigos únicos (eixo Y4)
            fig.add_trace(go.Scatter(
                x=vendas_diarias['Data_Dia'],
                y=vendas_diarias['Artigo'],
                mode='lines',
                name='Artigos Únicos',
                line=dict(color='orange', width=2, dash='dot'),
                yaxis='y4'
            ))
            
            fig.update_layout(
                title='📈 Evolução Diária - Múltiplas Métricas',
                xaxis=dict(title='Data'),
                yaxis=dict(
                    title='Vendas Líquidas (€)',
                    titlefont=dict(color='blue'),
                    tickfont=dict(color='blue')
                ),
                yaxis2=dict(
                    title='Quantidade',
                    titlefont=dict(color='lightblue'),
                    tickfont=dict(color='lightblue'),
                    overlaying='y',
                    side='right',
                    position=0.85
                ),
                yaxis3=dict(
                    title='Clientes Únicos',
                    titlefont=dict(color='green'),
                    tickfont=dict(color='green'),
                    overlaying='y',
                    side='right',
                    position=0.70
                ),
                yaxis4=dict(
                    title='Artigos Únicos',
                    titlefont=dict(color='orange'),
                    tickfont=dict(color='orange'),
                    overlaying='y',
                    side='right',
                    position=0.55
                ),
                hovermode='x unified',
                height=500,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estatísticas de tendência
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if len(vendas_diarias) > 1:
                    crescimento = ((vendas_diarias['V_Liquido'].iloc[-1] / vendas_diarias['V_Liquido'].iloc[0]) - 1) * 100
                    st.metric(
                        "📈 Crescimento Vendas",
                        f"{crescimento:+.1f}%"
                    )
            
            with col2:
                if len(vendas_diarias) > 1:
                    media_diaria = vendas_diarias['V_Liquido'].mean()
                    st.metric(
                        "📊 Média Diária",
                        f"€{media_diaria:,.2f}"
                    )
            
            with col3:
                melhor_dia = vendas_diarias.loc[vendas_diarias['V_Liquido'].idxmax()]
                st.metric(
                    "🏆 Melhor Dia",
                    f"€{melhor_dia['V_Liquido']:,.2f}"
                )
                st.caption(f"Data: {melhor_dia['Data_Dia']}")
    
    # Seção de Dados Detalhados
    st.markdown("---")
    st.header("📋 Dados Detalhados")
    
    # Opções de visualização
    col_view1, col_view2, col_view3 = st.columns([2, 1, 1])
    
    with col_view1:
        view_option = st.radio(
            "Selecione a visualização:",
            ["Visão Resumida", "Dados Completos Filtrados"],
            horizontal=True,
            index=0
        )
    
    with col_view2:
        num_registros = st.number_input(
            "Nº de registros:",
            min_value=10,
            max_value=500,
            value=50,
            step=10
        )
    
    with col_view3:
        if st.button("📤 Exportar Dados", use_container_width=True):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Criar arquivo Excel com múltiplas abas
            with pd.ExcelWriter(f'vendas_filtradas_{timestamp}.xlsx', engine='openpyxl') as writer:
                df_filtrado.to_excel(writer, sheet_name='Dados Completos', index=False)
                
                # Adicionar resumos
                resumo_entidades = df_filtrado.groupby('Entidade_Nome')['V_Liquido'].sum().reset_index()
                resumo_entidades.to_excel(writer, sheet_name='Resumo Entidades', index=False)
                
                resumo_artigos = df_filtrado.groupby('Artigo').agg({
                    'V_Liquido': 'sum',
                    'Quantidade': 'sum'
                }).reset_index()
                resumo_artigos.to_excel(writer, sheet_name='Resumo Artigos', index=False)
            
            st.success(f"✅ Dados exportados com sucesso!")
            st.balloons()
    
    # Mostrar dados
    if view_option == "Visão Resumida":
        # Colunas importantes para visualização
        colunas_importantes = ['Data', 'Entidade_Nome', 'Artigo', 'Quantidade', 'V_Liquido', 'Preco_Medio', 'Comercial']
        colunas_disponiveis = [col for col in colunas_importantes if col in df_filtrado.columns]
        
        # Formatar dados para exibição
        df_display = df_filtrado[colunas_disponiveis].copy()
        if 'Data' in df_display.columns:
            df_display['Data'] = df_display['Data'].dt.strftime('%Y-%m-%d')
        if 'V_Liquido' in df_display.columns:
            df_display['V_Liquido'] = df_display['V_Liquido'].apply(lambda x: f"€{x:,.2f}")
        if 'Preco_Medio' in df_display.columns:
            df_display['Preco_Medio'] = df_display['Preco_Medio'].apply(lambda x: f"€{x:,.2f}")
        
        st.dataframe(
            df_display.sort_values('Data' if 'Data' in df_display.columns else 'Entidade_Nome', ascending=False).head(num_registros),
            use_container_width=True,
            height=400
        )
    else:
        # Todos os dados filtrados
        df_display_full = df_filtrado.copy()
        if 'Data' in df_display_full.columns:
            df_display_full['Data'] = df_display_full['Data'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            df_display_full.sort_values('Data' if 'Data' in df_display_full.columns else 'Entidade_Nome', ascending=False),
            use_container_width=True,
            height=500
        )
    
    # Botão de download no rodapé
    st.markdown("---")
    col_download1, col_download2, col_download3 = st.columns([1, 2, 1])
    
    with col_download2:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Criar botão de download para CSV
        csv_data = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Baixar Dados Filtrados (CSV)",
            data=csv_data,
            file_name=f"vendas_filtradas_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Executar o aplicativo
if __name__ == "__main__":
    main()
