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
    
    /* Melhorar visualização dos filtros */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        padding: 20px;
    }
    
    /* Cards para KPIs */
    .kpi-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

# Função para carregar dados com tratamento robusto
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
            df['Mes'] = df['Data'].dt.month
            df['Mes_Nome'] = df['Data'].dt.strftime('%B')
            df['Dia'] = df['Data'].dt.day
            df['Semana'] = df['Data'].dt.isocalendar().week
        
        # Converter colunas numéricas com tratamento de erros
        numeric_cols = ['Quantidade', 'V_Liquido', 'Preco_Medio']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Substituir NaN por 0 para evitar problemas nas somas
                df[col] = df[col].fillna(0)
        
        # Verificar se coluna de Comercial existe, se não, criar uma padrão
        if 'Comercial' not in df.columns:
            df['Comercial'] = 'Não Informado'
        
        # Verificar se coluna de Artigo existe
        if 'Artigo' not in df.columns:
            # Procurar por colunas que podem conter o nome do artigo
            possible_article_cols = ['Artigo', 'Produto', 'Item', 'Descricao']
            for col in possible_article_cols:
                if col in df.columns:
                    df = df.rename(columns={col: 'Artigo'})
                    break
        
        return df
    
    except FileNotFoundError:
        st.error("❌ Arquivo 'ResumoTR.xlsx' não encontrado!")
        st.info("Certifique-se de que o arquivo está na mesma pasta do script.")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return None

# Função principal com tratamento de erros
def main():
    add_custom_css()
    
    # Título e descrição
    st.title("📊 Dashboard de Análise de Vendas - ResumoTR")
    st.markdown("---")
    
    # Carregar dados
    with st.spinner('Carregando dados...'):
        df = load_data()
    
    if df is None or df.empty:
        st.error("❌ Não foi possível carregar os dados. Verifique o arquivo.")
        
        # Mostrar exemplo de estrutura esperada
        with st.expander("ℹ️ Estrutura esperada do arquivo"):
            st.code("""
            Colunas esperadas:
            - Entidade (ID)
            - Nome (Nome da empresa/cliente)
            - Artigo (Nome do produto)
            - Quantidade
            - Unidade
            - V Líquido (Valor líquido)
            - PM (Preço médio)
            - Data
            - Comercial (Nome do vendedor)
            - Mês
            - Ano
            """)
        return
    
    # Mostrar informações básicas sobre os dados
    with st.sidebar:
        st.header("ℹ️ Informações dos Dados")
        st.info(f"""
        **Registros:** {len(df):,}
        **Período:** {df['Data'].min().date()} a {df['Data'].max().date()}
        **Entidades:** {df['Entidade_Nome'].nunique() if 'Entidade_Nome' in df.columns else 0:,}
        **Artigos:** {df['Artigo'].nunique() if 'Artigo' in df.columns else 0:,}
        """)
    
    # Sidebar - Filtros
    with st.sidebar:
        st.header("⚙️ Filtros Dinâmicos")
        
        # Filtro de Ano (dinâmico)
        if 'Ano' in df.columns:
            anos_disponiveis = sorted(df['Ano'].dropna().unique())
            if len(anos_disponiveis) > 0:
                ano_selecionado = st.selectbox(
                    "**Ano**",
                    options=["Todos"] + list(anos_disponiveis),
                    index=0 if len(anos_disponiveis) == 1 else 0
                )
            else:
                ano_selecionado = "Todos"
                st.warning("Nenhum ano disponível nos dados")
        else:
            ano_selecionado = "Todos"
            st.warning("Coluna 'Ano' não encontrada")
        
        # Filtro de Mês (dinâmico)
        if 'Mes_Nome' in df.columns:
            meses_disponiveis = sorted(df['Mes_Nome'].dropna().unique())
            if len(meses_disponiveis) > 0:
                mes_selecionado = st.selectbox(
                    "**Mês**",
                    options=["Todos"] + list(meses_disponiveis),
                    index=0
                )
            else:
                mes_selecionado = "Todos"
                st.warning("Nenhum mês disponível nos dados")
        else:
            mes_selecionado = "Todos"
        
        # Filtro de Comercial (dinâmico)
        if 'Comercial' in df.columns:
            comerciais_disponiveis = sorted(df['Comercial'].dropna().unique())
            if len(comerciais_disponiveis) > 0:
                comercial_selecionado = st.selectbox(
                    "**Comercial**",
                    options=["Todos"] + list(comerciais_disponiveis),
                    index=0
                )
            else:
                comercial_selecionado = "Todos"
                st.warning("Nenhum comercial disponível nos dados")
        else:
            comercial_selecionado = "Todos"
        
        # Filtro de Entidade/Nome (dinâmico)
        if 'Entidade_Nome' in df.columns:
            try:
                entidades_disponiveis = sorted(df['Entidade_Nome'].dropna().astype(str).unique())
                if len(entidades_disponiveis) > 0:
                    entidade_selecionada = st.selectbox(
                        "**Entidade (Nome)**",
                        options=["Todas"] + list(entidades_disponiveis),
                        index=0
                    )
                else:
                    entidade_selecionada = "Todas"
                    st.warning("Nenhuma entidade disponível nos dados")
            except Exception as e:
                entidade_selecionada = "Todas"
                st.warning(f"Erro ao carregar entidades: {str(e)}")
        else:
            entidade_selecionada = "Todas"
            st.warning("Coluna 'Nome' não encontrada")
        
        # Filtro de Artigo (dinâmico) - CORRIGIDO
        if 'Artigo' in df.columns:
            try:
                artigos_disponiveis = sorted(df['Artigo'].dropna().astype(str).unique())
                if len(artigos_disponiveis) > 0:
                    artigo_selecionado = st.selectbox(
                        "**Artigo**",
                        options=["Todos"] + list(artigos_disponiveis),
                        index=0
                    )
                else:
                    artigo_selecionado = "Todos"
                    st.warning("Nenhum artigo disponível nos dados")
            except Exception as e:
                artigo_selecionado = "Todos"
                st.warning(f"Erro ao carregar artigos: {str(e)}")
        else:
            artigo_selecionado = "Todos"
            st.warning("Coluna 'Artigo' não encontrada")
        
        # Botão para resetar filtros
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Resetar", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("📊 Atualizar", use_container_width=True, type="primary"):
                st.rerun()
        
        st.markdown("---")
    
    # Aplicar filtros com segurança
    df_filtrado = df.copy()
    
    try:
        # Aplicar filtro de ano
        if ano_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Ano'] == ano_selecionado]
        
        # Aplicar filtro de mês
        if mes_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Mes_Nome'] == mes_selecionado]
        
        # Aplicar filtro de comercial
        if comercial_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Comercial'] == comercial_selecionado]
        
        # Aplicar filtro de entidade
        if entidade_selecionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Entidade_Nome'] == entidade_selecionada]
        
        # Aplicar filtro de artigo - CORRIGIDO
        if artigo_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Artigo'] == artigo_selecionado]
    
    except Exception as e:
        st.error(f"❌ Erro ao aplicar filtros: {str(e)}")
        df_filtrado = df.copy()
    
    # Mostrar estatísticas dos filtros aplicados
    st.sidebar.markdown("### 📊 Estatísticas Filtradas")
    st.sidebar.success(f"""
    **Registros:** {len(df_filtrado):,}
    **Vendas Totais:** €{df_filtrado['V_Liquido'].sum():,.2f}
    **Quantidade:** {df_filtrado['Quantidade'].sum():,.0f}
    """)
    
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
        preco_medio = df_filtrado['V_Liquido'].sum() / total_quantidade if total_quantidade > 0 else 0
        st.metric(
            label="🏷️ Preço Médio Unitário",
            value=f"€{preco_medio:,.2f}",
            delta=None
        )
    
    st.markdown("---")
    
    # Gráficos e Análises em Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Visão Geral", 
        "👥 Por Entidade", 
        "🛒 Por Artigo", 
        "📈 Tendências"
    ])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Vendas por Comercial (Top 10)
            if 'Comercial' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
                try:
                    vendas_por_comercial = df_filtrado.groupby('Comercial')['V_Liquido'].sum().reset_index()
                    vendas_por_comercial = vendas_por_comercial.sort_values('V_Liquido', ascending=False).head(10)
                    
                    fig = px.bar(
                        vendas_por_comercial,
                        x='Comercial',
                        y='V_Liquido',
                        title='Top 10 Comerciais por Vendas',
                        color='V_Liquido',
                        color_continuous_scale='Blues',
                        text_auto='.2s'
                    )
                    fig.update_layout(
                        xaxis_title="Comercial",
                        yaxis_title="Vendas Líquidas (€)",
                        showlegend=False,
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Não foi possível gerar gráfico de comerciais: {str(e)}")
        
        with col2:
            # Distribuição por Mês
            if 'Mes_Nome' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
                try:
                    vendas_por_mes = df_filtrado.groupby('Mes_Nome')['V_Liquido'].sum().reset_index()
                    
                    if not vendas_por_mes.empty:
                        fig = px.line(
                            vendas_por_mes,
                            x='Mes_Nome',
                            y='V_Liquido',
                            title='Vendas por Mês',
                            markers=True,
                            line_shape='spline'
                        )
                        fig.update_layout(
                            xaxis_title="Mês",
                            yaxis_title="Vendas Líquidas (€)",
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Não foi possível gerar gráfico por mês: {str(e)}")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 Entidades por Compras
            if 'Entidade_Nome' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
                try:
                    top_entidades = df_filtrado.groupby('Entidade_Nome').agg({
                        'V_Liquido': 'sum',
                        'Quantidade': 'sum'
                    }).reset_index()
                    top_entidades = top_entidades.sort_values('V_Liquido', ascending=False).head(10)
                    
                    # Formatar para exibição
                    top_entidades_display = top_entidades.copy()
                    top_entidades_display['V_Liquido'] = top_entidades_display['V_Liquido'].apply(lambda x: f"€{x:,.2f}")
                    top_entidades_display['Quantidade'] = top_entidades_display['Quantidade'].apply(lambda x: f"{x:,.0f}")
                    top_entidades_display.columns = ['Entidade', 'Total Vendas', 'Quantidade Total']
                    
                    st.subheader("🏆 Top 10 Entidades")
                    st.dataframe(
                        top_entidades_display,
                        use_container_width=True,
                        height=400
                    )
                except Exception as e:
                    st.warning(f"Não foi possível gerar ranking de entidades: {str(e)}")
        
        with col2:
            # Distribuição de compras por entidade
            if 'Entidade_Nome' in df_filtrado.columns:
                try:
                    compras_por_entidade = df_filtrado['Entidade_Nome'].value_counts().reset_index()
                    compras_por_entidade.columns = ['Entidade', 'Nº Compras']
                    compras_por_entidade = compras_por_entidade.head(10)
                    
                    fig = px.pie(
                        compras_por_entidade,
                        values='Nº Compras',
                        names='Entidade',
                        title='Top 10 Entidades por Nº de Compras',
                        hole=0.4
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Não foi possível gerar gráfico de distribuição: {str(e)}")
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 Artigos mais vendidos (por quantidade)
            if 'Artigo' in df_filtrado.columns and 'Quantidade' in df_filtrado.columns:
                try:
                    top_artigos_qtd = df_filtrado.groupby('Artigo').agg({
                        'Quantidade': 'sum',
                        'V_Liquido': 'sum'
                    }).reset_index()
                    top_artigos_qtd = top_artigos_qtd.sort_values('Quantidade', ascending=False).head(10)
                    
                    fig = px.bar(
                        top_artigos_qtd,
                        x='Artigo',
                        y='Quantidade',
                        title='Top 10 Artigos por Quantidade Vendida',
                        color='V_Liquido',
                        color_continuous_scale='Viridis',
                        hover_data=['V_Liquido'],
                        text_auto=',.0f'
                    )
                    fig.update_layout(
                        xaxis_title="Artigo",
                        yaxis_title="Quantidade Vendida",
                        xaxis_tickangle=45,
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Não foi possível gerar gráfico de artigos por quantidade: {str(e)}")
        
        with col2:
            # Top 10 Artigos por valor (por vendas)
            if 'Artigo' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
                try:
                    top_artigos_valor = df_filtrado.groupby('Artigo').agg({
                        'V_Liquido': 'sum',
                        'Quantidade': 'sum',
                        'Preco_Medio': 'mean'
                    }).reset_index()
                    top_artigos_valor = top_artigos_valor.sort_values('V_Liquido', ascending=False).head(10)
                    
                    fig = px.bar(
                        top_artigos_valor,
                        x='Artigo',
                        y='V_Liquido',
                        title='Top 10 Artigos por Valor de Vendas',
                        color='Preco_Medio',
                        color_continuous_scale='Reds',
                        hover_data=['Quantidade', 'Preco_Medio'],
                        text_auto='.2s'
                    )
                    fig.update_layout(
                        xaxis_title="Artigo",
                        yaxis_title="Valor de Vendas (€)",
                        xaxis_tickangle=45,
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Não foi possível gerar gráfico de artigos por valor: {str(e)}")
    
    with tab4:
        # Análise temporal detalhada
        if 'Data' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns:
            try:
                # Agrupar por dia
                df_filtrado['Data_Dia'] = df_filtrado['Data'].dt.date
                vendas_diarias = df_filtrado.groupby('Data_Dia').agg({
                    'V_Liquido': 'sum',
                    'Quantidade': 'sum',
                    'Entidade_Nome': 'nunique'
                }).reset_index()
                
                # Criar gráfico combinado
                fig = go.Figure()
                
                # Linha para vendas
                fig.add_trace(go.Scatter(
                    x=vendas_diarias['Data_Dia'],
                    y=vendas_diarias['V_Liquido'],
                    mode='lines+markers',
                    name='Vendas Líquidas (€)',
                    line=dict(color='blue', width=2),
                    yaxis='y'
                ))
                
                # Barras para quantidade
                fig.add_trace(go.Bar(
                    x=vendas_diarias['Data_Dia'],
                    y=vendas_diarias['Quantidade'],
                    name='Quantidade Vendida',
                    marker_color='lightblue',
                    opacity=0.6,
                    yaxis='y2'
                ))
                
                # Linha para número de entidades
                fig.add_trace(go.Scatter(
                    x=vendas_diarias['Data_Dia'],
                    y=vendas_diarias['Entidade_Nome'],
                    mode='lines',
                    name='Nº de Entidades',
                    line=dict(color='green', width=2, dash='dash'),
                    yaxis='y3'
                ))
                
                fig.update_layout(
                    title='Evolução Diária - Vendas, Quantidade e Entidades',
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
                        side='right'
                    ),
                    yaxis3=dict(
                        title='Nº Entidades',
                        titlefont=dict(color='green'),
                        tickfont=dict(color='green'),
                        overlaying='y',
                        side='right',
                        position=0.95
                    ),
                    hovermode='x unified',
                    height=500,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.warning(f"Não foi possível gerar análise temporal: {str(e)}")
    
    # Seção de Dados Detalhados
    st.markdown("---")
    st.header("📋 Dados Detalhados")
    
    # Opções de visualização
    view_option = st.radio(
        "Selecione a visualização:",
        ["Visão Resumida (50 registros)", "Dados Completos Filtrados"],
        horizontal=True,
        index=0
    )
    
    if view_option == "Visão Resumida (50 registros)":
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
            df_display.sort_values('Data' if 'Data' in df_display.columns else 'Entidade_Nome', ascending=False).head(50),
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
    
    # Estatísticas descritivas em expander
    with st.expander("📊 Estatísticas Descritivas Detalhadas"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'V_Liquido' in df_filtrado.columns:
                st.subheader("Vendas Líquidas")
                stats_vendas = df_filtrado['V_Liquido'].describe()
                for idx, val in stats_vendas.items():
                    st.write(f"**{idx}:** €{val:,.2f}")
        
        with col2:
            if 'Quantidade' in df_filtrado.columns:
                st.subheader("Quantidade")
                stats_qtd = df_filtrado['Quantidade'].describe()
                for idx, val in stats_qtd.items():
                    st.write(f"**{idx}:** {val:,.0f}")
        
        with col3:
            if 'Preco_Medio' in df_filtrado.columns:
                st.subheader("Preço Médio")
                stats_pm = df_filtrado['Preco_Medio'].describe()
                for idx, val in stats_pm.items():
                    st.write(f"**{idx}:** €{val:,.2f}")
    
    # Download dos dados filtrados
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("💡 Os dados podem ser exportados para análise externa")
    
    with col2:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        st.download_button(
            label="📥 Baixar CSV",
            data=df_filtrado.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'),
            file_name=f"vendas_filtradas_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Executar o aplicativo
if __name__ == "__main__":
    main()
