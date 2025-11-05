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
# CONFIG & ESTILO
# =============================================
st.set_page_config(page_title="BI Pro", layout="wide", page_icon="📊")
st.markdown("""
<style>
    .main {background:#f8fafc; padding:2rem}
    h1 {color:#1e293b; font-size:2.6rem; font-weight:800; text-align:center}
    [data-testid="stSidebar"] {background:linear-gradient(#4f46e5,#7c3aed); border-radius:0 20px 20px 0; padding:2rem}
    .stSelectbox > div > div {background:white !important; border:2px solid #e2e8f0 !important; border-radius:12px !important}
    .stSelectbox span, .stSelectbox input {color:#1e293b !important}
    [data-testid="metric-container"] {background:white; border-radius:16px; padding:1.5rem; box-shadow:0 6px 25px rgba(0,0,0,0.1)}
    .plotly-graph-div {border-radius:18px; overflow:hidden; box-shadow:0 8px 30px rgba(0,0,0,0.12)}
</style>
""", unsafe_allow_html=True)

# =============================================
# CARREGAMENTO + VALIDAÇÃO 100% SEGURA
# =============================================
month_map = {'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,
             'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}

@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_excel(BytesIO(requests.get(
            "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx", 
            timeout=15).content))
        
        # === 1. PADRONIZAR COLUNAS ===
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

        # === 2. FORÇAR CONVERSÃO NUMÉRICA (100% SEGURA) ===
        df['mes'] = df['mes'].astype(str).str.strip().str.lower().map(month_map)
        df['mes'] = pd.to_numeric(df['mes'], errors='coerce')

        df['qtd'] = df['qtd'].astype(str).str.replace(r'\D', '', regex=True)
        df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce').fillna(0).astype(int)

        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')

        if 'v_liquido' in df.columns:
            # CORREÇÃO: Remover o parâmetro 'errors' do astype
            df['v_liquido'] = (df['v_liquido'].astype(str)
                               .str.replace(r'[^\d,.]', '', regex=True)
                               .str.replace(r'\.', '', regex=True)
                               .str.replace(',', '.', regex=False)
                               .str.replace(r'(\.\d{2})\d+', r'\1', regex=True))
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce').fillna(0)

        # === 3. LIMPEZA FINAL ===
        df = df.dropna(subset=['mes', 'qtd', 'ano', 'cliente', 'comercial', 'v_liquido'])
        df = df[(df['mes'].between(1, 12)) & 
                (df['qtd'] > 0) & 
                (df['v_liquido'] > 0)]
        df = df.drop_duplicates(subset=['cliente','comercial','ano','mes','qtd','v_liquido'])

        st.success("Dados carregados com sucesso!")
        return df

    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty: st.stop()

# =============================================
# SIDEBAR
# =============================================
with st.sidebar:
    st.markdown("<h2 style='color:white'>BI Pro</h2>", unsafe_allow_html=True)
    page = st.radio("Navegação", [
        "Visão Geral", "KPIs", "Tendências", "Alertas", "Clientes", "Comparação", "Comparação Clientes"
    ])
    
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
# FUNÇÕES
# =============================================
fmt = lambda x, u: f"{x:,.0f} {u}" if pd.notna(x) else f"0 {u}"

# =============================================
# PÁGINAS
# =============================================
if page == "Visão Geral":
    st.markdown("<h1>Visão Geral</h1>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Quantidade", fmt(data['qtd'].sum(), "kg"))
    with c2: st.metric("Valor Total", fmt(data['v_liquido'].sum(), "EUR"))
    with c3: st.metric("Clientes", data['cliente'].nunique())
    with c4: st.metric("Comerciais", data['comercial'].nunique())

elif page == "KPIs":
    st.markdown("<h1>KPIs</h1>", unsafe_allow_html=True)
    metrica = st.selectbox("Métrica", ["Quantidade", "Valor"])
    grupo = st.selectbox("Agrupar", ["Mês", "Comercial", "Cliente"])
    col = 'qtd' if metrica == "Quantidade" else 'v_liquido'
    gcol = {'Mês':'mes', 'Comercial':'comercial', 'Cliente':'cliente'}[grupo]
    agg = data.groupby(gcol)[col].sum().reset_index().sort_values(col, ascending=False).head(10)
    if grupo == "Mês": agg['mes'] = agg['mes'].map({v:k for k,v in {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}.items()})
    fig = px.bar(agg, x=gcol, y=col, title=f"Top 10 {metrica} por {grupo}")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Tendências":
    st.markdown("<h1>Tendências</h1>", unsafe_allow_html=True)
    temp = data.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    serie = temp.groupby('data')['v_liquido'].sum()
    fig = px.line(serie.reset_index(), x='data', y='v_liquido', title="Evolução de Vendas")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Alertas":
    st.markdown("<h1>Alertas</h1>", unsafe_allow_html=True)
    temp = data.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    mensal = temp.groupby(pd.Grouper(key='data', freq='M'))[['qtd','v_liquido']].sum()
    for i in range(1, len(mensal)):
        if mensal['qtd'].iloc[i] / mensal['qtd'].iloc[i-1] < 0.8:
            st.error(f"Queda >20% em Qtd: {mensal.index[i].strftime('%b/%Y')}")
    if mensal['qtd'].pct_change().dropna().ge(-0.2).all():
        st.success("Sem quedas críticas.")

elif page == "Clientes":
    st.markdown("<h1>Clientes</h1>", unsafe_allow_html=True)
    cli = st.selectbox("Cliente", ["Todos"] + sorted(data['cliente'].unique()))
    dfc = data if cli == "Todos" else data[data['cliente'] == cli]
    st.metric("Qtd", fmt(dfc['qtd'].sum(), "kg"))
    st.metric("Valor", fmt(dfc['v_liquido'].sum(), "EUR"))
    fig = px.scatter(dfc, x='qtd', y='v_liquido', color='comercial')
    st.plotly_chart(fig, use_container_width=True)

elif page == "Comparação":
    st.markdown("<h1>Comparação</h1>", unsafe_allow_html=True)
    anos = sorted(data['ano'].unique())
    if len(anos) >= 2:
        a1, a2 = st.columns(2)
        with a1: y1 = st.selectbox("Ano 1", anos)
        with a2: y2 = st.selectbox("Ano 2", anos, index=1)
        d1, d2 = data[data['ano']==y1], data[data['ano']==y2]
        c1, c2 = st.columns(2)
        with c1: st.metric(f"Qtd {y1}", fmt(d1['qtd'].sum(), "kg"))
        with c2: st.metric(f"Qtd {y2}", fmt(d2['qtd'].sum(), "kg"))

elif page == "Comparação Clientes":
    st.markdown("### Qtd Mensal por Cliente")
    pivot = data.assign(data=pd.to_datetime(data['ano'].astype(str)+'-'+data['mes'].astype(str).str.zfill(2)+'-01'))\
                .groupby(['cliente','data'])['qtd'].sum().unstack(fill_value=0)
    pivot.columns = pivot.columns.strftime('%b/%y')
    
    st.dataframe(pivot.style.format("{:,.0f}"), use_container_width=True)
    
    cresc = pivot.pct_change(axis=1).mul(100).round(1)
    st.dataframe(cresc.style.format("{:+.1f}%")\
                 .applymap(lambda v: f"color: {'#16a34a' if v>0 else '#dc2626' if v<0 else '#666'}"), 
                 use_container_width=True)
    
    sem_compra = (pivot==0).sum(axis=1)
    for cli, m in sem_compra[sem_compra>0].items():
        st.error(f"**{cli}** sem compra em **{m} mês(es)**")
    if sem_compra.sum()==0: st.success("Todos compraram todo mês!")
    
    st.plotly_chart(px.line(pivot.T.nlargest(10, columns=pivot.sum().idxmax()).T,
                            title="Top 10 Clientes", height=500), use_container_width=True)

# Exportar
if st.sidebar.button("Exportar"):
    st.download_button("Baixar CSV", data.to_csv(index=False), "vendas.csv", "text/csv")
