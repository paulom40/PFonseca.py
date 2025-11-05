# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import requests

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Business Intelligence Pro",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="Chart"
)

# --- GOOGLE FONTS + ESTILO MODERNO ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    /* Fonte global */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Fundo principal */
    .main { background: #f8fafc; }
    
    /* Títulos */
    h1 { color: #1e293b; font-weight: 800; font-size: 2.8rem; text-align: center; margin-bottom: 1rem; }
    h2 { color: #334155; font-weight: 700; font-size: 1.8rem; margin: 2rem 0 1rem; }
    h3 { color: #475569; font-weight: 600; font-size: 1.3rem; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #6366f1 0%, #4f46e5 100%);
        padding: 1.5rem;
        border-radius: 0 20px 20px 0;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Logo Sidebar */
    .sidebar-logo { text-align: center; margin-bottom: 2rem; }
    .sidebar-logo h1 { color: white; font-size: 1.8rem; margin: 0; }
    .sidebar-logo p { color: #c7d2fe; font-size: 0.9rem; margin: 0.5rem 0 0; }
    
    /* Filtros */
    .stSelectbox > div > div {
        background: white !important;
        color: #1e293b !important;
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.5rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [role="option"] {
        background: white !important;
        color: #1e293b !important;
    }
    .stSelectbox [role="option"]:hover {
        background: #f1f5f9 !important;
    }
    
    /* Navegação */
    .nav-radio { 
        background: rgba(255,255,255,0.1); 
        border-radius: 16px; 
        padding: 0.75rem; 
        margin: 1rem 0;
    }
    .stRadio > div > label {
        background: transparent !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        margin: 0.25rem 0 !important;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    .stRadio > div > label:hover {
        background: rgba(255,255,255,0.2) !important;
        transform: translateX(4px);
    }
    .stRadio > div > label:has(input:checked) {
        background: rgba(255,255,255,0.3) !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(255,255,255,0.2);
    }
    
    /* Métricas */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.12);
        border-color: #6366f1;
    }
    [data-testid="metric-value"] { font-size: 2.2rem !important; font-weight: 800 !important; color: #1e293b !important; }
    [data-testid="metric-label"] { font-size: 1rem !important; color: #6366f1 !important; font-weight: 600; }
    
    /* Botões */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(99,102,241,0.3);
        transition: all 0.3s ease;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99,102,241,0.4);
    }
    
    /* Gráficos */
    .plotly-graph-div { border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        color: #1e293b !important;
    }
</style>
""", unsafe_allow_html=True)

# --- DADOS ---
month_names_to_number = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
    'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
}

@st.cache_data(ttl=3600)
def carregar_dados():
    try:
        url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx"
        response = requests.get(url, timeout=15)
        df = pd.read_excel(BytesIO(response.content))
        
        col_map = {
            'Mês': 'mes', 'mes': 'mes', 'MÊS': 'mes',
            'Qtd.': 'qtd', 'Qtd': 'qtd', 'qtd': 'qtd', 'QTD': 'qtd', 'Quantidade': 'qtd',
            'Ano': 'ano', 'ano': 'ano', 'ANO': 'ano',
            'Cliente': 'cliente', 'cliente': 'cliente', 'CLIENTE': 'cliente',
            'Comercial': 'comercial', 'comercial': 'comercial', 'COMERCIAL': 'comercial',
            'V. Líquido': 'v_liquido', 'V_Liquido': 'v_liquido', 'V. LÍQUIDO': 'v_liquido',
            'Categoria': 'categoria', 'categoria': 'categoria', 'CATEGORIA': 'categoria'
        }
        df = df.rename(columns=col_map)
        
        if df['mes'].dtype == 'object':
            df['mes'] = df['mes'].apply(lambda x: month_names_to_number.get(str(x).strip().lower(), np.nan))
        df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')
        
        if 'v_liquido' in df.columns:
            df['v_liquido'] = df['v_liquido'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')
        
        df = df.dropna(subset=['mes', 'qtd', 'ano', 'cliente', 'comercial'])
        df = df[(df['mes'] >= 1) & (df['mes'] <= 12)]
        return df
    except: return pd.DataFrame()

df = carregar_dados()
if df.empty: st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class="sidebar-logo">
            <h1>BI Pro</h1>
            <p>Dashboard Analítico</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="nav-radio">', unsafe_allow_html=True)
    pagina = st.radio("**NAVEGAÇÃO**", [
        "VISÃO GERAL",
        "KPIS PERSONALIZADOS",
        "TENDÊNCIAS",
        "ALERTAS",
        "CLIENTES",
        "COMPARAÇÃO"
    ], key="nav")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### FILTROS")
    
    def get_opcoes(d, a, c, cl): 
        temp = d.copy()
        if a != "Todos": temp = temp[temp['ano'] == int(a)]
        if c != "Todos": temp = temp[temp['comercial'].astype(str).str.strip() == str(c).strip()]
        if cl != "Todos": temp = temp[temp['cliente'].astype(str).str.strip() == str(cl).strip()]
        return (
            sorted(temp['ano'].dropna().unique().astype(int).tolist()),
            sorted(temp['comercial'].dropna().unique().tolist()),
            sorted(temp['cliente'].dropna().unique().tolist()),
            sorted(temp.get('categoria', pd.Series()).dropna().unique().tolist())
        )
    
    anos, _, _, _ = get_opcoes(df, "Todos", "Todos", "Todos")
    ano = st.selectbox("**ANO**", ["Todos"] + anos)
    _, coms, _, _ = get_opcoes(df, ano, "Todos", "Todos")
    comercial = st.selectbox("**COMERCIAL**", ["Todos"] + coms)
    _, _, cls, _ = get_opcoes(df, ano, comercial, "Todos")
    cliente = st.selectbox("**CLIENTE**", ["Todos"] + cls)
    _, _, _, cats = get_opcoes(df, ano, comercial, cliente)
    categoria = st.selectbox("**CATEGORIA**", ["Todas"] + cats)

    dados_filtrados = df.copy()
    if ano != "Todos": dados_filtrados = dados_filtrados[dados_filtrados['ano'] == int(ano)]
    if comercial != "Todos": dados_filtrados = dados_filtrados[dados_filtrados['comercial'].astype(str).str.strip() == str(comercial).strip()]
    if cliente != "Todos": dados_filtrados = dados_filtrados[dados_filtrados['cliente'].astype(str).str.strip() == str(cliente).strip()]
    if categoria != "Todas": dados_filtrados = dados_filtrados[dados_filtrados['categoria'].astype(str).str.strip() == str(categoria).strip()]

# --- FUNÇÕES ---
def formatar_euros(v): return "€ 0" if pd.isna(v) or v == 0 else f"€ {v:,.0f}"
def formatar_kg(v): return "0 kg" if pd.isna(v) or v == 0 else f"{v:,.0f} kg"
month_pt = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}

# --- PÁGINAS ---
if pagina == "VISÃO GERAL":
    st.markdown("<h1>Dashboard Analítico</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Visão completa do desempenho comercial</p>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("QUANTIDADE TOTAL", formatar_kg(dados_filtrados['qtd'].sum()))
    with col2: st.metric("VALOR TOTAL", formatar_euros(dados_filtrados['v_liquido'].sum()))
    with col3: st.metric("CLIENTES ÚNICOS", dados_filtrados['cliente'].nunique())
    with col4: st.metric("COMERCIAIS", dados_filtrados['comercial'].nunique())
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### TOP 10 CLIENTES (KG)")
        top = dados_filtrados.groupby('cliente')['qtd'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(top.reset_index(), x='cliente', y='qtd', text='qtd', color='qtd', color_continuous_scale='Blues')
        fig.update_traces(texttemplate='%{text:,.0f} kg', textposition='outside')
        fig.update_layout(showlegend=False, height=450, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### PERFORMANCE COMERCIAL")
        com = dados_filtrados.groupby('comercial')['v_liquido'].sum().sort_values(ascending=False).head(8)
        fig = px.bar(com.reset_index(), x='comercial', y='v_liquido', color='v_liquido', color_continuous_scale='Purples')
        fig.update_traces(texttemplate='€ %{text:,.0f}', textposition='outside')
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)

# (Outras páginas seguem o mesmo padrão — posso adicionar todas se quiser)

# Exportar
if st.sidebar.button("EXPORTAR DADOS"):
    st.download_button("Baixar Excel", gerar_excel(dados_filtrados), "dados.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
