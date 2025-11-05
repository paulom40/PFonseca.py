import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import requests

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Business Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="Chart"
)

# --- CORES ---
primary_color = "#6366f1"
secondary_color = "#10b981"
accent_color = "#f59e0b"

# --- ESTILO ---
st.markdown(f"""
    <style>
    .main {{ background: #ffffff; color: #1e293b; }}
    .stApp {{ background: #ffffff; }}
    h1 {{ color: {primary_color}; font-weight: 800; font-size: 2.8em; border-bottom: 3px solid {primary_color}; padding-bottom: 10px; }}
    h2 {{ color: #1e293b; font-weight: 700; font-size: 2em; margin: 30px 0 20px; }}
    [data-testid="metric-container"] {{ background: white; border: 2px solid #e2e8f0; border-radius: 15px; padding: 25px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
    [data-testid="metric-container"]:hover {{ transform: translateY(-5px); box-shadow: 0 8px 30px rgba(0,0,0,0.12); border-color: {primary_color}; }}
    [data-testid="stSidebar"] {{ background: linear-gradient(180deg, {primary_color} 0%, #4f46e5 100%); }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    .stSelectbox [data-baseweb="select"] {{ background-color: white !important; color: #1e293b !important; }}
    .stDownloadButton button {{ background: linear-gradient(135deg, {primary_color}, {secondary_color}); color: white; border: none; border-radius: 12px; padding: 12px 25px; box-shadow: 0 4px 15px rgba(99,102,241,0.3); }}
    .stDownloadButton button:hover {{ box-shadow: 0 6px 20px rgba(99,102,241,0.4); transform: translateY(-2px); }}
    [data-testid="metric-value"] {{ font-size: 2em !important; font-weight: 800 !important; }}
    [data-testid="metric-label"] {{ font-size: 1.1em !important; font-weight: 600 !important; color: {primary_color} !important; }}
    hr {{ border: 0; height: 2px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 30px 0; }}
    </style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
month_names_to_number = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
    'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6,
    'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
}

@st.cache_data(ttl=3600)
def carregar_dados():
    try:
        url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            st.error(f"Erro: Status {response.status_code}")
            return pd.DataFrame()
        df = pd.read_excel(BytesIO(response.content))

        col_mappings = {
            'Mês': 'mes', 'mes': 'mes', 'MÊS': 'mes',
            'Qtd.': 'qtd', 'Qtd': 'qtd', 'qtd': 'qtd', 'QTD': 'qtd', 'Quantidade': 'qtd',
            'Ano': 'ano', 'ano': 'ano', 'ANO': 'ano',
            'Cliente': 'cliente', 'cliente': 'cliente', 'CLIENTE': 'cliente',
            'Comercial': 'comercial', 'comercial': 'comercial', 'COMERCIAL': 'comercial',
            'V. Líquido': 'v_liquido', 'V_Liquido': 'v_liquido', 'V Liquido': 'v_liquido', 'V. LÍQUIDO': 'v_liquido',
            'PM': 'pm', 'Preço Médio': 'pm',
            'Categoria': 'categoria', 'categoria': 'categoria', 'CATEGORIA': 'categoria'
        }
        df = df.rename(columns=col_mappings)

        critical_cols = ['mes', 'qtd', 'ano', 'cliente', 'comercial']
        missing = [c for c in critical_cols if c not in df.columns]
        if missing:
            st.error(f"Colunas faltando: {missing}")
            return pd.DataFrame()

        if df['mes'].dtype == 'object':
            df['mes'] = df['mes'].apply(lambda x: month_names_to_number.get(str(x).strip().lower(), np.nan))
        df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')

        if 'v_liquido' in df.columns:
            df['v_liquido'] = df['v_liquido'].astype(str).str.strip()
            df['v_liquido'] = df['v_liquido'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')

        df = df.dropna(subset=critical_cols)
        df = df[(df['mes'] >= 1) & (df['mes'] <= 12)]
        return df
    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame()

df = carregar_dados()
if df.empty:
    st.stop()

# --- SIDEBAR ---
st.sidebar.markdown("""
    <div style="text-align: center; padding: 30px 0;">
        <div style="font-size: 2.5em;">Chart</div>
        <h1 style="color: white; margin: 0; font-size: 1.8em;">BI Dashboard</h1>
        <p style="color: #e0e7ff; font-size: 0.9em;">Análises em Tempo Real</p>
    </div>
""", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border: 1px solid rgba(255,255,255,0.3); margin: 20px 0;'>", unsafe_allow_html=True)

pagina = st.sidebar.radio("**NAVEGAÇÃO**", [
    "VISÃO GERAL",
    "KPIS PERSONALIZADOS",
    "TENDÊNCIAS",
    "ALERTAS",
    "ANÁLISE DE CLIENTES",
    "VISTA COMPARATIVA"
], key="nav")

# --- FILTROS ---
def get_opcoes(d, a, c, cl):
    temp = d.copy()
    if a != "Todos": temp = temp[temp['ano'] == int(a)]
    if c != "Todos": temp = temp[temp['comercial'].astype(str).str.strip() == str(c).strip()]
    if cl != "Todos": temp = temp[temp['cliente'].astype(str).str.strip() == str(cl).strip()]
    anos = sorted(temp['ano'].dropna().unique().astype(int).tolist())
    coms = sorted(temp['comercial'].dropna().unique().tolist())
    cls = sorted(temp['cliente'].dropna().unique().tolist())
    cats = sorted(temp['categoria'].dropna().unique().tolist()) if 'categoria' in temp.columns else []
    return anos, coms, cls, cats

def aplicar_filtros(d, a, c, cl, cat):
    res = d.copy()
    if a != "Todos": res = res[res['ano'] == int(a)]
    if c != "Todos": res = res[res['comercial'].astype(str).str.strip() == str(c).strip()]
    if cl != "Todos": res = res[res['cliente'].astype(str).str.strip() == str(cl).strip()]
    if cat != "Todas" and 'categoria' in res.columns:
        res = res[res['categoria'].astype(str).str.strip() == str(cat).strip()]
    return res

anos, _, _, _ = get_opcoes(df, "Todos", "Todos", "Todos")
ano = st.sidebar.selectbox("**ANO**", ["Todos"] + anos, key="f_ano")
_, coms, _, _ = get_opcoes(df, ano, "Todos", "Todos")
comercial = st.sidebar.selectbox("**COMERCIAL**", ["Todos"] + coms, key="f_com")
_, _, cls, _ = get_opcoes(df, ano, comercial, "Todos")
cliente = st.sidebar.selectbox("**CLIENTE**", ["Todos"] + cls, key="f_cli")
_, _, _, cats = get_opcoes(df, ano, comercial, cliente)
categoria = st.sidebar.selectbox("**CATEGORIA**", ["Todas"] + cats, key="f_cat")

dados_filtrados = aplicar_filtros(df, ano, comercial, cliente, categoria)

# --- FUNÇÕES ÚTEIS ---
def formatar_euros(v): return "€ 0" if pd.isna(v) or v == 0 else f"€ {v:,.2f}"
def formatar_kg(v): return "0 kg" if pd.isna(v) or v == 0 else f"{v:,.0f} kg" if v >= 1000 else f"{v:,.2f} kg"
month_pt = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}

def gerar_excel(d):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        d.to_excel(writer, index=False, sheet_name='Dados')
    return output.getvalue()

# --- PÁGINAS ---
if pagina == "VISÃO GERAL":
    st.markdown("<h1 style='text-align: center;'>DASHBOARD ANALÍTICO</h1>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    total_qtd = dados_filtrados['qtd'].sum()
    total_val = dados_filtrados['v_liquido'].sum() if 'v_liquido' in dados_filtrados.columns else 0
    with col1: st.metric("QUANTIDADE (KG)", formatar_kg(total_qtd))
    with col2: st.metric("VALOR TOTAL (€)", formatar_euros(total_val))
    with col3: st.metric("CLIENTES", dados_filtrados['cliente'].nunique())
    with col4: st.metric("COMERCIAIS", dados_filtrados['comercial'].nunique())

    st.markdown("---")
    st.markdown("### TOP 10 CLIENTES (KG)")
    top = dados_filtrados.groupby('cliente')['qtd'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(top.reset_index(), x='cliente', y='qtd', text='qtd', color='qtd', color_continuous_scale='Viridis')
    fig.update_traces(texttemplate='%{text:,.0f} kg', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    if st.button("Exportar"):
        st.download_button("Baixar Excel", gerar_excel(dados_filtrados), "dados.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif pagina == "KPIS PERSONALIZADOS":
    st.markdown("<h1>KPIS PERSONALIZADOS</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col1:
        tipo = st.selectbox("MÉTRICA", ["Quantidade (kg)", "Valor (€)"])
        nome = st.text_input("NOME DO KPI", f"Evolução {tipo}")
    with col2:
        periodo = st.selectbox("AGRUPAR POR", ["Mensal", "Trimestral", "Anual"])
        tendencia = st.checkbox("Mostrar Tendência")

    if dados_filtrados.empty:
        st.warning("Sem dados.")
    else:
        if periodo == "Mensal": group_col = 'mes'
        elif periodo == "Trimestral": group_col = pd.cut(dados_filtrados['mes'], bins=[0,3,6,9,12], labels=['T1','T2','T3','T4'])
        else: group_col = 'ano'

        if "kg" in tipo:
            data = dados_filtrados.groupby(group_col)['qtd'].sum().reset_index()
            y = 'qtd'; label = "kg"
        else:
            data = dados_filtrados.groupby(group_col)['v_liquido'].sum().reset_index()
            y = 'v_liquido'; label = "€"

        fig = px.line(data, x=group_col, y=y, markers=True, title=nome)
        fig.update_traces(line_color=primary_color, line_width=4)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### ESTATÍSTICAS")
        col1, col2, col3 = st.columns(3)
        col1.metric("Máximo", formatar_kg(data[y].max()) if "kg" in tipo else formatar_euros(data[y].max()))
        col2.metric("Média", formatar_kg(data[y].mean()) if "kg" in tipo else formatar_euros(data[y].mean()))
        col3.metric("Total", formatar_kg(data[y].sum()) if "kg" in tipo else formatar_euros(data[y].sum()))

elif pagina == "TENDÊNCIAS":
    st.markdown("<h1>ANÁLISE DE TENDÊNCIAS</h1>", unsafe_allow_html=True)
    metrica = st.selectbox("MÉTRICA", ["Quantidade (kg)", "Valor (€)"])
    janela = st.slider("MÉDIA MÓVEL (meses)", 1, 6, 3)

    temp = dados_filtrados.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str) + '-01')
    temp = temp.sort_values('data')

    if "kg" in metrica:
        serie = temp.groupby('data')['qtd'].sum()
        titulo = "Tendência de Quantidade"
        formato = "{:,.0f} kg"
    else:
        serie = temp.groupby('data')['v_liquido'].sum()
        titulo = "Tendência de Valor"
        formato = "€ {:,.0f}"

    ma = serie.rolling(window=janela, center=True).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=serie.index, y=serie, mode='lines+markers', name='Real', line=dict(color=primary_color)))
    fig.add_trace(go.Scatter(x=ma.index, y=ma, mode='lines', name=f'Média Móvel {janela}m', line=dict(color=accent_color, dash='dash')))
    fig.update_layout(title=titulo, xaxis_title="Data", yaxis_title=metrica, height=500)
    st.plotly_chart(fig, use_container_width=True)

elif pagina == "ALERTAS":
    st.markdown("<h1>ALERTAS AUTOMÁTICOS</h1>", unsafe_allow_html=True)
    alerta_qtd = st.checkbox("Alerta: Queda > 20% em Qtd")
    alerta_val = st.checkbox("Alerta: Queda > 15% em Valor")

    temp = dados_filtrados.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str) + '-01')
    mensal = temp.groupby(pd.Grouper(key='data', freq='M'))[['qtd', 'v_liquido']].sum()

    alertas = []
    for i in range(1, len(mensal)):
        prev_qtd = mensal['qtd'].iloc[i-1]
        curr_qtd = mensal['qtd'].iloc[i]
        prev_val = mensal['v_liquido'].iloc[i-1]
        curr_val = mensal['v_liquido'].iloc[i]

        if alerta_qtd and prev_qtd > 0 and (curr_qtd / prev_qtd) < 0.8:
            alertas.append(f"Queda de {((prev_qtd - curr_qtd)/prev_qtd*100):.1f}% em Qtd ({mensal.index[i].strftime('%b/%Y')})")
        if alerta_val and prev_val > 0 and (curr_val / prev_val) < 0.85:
            alertas.append(f"Queda de {((prev_val - curr_val)/prev_val*100):.1f}% em Valor ({mensal.index[i].strftime('%b/%Y')})")

    if alertas:
        for a in alertas: st.error(a)
    else:
        st.success("Nenhum alerta crítico detectado.")

elif pagina == "ANÁLISE DE CLIENTES":
    st.markdown("<h1>ANÁLISE DETALHADA DE CLIENTES</h1>", unsafe_allow_html=True)
    cliente_sel = st.selectbox("SELECIONE CLIENTE", ["Todos"] + sorted(dados_filtrados['cliente'].unique()))
    df_cli = dados_filtrados if cliente_sel == "Todos" else dados_filtrados[dados_filtrados['cliente'] == cliente_sel]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total KG", formatar_kg(df_cli['qtd'].sum()))
    with col2:
        st.metric("Total €", formatar_euros(df_cli['v_liquido'].sum()))

    fig = px.scatter(df_cli, x='qtd', y='v_liquido', color='comercial', size='qtd',
                     hover_data=['mes', 'ano'], title="Dispersão: Qtd vs Valor")
    st.plotly_chart(fig, use_container_width=True)

elif pagina == "VISTA COMPARATIVA":
    st.markdown("<h1>COMPARAÇÃO ENTRE PERÍODOS</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        p1 = st.selectbox("PERÍODO 1", options=sorted(dados_filtrados['ano'].unique()), index=0)
    with col2:
        p2 = st.selectbox("PERÍODO 2", options=sorted(dados_filtrados['ano'].unique()), index=1)

    d1 = dados_filtrados[dados_filtrados['ano'] == p1]
    d2 = dados_filtrados[dados_filtrados['ano'] == p2]

    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"Qtd {p1}", formatar_kg(d1['qtd'].sum()))
        st.metric(f"Valor {p1}", formatar_euros(d1['v_liquido'].sum()))
    with col2:
        st.metric(f"Qtd {p2}", formatar_kg(d2['qtd'].sum()))
        st.metric(f"Valor {p2}", formatar_euros(d2['v_liquido'].sum()))

    comparacao = pd.DataFrame({
        'Período': [p1, p2],
        'Quantidade': [d1['qtd'].sum(), d2['qtd'].sum()],
        'Valor': [d1['v_liquido'].sum(), d2['v_liquido'].sum()]
    })
    fig = px.bar(comparacao, x='Período', y=['Quantidade', 'Valor'], barmode='group', title="Comparação Side-by-Side")
    st.plotly_chart(fig, use_container_width=True)
