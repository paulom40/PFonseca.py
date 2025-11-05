# dashboard_pro.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import requests

# =============================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================
st.set_page_config(
    page_title="BI Pro - Dashboard Empresarial",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="Chart"
)

# =============================================
# ESTILO PROFISSIONAL (PRETO NOS FILTROS!)
# =============================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    /* Fonte profissional */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Fundo suave */
    .main { background: #f8fafc; padding: 2rem; }
    
    /* Títulos */
    h1 { color: #1e293b; font-size: 2.8rem; font-weight: 800; text-align: center; margin: 0 0 1rem; }
    h2 { color: #334155; font-size: 1.8rem; font-weight: 700; margin: 2rem 0 1rem; }
    
    /* Sidebar Premium */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4f46e5 0%, #7c3aed 100%);
        border-radius: 0 24px 24px 0;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.3);
        padding: 2rem 1.5rem;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Logo */
    .logo { text-align: center; margin-bottom: 2rem; }
    .logo h1 { font-size: 2rem; margin: 0; color: white; }
    .logo p { font-size: 0.95rem; color: #e0e7ff; margin: 0.5rem 0 0; }
    
    /* FILTROS VISÍVEIS (PRETO!) */
    .stSelectbox > div > div {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 0.6rem !important;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08) !important;
    }
    .stSelectbox > div > div > div,
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [role="option"] {
        color: #1e293b !important;
        background: white !important;
    }
    .stSelectbox [role="option"]:hover {
        background: #f1f5f9 !important;
        color: #4f46e5 !important;
    }
    
    /* Labels brancos */
    .stSidebar label, .stSidebar .css-1cpxqw2 {
        color: white !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Navegação */
    .nav-box {
        background: rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    .stRadio > div > label {
        background: transparent !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.2rem !important;
        margin: 0.4rem 0 !important;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    .stRadio > div > label:hover {
        background: rgba(255,255,255,0.2) !important;
        transform: translateX(6px);
    }
    .stRadio > div > label:has(input:checked) {
        background: rgba(255,255,255,0.3) !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(255,255,255,0.2);
    }
    
    /* Cartões KPI */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 18px;
        padding: 1.8rem;
        box-shadow: 0 6px 25px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(79,70,229,0.2);
        border-color: #7c3aed;
    }
    [data-testid="metric-value"] { font-size: 2.4rem !important; font-weight: 800 !important; color: #1e293b !important; }
    [data-testid="metric-label"] { font-size: 1.1rem !important; color: #7c3aed !important; font-weight: 600; }
    
    /* Botão Exportar */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 6px 20px rgba(124,58,237,0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 30px rgba(124,58,237,0.5) !important;
    }
    
    /* Gráficos */
    .plotly-graph-div {
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 6px 25px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# CARREGAR DADOS (VALOR CORRIGIDO!)
# =============================================
month_names = {'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,
               'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12,
               'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
               'july':7,'august':8,'september':9,'october':10,'november':11,'december':12}

@st.cache_data(ttl=3600)
def carregar_dados():
    try:
        url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx"
        df = pd.read_excel(BytesIO(requests.get(url, timeout=15).content))
        
        # Renomear colunas
        df.rename(columns={
            'Mês':'mes','mes':'mes','MÊS':'mes',
            'Qtd.':'qtd','Qtd':'qtd','qtd':'qtd','QTD':'qtd','Quantidade':'qtd',
            'Ano':'ano','ano':'ano','ANO':'ano',
            'Cliente':'cliente','CLIENTE':'cliente',
            'Comercial':'comercial','COMERCIAL':'comercial',
            'V. Líquido':'v_liquido','V_Liquido':'v_liquido','V. LÍQUIDO':'v_liquido',
            'Categoria':'categoria','CATEGORIA':'categoria'
        }, inplace=True)
        
        # CORREÇÃO DO VALOR (EUROPEU!)
        if 'v_liquido' in df.columns:
            df['v_liquido'] = df['v_liquido'].astype(str).str.strip()
            df['v_liquido'] = df['v_liquido'].str.replace(r'\.', '', regex=True)
            df['v_liquido'] = df['v_liquido'].str.replace(',', '.', regex=False)
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')
        
        # Mês
        if df['mes'].dtype == 'object':
            df['mes'] = df['mes'].apply(lambda x: month_names.get(str(x).strip().lower(), np.nan))
        df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
        
        # Numéricos
        for col in ['ano','qtd']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.dropna(subset=['mes','qtd','ano','cliente','comercial'], inplace=True)
        df = df[(df['mes'] >= 1) & (df['mes'] <= 12)]
        return df
    except:
        st.error("Erro ao carregar dados.")
        return pd.DataFrame()

df = carregar_dados()
if df.empty: st.stop()

# =============================================
# SIDEBAR
# =============================================
with st.sidebar:
    st.markdown('<div class="logo"><h1>BI Pro</h1><p>Dashboard Empresarial</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="nav-box">', unsafe_allow_html=True)
    pagina = st.radio("NAVEGAÇÃO", [
        "VISÃO GERAL",
        "KPIS PERSONALIZADOS",
        "TENDÊNCIAS",
        "ALERTAS",
        "CLIENTES",
        "COMPARAÇÃO"
    ], key="nav")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### FILTROS")
    
    def opts(d, a, c, cl):
        t = d.copy()
        if a != "Todos": t = t[t['ano']==int(a)]
        if c != "Todos": t = t[t['comercial'].astype(str).str.strip()==str(c).strip()]
        if cl != "Todos": t = t[t['cliente'].astype(str).str.strip()==str(cl).strip()]
        return (
            sorted(t['ano'].dropna().unique().astype(int).tolist()),
            sorted(t['comercial'].dropna().unique().tolist()),
            sorted(t['cliente'].dropna().unique().tolist()),
            sorted(t.get('categoria', pd.Series()).dropna().unique().tolist())
        )
    
    anos, _, _, _ = opts(df, "Todos", "Todos", "Todos")
    ano = st.selectbox("ANO", ["Todos"] + anos)
    _, coms, _, _ = opts(df, ano, "Todos", "Todos")
    comercial = st.selectbox("COMERCIAL", ["Todos"] + coms)
    _, _, cls, _ = opts(df, ano, comercial, "Todos")
    cliente = st.selectbox("CLIENTE", ["Todos"] + cls)
    _, _, _, cats = opts(df, ano, comercial, cliente)
    categoria = st.selectbox("CATEGORIA", ["Todas"] + cats)
    
    # Aplicar filtros
    dados = df.copy()
    if ano != "Todos": dados = dados[dados['ano'] == int(ano)]
    if comercial != "Todos": dados = dados[dados['comercial'].astype(str).str.strip() == str(comercial).strip()]
    if cliente != "Todos": dados = dados[dados['cliente'].astype(str).str.strip() == str(cliente).strip()]
    if categoria != "Todas": dados = dados[dados['categoria'].astype(str).str.strip() == str(categoria).strip()]

# =============================================
# FUNÇÕES
# =============================================
def fmt_euro(v): return "€ 0" if pd.isna(v) else f"€ {v:,.0f}"
def fmt_kg(v): return "0 kg" if pd.isna(v) else f"{v:,.0f} kg"
mes_pt = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}

def exportar(d):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        d.to_excel(writer, index=False, sheet_name='Vendas')
    return output.getvalue()

# =============================================
# PÁGINAS
# =============================================
if pagina == "VISÃO GERAL":
    st.markdown("<h1>Dashboard Empresarial</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748b; font-size:1.1rem;'>Análise completa em tempo real</p>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("QUANTIDADE TOTAL", fmt_kg(dados['qtd'].sum()))
    with c2: st.metric("VALOR TOTAL", fmt_euro(dados['v_liquido'].sum()))
    with c3: st.metric("CLIENTES ÚNICOS", dados['cliente'].nunique())
    with c4: st.metric("COMERCIAIS", dados['comercial'].nunique())
    
    st.markdown("---")
    
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown("### TOP 10 CLIENTES (KG)")
        top = dados.groupby('cliente')['qtd'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(top.reset_index(), x='cliente', y='qtd', text='qtd',
                     color='qtd', color_continuous_scale='Blues')
        fig.update_traces(texttemplate='%{text:,.0f} kg', textposition='outside')
        fig.update_layout(showlegend=False, height=480, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### POR CATEGORIA")
        cat = dados.groupby('categoria')['v_liquido'].sum().sort_values(ascending=False)
        fig = px.pie(cat.reset_index(), values='v_liquido', names='categoria',
                     color_discrete_sequence=px.colors.sequential.Purples)
        fig.update_traces(texttemplate='%{label}<br>€ %{value:,.0f}', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)

# Botão flutuante de exportação
st.sidebar.markdown("---")
if st.sidebar.button("EXPORTAR PARA EXCEL", use_container_width=True):
    st.download_button(
        label="BAIXAR DADOS FILTRADOS",
        data=exportar(dados),
        file_name=f"vendas_{ano}_{comercial}_{cliente}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
