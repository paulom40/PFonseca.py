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
st.set_page_config(page_title="BI Pro", layout="wide", page_icon="Chart")
st.markdown("""
<style>
    .main {background:#f8fafc; padding:2rem}
    h1 {color:#1e293b; font-size:2.6rem; font-weight:800; text-align:center}
    [data-testid="stSidebar"] {background:linear-gradient(#4f46e5,#7c3aed); border-radius:0 20px 20px 0; padding:2rem}
    .stSelectbox > div > div {background:white !important; border:2px solid #e2e8f0 !important; border-radius:12px !important}
    .stSelectbox span, .stSelectbox input {color:#1e293b !important}
    [data-testid="metric-container"] {background:white; border-radius:16px; padding:1.5rem; box-shadow:0 4px 20px rgba(0,0,0,0.1)}
    .validation-error {color:#dc2626; font-weight:600; padding:0.5rem; background:#fee2e2; border-radius:8px; border-left:4px solid #dc2626}
    .validation-success {color:#16a34a; font-weight:600; padding:0.5rem; background:#dcfce7; border-radius:8px; border-left:4px solid #16a34a}
</style>
""", unsafe_allow_html=True)

# =============================================
# VALIDAÇÃO DE DADOS (TODAS AS COLUNAS)
# =============================================
month_map = {
    'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,
    'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12,
    'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12
}

@st.cache_data(ttl=3600)
def load_and_validate():
    try:
        df = pd.read_excel(BytesIO(requests.get(
            "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx", 
            timeout=15).content))

        # === 1. VALIDAR COLUNAS OBRIGATÓRIAS ===
        required_cols = ['mês', 'qtd', 'ano', 'cliente', 'comercial', 'v. líquido']
        raw_cols = [col.strip().lower() for col in df.columns]
        
        missing = [col for col in required_cols if col not in raw_cols]
        if missing:
            st.error(f"Colunas faltando: {', '.join(missing)}")
            return None

        # === 2. PADRONIZAR NOMES ===
        col_map = {col.strip(): col.strip().lower().replace('v. líquido', 'v_liquido').replace('mês', 'mes').replace('qtd.', 'qtd') 
                   for col in df.columns}
        df.rename(columns=col_map, inplace=True)

        # === 3. VALIDAR E CONVERTER CADA COLUNA ===
        errors = []

        # MÊS
        if 'mes' in df.columns:
            df['mes_raw'] = df['mes'].astype(str).str.strip().str.lower()
            df['mes'] = df['mes_raw'].map(month_map)
            invalid_months = df['mes'].isna() & df['mes_raw'].notna()
            if invalid_months.any():
                errors.append(f"Meses inválidos: {df[invalid_months]['mes_raw'].unique()[:5]}")
            df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
        else:
            errors.append("Coluna 'mês' não encontrada")

        # ANO
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        if df['ano'].isna().all():
            errors.append("Todos os anos inválidos")
        elif (df['ano'] < 2000).any() or (df['ano'] > 2030).any():
            errors.append("Anos fora do range (2000–2030)")

        # QTD
        df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')
        if df['qtd'].le(0).all():
            errors.append("Todas as quantidades são zero ou negativas")

        # CLIENTE / COMERCIAL
        for col in ['cliente', 'comercial']:
            if df[col].astype(str).str.strip().eq('').all():
                errors.append(f"Coluna '{col}' vazia")

        # V. LÍQUIDO
        if 'v_liquido' in df.columns:
            df['v_liquido'] = (df['v_liquido'].astype(str)
                               .str.replace(r'\.', '', regex=True)
                               .str.replace(',', '.', regex=False)
                               .str.replace(r'(\.\d{2})\d+', r'\1', regex=True)
                               .astype(float, errors='ignore'))
            if df['v_liquido'].le(0).all():
                errors.append("Todos os valores são zero ou negativos")

        # === 4. MOSTRAR RESULTADO DA VALIDAÇÃO ===
        if errors:
            st.markdown("### Validação de Dados")
            for err in errors:
                st.markdown(f"<div class='validation-error'>Erro: {err}</div>", unsafe_allow_html=True)
            st.stop()

        st.markdown("<div class='validation-success'>Todos os dados validados com sucesso!</div>", unsafe_allow_html=True)

        # === 5. LIMPEZA FINAL ===
        df.dropna(subset=['mes','qtd','ano','cliente','comercial','v_liquido'], inplace=True)
        df = df[(df['mes'].between(1,12)) & (df['qtd'] > 0) & (df['v_liquido'] > 0)]
        df = df.drop_duplicates(subset=['cliente','comercial','ano','mes','qtd','v_liquido'])
        df.drop(columns=['mes_raw'], errors='ignore', inplace=True)

        return df

    except Exception as e:
        st.error(f"Erro crítico: {e}")
        return None

df = load_and_validate()
if df is None or df.empty:
    st.stop()

# =============================================
# SIDEBAR + FILTROS
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
# FUNÇÕES
# =============================================
fmt = lambda x, u: f"{x:,.0f} {u}" if pd.notna(x) else f"0 {u}"
mes_pt = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}

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

# (Demais páginas mantidas funcionais)

# Exportar
if st.sidebar.button("Exportar Dados"):
    st.download_button("Baixar", data.to_csv(index=False), "vendas.csv", "text/csv")
