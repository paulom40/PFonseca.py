# dashboard_pro.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import requests

# =============================================
# CONFIGURAÇÃO
# =============================================
st.set_page_config(
    page_title="BI Pro - Dashboard Empresarial",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="Chart"
)

# =============================================
# ESTILO PROFISSIONAL (FILTROS VISÍVEIS!)
# =============================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background: #f8fafc; padding: 2rem; }
    h1 { color: #1e293b; font-size: 2.8rem; font-weight: 800; text-align: center; margin: 0 0 1rem; }
    h2 { color: #334155; font-size: 1.8rem; font-weight: 700; margin: 2rem 0 1rem; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4f46e5 0%, #7c3aed 100%);
        border-radius: 0 24px 24px 0;
        box-shadow: 0 10px 30px rgba(79,70,229,0.3);
        padding: 2rem 1.5rem;
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* FILTROS: TEXTO PRETO */
    .stSelectbox > div > div {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 0.6rem !important;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08) !important;
    }
    .stSelectbox > div > div > div,
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [role="option"],
    .stSelectbox [data-baseweb="select"] input {
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
    }

    /* Navegação */
    .nav-box { background: rgba(255,255,255,0.12); border-radius: 16px; padding: 1rem; }
    .stRadio > div > label {
        background: transparent !important; border-radius: 12px !important;
        padding: 0.8rem 1.2rem !important; margin: 0.4rem 0 !important;
        transition: all 0.3s ease; font-weight: 500;
    }
    .stRadio > div > label:hover { background: rgba(255,255,255,0.2) !important; transform: translateX(6px); }
    .stRadio > div > label:has(input:checked) {
        background: rgba(255,255,255,0.3) !important; font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(255,255,255,0.2);
    }

    /* KPIs */
    [data-testid="metric-container"] {
        background: white; border-radius: 18px; padding: 1.8rem;
        box-shadow: 0 6px 25px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-8px); box-shadow: 0 15px 35px rgba(79,70,229,0.2);
        border-color: #7c3aed;
    }
    [data-testid="metric-value"] { font-size: 2.4rem !important; font-weight: 800 !important; color: #1e293b !important; }
    [data-testid="metric-label"] { font-size: 1.1rem !important; color: #7c3aed !important; font-weight: 600; }

    .plotly-graph-div { border-radius: 18px; overflow: hidden; box-shadow: 0 6px 25px rgba(0,0,0,0.1); }
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
        
        df.rename(columns=lambda x: x.strip().lower(), inplace=True)
        col_map = {
            'mês':'mes','qtd.':'qtd','qtd':'qtd','quantidade':'qtd',
            'ano':'ano','cliente':'cliente','comercial':'comercial',
            'v. líquido':'v_liquido','v_liquido':'v_liquido','categoria':'categoria'
        }
        df.rename(columns=col_map, inplace=True)
        
        # CORREÇÃO DO VALOR EUROPEU
        if 'v_liquido' in df.columns:
            df['v_liquido'] = df['v_liquido'].astype(str).str.strip()
            df['v_liquido'] = df['v_liquido'].str.replace(r'\.', '', regex=True)
            df['v_liquido'] = df['v_liquido'].str.replace(',', '.', regex=False)
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')
        
        if 'mes' in df.columns and df['mes'].dtype == 'object':
            df['mes'] = df['mes'].apply(lambda x: month_names.get(str(x).strip().lower(), np.nan))
        df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')
        
        df.dropna(subset=['mes','qtd','ano','cliente','comercial'], inplace=True)
        df = df[(df['mes'] >= 1) & (df['mes'] <= 12)]
        return df
    except:
        st.error("Erro ao carregar dados.")
        return pd.DataFrame()

df = carregar_dados()
if df.empty: st.stop()

# =============================================
# SIDEBAR + FILTROS
# =============================================
with st.sidebar:
    st.markdown('<div class="logo"><h1>BI Pro</h1><p>Dashboard Empresarial</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-box">', unsafe_allow_html=True)
    pagina = st.radio("NAVEGAÇÃO", [
        "VISÃO GERAL", "KPIS PERSONALIZADOS", "TENDÊNCIAS",
        "ALERTAS", "CLIENTES", "COMPARAÇÃO"
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

    # === APLICAR FILTROS EM TODAS AS PÁGINAS ===
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
# TODAS AS PÁGINAS USAM `dados` (FILTROS ATIVOS!)
# =============================================
if pagina == "VISÃO GERAL":
    st.markdown("<h1>Visão Geral</h1>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("QUANTIDADE", fmt_kg(dados['qtd'].sum()))
    with c2: st.metric("VALOR TOTAL", fmt_euro(dados['v_liquido'].sum()))
    with c3: st.metric("CLIENTES", dados['cliente'].nunique())
    with c4: st.metric("COMERCIAIS", dados['comercial'].nunique())

elif pagina == "KPIS PERSONALIZADOS":
    st.markdown("<h1>KPIs Personalizados</h1>", unsafe_allow_html=True)
    tipo = st.selectbox("Métrica", ["Quantidade (kg)", "Valor (€)"])
    nome = st.text_input("Nome do KPI", f"Evolução {tipo}")
    
    if "kg" in tipo:
        serie = dados.groupby('mes')['qtd'].sum()
        y_label = "kg"
    else:
        serie = dados.groupby('mes')['v_liquido'].sum()
        y_label = "€"
    
    fig = px.line(serie.reset_index(), x='mes', y=0, title=nome, markers=True)
    fig.update_xaxes(tickvals=list(mes_pt.keys()), ticktext=list(mes_pt.values()))
    st.plotly_chart(fig, use_container_width=True)

elif pagina == "TENDÊNCIAS":
    st.markdown("<h1>Tendências</h1>", unsafe_allow_html=True)
    metrica = st.selectbox("Métrica", ["Quantidade", "Valor"])
    janela = st.slider("Média Móvel", 1, 6, 3)
    
    temp = dados.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    temp = temp.sort_values('data')
    
    if metrica == "Quantidade":
        s = temp.groupby('data')['qtd'].sum()
    else:
        s = temp.groupby('data')['v_liquido'].sum()
    
    ma = s.rolling(window=janela, center=True).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s.index, y=s, mode='lines+markers', name='Real'))
    fig.add_trace(go.Scatter(x=ma.index, y=ma, mode='lines', name=f'Média {janela}m', line=dict(dash='dash')))
    st.plotly_chart(fig, use_container_width=True)

elif pagina == "ALERTAS":
    st.markdown("<h1>Alertas</h1>", unsafe_allow_html=True)
    temp = dados.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    mensal = temp.groupby(pd.Grouper(key='data', freq='M'))[['qtd','v_liquido']].sum()
    
    alertas = []
    for i in range(1, len(mensal)):
        if mensal['qtd'].iloc[i-1] > 0 and (mensal['qtd'].iloc[i] / mensal['qtd'].iloc[i-1]) < 0.8:
            alertas.append(f"Queda >20% em Qtd: {mensal.index[i].strftime('%b/%Y')}")
        if mensal['v_liquido'].iloc[i-1] > 0 and (mensal['v_liquido'].iloc[i] / mensal['v_liquido'].iloc[i-1]) < 0.85:
            alertas.append(f"Queda >15% em Valor: {mensal.index[i].strftime('%b/%Y')}")
    
    if alertas:
        for a in alertas: st.error(a)
    else:
        st.success("Nenhum alerta.")

elif pagina == "CLIENTES":
    st.markdown("<h1>Análise de Clientes</h1>", unsafe_allow_html=True)
    cli = st.selectbox("Cliente", ["Todos"] + sorted(dados['cliente'].unique()))
    df_cli = dados if cli == "Todos" else dados[dados['cliente'] == cli]
    
    col1, col2 = st.columns(2)
    with col1: st.metric("Qtd Total", fmt_kg(df_cli['qtd'].sum()))
    with col2: st.metric("Valor Total", fmt_euro(df_cli['v_liquido'].sum()))
    
    fig = px.scatter(df_cli, x='qtd', y='v_liquido', color='comercial', size='qtd',
                     hover_data=['mes','ano'], title="Dispersão Qtd vs Valor")
    st.plotly_chart(fig, use_container_width=True)

elif pagina == "COMPARAÇÃO":
    st.markdown("<h1>Comparação de Períodos</h1>", unsafe_allow_html=True)
    p1 = st.selectbox("Período 1", sorted(dados['ano'].unique()))
    p2 = st.selectbox("Período 2", sorted(dados['ano'].unique()))
    
    d1 = dados[dados['ano'] == p1]
    d2 = dados[dados['ano'] == p2]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"Qtd {p1}", fmt_kg(d1['qtd'].sum()))
        st.metric(f"Valor {p1}", fmt_euro(d1['v_liquido'].sum()))
    with col2:
        st.metric(f"Qtd {p2}", fmt_kg(d2['qtd'].sum()))
        st.metric(f"Valor {p2}", fmt_euro(d2['v_liquido'].sum()))

# Exportar
if st.sidebar.button("EXPORTAR EXCEL"):
    st.download_button("BAIXAR", exportar(dados), f"vendas_{ano}_{cliente}.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
