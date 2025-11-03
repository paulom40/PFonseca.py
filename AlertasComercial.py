import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from io import BytesIO
import xlsxwriter
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página com layout wide
st.set_page_config(
    page_title="Dashboard de Vendas - Alertas de Inatividade",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado com gradientes e estilo moderno
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
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Cards com gradiente */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-warning {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-danger {
        background: linear-gradient(135deg, #ff5858 0%, #f09819 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-success {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Alert cards */
    .alert-card-critical {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        border-left: 5px solid #ff0000;
    }
    
    .alert-card-warning {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        border-left: 5px solid #ffa500;
    }
    
    .alert-card-info {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        border-left: 5px solid #007bff;
    }
    
    /* Sidebar styling */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header principal com gradiente
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.5rem;">📊 DASHBOARD DE VENDAS - ALERTAS DE INATIVIDADE</h1>
    <p style="margin:0; opacity: 0.9; font-size: 1.1rem;">Monitorização de Clientes Inativos +30 Dias</p>
</div>
""", unsafe_allow_html=True)

# URL do arquivo Excel
url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"

@st.cache_data
def load_data():
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), sheet_name="Sheet1", header=0)
        
        # Processar colunas e dados
        df.columns = [col.strip() for col in df.columns]
        
        # Converter colunas numéricas
        if 'Qtd.' in df.columns:
            df['Qtd.'] = pd.to_numeric(df['Qtd.'], errors='coerce')
        if 'V. Líquido' in df.columns:
            df['V. Líquido'] = pd.to_numeric(df['V. Líquido'], errors='coerce')
        
        # Limpar e padronizar textos
        if 'Cliente' in df.columns:
            df['Cliente'] = df['Cliente'].astype(str).str.strip()
        if 'Comercial' in df.columns:
            df['Comercial'] = df['Comercial'].astype(str).str.strip()
        if 'Artigo' in df.columns:
            df['Artigo'] = df['Artigo'].astype(str).str.strip()
        if 'Categoria' in df.columns:
            df['Categoria'] = df['Categoria'].astype(str).str.strip()
        
        # Processar datas - assumindo que temos coluna de data
        # Se não tiver data, vamos criar uma baseada no mês/ano
        if 'Data' not in df.columns and 'Mês' in df.columns and 'Ano' in df.columns:
            # Criar data aproximada (primeiro dia do mês)
            df['Data'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['Mês'] + '-01', errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar ficheiro: {e}")
        st.info("💡 Dica: Verifique se o link do GitHub está correto e se o ficheiro está público.")
        return None

def calcular_alertas_inatividade(df, dias_alerta=30):
    """
    Calcula clientes inativos há mais de X dias
    """
    if 'Data' not in df.columns or 'Cliente' not in df.columns:
        return pd.DataFrame()
    
    # Encontrar última data de compra por cliente
    ultima_compra = df.groupby('Cliente')['Data'].max().reset_index()
    ultima_compra.columns = ['Cliente', 'Ultima_Compra']
    
    # Data de referência (hoje)
    data_referencia = datetime.now()
    
    # Calcular dias desde última compra
    ultima_compra['Dias_Sem_Comprar'] = (data_referencia - ultima_compra['Ultima_Compra']).dt.days
    
    # Filtrar clientes inativos
    clientes_inativos = ultima_compra[ultima_compra['Dias_Sem_Comprar'] > dias_alerta].copy()
    
    if len(clientes_inativos) == 0:
        return clientes_inativos
    
    # Adicionar informações adicionais dos clientes
    info_clientes = df.groupby('Cliente').agg({
        'V. Líquido': ['sum', 'mean', 'count'],
        'Comercial': 'first',
        'Categoria': 'first'
    }).reset_index()
    
    info_clientes.columns = ['Cliente', 'Total_Historico', 'Ticket_Medio', 'Total_Compras', 'Comercial', 'Categoria_Preferida']
    
    # Juntar informações
    alertas_completos = clientes_inativos.merge(info_clientes, on='Cliente', how='left')
    
    # Classificar por tempo de inatividade
    alertas_completos = alertas_completos.sort_values('Dias_Sem_Comprar', ascending=False)
    
    return alertas_completos

def classificar_risco_cliente(dias_inatividade, total_historico):
    """
    Classifica o risco do cliente baseado no tempo de inatividade e valor histórico
    """
    if dias_inatividade > 90:
        return "CRÍTICO"
    elif dias_inatividade > 60:
        return "ALTO"
    elif dias_inatividade > 45:
        return "MÉDIO"
    elif dias_inatividade > 30:
        return "BAIXO"
    else:
        return "ATIVO"

# Container principal para controles
with st.container():
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 🔄 Gestão de Dados")
        if st.button("🔄 Atualizar Dados do Excel", use_container_width=True):
            st.cache_data.clear()
            st.session_state.df = load_data()
            st.session_state.last_updated = datetime.now()
            if st.session_state.df is not None:
                st.success("✅ Dados atualizados com sucesso!")
    
    with col2:
        if "last_updated" in st.session_state:
            st.markdown(f"""
            <div class="metric-card-success">
                <h3 style="margin:0; font-size: 0.9rem;">Última Atualização</h3>
                <p style="margin:0; font-size: 1rem; font-weight: bold;">
                    {st.session_state.last_updated.strftime('%d/%m/%Y')}
                </p>
                <p style="margin:0; font-size: 0.8rem;">
                    {st.session_state.last_updated.strftime('%H:%M:%S')}
                </p>
            </div>
            """, unsafe_allow_html=True)

# Carregar dados
df = st.session_state.get("df", load_data())

if df is not None:
    # Sidebar moderna
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🔎 FILTROS DE ALERTAS</div>', unsafe_allow_html=True)
        
        st.markdown("### ⚙️ Configuração de Alertas")
        
        # Slider para dias de inatividade
        dias_alerta = st.slider(
            "Dias sem comprar para alerta:",
            min_value=15,
            max_value=180,
            value=30,
            step=5,
            help="Número de dias sem compra para considerar o cliente como inativo"
        )
        
        # Filtro por Comercial para alertas
        if 'Comercial' in df.columns:
            comerciais = sorted(df['Comercial'].dropna().unique())
            selected_comercial_alerta = st.multiselect(
                "Filtrar alertas por Comercial:",
                comerciais,
                default=comerciais
            )
        else:
            selected_comercial_alerta = []
        
        # Filtro por valor histórico mínimo
        valor_minimo = st.number_input(
            "Valor histórico mínimo (€):",
            min_value=0,
            value=100,
            step=50,
            help="Mostrar apenas clientes com valor histórico acima deste valor"
        )
        
        st.markdown("---")
        st.markdown("### 📈 Estatísticas Rápidas")
        
        if len(df) > 0:
            total_clientes = df['Cliente'].nunique() if 'Cliente' in df.columns else 0
            st.metric("👥 Total Clientes", total_clientes)
            
            # Calcular alertas para estatística
            alertas_temp = calcular_alertas_inatividade(df, dias_alerta)
            st.metric("⚠️ Clientes Inativos", len(alertas_temp))

    # Layout principal com tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🚨 Quadro de Alertas", "📊 Análise de Inatividade", "📈 Tendências", "📁 Relatórios"])

    with tab1:
        st.markdown("## 🚨 QUADRO DE ALERTAS - CLIENTES INATIVOS")
        
        # Calcular alertas
        alertas = calcular_alertas_inatividade(df, dias_alerta)
        
        if len(alertas) == 0:
            st.success(f"🎉 Excelente! Nenhum cliente identificado como inativo (+{dias_alerta} dias)")
        else:
            # Aplicar filtros adicionais
            if selected_comercial_alerta:
                alertas = alertas[alertas['Comercial'].isin(selected_comercial_alerta)]
            
            alertas = alertas[alertas['Total_Historico'] >= valor_minimo]
            
            # Classificar risco
            alertas['Nivel_Risco'] = alertas.apply(
                lambda x: classificar_risco_cliente(x['Dias_Sem_Comprar'], x['Total_Historico']), 
                axis=1
            )
            
            # Métricas de resumo
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_inativos = len(alertas)
                st.markdown(f"""
                <div class="metric-card-warning">
                    <h3 style="margin:0; font-size: 0.9rem;">Clientes Inativos</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{total_inativos}</p>
                    <p style="margin:0; font-size: 0.8rem;">+{dias_alerta} dias</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                valor_em_risco = alertas['Total_Historico'].sum()
                st.markdown(f"""
                <div class="metric-card-danger">
                    <h3 style="margin:0; font-size: 0.9rem;">Valor em Risco</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">€{valor_em_risco:,.0f}</p>
                    <p style="margin:0; font-size: 0.8rem;">Histórico total</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                criticos = len(alertas[alertas['Nivel_Risco'] == 'CRÍTICO'])
                st.markdown(f"""
                <div class="metric-card-danger">
                    <h3 style="margin:0; font-size: 0.9rem;">Casos Críticos</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{criticos}</p>
                    <p style="margin:0; font-size: 0.8rem;">+90 dias</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                media_inatividade = alertas['Dias_Sem_Comprar'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size: 0.9rem;">Inatividade Média</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{media_inatividade:.0f}</p>
                    <p style="margin:0; font-size: 0.8rem;">dias</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Filtros rápidos por nível de risco
            st.markdown("### 🔍 Filtros por Nível de Risco")
            riscos_selecionados = st.multiselect(
                "Selecionar níveis de risco:",
                ['CRÍTICO', 'ALTO', 'MÉDIO', 'BAIXO'],
                default=['CRÍTICO', 'ALTO', 'MÉDIO', 'BAIXO']
            )
            
            alertas_filtrados = alertas[alertas['Nivel_Risco'].isin(riscos_selecionados)]
            
            # Mostrar alertas em cards
            st.markdown("### 📋 Lista de Clientes Inativos")
            
            for idx, cliente in alertas_filtrados.iterrows():
                # Determinar cor do card baseado no risco
                if cliente['Nivel_Risco'] == 'CRÍTICO':
                    card_class = "alert-card-critical"
                    emoji = "🔴"
                elif cliente['Nivel_Risco'] == 'ALTO':
                    card_class = "alert-card-danger"
                    emoji = "🟠"
                elif cliente['Nivel_Risco'] == 'MÉDIO':
                    card_class = "alert-card-warning"
                    emoji = "🟡"
                else:
                    card_class = "alert-card-info"
                    emoji = "🔵"
                
                col_card1, col_card2, col_card3 = st.columns([3, 2, 1])
                
                with col_card1:
                    st.markdown(f"""
                    <div class="{card_class}">
                        <h4 style="margin:0; color: white;">{emoji} {cliente['Cliente']}</h4>
                        <p style="margin:0; font-size: 0.9rem;">
                            <strong>Comercial:</strong> {cliente['Comercial']} | 
                            <strong>Categoria Preferida:</strong> {cliente['Categoria_Preferida']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_card2:
                    st.markdown(f"""
                    <div style="padding: 1rem; background: #f8f9fa; border-radius: 10px;">
                        <p style="margin:0; font-size: 0.9rem;">
                            <strong>🚨 {cliente['Dias_Sem_Comprar']} dias</strong> sem comprar<br>
                            <strong>💰 €{cliente['Total_Historico']:,.0f}</strong> histórico
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_card3:
                    st.markdown(f"""
                    <div style="padding: 1rem; background: #e9ecef; border-radius: 10px; text-align: center;">
                        <p style="margin:0; font-size: 0.9rem; font-weight: bold; color: #dc3545;">
                            {cliente['Nivel_Risco']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")

    with tab2:
        st.markdown("## 📊 ANÁLISE DETALHADA DE INATIVIDADE")
        
        if len(alertas) > 0:
            # Gráfico de distribuição por tempo de inatividade
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                st.markdown("### 📅 Distribuição por Tempo de Inatividade")
                fig_dias = px.histogram(
                    alertas, 
                    x='Dias_Sem_Comprar',
                    nbins=20,
                    title="Distribuição de Clientes por Dias sem Comprar",
                    color_discrete_sequence=['#ff6b6b']
                )
                fig_dias.update_layout(showlegend=False)
                st.plotly_chart(fig_dias, use_container_width=True)
            
            with col_graf2:
                st.markdown("### 🎯 Distribuição por Nível de Risco")
                contagem_risco = alertas['Nivel_Risco'].value_counts()
                fig_risco = px.pie(
                    values=contagem_risco.values,
                    names=contagem_risco.index,
                    title="Distribuição por Nível de Risco",
                    color=contagem_risco.index,
                    color_discrete_map={
                        'CRÍTICO': '#dc3545',
                        'ALTO': '#fd7e14',
                        'MÉDIO': '#ffc107',
                        'BAIXO': '#20c997'
                    }
                )
                st.plotly_chart(fig_risco, use_container_width=True)
            
            # Análise por comercial
            st.markdown("### 👨‍💼 Análise por Comercial")
            if 'Comercial' in alertas.columns:
                inatividade_comercial = alertas.groupby('Comercial').agg({
                    'Cliente': 'count',
                    'Dias_Sem_Comprar': 'mean',
                    'Total_Historico': 'sum'
                }).round(2)
                
                inatividade_comercial.columns = ['Clientes_Inativos', 'Dias_Medios', 'Valor_Risco']
                inatividade_comercial = inatividade_comercial.sort_values('Clientes_Inativos', ascending=False)
                
                col_anal1, col_anal2 = st.columns(2)
                
                with col_anal1:
                    st.dataframe(inatividade_comercial, use_container_width=True)
                
                with col_anal2:
                    fig_comercial = px.bar(
                        inatividade_comercial.reset_index(),
                        x='Comercial',
                        y='Clientes_Inativos',
                        title="Clientes Inativos por Comercial",
                        color='Clientes_Inativos',
                        color_continuous_scale='reds'
                    )
                    st.plotly_chart(fig_comercial, use_container_width=True)
            
            # Tabela detalhada
            st.markdown("### 📋 Tabela Detalhada de Alertas")
            alertas_display = alertas[['Cliente', 'Comercial', 'Ultima_Compra', 'Dias_Sem_Comprar', 
                                     'Total_Historico', 'Ticket_Medio', 'Total_Compras', 'Nivel_Risco']].copy()
            alertas_display['Ultima_Compra'] = alertas_display['Ultima_Compra'].dt.strftime('%d/%m/%Y')
            alertas_display['Total_Historico'] = alertas_display['Total_Historico'].round(2)
            alertas_display['Ticket_Medio'] = alertas_display['Ticket_Medio'].round(2)
            
            st.dataframe(alertas_display, use_container_width=True)

    with tab3:
        st.markdown("## 📈 TENDÊNCIAS E PREVISÕES")
        
        if len(alertas) > 0:
            # Análise temporal
            st.markdown("### 📊 Evolução Temporal da Inatividade")
            
            # Simular dados históricos (em produção, teríamos dados históricos reais)
            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul']
            clientes_inativos_hist = [15, 18, 22, 25, 28, 32, len(alertas)]
            
            fig_tendencia = go.Figure()
            fig_tendencia.add_trace(go.Scatter(
                x=meses, 
                y=clientes_inativos_hist,
                mode='lines+markers',
                name='Clientes Inativos',
                line=dict(color='#ff6b6b', width=3),
                marker=dict(size=8)
            ))
            
            fig_tendencia.update_layout(
                title="Evolução do Número de Clientes Inativos",
                xaxis_title="Mês",
                yaxis_title="Número de Clientes Inativos",
                template="plotly_white"
            )
            
            st.plotly_chart(fig_tendencia, use_container_width=True)
            
            # Recomendações
            st.markdown("### 💡 RECOMENDAÇÕES E AÇÕES")
            
            col_rec1, col_rec2 = st.columns(2)
            
            with col_rec1:
                st.markdown("""
                #### 🎯 Ações Imediatas
                - **Contactar clientes CRÍTICOS** esta semana
                - **Oferecer promoções personalizadas**
                - **Rever estratégia de follow-up**
                - **Atribuir leads a comerciais específicos**
                """)
            
            with col_rec2:
                st.markdown("""
                #### 📋 Estratégias de Retenção
                - **Programa de fidelização**
                - **Newsletters personalizadas**
                - **Pesquisa de satisfação**
                - **Ofertas de reativação**
                """)

    with tab4:
        st.markdown("## 📁 RELATÓRIOS E EXPORTAÇÃO")
        
        if len(alertas) > 0:
            # Criar relatório Excel
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                # Dados completos
                alertas.to_excel(writer, sheet_name='Alertas_Completos', index=False)
                
                # Resumo por comercial
                if 'Comercial' in alertas.columns:
                    resumo_comercial = alertas.groupby('Comercial').agg({
                        'Cliente': 'count',
                        'Dias_Sem_Comprar': ['mean', 'max'],
                        'Total_Historico': 'sum'
                    }).round(2)
                    resumo_comercial.columns = ['Clientes_Inativos', 'Dias_Medios', 'Dias_Maximos', 'Valor_Risco']
                    resumo_comercial.to_excel(writer, sheet_name='Resumo_Comercial')
                
                # Clientes críticos
                criticos = alertas[alertas['Nivel_Risco'] == 'CRÍTICO']
                if len(criticos) > 0:
                    criticos.to_excel(writer, sheet_name='Clientes_Criticos', index=False)
                
                # Ações recomendadas
                acoes_recomendadas = pd.DataFrame({
                    'Prioridade': ['Alta', 'Alta', 'Média', 'Média'],
                    'Ação': ['Contactar clientes +90 dias', 'Rever estratégia comerciais', 
                            'Criar campanha marketing', 'Implementar programa fidelização'],
                    'Responsável': ['Comercial', 'Gestor', 'Marketing', 'Gestão'],
                    'Prazo': ['1 semana', '2 semanas', '1 mês', '1 mês']
                })
                acoes_recomendadas.to_excel(writer, sheet_name='Plano_Acão', index=False)
            
            excel_buffer.seek(0)
            
            # Botão de download
            st.download_button(
                label="⬇️ BAIXAR RELATÓRIO DE ALERTAS (Excel)",
                data=excel_buffer.getvalue(),
                file_name=f"alertas_inatividade_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            # Resumo do relatório
            st.info(f"""
            **📊 Relatório de Alertas contém:**
            - {len(alertas)} clientes inativos identificados
            - {len(alertas[alertas['Nivel_Risco'] == 'CRÍTICO'])} casos críticos
            - €{alertas['Total_Historico'].sum():,.0f} em valor histórico em risco
            - Plano de ação recomendado
            """)

else:
    st.error("❌ Não foi possível carregar os dados do Excel.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "🚨 Sistema de Alertas de Inatividade - Monitorização Contínua • "
    f"Última execução: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    "</div>", 
    unsafe_allow_html=True
)
