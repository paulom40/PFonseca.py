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

        # === 1. COLUNAS REAIS ===
        raw_cols = [col.strip().lower() for col in df.columns]

        # === 2. MAPEAR VARIAÇÕES ===
        col_variants = {
            'mes': ['mês', 'mes', 'mês', 'month'],
            'qtd': ['qtd.', 'qtd', 'quantidade', 'qtd.', 'qty'],
            'ano': ['ano', 'year'],
            'cliente': ['cliente', 'client'],
            'comercial': ['comercial', 'vendedor', 'sales'],
            'v_liquido': ['v. líquido', 'v_liquido', 'valor', 'v. liquido', 'valor líquido']
        }

        col_map = {}
        missing = []
        for std_name, variants in col_variants.items():
            found = None
            for var in variants:
                if var in raw_cols:
                    found = var
                    break
            if found:
                col_map[found] = std_name
            else:
                missing.append(std_name)

        if missing:
            st.error(f"Colunas faltando: {', '.join(missing)}")
            return None

        # === 3. RENOMEAR ===
        df.rename(columns=col_map, inplace=True)

        # === 4. VALIDAÇÃO E CONVERSÃO ===
        # Mês
        df['mes'] = df['mes'].astype(str).str.strip().str.lower().map(month_map, na_action='ignore')
        df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
        if df['mes'].isna().all():
            st.error("Nenhum mês válido.")
            return None

        # Qtd
        df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')
        if df['qtd'].le(0).all():
            st.error("Quantidades inválidas (≤ 0).")
            return None

        # Ano
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        if df['ano'].isna().all() or not df['ano'].between(2000, 2030).any():
            st.error("Anos inválidos.")
            return None

        # Cliente / Comercial
        for col in ['cliente', 'comercial']:
            df[col] = df[col].astype(str).str.strip()
            if df[col].eq('').all():
                st.error(f"Coluna '{col}' vazia.")
                return None

        # Valor Líquido
        if 'v_liquido' in df.columns:
            df['v_liquido'] = (df['v_liquido'].astype(str)
                               .str.replace(r'\.', '', regex=True)
                               .str.replace(',', '.', regex=False)
                               .str.replace(r'(\.\d{2})\d+', r'\1', regex=True)
                               .astype(float, errors='ignore'))
            if df['v_liquido'].le(0).all():
                st.error("Valores ≤ 0.")
                return None

        # === 5. LIMPEZA FINAL ===
        df.dropna(subset=['mes','qtd','ano','cliente','comercial','v_liquido'], inplace=True)
        df = df[(df['mes'].between(1,12)) & (df['qtd'] > 0) & (df['v_liquido'] > 0)]
        df = df.drop_duplicates(subset=['cliente','comercial','ano','mes','qtd','v_liquido'])

        st.markdown("<div class='validation-success'>Dados validados com sucesso!</div>", unsafe_allow_html=True)
        return df

    except Exception as e:
        st.error(f"Erro: {e}")
        return None

df = load_and_validate()
if df is None or df.empty:
    st.stop()

# =============================================
# SIDEBAR + FILTROS
# =============================================
with st.sidebar:
    st.markdown("<h2 style='color:white'>BI Pro</h2>", unsafe_allow_html=True)
    page = st.radio("Navegação", [
        "Visão Geral", "KPIs", "Tendências", "Alertas", "Clientes", "Comparação"
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
fmt = lambda x, u: f"{x:,.0f} {u}" if pd.notna(x) and x > 0 else f"0 {u}"
mes_pt = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}

def export_excel(df_hist, df_pred=None):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_hist.to_excel(writer, sheet_name='Histórico', index=False)
        if df_pred is not None:
            df_pred.to_excel(writer, sheet_name='Previsão', index=False)
    return output.getvalue()

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
    st.markdown("<h1>KPIs Personalizados</h1>", unsafe_allow_html=True)
    metrica = st.selectbox("Métrica", ["Quantidade", "Valor"])
    grupo = st.selectbox("Agrupar por", ["Mês", "Ano"])
    col = 'qtd' if metrica == "Quantidade" else 'v_liquido'
    gcol = 'mes' if grupo == "Mês" else 'ano'
    serie = data.groupby(gcol)[col].sum()
    if serie.empty:
        st.info("Sem dados.")
    else:
        df_plot = serie.reset_index()
        fig = px.line(df_plot, x=gcol, y=col, markers=True, title=f"{metrica} por {grupo}")
        if grupo == "Mês":
            fig.update_xaxes(tickvals=df_plot[gcol], ticktext=[mes_pt.get(m, m) for m in df_plot[gcol]])
        st.plotly_chart(fig, use_container_width=True)

elif page == "Tendências":
    st.markdown("<h1>Tendências & Previsão</h1>", unsafe_allow_html=True)
    metrica = st.selectbox("Métrica", ["Quantidade", "Valor"])
    meses = st.slider("Prever (meses)", 1, 12, 6)
    temp = data.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    serie = temp.groupby('data')[['qtd','v_liquido']].sum()
    col = 'qtd' if metrica == "Quantidade" else 'v_liquido'
    s = serie[col].asfreq('MS').ffill()
    if len(s) < 12:
        st.warning("Dados insuficientes.")
    else:
        try:
            import pmdarima as pm
            model = pm.auto_arima(s, seasonal=True, m=12, stepwise=True, suppress_warnings=True)
            pred = model.predict(n_periods=meses, return_conf_int=True)
            forecast, conf = pred[0], pred[1]
            future = pd.date_range(s.index[-1] + pd.DateOffset(months=1), periods=meses, freq='MS')
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=s.index, y=s, mode='lines+markers', name='Real'))
            fig.add_trace(go.Scatter(x=future, y=forecast, mode='lines+markers', name='Previsão'))
            fig.add_trace(go.Scatter(x=list(future)+list(future)[::-1],
                                   y=list(conf[:,1])+list(conf[:,0])[::-1],
                                   fill='toself', fillcolor='rgba(16,185,129,0.2)', name='95%'))
            st.plotly_chart(fig, use_container_width=True)
            hist = pd.DataFrame({'Data': s.index.strftime('%b/%Y'), 'Real': s.values})
            prev = pd.DataFrame({'Mês': future.strftime('%b/%Y'), 'Previsão': forecast.round(2)})
            st.download_button("Exportar Previsão", export_excel(hist, prev), "previsao.xlsx")
        except: st.error("Previsão indisponível.")

elif page == "Alertas":
    st.markdown("<h1>Alertas</h1>", unsafe_allow_html=True)
    temp = data.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    mensal = temp.groupby(pd.Grouper(key='data', freq='M'))[['qtd','v_liquido']].sum()
    alertas = []
    for i in range(1, len(mensal)):
        if mensal['qtd'].iloc[i-1] > 0 and mensal['qtd'].iloc[i] / mensal['qtd'].iloc[i-1] < 0.8:
            alertas.append(f"Queda >20% Qtd: {mensal.index[i].strftime('%b/%Y')}")
        if 'v_liquido' in mensal.columns and mensal['v_liquido'].iloc[i-1] > 0 and mensal['v_liquido'].iloc[i] / mensal['v_liquido'].iloc[i-1] < 0.85:
            alertas.append(f"Queda >15% Valor: {mensal.index[i].strftime('%b/%Y')}")
    for a in alertas: st.error(a)
    if not alertas: st.success("Sem alertas.")

elif page == "Clientes":
    st.markdown("<h1>Clientes</h1>", unsafe_allow_html=True)
    cli = st.selectbox("Cliente", ["Todos"] + sorted(data['cliente'].unique()))
    dfc = data if cli == "Todos" else data[data['cliente'] == cli]
    st.metric("Qtd", fmt(dfc['qtd'].sum(), "kg"))
    st.metric("Valor", fmt(dfc['v_liquido'].sum(), "EUR"))
    fig = px.scatter(dfc, x='qtd', y='v_liquido', color='comercial', size='qtd')
    st.plotly_chart(fig, use_container_width=True)

elif page == "Comparação":
    st.markdown("<h1>Comparação</h1>", unsafe_allow_html=True)
    anos = sorted(data['ano'].unique())
    if len(anos) < 2: st.info("Apenas um ano.")
    else:
        p1, p2 = st.columns(2)
        with p1: a1 = st.selectbox("Ano 1", anos)
        with p2: a2 = st.selectbox("Ano 2", anos, index=1)
        d1, d2 = data[data['ano']==a1], data[data['ano']==a2]
        c1, c2 = st.columns(2)
        with c1:
            st.metric(f"Qtd {a1}", fmt(d1['qtd'].sum(), "kg"))
            st.metric(f"Valor {a1}", fmt(d1['v_liquido'].sum(), "EUR"))
        with c2:
            st.metric(f"Qtd {a2}", fmt(d2['qtd'].sum(), "kg"))
            st.metric(f"Valor {a2}", fmt(d2['v_liquido'].sum(), "EUR"))

# Exportar
if st.sidebar.button("Exportar Dados"):
    st.download_button("Baixar", data.to_csv(index=False), "vendas.csv", "text/csv")
