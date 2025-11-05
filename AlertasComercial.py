import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
import unicodedata
from datetime import datetime, timedelta
import requests

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Business Intelligence Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded",
    page_icon="🚀"
)

# --- MODERN COLOR SCHEME ---
primary_color = "#6366f1"  # Modern purple
secondary_color = "#10b981"  # Emerald green
accent_color = "#f59e0b"   # Amber
warning_color = "#ef4444"  # Red
success_color = "#22c55e"  # Green
info_color = "#3b82f6"     # Blue

# --- CLEAN WHITE STYLING ---
st.markdown(f"""
    <style>
    /* Clean White Design */
    .main {{
        background: #ffffff;
        color: #1e293b;
    }}
    
    .stApp {{
        background: #ffffff;
    }}
    
    /* Modern Headers */
    h1 {{
        color: {primary_color};
        font-weight: 800;
        font-size: 2.8em;
        margin-bottom: 20px;
        font-family: 'Inter', sans-serif;
        border-bottom: 3px solid {primary_color};
        padding-bottom: 10px;
    }}
    
    h2 {{
        color: #1e293b;
        font-weight: 700;
        font-size: 2em;
        margin-top: 30px;
        margin-bottom: 20px;
        font-family: 'Inter', sans-serif;
    }}
    
    h3 {{
        color: #475569;
        font-weight: 600;
        font-size: 1.4em;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Modern Cards */
    [data-testid="metric-container"] {{
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }}
    
    [data-testid="metric-container"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        border-color: {primary_color};
    }}
    
    /* Modern Sidebar */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {primary_color} 0%, #4f46e5 100%);
        border-right: none;
    }}
    
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    /* CORREÇÃO DOS FILTROS - Texto escuro nos selects */
    .stSelectbox [data-baseweb="select"] {{
        background-color: white !important;
        color: #1e293b !important;
    }}
    
    .stSelectbox [data-baseweb="select"] div {{
        color: #1e293b !important;
        background-color: white !important;
    }}
    
    .stSelectbox [data-baseweb="select"] input {{
        color: #1e293b !important;
        background-color: white !important;
    }}
    
    .stSelectbox [data-baseweb="select"] span {{
        color: #1e293b !important;
        background-color: white !important;
    }}
    
    /* CORREÇÃO DO PAINEL DE NAVEGAÇÃO - Radio buttons */
    .stRadio [role="radiogroup"] {{
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }}
    
    .stRadio [role="radiogroup"] label {{
        color: white !important;
        background: transparent !important;
        padding: 10px 15px !important;
        margin: 5px 0 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        border: 1px solid transparent !important;
    }}
    
    .stRadio [role="radiogroup"] label:hover {{
        background: rgba(255, 255, 255, 0.2) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }}
    
    .stRadio [role="radiogroup"] label:has(input:checked) {{
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
        font-weight: 600 !important;
    }}
    
    .stRadio [data-testid="stMarkdownContainer"] {{
        color: white !important;
    }}
    
    .stRadio [data-testid="stMarkdownContainer"] p {{
        color: white !important;
        font-weight: 500 !important;
    }}
    
    /* Radio button custom styling */
    .stRadio [class*="st-"] {{
        color: white !important;
    }}
    
    /* Dropdown menu styling */
    [role="listbox"] {{
        background-color: white !important;
        color: #1e293b !important;
    }}
    
    [role="option"] {{
        background-color: white !important;
        color: #1e293b !important;
    }}
    
    [role="option"]:hover {{
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
    }}
    
    /* Enhanced Form Elements */
    .stRadio, .stSelectbox, .stMultiSelect {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }}
    
    .stRadio label, .stSelectbox label, .stMultiSelect label {{
        font-weight: 600;
        color: white !important;
        font-size: 1.1em;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Modern Buttons */
    .stDownloadButton button {{
        background: linear-gradient(135deg, {primary_color}, {secondary_color});
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 12px 25px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }}
    
    .stDownloadButton button:hover {{
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }}
    
    /* Metric Value Styling */
    [data-testid="metric-value"] {{
        font-size: 2em !important;
        font-weight: 800 !important;
        color: #1e293b !important;
        font-family: 'Inter', sans-serif;
    }}
    
    [data-testid="metric-label"] {{
        font-size: 1.1em !important;
        font-weight: 600 !important;
        color: {primary_color} !important;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Elegant Dividers */
    hr {{
        border: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 30px 0;
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: #f1f5f9;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {primary_color};
        border-radius: 3px;
    }}
    
    /* Streamlit element overrides */
    .st-bb {{
        background-color: transparent;
    }}
    
    .st-at {{
        background-color: white;
    }}
    
    /* Expander styling */
    .streamlit-expanderHeader {{
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        font-weight: 600;
    }}
    
    /* Dataframe styling */
    .dataframe {{
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }}
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING FUNCTION ---
month_names_to_number = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
    'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
    'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
    'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
    'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
}

@st.cache_data
def carregar_dados():
    try:
        url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx"
        response = requests.get(url, timeout=15, allow_redirects=True)
        
        if response.status_code != 200:
            st.error(f"❌ Erro ao carregar dados: Status {response.status_code}")
            return pd.DataFrame()
        
        df = pd.read_excel(BytesIO(response.content))
        
        # Column mapping
        col_mappings = {
            'Mês': 'mes', 'mes': 'mes', 'MÊS': 'mes',
            'Qtd.': 'qtd', 'Qtd': 'qtd', 'qtd': 'qtd', 'QTD': 'qtd', 'Quantidade': 'qtd',
            'Ano': 'ano', 'ano': 'ano', 'ANO': 'ano',
            'Cliente': 'cliente', 'cliente': 'cliente', 'CLIENTE': 'cliente',
            'Comercial': 'comercial', 'comercial': 'comercial', 'COMERCIAL': 'comercial',
            'V. Líquido': 'v_liquido', 'V_Liquido': 'v_liquido', 'V Liquido': 'v_liquido', 'V. LÍQUIDO': 'v_liquido',
            'PM': 'pm', 'pm': 'pm', 'Preço Médio': 'pm',
            'Categoria': 'categoria', 'categoria': 'categoria', 'CATEGORIA': 'categoria'
        }
        
        df = df.rename(columns=col_mappings)
        
        # Check critical columns
        critical_cols = ['mes', 'qtd', 'ano', 'cliente', 'comercial']
        missing_cols = [col for col in critical_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ Colunas em falta: {missing_cols}")
            return pd.DataFrame()
        
        # Convert month names to numbers
        if df['mes'].dtype == 'object':
            df['mes'] = df['mes'].apply(lambda x: month_names_to_number.get(str(x).strip(), np.nan))
        else:
            df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
        
        # Convert numeric columns
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')
        if 'v_liquido' in df.columns:
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')
        
        # Clean data
        df = df.dropna(subset=['mes', 'qtd', 'ano', 'cliente', 'comercial'])
        df = df[(df['mes'] >= 1) & (df['mes'] <= 12)]
        
        return df
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# Load data
df = carregar_dados()

if df.empty:
    st.error("❌ Não foi possível carregar os dados. Verifique a conexão e o URL.")
    st.stop()

# --- MODERN SIDEBAR ---
st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 30px 0;">
        <div style="font-size: 2.5em; margin-bottom: 10px;">📊</div>
        <h1 style="color: white; margin: 0; font-size: 1.8em; font-weight: 700;">Business Intelligence</h1>
        <p style="color: rgba(255, 255, 255, 0.8); margin: 5px 0 0 0; font-size: 0.9em;">Dashboard Analítico</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div style='height: 2px; background: rgba(255,255,255,0.3); margin: 20px 0;'></div>", unsafe_allow_html=True)

# Navigation - AGORA COM ESTILO CORRETO
st.sidebar.markdown("""
    <style>
    /* Estilo personalizado para a navegação */
    .navigation-radio {{
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }}
    
    .navigation-radio [role="radiogroup"] {{
        background: transparent !important;
        border: none !important;
    }}
    
    .navigation-radio label {{
        color: white !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        margin: 8px 0 !important;
        padding: 12px 15px !important;
        transition: all 0.3s ease !important;
    }}
    
    .navigation-radio label:hover {{
        background: rgba(255, 255, 255, 0.2) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
        transform: translateX(5px);
    }}
    
    .navigation-radio label:has(input:checked) {{
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.6) !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 10px rgba(255, 255, 255, 0.2);
    }}
    
    .navigation-radio [data-testid="stMarkdownContainer"] p {{
        color: white !important;
        font-weight: 500 !important;
        margin: 0 !important;
        font-size: 1em !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Navigation com classe personalizada
with st.sidebar:
    st.markdown('<div class="navigation-radio">', unsafe_allow_html=True)
    pagina = st.radio(
        "**🌐 NAVEGAÇÃO**", 
        [
            "📊 VISÃO GERAL", 
            "🎯 KPIS PERSONALIZADOS", 
            "📈 TENDÊNCIAS", 
            "⚠️ ALERTAS",
            "👥 ANÁLISE DE CLIENTES",
            "🔍 VISTA COMPARATIVA"
        ], 
        key="navigation"
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("<div style='height: 2px; background: rgba(255,255,255,0.3); margin: 20px 0;'></div>", unsafe_allow_html=True)

# Filters
st.sidebar.markdown("### 🔍 FILTROS")
st.sidebar.markdown("<p style='color: rgba(255,255,255,0.7); font-size: 0.9em;'>Filtre os dados conforme necessário</p>", unsafe_allow_html=True)

# Filter functions
def get_filtro_opcoes(dados, ano, comercial, cliente):
    temp = dados.copy()
    if ano != "Todos":
        temp = temp[temp['ano'] == int(ano)]
    if comercial != "Todos":
        temp = temp[temp['comercial'].astype(str) == str(comercial)]
    if cliente != "Todos":
        temp = temp[temp['cliente'].astype(str) == str(cliente)]
    
    anos = sorted([int(x) for x in temp['ano'].dropna().unique()])
    comerciais = sorted(list(temp['comercial'].dropna().unique()))
    clientes = sorted(list(temp['cliente'].dropna().unique()))
    categorias = sorted(list(temp['categoria'].dropna().unique())) if 'categoria' in temp.columns else []
    
    return anos, comerciais, clientes, categorias

def aplicar_filtros(dados, ano, comercial, cliente, categoria):
    resultado = dados.copy()
    if ano != "Todos":
        resultado = resultado[resultado['ano'] == int(ano)]
    if comercial != "Todos":
        resultado = resultado[resultado['comercial'].astype(str) == str(comercial)]
    if cliente != "Todos":
        resultado = resultado[resultado['cliente'].astype(str) == str(cliente)]
    if categoria != "Todas" and 'categoria' in resultado.columns:
        resultado = resultado[resultado['categoria'].astype(str) == str(categoria)]
    return resultado

# Get initial options
anos_disponiveis, comerciais_disponiveis, clientes_disponiveis, categorias_disponiveis = get_filtro_opcoes(df, "Todos", "Todos", "Todos")

# Filters - COM ESTILO PERSONALIZADO
st.sidebar.markdown("""
    <style>
    .stSelectbox [data-baseweb="select"] {{
        background-color: white !important;
        color: #1e293b !important;
    }}
    .stSelectbox [data-baseweb="select"] div {{
        color: #1e293b !important;
    }}
    .stSelectbox [data-baseweb="select"] input {{
        color: #1e293b !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Ano filter
ano = st.sidebar.selectbox(
    "**📅 ANO**", 
    ["Todos"] + anos_disponiveis,
    key="ano_select"
)

# Commercial filter
_, comerciais_for_year, _, _ = get_filtro_opcoes(df, ano, "Todos", "Todos")
comercial = st.sidebar.selectbox(
    "**👨‍💼 COMERCIAL**", 
    ["Todos"] + comerciais_for_year,
    key="comercial_select"
)

# Customer filter
_, _, clientes_for_filters, _ = get_filtro_opcoes(df, ano, comercial, "Todos")
cliente = st.sidebar.selectbox(
    "**🏢 CLIENTE**", 
    ["Todos"] + clientes_for_filters,
    key="cliente_select"
)

# Category filter
_, _, _, categorias_for_filters = get_filtro_opcoes(df, ano, comercial, cliente)
categoria = st.sidebar.selectbox(
    "**📦 CATEGORIA**", 
    ["Todas"] + categorias_for_filters,
    key="categoria_select"
)

# Apply filters
dados_filtrados = aplicar_filtros(df, ano, comercial, cliente, categoria)

# Export function
def gerar_excel(dados):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dados.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

# Chart settings
color_scale_modern = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
month_names_pt = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}

# --- FUNÇÃO PARA FORMATAR VALORES EM EUROS ---
def formatar_euros(valor):
    """Formata valores em euros com símbolo € e separadores de milhares"""
    if pd.isna(valor) or valor == 0:
        return "€ 0"
    return f"€ {valor:,.2f}"

def formatar_euros_simples(valor):
    """Formata valores em euros sem casas decimais para valores grandes"""
    if pd.isna(valor) or valor == 0:
        return "€ 0"
    if valor >= 1000:
        return f"€ {valor:,.0f}"
    return f"€ {valor:,.2f}"

# --- PAGE 1: MODERN OVERVIEW ---
if pagina == "📊 VISÃO GERAL":
    st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <h1>📊 DASHBOARD ANALÍTICO</h1>
            <p style="font-size: 1.2em; color: #64748b; font-weight: 500;">Visão Geral de Performance Comercial</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_qty = dados_filtrados['qtd'].sum()
    total_value = dados_filtrados['v_liquido'].sum() if 'v_liquido' in dados_filtrados.columns else 0
    num_customers = dados_filtrados['cliente'].nunique()
    num_commercials = dados_filtrados['comercial'].nunique()
    
    with col1:
        st.metric(
            label="📦 QUANTIDADE TOTAL", 
            value=f"{total_qty:,.0f}",
            delta=None
        )
    with col2:
        st.metric(
            label="💰 VALOR TOTAL", 
            value=formatar_euros_simples(total_value) if total_value > 0 else "€ 0",
            delta=None
        )
    with col3:
        st.metric(
            label="👥 CLIENTES ÚNICOS", 
            value=f"{num_customers}",
            delta=None
        )
    with col4:
        st.metric(
            label="👨‍💼 COMERCIAIS", 
            value=f"{num_commercials}",
            delta=None
        )
    
    st.markdown("---")
    
    # Top Customers by Quantity
    st.markdown("### 🏆 TOP 10 CLIENTES (QUANTIDADE)")
    top_clientes_qtd = dados_filtrados.groupby('cliente')[['qtd', 'v_liquido']].sum().sort_values('qtd', ascending=False).head(10)
    
    fig_top_qtd = px.bar(
        top_clientes_qtd.reset_index(),
        x='cliente',
        y='qtd',
        color='v_liquido',
        title='',
        labels={'qtd': 'Quantidade', 'cliente': 'Cliente', 'v_liquido': 'Valor em €'},
        color_continuous_scale='Viridis',
        text='qtd'
    )
    fig_top_qtd.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside',
        marker_line_color='white',
        marker_line_width=2
    )
    fig_top_qtd.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color="#1e293b", size=12),
        xaxis_tickangle=-45,
        showlegend=False,
        height=500
    )
    st.plotly_chart(fig_top_qtd, use_container_width=True)

# [CONTINUAÇÃO DAS OUTRAS PÁGINAS...]

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.9em; padding: 20px;">
        <p>📊 Business Intelligence Dashboard • Desenvolvido com Streamlit</p>
    </div>
""", unsafe_allow_html=True)
