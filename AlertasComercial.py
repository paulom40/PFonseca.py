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
    page_title="Dashboard de Vendas - Análise Completa",
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
    
    /* Botões modernos */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: white;
        border-radius: 10px;
        padding: 0 2rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Header principal com gradiente
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.5rem;">📊 DASHBOARD DE VENDAS - ANÁLISE COMPLETA</h1>
    <p style="margin:0; opacity: 0.9; font-size: 1.1rem;">Análise Cliente x Comercial + Alertas de Inatividade</p>
</div>
""", unsafe_allow_html=True)

# URL do arquivo Excel
url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"

@st.cache_data
def load_data():
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Carregar o ficheiro Excel
        excel_file = BytesIO(response.content)
        
        # Ler o ficheiro mantendo a estrutura original das colunas
        df = pd.read_excel(excel_file, sheet_name="Sheet1", header=0)
        
        st.info(f"📊 Colunas originais carregadas: {list(df.columns)}")
        
        # CORREÇÃO: Renomear a coluna G (índice 6) para 'Artigo'
        if len(df.columns) > 6:
            # Guardar o nome original da coluna G
            nome_original_coluna_g = df.columns[6]
            st.info(f"🔧 Coluna G original: '{nome_original_coluna_g}'")
            
            # Renomear a coluna G para 'Artigo'
            df = df.rename(columns={df.columns[6]: 'Artigo'})
            st.success(f"✅ Coluna G renomeada de '{nome_original_coluna_g}' para 'Artigo'")
        
        # Processar colunas e dados
        df.columns = [col.strip() for col in df.columns]
        
        # Verificar se temos a coluna Artigo
        if 'Artigo' not in df.columns:
            st.error("❌ Coluna 'Artigo' não encontrada após processamento")
            st.info("📋 Colunas disponíveis:")
            for i, col in enumerate(df.columns):
                st.info(f"{i}: {col}")
            return None
        
        # Converter colunas numéricas
        if 'Qtd.' in df.columns:
            df['Qtd.'] = pd.to_numeric(df['Qtd.'], errors='coerce')
        if 'V. Líquido' in df.columns:
            df['V. Líquido'] = pd.to_numeric(df['V. Líquido'], errors='coerce')
        
        # Limpar e padronizar textos
        text_columns = ['Cliente', 'Comercial', 'Artigo', 'Categoria']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Processar datas - criar data baseada no mês/ano
        if 'Mês' in df.columns and 'Ano' in df.columns:
            # Mapear meses em português para inglês
            meses_map = {
                'Janeiro': '01', 'Fevereiro': '02', 'Março': '03', 'Abril': '04',
                'Maio': '05', 'Junho': '06', 'Julho': '07', 'Agosto': '08',
                'Setembro': '09', 'Outubro': '10', 'Novembro': '11', 'Dezembro': '12',
                'Jan': '01', 'Fev': '02', 'Mar': '03', 'Abr': '04', 'Mai': '05', 'Jun': '06',
                'Jul': '07', 'Ago': '08', 'Set': '09', 'Out': '10', 'Nov': '11', 'Dez': '12'
            }
            
            # Aplicar mapeamento
            df['Mês_Num'] = df['Mês'].map(meses_map)
            
            # Criar data aproximada (primeiro dia do mês)
            df['Data'] = pd.to_datetime(
                df['Ano'].astype(str) + '-' + df['Mês_Num'] + '-01', 
                errors='coerce'
            )
            
            # Remover coluna auxiliar
            df = df.drop('Mês_Num', axis=1, errors='ignore')
            
            st.success(f"✅ Datas processadas: {df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}")
        
        st.success(f"✅ Dados carregados com sucesso: {len(df)} registos")
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar ficheiro: {e}")
        st.info("💡 Dica: Verifique se o link do GitHub está correto e se o ficheiro está público.")
        return None

def calcular_alertas_inatividade(df, dias_alerta=30):
    """
    Calcula clientes inativos há mais de X dias baseado no Mês e Ano
    """
    if 'Data' not in df.columns or 'Cliente' not in df.columns:
        st.warning("⚠️ Dados insuficientes para calcular alertas de inatividade")
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
        'Categoria': 'first',
        'Artigo': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'N/A'
    }).reset_index()
    
    info_clientes.columns = ['Cliente', 'Total_Historico', 'Ticket_Medio', 'Total_Compras', 'Comercial', 'Categoria_Preferida', 'Artigo_Mais_Comprado']
    
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
    # Mostrar informações sobre as colunas carregadas
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🔎 FILTROS E CONTROLES</div>', unsafe_allow_html=True)
        
        st.markdown("### 📊 Filtros Principais")
        
        # Filtro por Comercial
        if 'Comercial' in df.columns:
            comerciais = sorted(df['Comercial'].dropna().unique())
            selected_comercial = st.multiselect(
                "Selecione o(s) Comercial(ais):",
                comerciais,
                default=comerciais[:3] if len(comerciais) > 3 else comerciais
            )
        else:
            st.warning("Coluna 'Comercial' não encontrada")
            selected_comercial = []
        
        # Filtro por Cliente
        if 'Cliente' in df.columns:
            clientes = sorted(df['Cliente'].dropna().unique())
            selected_cliente = st.multiselect(
                "Selecione o(s) Cliente(s):",
                clientes,
                default=clientes[:3] if len(clientes) > 3 else clientes
            )
        else:
            st.warning("Coluna 'Cliente' não encontrada")
            selected_cliente = []
        
        # Filtro por Artigo - CORREÇÃO: Usar coluna G corretamente
        if 'Artigo' in df.columns:
            artigos = sorted(df['Artigo'].dropna().unique())
            selected_artigo = st.multiselect(
                "Selecione o(s) Artigo(s):",
                artigos,
                default=artigos[:5] if len(artigos) > 5 else artigos
            )
            
            # Mostrar estatísticas dos artigos
            st.info(f"📦 {len(artigos)} artigos disponíveis")
        else:
            st.error("❌ Coluna 'Artigo' não encontrada")
            st.info("📋 Colunas disponíveis:")
            for i, col in enumerate(df.columns):
                st.write(f"- {i}: {col}")
            selected_artigo = []
        
        # Filtro por Categoria
        if 'Categoria' in df.columns:
            categorias = sorted(df['Categoria'].dropna().unique())
            selected_categoria = st.multiselect(
                "Selecione a(s) Categoria(s):",
                categorias,
                default=categorias
            )
        else:
            st.warning("Coluna 'Categoria' não encontrada")
            selected_categoria = []
        
        # Configuração específica para alertas
        st.markdown("---")
        st.markdown("### 🚨 Configuração de Alertas")
        
        dias_alerta = st.slider(
            "Dias sem comprar para alerta:",
            min_value=15,
            max_value=180,
            value=30,
            step=5,
            help="Número de dias sem compra para considerar o cliente como inativo"
        )
        
        # Filtro por valor histórico mínimo para alertas
        valor_minimo_alerta = st.number_input(
            "Valor histórico mínimo para alertas (€):",
            min_value=0,
            value=100,
            step=50,
            help="Mostrar apenas clientes com valor histórico acima deste valor"
        )
        
        st.markdown("---")
        st.markdown("### 📈 Estatísticas Rápidas")
        
        if len(df) > 0:
            total_vendas = df['V. Líquido'].sum() if 'V. Líquido' in df.columns else 0
            total_clientes = df['Cliente'].nunique() if 'Cliente' in df.columns else 0
            total_comerciais = df['Comercial'].nunique() if 'Comercial' in df.columns else 0
            total_artigos = df['Artigo'].nunique() if 'Artigo' in df.columns else 0
            
            st.metric("💰 Total Vendas", f"€{total_vendas:,.2f}")
            st.metric("👥 Total Clientes", total_clientes)
            st.metric("👨‍💼 Total Comerciais", total_comerciais)
            st.metric("📦 Total Artigos", total_artigos)

    # Layout principal com tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard Principal", "📈 Análise Comparativa", "📋 Detalhes por Artigo", "🚨 Alertas Inatividade", "📁 Exportação"])

    with tab1:
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if selected_comercial:
            df_filtrado = df_filtrado[df_filtrado['Comercial'].isin(selected_comercial)]
        
        if selected_cliente:
            df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(selected_cliente)]
        
        if selected_artigo:
            df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(selected_artigo)]
        
        if selected_categoria:
            df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(selected_categoria)]
        
        if len(df_filtrado) == 0:
            st.warning("❌ Nenhum dado encontrado com os filtros aplicados.")
        else:
            st.success(f"✅ {len(df_filtrado)} registros encontrados")
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_vendas_filtrado = df_filtrado['V. Líquido'].sum()
                st.markdown(f"""
                <div class="metric-card-success">
                    <h3 style="margin:0; font-size: 0.9rem;">Total Vendas Filtrado</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">€{total_vendas_filtrado:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                qtd_total = df_filtrado['Qtd.'].sum() if 'Qtd.' in df_filtrado.columns else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size: 0.9rem;">Quantidade Total</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{qtd_total:,.0f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                clientes_unicos = df_filtrado['Cliente'].nunique()
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size: 0.9rem;">Clientes Únicos</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{clientes_unicos}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                ticket_medio = total_vendas_filtrado / len(df_filtrado) if len(df_filtrado) > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size: 0.9rem;">Ticket Médio</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">€{ticket_medio:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Gráficos
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("### 📈 Vendas por Comercial")
                if 'Comercial' in df_filtrado.columns and 'V. Líquido' in df_filtrado.columns:
                    vendas_comercial = df_filtrado.groupby('Comercial')['V. Líquido'].sum().sort_values(ascending=False)
                    fig1 = px.bar(
                        vendas_comercial, 
                        x=vendas_comercial.index, 
                        y=vendas_comercial.values,
                        title="Vendas Totais por Comercial",
                        color=vendas_comercial.values,
                        color_continuous_scale='viridis'
                    )
                    fig1.update_layout(showlegend=False)
                    st.plotly_chart(fig1, use_container_width=True)
            
            with col_chart2:
                st.markdown("### 📊 Vendas por Categoria")
                if 'Categoria' in df_filtrado.columns and 'V. Líquido' in df_filtrado.columns:
                    vendas_categoria = df_filtrado.groupby('Categoria')['V. Líquido'].sum().sort_values(ascending=False)
                    fig2 = px.pie(
                        vendas_categoria, 
                        values=vendas_categoria.values, 
                        names=vendas_categoria.index,
                        title="Distribuição de Vendas por Categoria"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
            
            # Top clientes e artigos
            col_top1, col_top2 = st.columns(2)
            
            with col_top1:
                st.markdown("### 🏆 Top 10 Clientes")
                if 'Cliente' in df_filtrado.columns and 'V. Líquido' in df_filtrado.columns:
                    top_clientes = df_filtrado.groupby('Cliente')['V. Líquido'].sum().nlargest(10)
                    st.dataframe(top_clientes.reset_index().rename(columns={'V. Líquido': 'Total Vendas'}), use_container_width=True)
            
            with col_top2:
                st.markdown("### 🎯 Top 10 Artigos")
                if 'Artigo' in df_filtrado.columns and 'V. Líquido' in df_filtrado.columns:
                    top_artigos = df_filtrado.groupby('Artigo')['V. Líquido'].sum().nlargest(10)
                    st.dataframe(top_artigos.reset_index().rename(columns={'V. Líquido': 'Total Vendas'}), use_container_width=True)

    # ... (resto do código mantém-se igual para as outras tabs)

else:
    st.error("❌ Não foi possível carregar os dados do Excel.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "📊 Dashboard de Análise Completa de Vendas • "
    f"Última execução: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    "</div>", 
    unsafe_allow_html=True
)
