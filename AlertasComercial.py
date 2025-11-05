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
# CONFIGURAÇÃO
# =============================================
st.set_page_config(
    page_title="BI Pro - Dashboard Empresarial",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="Chart"
)

# =============================================
# ESTILO PROFISSIONAL
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
# CARREGAR DADOS
# =============================================
month_names = {
    'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,
    'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12,
    'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
    'july':7,'august':8,'september':9,'october':10,'november':11,'december':12
}

@st.cache_data(ttl=3600)
def carregar_dados():
    try:
        url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx"
        df = pd.read_excel(BytesIO(requests.get(url, timeout=15).content))
        df.columns = df.columns.str.strip().str.lower()
        col_map = {
            'mês':'mes','qtd.':'qtd','qtd':'qtd','quantidade':'qtd',
            'ano':'ano','cliente':'cliente','comercial':'comercial',
            'v. líquido':'v_liquido','v_liquido':'v_liquido','categoria':'categoria'
        }
        df.rename(columns=col_map, inplace=True)

        if 'v_liquido' in df.columns:
            df['v_liquido'] = df['v_liquido'].astype(str).str.strip()
            df['v_liquido'] = df['v_liquido'].str.replace(r'\.', '', regex=True)
            df['v_liquido'] = df['v_liquido'].str.replace(',', '.', regex=False)
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')

        if 'mes' in df.columns:
            df['mes'] = df['mes'].apply(lambda x: month_names.get(str(x).strip().lower(), np.nan))
            df['mes'] = pd.to_numeric(df['mes'], errors='coerce')

        for col in ['ano', 'qtd']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        required = ['mes','qtd','ano','cliente','comercial']
        if not all(c in df.columns for c in required):
            st.error("Colunas faltando.")
            return pd.DataFrame()

        df.dropna(subset=required, inplace=True)
        df = df[(df['mes'] >= 1) & (df['mes'] <= 12)]
        return df
    except Exception as e:
        st.error(f"Erro: {e}")
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
        anos = sorted(t['ano'].dropna().unique().astype(int).tolist())
        coms = sorted(t['comercial'].dropna().unique().tolist())
        cls = sorted(t['cliente'].dropna().unique().tolist())
        cats = sorted(t.get('categoria', pd.Series()).dropna().unique().tolist())
        return anos, coms, cls, cats

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
    if categoria != "Todas" and 'categoria' in dados.columns:
        dados = dados[dados['categoria'].astype(str).str.strip() == str(categoria).strip()]

# =============================================
# FUNÇÕES
# =============================================
def fmt_euro(v): return "€ 0" if pd.isna(v) or v == 0 else f"€ {v:,.0f}"
def fmt_kg(v): return "0 kg" if pd.isna(v) or v == 0 else f"{v:,.0f} kg"
mes_pt = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}

def exportar_dados(d):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        d.to_excel(writer, index=False, sheet_name='Vendas')
    return output.getvalue()

# =============================================
# PÁGINAS FUNCIONAIS
# =============================================
if pagina == "VISÃO GERAL":
    st.markdown("<h1>Visão Geral</h1>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("QUANTIDADE", fmt_kg(dados['qtd'].sum()))
    with c2: st.metric("VALOR TOTAL", fmt_euro(dados['v_liquido'].sum() if 'v_liquido' in dados.columns else 0))
    with c3: st.metric("CLIENTES", dados['cliente'].nunique())
    with c4: st.metric("COMERCIAIS", dados['comercial'].nunique())

elif pagina == "KPIS PERSONALIZADOS":
    st.markdown("<h1>KPIs Personalizados</h1>", unsafe_allow_html=True)
    tipo = st.selectbox("Métrica", ["Quantidade (kg)", "Valor (€)"])
    nome = st.text_input("Nome", f"Evolução {tipo}")
    agrupar = st.selectbox("Agrupar por", ["Mês", "Trimestre", "Ano"])

    if agrupar == "Trimestre":
        dados['grupo'] = ((dados['mes'] - 1) // 3) + 1
        group_col = 'grupo'
    elif agrupar == "Ano":
        group_col = 'ano'
    else:
        group_col = 'mes'

    if "kg" in tipo:
        serie = dados.groupby(group_col)['qtd'].sum()
        y_col = 'qtd'
    else:
        serie = dados.groupby(group_col)['v_liquido'].sum() if 'v_liquido' in dados.columns else pd.Series()
        y_col = 'v_liquido'

    if serie.empty:
        st.warning("Sem dados.")
    else:
        df_plot = serie.reset_index()
        df_plot.columns = [group_col, y_col]
        fig = px.line(df_plot, x=group_col, y=y_col, title=nome, markers=True)
        if agrupar == "Mês":
            fig.update_xaxes(tickvals=df_plot[group_col], ticktext=[mes_pt.get(int(m), m) for m in df_plot[group_col]])
        st.plotly_chart(fig, use_container_width=True)

elif pagina == "TENDÊNCIAS":
    st.markdown("<h1>Tendências & Previsão</h1>", unsafe_allow_html=True)
    metrica = st.selectbox("Métrica", ["Quantidade (kg)", "Valor (€)"])
    horizonte = st.slider("Prever (meses)", 1, 12, 6)

    temp = dados.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    temp = temp.sort_values('data')

    if "kg" in metrica:
        serie = temp.groupby('data')['qtd'].sum()
        fmt_func = fmt_kg
    else:
        serie = temp.groupby('data')['v_liquido'].sum() if 'v_liquido' in temp.columns else pd.Series()
        fmt_func = fmt_euro

    if len(serie) < 12:
        st.warning("Dados insuficientes.")
    else:
        try:
            import pmdarima as pm
            serie_full = serie.asfreq('MS').ffill().fillna(0)
            model = pm.auto_arima(serie_full, seasonal=True, m=12, stepwise=True, suppress_warnings=True)
            forecast_result = model.predict(n_periods=horizonte, return_conf_int=True)
            forecast, conf_int = forecast_result[0], forecast_result[1]
            last_date = serie_full.index[-1]
            future_dates = pd.date_range(last_date + pd.DateOffset(months=1), periods=horizonte, freq='MS')

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=serie_full.index, y=serie_full, mode='lines+markers', name='Real'))
            fig.add_trace(go.Scatter(x=future_dates, y=forecast, mode='lines+markers', name='Previsão'))
            fig.add_trace(go.Scatter(x=list(future_dates)+list(future_dates)[::-1],
                                   y=list(conf_int[:,1])+list(conf_int[:,0])[::-1],
                                   fill='toself', fillcolor='rgba(16,185,129,0.2)', line=dict(color='rgba(0,0,0,0)'), name='95%'))
            st.plotly_chart(fig, use_container_width=True)

            def exportar_previsao():
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    pd.DataFrame({'Data': serie_full.index.strftime('%b/%Y'), 'Real': serie_full.values}).to_excel(writer, sheet_name='Histórico', index=False)
                    pd.DataFrame({'Mês': future_dates.strftime('%b/%Y'), 'Previsão': forecast}).to_excel(writer, sheet_name='Previsão', index=False)
                return output.getvalue()
            st.download_button("EXPORTAR PREVISÃO", exportar_previsao(), "previsao.xlsx")

        except Exception as e:
            st.error(f"Previsão falhou: {e}")

elif pagina == "ALERTAS":
    st.markdown("<h1>Alertas Automáticos</h1>", unsafe_allow_html=True)
    temp = dados.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    mensal = temp.groupby(pd.Grouper(key='data', freq='M'))[['qtd', 'v_liquido']].sum().reset_index()
    mensal = mensal.sort_values('data')

    alertas = []
    for i in range(1, len(mensal)):
        prev_qtd = mensal['qtd'].iloc[i-1]
        curr_qtd = mensal['qtd'].iloc[i]
        if prev_qtd > 0 and (curr_qtd / prev_qtd) < 0.8:
            alertas.append(f"Queda >20% em Qtd: {mensal['data'].iloc[i].strftime('%b/%Y')}")
        if 'v_liquido' in mensal.columns:
            prev_val = mensal['v_liquido'].iloc[i-1]
            curr_val = mensal['v_liquido'].iloc[i]
            if prev_val > 0 and (curr_val / prev_val) < 0.85:
                alertas.append(f"Queda >15% em Valor: {mensal['data'].iloc[i].strftime('%b/%Y')}")

    if alertas:
        for a in alertas: st.error(a)
    else:
        st.success("Nenhum alerta crítico.")

elif pagina == "CLIENTES":
    st.markdown("<h1>Análise de Clientes</h1>", unsafe_allow_html=True)
    cli = st.selectbox("Cliente", ["Todos"] + sorted(dados['cliente'].unique()))
    df_cli = dados if cli == "Todos" else dados[dados['cliente'] == cli]

    col1, col2 = st.columns(2)
    with col1: st.metric("Qtd Total", fmt_kg(df_cli['qtd'].sum()))
    with col2: st.metric("Valor Total", fmt_euro(df_cli['v_liquido'].sum() if 'v_liquido' in df_cli.columns else 0))

    fig = px.scatter(df_cli, x='qtd', y='v_liquido' if 'v_liquido' in df_cli.columns else None,
                     color='comercial', size='qtd', hover_data=['mes','ano'], title="Dispersão")
    st.plotly_chart(fig, use_container_width=True)

elif pagina == "COMPARAÇÃO":
    st.markdown("<h1>Comparação de Períodos</h1>", unsafe_allow_html=True)
    anos_disp = sorted(dados['ano'].unique())
    if len(anos_disp) < 2:
        st.warning("Dados de apenas um ano.")
    else:
        col1, col2 = st.columns(2)
        with col1: p1 = st.selectbox("Período 1", anos_disp, index=0)
        with col2: p2 = st.selectbox("Período 2", anos_disp, index=1)

        d1 = dados[dados['ano'] == p1]
        d2 = dados[dados['ano'] == p2]

        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"Qtd {p1}", fmt_kg(d1['qtd'].sum()))
            st.metric(f"Valor {p1}", fmt_euro(d1['v_liquido'].sum() if 'v_liquido' in d1.columns else 0))
        with col2:
            st.metric(f"Qtd {p2}", fmt_kg(d2['qtd'].sum()))
            st.metric(f"Valor {p2}", fmt_euro(d2['v_liquido'].sum() if 'v_liquido' in d2.columns else 0))

# Exportar
if st.sidebar.button("EXPORTAR DADOS"):
    st.download_button("BAIXAR", exportar_dados(dados), "vendas.xlsx")
