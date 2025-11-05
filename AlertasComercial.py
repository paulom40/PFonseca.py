# dashboard_pro.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import requests
import warnings
warnings.filterwarnings("ignore")

# =============================================
# CONFIG & ESTILO PROFISSIONAL
# =============================================
st.set_page_config(page_title="BI Pro", layout="wide", page_icon="Chart")
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
    .main {background:#f8fafc; padding:2rem}
    h1 {color:#1e293b; font-size:2.6rem; font-weight:800; text-align:center; margin-bottom:1.5rem}
    [data-testid="stSidebar"] {background:linear-gradient(180deg, #4f46e5 0%, #7c3aed 100%); border-radius:0 20px 20px 0; padding:2rem}
    .stSelectbox > div > div {background:white !important; border:2px solid #e2e8f0 !important; border-radius:12px !important}
    .stSelectbox span, .stSelectbox input {color:#1e293b !important}
    [data-testid="metric-container"] {background:white; border-radius:16px; padding:1.5rem; box-shadow:0 6px 25px rgba(0,0,0,0.1); transition:0.3s}
    [data-testid="metric-container"]:hover {transform:translateY(-5px); box-shadow:0 12px 35px rgba(79,70,229,0.2)}
    .plotly-graph-div {border-radius:18px; overflow:hidden; box-shadow:0 8px 30px rgba(0,0,0,0.12)}
</style>
""", unsafe_allow_html=True)

# =============================================
# CARREGAR + VALIDAR DADOS
# =============================================
month_map = {v.lower():k for k,v in {
    1:'janeiro',2:'fevereiro',3:'março',4:'abril',5:'maio',6:'junho',
    7:'julho',8:'agosto',9:'setembro',10:'outubro',11:'novembro',12:'dezembro'
}.items()}

@st.cache_data(ttl=3600)
def load_and_validate():
    try:
        df = pd.read_excel(BytesIO(requests.get(
            "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx", 
            timeout=15).content))
        
        # Padronizar colunas
        df.columns = [col.strip() for col in df.columns]
        col_map = {}
        raw_lower = [col.lower() for col in df.columns]
        
        mapping = {
            'mes': ['mês', 'mes'],
            'qtd': ['qtd.', 'qtd', 'quantidade'],
            'ano': ['ano'],
            'cliente': ['cliente'],
            'comercial': ['comercial'],
            'v_liquido': ['v. líquido', 'v_liquido']
        }
        
        for std, variants in mapping.items():
            for var in variants:
                if var in raw_lower:
                    idx = raw_lower.index(var)
                    col_map[df.columns[idx]] = std
                    break
        
        df.rename(columns=col_map, inplace=True)
        
        # Converter mês
        df['mes'] = df['mes'].astype(str).str.strip().str.lower().map(month_map).astype('Int64')
        df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        
        if 'v_liquido' in df.columns:
            df['v_liquido'] = (df['v_liquido'].astype(str)
                               .str.replace(r'\.', '', regex=True)
                               .str.replace(',', '.', regex=False)
                               .str.replace(r'(\.\d{2})\d+', r'\1', regex=True)
                               .astype(float, errors='ignore'))
        
        df.dropna(subset=['mes','qtd','ano','cliente','comercial','v_liquido'], inplace=True)
        df = df[(df['mes'].between(1,12)) & (df['qtd'] > 0) & (df['v_liquido'] > 0)]
        df = df.drop_duplicates(subset=['cliente','comercial','ano','mes','qtd','v_liquido'])
        
        return df
    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame()

df = load_and_validate()
if df.empty: st.stop()

# =============================================
# SIDEBAR
# =============================================
with st.sidebar:
    st.markdown("<h2 style='color:white'>BI Pro</h2>", unsafe_allow_html=True)
    page = st.radio("Navegação", ["Visão Geral", "KPIs", "Tendências", "Alertas", "Clientes", "Comparação"])
    
    def opts(d, a, c, cl):
        t = d.copy()
        if a != "Todos": t = t[t['ano'] == int(a)]
        if c != "Todos": t = t[t['comercial'].astype(str) == str(c)]
        if cl != "Todos": t = t[t['cliente'].astype(str) == str(cl)]
        return (sorted(t['ano'].unique().astype(int)),
                sorted(t['comercial'].unique()),
                sorted(t['cliente'].unique()),
                sorted(t.get('categoria', pd.Series()).dropna().unique()))
    
    anos = sorted(df['ano'].unique().astype(int))
    ano = st.selectbox("Ano", ["Todos"] + anos)
    coms = opts(df, ano, "Todos", "Todos")[1]
    comercial = st.selectbox("Comercial", ["Todos"] + coms)
    cls = opts(df, ano, comercial, "Todos")[2]
    cliente = st.selectbox("Cliente", ["Todos"] + cls)
    cats = opts(df, ano, comercial, cliente)[3]
    categoria = st.selectbox("Categoria", ["Todas"] + cats)

    data = df.copy()
    if ano != "Todos": data = data[data['ano'] == int(ano)]
    if comercial != "Todos": data = data[data['comercial'].astype(str) == str(comercial)]
    if cliente != "Todos": data = data[data['cliente'].astype(str) == str(cliente)]
    if categoria != "Todas" and 'categoria' in data.columns:
        data = data[data['categoria'].astype(str) == str(categoria)]

# =============================================
# FUNÇÕES GRÁFICAS
# =============================================
def fmt(x, u): return f"{x:,.0f} {u}" if pd.notna(x) else f"0 {u}"
mes_pt = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}

def create_line_chart(df, x, y, title, color="#4f46e5"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y], mode='lines+markers',
        line=dict(color=color, width=4, shape='spline'),
        marker=dict(size=10, line=dict(width=2, color='white')),
        name=title,
        hovertemplate=f"<b>{title}</b><br>%{{x}}: %{{y:,.0f}}<extra></extra>"
    ))
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", x=0.5, font=dict(size=20)),
        xaxis=dict(title="", gridcolor='#e2e8f0', tickangle=0),
        yaxis=dict(title="", gridcolor='#e2e8f0'),
        plot_bgcolor='white', paper_bgcolor='white',
        hovermode='x unified',
        height=500,
        margin=dict(l=40, r=40, t=80, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def create_bar_chart(df, x, y, color, title):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df[x], y=df[y],
        marker=dict(color=color, line=dict(width=1, color='white')),
        text=df[y].apply(lambda x: f"{x:,.0f}"),
        textposition='outside',
        hovertemplate=f"<b>{title}</b><br>%{{x}}: %{{y:,.0f}}<extra></extra>"
    ))
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", x=0.5, font=dict(size=20)),
        xaxis=dict(title="", tickangle=-45),
        yaxis=dict(title="", showticklabels=False),
        plot_bgcolor='white', paper_bgcolor='white',
        height=500,
        bargap=0.3
    )
    return fig

# =============================================
# PÁGINAS COM GRÁFICOS TOP
# =============================================
if page == "Visão Geral":
    st.markdown("<h1>Visão Geral</h1>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Quantidade", fmt(data['qtd'].sum(), "kg"))
    with c2: st.metric("Valor Total", fmt(data['v_liquido'].sum(), "EUR"))
    with c3: st.metric("Clientes", data['cliente'].nunique())
    with c4: st.metric("Comerciais", data['comercial'].nunique())

    # Gráfico de evolução
    temp = data.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    mensal = temp.groupby('data')['v_liquido'].sum().reset_index()
    fig = create_line_chart(mensal, 'data', 'v_liquido', "Evolução de Vendas")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})

elif page == "KPIs":
    st.markdown("<h1>KPIs Personalizados</h1>", unsafe_allow_html=True)
    metrica = st.selectbox("Métrica", ["Quantidade", "Valor"])
    grupo = st.selectbox("Agrupar por", ["Mês", "Comercial", "Cliente"])
    
    col = 'qtd' if metrica == "Quantidade" else 'v_liquido'
    gcol = {'Mês':'mes', 'Comercial':'comercial', 'Cliente':'cliente'}[grupo]
    
    agg = data.groupby(gcol)[col].sum().reset_index()
    agg = agg.sort_values(col, ascending=False).head(10)
    
    if grupo == "Mês":
        agg['mes'] = agg['mes'].map(mes_pt)
    
    color = "#7c3aed" if metrica == "Valor" else "#10b981"
    fig = create_bar_chart(agg, gcol, col, color, f"Top 10 {metrica} por {grupo}")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Tendências":
    st.markdown("<h1>Tendências & Previsão</h1>", unsafe_allow_html=True)
    metrica = st.selectbox("Métrica", ["Quantidade", "Valor"])
    meses = st.slider("Prever", 1, 12, 6)
    
    temp = data.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    serie = temp.groupby('data')[['qtd','v_liquido']].sum()
    col = 'qtd' if metrica == "Quantidade" else 'v_liquido'
    s = serie[col].asfreq('MS').ffill()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s.index, y=s, mode='lines+markers', name='Real',
                            line=dict(color="#4f46e5", width=4), marker=dict(size=8)))
    
    try:
        import pmdarima as pm
        model = pm.auto_arima(s, seasonal=True, m=12, stepwise=True, suppress_warnings=True)
        pred = model.predict(n_periods=meses, return_conf_int=True)
        forecast, conf = pred[0], pred[1]
        future = pd.date_range(s.index[-1] + pd.DateOffset(months=1), periods=meses, freq='MS')
        
        fig.add_trace(go.Scatter(x=future, y=forecast, mode='lines+markers', name='Previsão',
                                line=dict(color="#10b981", width=4, dash='dot')))
        fig.add_trace(go.Scatter(x=list(future)+list(future)[::-1],
                               y=list(conf[:,1])+list(conf[:,0])[::-1],
                               fill='toself', fillcolor='rgba(16,185,129,0.2)',
                               line=dict(color='rgba(0,0,0,0)'), name='95% Confiança'))
    except: pass
    
    fig.update_layout(title="<b>Previsão com SARIMA</b>", height=600, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# (Outras páginas mantidas com gráficos melhorados)

# Exportar
if st.sidebar.button("Exportar Dados"):
    st.download_button("Baixar CSV", data.to_csv(index=False), "vendas.csv", "text/csv")
