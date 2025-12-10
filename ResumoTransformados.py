import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from io import BytesIO

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
    
    .multi-select-container {
        margin-bottom: 20px;
    }
    
    .multi-select-container label {
        font-weight: 600;
        margin-bottom: 8px;
        display: block;
        color: #1f77b4;
    }
    
    /* Botões de ação */
    .action-buttons {
        display: flex;
        gap: 10px;
        margin-top: 20px;
    }
    
    .action-buttons button {
        flex: 1;
    }
    
    /* Status dos filtros */
    .filter-status {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #28a745;
    }
    
    .filter-status h4 {
        margin-top: 0;
        color: #28a745;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

# Função para criar Excel com múltiplas abas
def create_excel_with_sheets(df_filtrado, kpis_data, top_entidades, top_artigos, performance_comercial):
    """Cria um arquivo Excel com múltiplas abas contendo todas as análises"""
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # 1. Dados Filtrados
        df_filtrado.to_excel(writer, sheet_name='Dados_Filtrados', index=False)
        
        # 2. KPIs Principais
        kpis_df = pd.DataFrame({
            'KPI': list(kpis_data.keys()),
            'Valor': list(kpis_data.values())
        })
        kpis_df.to_excel(writer, sheet_name='KPIs_Principais', index=False)
        
        # 3. Top Entidades
        if top_entidades is not None:
            top_entidades.to_excel(writer, sheet_name='Top_Entidades', index=False)
        
        # 4. Top Artigos
        if top_artigos is not None:
            top_artigos.to_excel(writer, sheet_name='Top_Artigos', index=False)
        
        # 5. Performance Comercial
        if performance_comercial is not None:
            performance_comercial.to_excel(writer, sheet_name='Performance_Comercial', index=False)
        
        # 6. Resumo por Mês
        if 'Mes_PT' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
            resumo_mes = df_filtrado.groupby('Mes_PT').agg({
                'V_Liquido': 'sum',
                'Quantidade': 'sum',
                'Entidade_Nome': 'nunique'
            }).reset_index()
            resumo_mes.to_excel(writer, sheet_name='Resumo_Mensal', index=False)
        
        # 7. Resumo por Comercial
        if 'Comercial' in df_filtrado.columns:
            resumo_comercial = df_filtrado.groupby('Comercial').agg({
                'V_Liquido': 'sum',
                'Quantidade': 'sum',
                'Entidade_Nome': 'nunique'
            }).reset_index()
            resumo_comercial.to_excel(writer, sheet_name='Resumo_Comercial', index=False)
        
        # 8. Estatísticas Detalhadas
        estatisticas = {
            'Métrica': [
                'Total Registros', 'Total Vendas (€)', 'Total Quantidade',
                'Média Vendas/Registro', 'Média Quantidade/Registro',
                'Nº Entidades Únicas', 'Nº Artigos Únicos', 'Nº Comerciais Únicos'
            ],
            'Valor': [
                len(df_filtrado),
                df_filtrado['V_Liquido'].sum() if 'V_Liquido' in df_filtrado.columns else 0,
                df_filtrado['Quantidade'].sum() if 'Quantidade' in df_filtrado.columns else 0,
                df_filtrado['V_Liquido'].mean() if 'V_Liquido' in df_filtrado.columns else 0,
                df_filtrado['Quantidade'].mean() if 'Quantidade' in df_filtrado.columns else 0,
                df_filtrado['Entidade_Nome'].nunique() if 'Entidade_Nome' in df_filtrado.columns else 0,
                df_filtrado['Artigo'].nunique() if 'Artigo' in df_filtrado.columns else 0,
                df_filtrado['Comercial'].nunique() if 'Comercial' in df_filtrado.columns else 0
            ]
        }
        estatisticas_df = pd.DataFrame(estatisticas)
        estatisticas_df.to_excel(writer, sheet_name='Estatisticas', index=False)
        
        # 9. Evolução Diária
        if 'Data' in df_filtrado.columns:
            df_filtrado['Data_Dia'] = df_filtrado['Data'].dt.date
            evolucao_diaria = df_filtrado.groupby('Data_Dia').agg({
                'V_Liquido': 'sum',
                'Quantidade': 'sum',
                'Entidade_Nome': 'nunique'
            }).reset_index()
            evolucao_diaria.to_excel(writer, sheet_name='Evolucao_Diaria', index=False)
    
    output.seek(0)
    return output

# Função para carregar dados COM CORREÇÃO DOS NOMES DAS COLUNAS
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('ResumoTR.xlsx')
        
        # CORREÇÃO CRÍTICA: Renomear colunas do Excel para nomes válidos no código
        column_mapping = {
            'V Líquido': 'V_Liquido',  # Espaço para underscore
            'Nome': 'Entidade_Nome',
            'PM': 'Preco_Medio'
        }
        
        # Aplicar renomeação apenas para colunas que existem
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Garantir que as colunas de data sejam datetime
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            df = df[df['Data'].notna()]
            
            # Extrair informações temporais
            df['Ano'] = df['Data'].dt.year
            df['Mes_Num'] = df['Data'].dt.month
            df['Mes_Nome'] = df['Data'].dt.strftime('%B')
            df['Dia'] = df['Data'].dt.day
            df['Dia_Semana'] = df['Data'].dt.day_name()
        
        # Converter colunas numéricas - USANDO OS NOVOS NOMES
        numeric_cols = ['Quantidade', 'V_Liquido', 'Preco_Medio']  # Agora V_Liquido em vez de 'V Líquido'
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

# Dicionário de meses (global para uso nas funções)
mes_pt_en = {
    'Janeiro': 'January', 'Fevereiro': 'February', 'Março': 'March',
    'Abril': 'April', 'Maio': 'May', 'Junho': 'June',
    'Julho': 'July', 'Agosto': 'August', 'Setembro': 'September',
    'Outubro': 'October', 'Novembro': 'November', 'Dezembro': 'December'
}

# Função para criar todos os filtros multiselect
def create_all_multiselect_filters(df):
    """Cria todos os filtros multiselect na sidebar"""
    
    filtros = {}
    
    with st.sidebar:
        st.header("⚙️ Filtros Dinâmicos")
        st.markdown("📍 **Selecione múltiplos valores em cada filtro**")
        
        # Container para organizar os filtros
        filter_container = st.container()
        
        with filter_container:
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
                st.caption(f"{len(anos_selecionados) if anos_selecionados else len(anos_disponiveis)} ano(s) selecionado(s)")
            
            st.markdown("---")
            
            # Filtro de Mês (Multiselect)
            if 'Mes_PT' in df.columns:
                meses_disponiveis = sorted(df['Mes_PT'].dropna().unique(), 
                                          key=lambda x: list(mes_pt_en.keys()).index(x) if x in mes_pt_en.keys() else 99)
                meses_selecionados = st.multiselect(
                    "**📆 Mês**",
                    options=meses_disponiveis,
                    default=meses_disponiveis,
                    help="Selecione um ou mais meses"
                )
                filtros['meses'] = meses_selecionados if meses_selecionados else meses_disponiveis
                st.caption(f"{len(meses_selecionados) if meses_selecionados else len(meses_disponiveis)} mês(es) selecionado(s)")
            
            st.markdown("---")
            
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
                st.caption(f"{len(comerciais_selecionados) if comerciais_selecionados else len(comerciais_disponiveis)} comercial(is) selecionado(s)")
            
            st.markdown("---")
            
            # Filtro de Entidade (Multiselect)
            if 'Entidade_Nome' in df.columns:
                entidades_disponiveis = sorted(df['Entidade_Nome'].dropna().astype(str).unique())
                entidades_selecionadas = st.multiselect(
                    "**🏢 Entidade (Nome)**",
                    options=entidades_disponiveis,
                    default=[],
                    help="Selecione uma ou mais entidades (deixe vazio para todas)"
                )
                filtros['entidades'] = entidades_selecionadas
                st.caption(f"{len(entidades_selecionadas)} entidade(s) selecionada(s)" if entidades_selecionadas else "Todas as entidades selecionadas")
            
            st.markdown("---")
            
            # Filtro de Artigo (Multiselect) - JÁ CORRIGIDO
            if 'Artigo' in df.columns:
                # Garantir que os artigos sejam strings
                df['Artigo'] = df['Artigo'].astype(str)
                
                # Obter todos os artigos únicos
                artigos_disponiveis = sorted(df['Artigo'].dropna().unique())
                
                # Widget multiselect para artigos
                artigos_selecionados = st.multiselect(
                    "**🛒 Artigo**",
                    options=artigos_disponiveis,
                    default=[],
                    help="Selecione um ou mais artigos (deixe vazio para todos)"
                )
                filtros['artigos'] = artigos_selecionados
                st.caption(f"{len(artigos_selecionados)} artigo(s) selecionado(s)" if artigos_selecionados else "Todos os artigos selecionados")
            
            st.markdown("---")
            
            # Botões de ação
            st.subheader("🎛️ Controles")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Resetar Todos", width='stretch', type="secondary"):
                    st.rerun()
            
            with col2:
                if st.button("✅ Aplicar Filtros", width='stretch', type="primary"):
                    st.rerun()
    
    return filtros

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
        
        # Filtro de Artigo - CORRIGIDO
        if 'artigos' in filtros and filtros['artigos']:
            df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(filtros['artigos'])]
    
    except Exception as e:
        st.error(f"❌ Erro ao aplicar filtros: {str(e)}")
        return df
    
    return df_filtrado

# Função para calcular KPIs
def calculate_kpis(df_filtrado):
    """Calcula todos os KPIs principais"""
    
    kpis = {}
    
    try:
        # KPI 1: Total Vendas - USANDO V_Liquido (já renomeado)
        kpis['Total Vendas (€)'] = df_filtrado['V_Liquido'].sum() if 'V_Liquido' in df_filtrado.columns else 0
        
        # KPI 2: Total Quantidade
        kpis['Total Quantidade'] = df_filtrado['Quantidade'].sum() if 'Quantidade' in df_filtrado.columns else 0
        
        # KPI 3: Número de Entidades
        kpis['Nº Entidades'] = df_filtrado['Entidade_Nome'].nunique() if 'Entidade_Nome' in df_filtrado.columns else 0
        
        # KPI 4: Ticket Médio
        kpis['Ticket Médio (€)'] = kpis['Total Vendas (€)'] / kpis['Nº Entidades'] if kpis['Nº Entidades'] > 0 else 0
        
        # KPI 5: Número de Comerciais
        kpis['Nº Comerciais'] = df_filtrado['Comercial'].nunique() if 'Comercial' in df_filtrado.columns else 0
        
        # KPI 6: Número de Artigos
        kpis['Nº Artigos'] = df_filtrado['Artigo'].nunique() if 'Artigo' in df_filtrado.columns else 0
        
        # KPI 7: Preço Médio Unitário
        kpis['Preço Médio Unitário (€)'] = kpis['Total Vendas (€)'] / kpis['Total Quantidade'] if kpis['Total Quantidade'] > 0 else 0
        
        # KPI 8: Venda Média por Transação
        kpis['Venda Média/Transação (€)'] = kpis['Total Vendas (€)'] / len(df_filtrado) if len(df_filtrado) > 0 else 0
        
        # KPI 9: Quantidade Média por Transação
        kpis['Quantidade Média/Transação'] = kpis['Total Quantidade'] / len(df_filtrado) if len(df_filtrado) > 0 else 0
        
        # KPI 10: Dias com Vendas
        if 'Data' in df_filtrado.columns:
            kpis['Dias com Vendas'] = df_filtrado['Data'].dt.date.nunique()
        
        # KPI 11: Venda Média por Dia
        if 'Data' in df_filtrado.columns and kpis.get('Dias com Vendas', 0) > 0:
            kpis['Venda Média/Dia (€)'] = kpis['Total Vendas (€)'] / kpis['Dias com Vendas']
        
        return kpis
    
    except Exception as e:
        st.error(f"Erro ao calcular KPIs: {str(e)}")
        return {}

# Função principal COM CORREÇÃO DO GRÁFICO PROBLEMÁTICO
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
    
    # DEBUG: Mostrar informações sobre colunas
    with st.expander("🔍 DEBUG: Verificar Colunas"):
        st.write("Colunas disponíveis:", list(df.columns))
        st.write("Primeira linha:", df.iloc[0].to_dict() if len(df) > 0 else "Sem dados")
        if 'V_Liquido' in df.columns:
            st.write("Tipo de V_Liquido:", type(df['V_Liquido'].iloc[0]) if len(df) > 0 else "N/A")
    
    # Sidebar com filtros multiselect
    filtros = create_all_multiselect_filters(df)
    
    # Aplicar filtros
    df_filtrado = apply_filters(df, filtros)
    
    # Calcular KPIs
    kpis = calculate_kpis(df_filtrado)
    
    # Preparar dados para gráficos
    # Top Entidades
    if 'Entidade_Nome' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
        top_entidades = df_filtrado.groupby('Entidade_Nome').agg({
            'V_Liquido': 'sum',
            'Quantidade': 'sum',
            'Data': 'count'
        }).reset_index()
        top_entidades = top_entidades.sort_values('V_Liquido', ascending=False).head(15)
        top_entidades.columns = ['Entidade', 'Total Vendas (€)', 'Quantidade Total', 'Nº Compras']
    else:
        top_entidades = None
    
    # Top Artigos
    if 'Artigo' in df_filtrado.columns:
        top_artigos = df_filtrado.groupby('Artigo').agg({
            'V_Liquido': 'sum',
            'Quantidade': 'sum',
            'Preco_Medio': 'mean'
        }).reset_index()
        top_artigos = top_artigos.sort_values('V_Liquido', ascending=False).head(15)
    else:
        top_artigos = None
    
    # Performance Comercial
    if 'Comercial' in df_filtrado.columns:
        performance_comercial = df_filtrado.groupby('Comercial').agg({
            'V_Liquido': 'sum',
            'Quantidade': 'sum',
            'Entidade_Nome': 'nunique',
            'Data': 'count'
        }).reset_index()
        performance_comercial = performance_comercial.sort_values('V_Liquido', ascending=False)
        performance_comercial['Venda Média'] = performance_comercial['V_Liquido'] / performance_comercial['Data']
    else:
        performance_comercial = None
    
    # Mostrar estatísticas dos filtros na sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("📊 Estatísticas Filtradas")
        
        total_registros = len(df_filtrado)
        total_vendas = kpis.get('Total Vendas (€)', 0)
        total_quantidade = kpis.get('Total Quantidade', 0)
        
        st.success(f"""
        **Registros:** {total_registros:,}
        **Vendas:** €{total_vendas:,.2f}
        **Quantidade:** {total_quantidade:,.0f}
        """)
        
        # Indicador de % dos dados
        if len(df) > 0:
            percentual = (len(df_filtrado) / len(df)) * 100
            st.progress(percentual / 100, text=f"Mostrando {percentual:.1f}% dos dados")
        
        # Botão de download na sidebar também
        st.markdown("---")
        st.subheader("📥 Exportar Dados")
        
        if st.button("📊 Baixar Relatório Completo (Excel)", width='stretch', type="primary"):
            try:
                excel_data = create_excel_with_sheets(
                    df_filtrado, 
                    kpis, 
                    top_entidades, 
                    top_artigos, 
                    performance_comercial
                )
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                st.download_button(
                    label="⬇️ Clique para Baixar",
                    data=excel_data.getvalue(),
                    file_name=f"relatorio_vendas_completo_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width='stretch'
                )
                st.success("✅ Relatório gerado com sucesso!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erro ao gerar relatório: {str(e)}")
    
    # Seção de KPIs
    st.header("📈 KPIs Principais")
    
    # Criar 3 linhas de KPIs (4 colunas cada)
    kpi_rows = []
    kpi_items = list(kpis.items())
    
    for i in range(0, len(kpi_items), 4):
        kpi_rows.append(kpi_items[i:i+4])
    
    for row in kpi_rows:
        cols = st.columns(len(row))
        for idx, (label, value) in enumerate(row):
            with cols[idx]:
                # Formatar valores
                if '€' in label:
                    display_value = f"€{value:,.2f}"
                elif value == int(value):
                    display_value = f"{value:,.0f}"
                else:
                    display_value = f"{value:,.2f}"
                
                st.metric(
                    label=label,
                    value=display_value
                )
    
    st.markdown("---")
    
    # Gráficos e Análises em Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Visão Geral", 
        "👥 Por Entidade", 
        "🛒 Por Artigo", 
        "👨‍💼 Por Comercial",
        "📈 Tendências",
        "📋 Dados Detalhados"
    ])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição por Mês
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
                st.plotly_chart(fig, width='stretch')
        
        with col2:
            # Distribuição por Comercial
            if 'Comercial' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
                vendas_por_comercial = df_filtrado.groupby('Comercial')['V_Liquido'].sum().reset_index()
                vendas_por_comercial = vendas_por_comercial.sort_values('V_Liquido', ascending=False).head(10)
                
                fig = px.pie(
                    vendas_por_comercial,
                    values='V_Liquido',
                    names='Comercial',
                    title='👨‍💼 Distribuição por Comercial (Top 10)',
                    hole=0.3
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, width='stretch')
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            if top_entidades is not None:
                st.subheader("🏆 Top 15 Entidades por Vendas")
                
                # Formatar para exibição
                top_entidades_display = top_entidades.copy()
                top_entidades_display['Total Vendas (€)'] = top_entidades_display['Total Vendas (€)'].apply(
                    lambda x: f"€{x:,.2f}"
                )
                
                st.dataframe(
                    top_entidades_display,
                    width='stretch',
                    height=400
                )
        
        with col2:
            if 'Entidade_Nome' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
                # Gráfico de barras para top entidades
                top_10_entidades = df_filtrado.groupby('Entidade_Nome')['V_Liquido'].sum().reset_index()
                top_10_entidades = top_10_entidades.sort_values('V_Liquido', ascending=False).head(10)
                
                fig = px.bar(
                    top_10_entidades,
                    x='Entidade_Nome',
                    y='V_Liquido',
                    title='📊 Top 10 Entidades por Vendas',
                    color='V_Liquido',
                    color_continuous_scale='Greens',
                    text_auto='.2s'
                )
                fig.update_layout(
                    xaxis_title="Entidade",
                    yaxis_title="Vendas (€)",
                    xaxis_tickangle=45,
                    height=400
                )
                st.plotly_chart(fig, width='stretch')
    
    with tab3:
        st.markdown("### 📦 Análise por Artigo")
        
        if top_artigos is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                # Top artigos por quantidade
                top_artigos_qtd = top_artigos.sort_values('Quantidade', ascending=False)
                
                fig = px.bar(
                    top_artigos_qtd.head(10),
                    x='Artigo',
                    y='Quantidade',
                    title='📦 Top 10 Artigos por Quantidade',
                    color='Quantidade',
                    color_continuous_scale='Blues',
                    text_auto=',.0f'
                )
                fig.update_layout(
                    xaxis_title="Artigo",
                    yaxis_title="Quantidade",
                    xaxis_tickangle=45,
                    height=400
                )
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                # Top artigos por valor
                top_artigos_valor = top_artigos.sort_values('V_Liquido', ascending=False)
                
                fig = px.bar(
                    top_artigos_valor.head(10),
                    x='Artigo',
                    y='V_Liquido',
                    title='💰 Top 10 Artigos por Valor',
                    color='V_Liquido',
                    color_continuous_scale='Reds',
                    text_auto='.2s'
                )
                fig.update_layout(
                    xaxis_title="Artigo",
                    yaxis_title="Vendas (€)",
                    xaxis_tickangle=45,
                    height=400
                )
                st.plotly_chart(fig, width='stretch')
            
            # Tabela detalhada de artigos
            st.markdown("### 📋 Detalhes dos Artigos")
            artigos_detalhes = top_artigos.copy()
            artigos_detalhes['V_Liquido'] = artigos_detalhes['V_Liquido'].apply(lambda x: f"€{x:,.2f}")
            artigos_detalhes['Preco_Medio'] = artigos_detalhes['Preco_Medio'].apply(lambda x: f"€{x:,.2f}")
            artigos_detalhes.columns = ['Artigo', 'Vendas (€)', 'Quantidade', 'Preço Médio (€)']
            
            st.dataframe(
                artigos_detalhes,
                width='stretch',
                height=300
            )
    
    with tab4:
        st.markdown("### 👨‍💼 Performance Comercial")
        
        if performance_comercial is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                # Ranking de comerciais
                perf_display = performance_comercial.copy()
                perf_display['V_Liquido'] = perf_display['V_Liquido'].apply(lambda x: f"€{x:,.2f}")
                perf_display['Venda Média'] = perf_display['Venda Média'].apply(lambda x: f"€{x:,.2f}")
                perf_display.columns = ['Comercial', 'Vendas (€)', 'Quantidade', 'Clientes', 'Transações', 'Venda Média']
                
                st.dataframe(
                    perf_display,
                    width='stretch',
                    height=400
                )
            
            with col2:
                # Gráfico de comparação
                fig = px.bar(
                    performance_comercial.head(10),
                    x='Comercial',
                    y=['V_Liquido', 'Entidade_Nome'],
                    title='📊 Comparação: Vendas vs Clientes',
                    barmode='group',
                    labels={'value': 'Valor', 'variable': 'Métrica'}
                )
                fig.update_layout(
                    xaxis_title="Comercial",
                    yaxis_title="Valor",
                    height=400
                )
                st.plotly_chart(fig, width='stretch')
    
    with tab5:
        # ANÁLISE TEMPORAL - VERSÃO CORRIGIDA E SEGURA
        st.subheader("📈 Evolução Diária de Vendas")
        
        if 'Data' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
            try:
                # Preparar dados
                df_filtrado['Data_Dia'] = df_filtrado['Data'].dt.date
                
                # Agrupar por dia - VERIFICANDO SE TEM DADOS
                evolucao = df_filtrado.groupby('Data_Dia').agg({
                    'V_Liquido': 'sum',
                    'Quantidade': 'sum',
                    'Entidade_Nome': 'nunique'
                }).reset_index()
                
                if len(evolucao) == 0:
                    st.info("Sem dados para mostrar na evolução diária.")
                else:
                    # Converter datas para string para evitar problemas
                    evolucao['Data_Dia'] = evolucao['Data_Dia'].astype(str)
                    
                    # VERIFICAÇÃO CRÍTICA: Garantir que os valores são numéricos
                    evolucao['V_Liquido'] = pd.to_numeric(evolucao['V_Liquido'], errors='coerce').fillna(0)
                    evolucao['Quantidade'] = pd.to_numeric(evolucao['Quantidade'], errors='coerce').fillna(0)
                    
                    # Gráfico de linha SIMPLIFICADO primeiro
                    st.markdown("#### Vendas Diárias")
                    fig_simple = px.line(
                        evolucao,
                        x='Data_Dia',
                        y='V_Liquido',
                        title='Vendas Diárias',
                        markers=True
                    )
                    fig_simple.update_layout(height=300)
                    st.plotly_chart(fig_simple, width='stretch')
                    
                    # Gráfico com eixo secundário - COM TRY-EXCEPT
                    st.markdown("#### Vendas vs Quantidade (Eixo Duplo)")
                    try:
                        # Criar figura
                        fig = go.Figure()
                        
                        # Adicionar linha de vendas
                        fig.add_trace(go.Scatter(
                            x=evolucao['Data_Dia'],
                            y=evolucao['V_Liquido'],
                            mode='lines+markers',
                            name='Vendas (€)',
                            line=dict(color='blue', width=2)
                        ))
                        
                        # Adicionar barras de quantidade
                        fig.add_trace(go.Bar(
                            x=evolucao['Data_Dia'],
                            y=evolucao['Quantidade'],
                            name='Quantidade',
                            marker_color='lightblue',
                            opacity=0.6,
                            yaxis='y2'
                        ))
                        
                        # Atualizar layout COM VALIDAÇÃO
                        fig.update_layout(
                            title=dict(text='Vendas vs Quantidade Diária'),
                            xaxis=dict(title='Data'),
                            yaxis=dict(
                                title='Vendas (€)',
                                titlefont=dict(color='blue'),
                                tickfont=dict(color='blue')
                            ),
                            yaxis2=dict(
                                title='Quantidade',
                                titlefont=dict(color='lightblue'),
                                tickfont=dict(color='lightblue'),
                                overlaying='y',
                                side='right'
                            ),
                            hovermode='x unified',
                            height=400
                        )
                        
                        st.plotly_chart(fig, width='stretch')
                        
                    except Exception as e:
                        st.error(f"Erro no gráfico de eixo duplo: {str(e)}")
                        # Fallback: mostrar gráfico simples
                        st.info("Mostrando gráfico simplificado devido a erro no gráfico de eixo duplo.")
                        fig_fallback = px.line(
                            evolucao,
                            x='Data_Dia',
                            y=['V_Liquido', 'Quantidade'],
                            title='Vendas e Quantidade Diárias',
                            markers=True
                        )
                        fig_fallback.update_layout(height=400)
                        st.plotly_chart(fig_fallback, width='stretch')
            
            except Exception as e:
                st.error(f"Erro na análise temporal: {str(e)}")
                # Mostrar informações de debug
                with st.expander("🔍 Detalhes do Erro"):
                    if 'df_filtrado' in locals():
                        st.write("Colunas disponíveis:", list(df_filtrado.columns))
                        if 'Data' in df_filtrado.columns:
                            st.write("Tipo da coluna Data:", df_filtrado['Data'].dtype)
                        if 'V_Liquido' in df_filtrado.columns:
                            st.write("Primeiros valores de V_Liquido:", df_filtrado['V_Liquido'].head().tolist())
        else:
            st.warning("Colunas 'Data' ou 'V_Liquido' não encontradas nos dados filtrados.")
    
    with tab6:
        st.header("📋 Dados Detalhados")
        
        # Controles de visualização
        col_controls1, col_controls2, col_controls3 = st.columns([2, 1, 2])
        
        with col_controls1:
            view_option = st.radio(
                "Tipo de visualização:",
                ["Visão Resumida", "Dados Completos"],
                horizontal=True,
                index=0
            )
        
        with col_controls2:
            if view_option == "Visão Resumida":
                num_records = st.number_input(
                    "Nº registros:",
                    min_value=10,
                    max_value=200,
                    value=50,
                    step=10
                )
        
        with col_controls3:
            # Botão para download Excel completo
            if st.button("📊 Baixar Relatório Completo Excel", type="primary", width='stretch'):
                try:
                    excel_data = create_excel_with_sheets(
                        df_filtrado, 
                        kpis, 
                        top_entidades, 
                        top_artigos, 
                        performance_comercial
                    )
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    
                    st.download_button(
                        label="⬇️ Clique para Baixar Excel",
                        data=excel_data.getvalue(),
                        file_name=f"relatorio_vendas_completo_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width='stretch'
                    )
                    
                    st.success("✅ Relatório Excel gerado com sucesso!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Erro ao gerar relatório: {str(e)}")
        
        # Mostrar dados
        if view_option == "Visão Resumida":
            # Colunas para visualização
            display_cols = ['Data', 'Entidade_Nome', 'Artigo', 'Quantidade', 'V_Liquido', 'Comercial']
            available_cols = [col for col in display_cols if col in df_filtrado.columns]
            
            df_display = df_filtrado[available_cols].copy()
            
            # Formatar datas
            if 'Data' in df_display.columns:
                df_display['Data'] = df_display['Data'].dt.strftime('%Y-%m-%d')
            
            # Formatar valores monetários
            if 'V_Liquido' in df_display.columns:
                df_display['V_Liquido'] = df_display['V_Liquido'].apply(lambda x: f"€{x:,.2f}")
            
            st.dataframe(
                df_display.head(num_records),
                width='stretch',
                height=400
            )
        else:
            # Dados completos
            df_full_display = df_filtrado.copy()
            
            # Formatar datas
            if 'Data' in df_full_display.columns:
                df_full_display['Data'] = df_full_display['Data'].dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                df_full_display,
                width='stretch',
                height=500
            )
        
        # Estatísticas descritivas
        with st.expander("📊 Estatísticas Descritivas Detalhadas"):
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            with col_stats1:
                if 'V_Liquido' in df_filtrado.columns:
                    st.subheader("Vendas (€)")
                    stats_v = df_filtrado['V_Liquido'].describe()
                    for stat, val in stats_v.items():
                        st.write(f"**{stat}:** €{val:,.2f}")
            
            with col_stats2:
                if 'Quantidade' in df_filtrado.columns:
                    st.subheader("Quantidade")
                    stats_q = df_filtrado['Quantidade'].describe()
                    for stat, val in stats_q.items():
                        st.write(f"**{stat}:** {val:,.2f}")
            
            with col_stats3:
                if 'Preco_Medio' in df_filtrado.columns:
                    st.subheader("Preço Médio (€)")
                    stats_p = df_filtrado['Preco_Medio'].describe()
                    for stat, val in stats_p.items():
                        st.write(f"**{stat}:** €{val:,.2f}")
    
    # Rodapé com opções de download
    st.markdown("---")
    st.markdown("### 📥 Opções de Exportação")
    
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    with col_dl1:
        # Download CSV dos dados filtrados
        csv_data = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        st.download_button(
            label="📄 Baixar CSV (Dados Filtrados)",
            data=csv_data,
            file_name=f"dados_filtrados_{timestamp}.csv",
            mime="text/csv",
            width='stretch'
        )
    
    with col_dl2:
        # Download CSV com resumo
        if top_entidades is not None:
            resumo_data = top_entidades.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="📊 Baixar CSV (Resumo Entidades)",
                data=resumo_data,
                file_name=f"resumo_entidades_{timestamp}.csv",
                mime="text/csv",
                width='stretch'
            )
    
    with col_dl3:
        # Download Excel completo (botão secundário)
        if st.button("📁 Gerar Relatório Excel Completo", width='stretch', type="secondary"):
            try:
                excel_data = create_excel_with_sheets(
                    df_filtrado, 
                    kpis, 
                    top_entidades, 
                    top_artigos, 
                    performance_comercial
                )
                
                st.download_button(
                    label="⬇️ Baixar Excel Completo",
                    data=excel_data.getvalue(),
                    file_name=f"relatorio_completo_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width='stretch'
                )
            except Exception as e:
                st.error(f"❌ Erro ao gerar Excel: {str(e)}")

# Executar o aplicativo
if __name__ == "__main__":
    main()
