import pandas as pd
import streamlit as st
import plotly.express as px
import io
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ====================== CONFIGURAÇÃO DA PÁGINA ======================
st.set_page_config(
    page_title="Dashboard Compras - Análise Premium",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="chart_with_upwards_trend"
)

# ====================== CSS PREMIUM ======================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    .stMetric {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .stMetric:hover { transform: translateY(-5px); }
    [data-testid="stSidebar"] { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); }
    .sidebar-section {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ====================== HEADER ======================
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size:2.8rem;">DASHBOARD DE COMPRAS</h1>
    <p style="margin:5px 0 0 0; opacity:0.9;">Análise Avançada • KPIs em Tempo Real • Insights Estratégicos</p>
</div>
""", unsafe_allow_html=True)

# ====================== CARREGAR DADOS ======================
@st.cache_data(show_spinner="Carregando dados...")
def load_data():
    try:
        df = pd.read_excel("ResumoTR.xlsx")

        # Renomear colunas se necessário
        mapa = {'entidade':'Entidade', 'nome':'Nome', 'artigo':'Artigo', 'quantidade':'Quantidade',
                'v líquido':'V Líquido', 'v liquido':'V Líquido', 'pm':'PM', 'data':'Data',
                'comercial':'Comercial', 'mês':'Mês', 'ano':'Ano'}
        df = df.rename(columns=lambda c: next((v for k,v in mapa.items() if k in c.lower()), c))

        essenciais = ['Nome', 'Artigo', 'Quantidade', 'V Líquido', 'Data', 'Comercial']
        for col in essenciais:
            if col not in df.columns:
                st.error(f"Coluna essencial não encontrada: {col}")
                st.stop()

        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df = df.dropna(subset=['Data'])
        df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce').fillna(0)
        df['V Líquido'] = pd.to_numeric(df['V Líquido'], errors='coerce').fillna(0)

        df = df[(df['Quantidade'] > 0) & (df['V Líquido'] > 0)].copy()

        df['Ano'] = df['Data'].dt.year
        df['Mes_Numero'] = df['Data'].dt.month
        df['Mês'] = df['Data'].dt.strftime('%B')
        df['AnoMes'] = df['Data'].dt.strftime('%Y-%m')
        df['Trimestre'] = df['Data'].dt.quarter

        return df.sort_values('Data').reset_index(drop=True)
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# ====================== SIDEBAR - FILTROS ======================
st.sidebar.markdown("""
<div style="text-align:center;padding:1rem;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;color:white;margin-bottom:1rem;">
    <h3 style="margin:0;">FILTROS DINÂMICOS</h3>
</div>
""", unsafe_allow_html=True)

df_temp = df.copy()

def secao(titulo):
    st.sidebar.markdown(f"""
    <div class="sidebar-section">
        <h4 style="margin:0 0 10px 0;color:#2c3e50;border-bottom:2px solid #667eea;padding-bottom:5px;">{titulo}</h4>
    </div>
    """, unsafe_allow_html=True)

# Ano
secao("ANO")
anos = sorted(df['Ano'].unique(), reverse=True)
todos_anos = st.sidebar.checkbox("Todos os anos", value=True, key="a1")
anos_sel = anos if todos_anos else st.sidebar.multiselect("Anos", anos, default=anos[:2], key="a2")
if anos_sel: df_temp = df_temp[df_temp['Ano'].isin(anos_sel)]

# Mês
secao("MÊS")
if df_temp.empty:
    st.sidebar.info("Selecione pelo menos um ano")
else:
    meses_num = sorted(df_temp['Mes_Numero'].unique())
    meses_nomes = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    opcoes = [meses_nomes[i-1] for i in meses_num]
    todos_meses = st.sidebar.checkbox("Todos os meses", value=True, key="m1")
    meses_sel_nome = opcoes if todos_meses else st.sidebar.multiselect("Mês", opcoes, default=opcoes[-3:], key="m2")
    meses_sel = [meses_nomes.index(m)+1 for m in meses_sel_nome]
    if meses_sel: df_temp = df_temp[df_temp['Mes_Numero'].isin(meses_sel)]

# Comercial
secao("COMERCIAL")
if not df_temp.empty:
    coms = sorted(df_temp['Comercial'].dropna().unique())
    todos_com = st.sidebar.checkbox("Todos comerciais", value=True, key="c1")
    com_sel = coms if todos_com else st.sidebar.multiselect("Comercial", coms, default=coms[:3], key="c2")
    if com_sel: df_temp = df_temp[df_temp[df_temp['Comercial'].isin(com_sel)]

# Cliente
secao("CLIENTE")
if not df_temp.empty:
    cli = sorted(df_temp['Nome'].dropna().unique())
    todos_cli = st.sidebar.checkbox("Todos clientes", value=len(cli)<=30, key="cl1")
    cli_sel = cli if todos_cli else st.sidebar.multiselect("Cliente", cli, default=cli[:5], key="cl2")
    if cli_sel: df_temp = df_temp[df_temp['Nome'].isin(cli_sel)]

# Produto
secao("PRODUTO")
if not df_temp.empty:
    prod = sorted(df_temp['Artigo'].dropna().unique())
    todos_prod = st.sidebar.checkbox("Todos produtos", value=True, key="p1")
    prod_sel = prod if todos_prod else st.sidebar.multiselect("Produto", prod, default=prod[:10], key="p2")
    if prod_sel: df_temp = df_temp[df_temp['Artigo'].isin(prod_sel)]

# Botões
st.sidebar.markdown("---")
c1, c2 = st.sidebar.columns(2)
if c1.button("APLICAR FILTROS", type="primary", use_container_width=True):
    st.session_state.df_filtrado = df_temp.copy()
    st.success("Filtros aplicados!")
if c2.button("LIMPAR", use_container_width=True):
    for k in list(st.session_state.keys()):
        if k.startswith(("a", "m", "c", "cl", "p")):
            del st.session_state[k]
    st.session_state.df_filtrado = df.copy()
    st.rerun()

df_filtrado = st.session_state.get("df_filtrado", df.copy())

st.sidebar.markdown("**Resumo**")
st.sidebar.write(f"Registros: **{len(df_filtrado):,}**")
st.sidebar.write(f"Período: {df_filtrado['Data'].min().strftime('%d/%m/%Y')} → {df_filtrado['Data'].max().strftime('%d/%m/%Y')}")

# ====================== KPIs ======================
def kpis(d):
    if d.empty: return {}
    total = d["V Líquido"].sum()
    qtd = d["Quantidade"].sum()
    return {
        "total_vendas": total,
        "qtd_total": qtd,
        "clientes": d["Nome"].nunique(),
        "produtos": d["Artigo"].nunique(),
        "trans": len(d),
        "ticket": total/len(d) if len(d)>0 else 0,
        "venda_dia": total / d["Data"].dt.date.nunique() if d["Data"].dt.date.nunique()>0 else 0,
        "valor_kg": total/qtd if qtd>0 else 0,
        "periodo": f"{d['Data'].min().strftime('%d/%m/%Y')} a {d['Data'].max().strftime('%d/%m/%Y')}"
    }

kpi = kpis(df_filtrado)

# ====================== TABS ======================
t1, t2, t3, t4 = st.tabs(["KPIs", "Temporal", "Top 10", "Dados"])

with t1:
    st.subheader("Principais KPIs")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Vendas", f"€{kpi['total_vendas']:,.0f}")
    c2.metric("Quantidade", f"{kpi['qtd_total']:,.0f}")
    c3.metric("Clientes", kpi['clientes'])
    c4.metric("Produtos", kpi['produtos'])
    c5.metric("Transações", f"{kpi['trans']:,}")
    st.info(f"**Período:** {kpi['periodo']}")

with t2:
    mensal = df_filtrado.groupby('AnoMes')['V Líquido'].sum().reset_index()
    fig = px.bar(mensal, x='AnoMes', y='V Líquido', title="Vendas Mensais (€)",
                 color_discrete_sequence=['#667eea'])
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

with t3:
    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Clientes")
        topc = df_filtrado.groupby('Nome')['V Líquido'].sum().nlargest(10)
        figc = px.bar(x=topc.values, y=topc.index, orientation='h', color=topc.values,
                      color_continuous_scale='Viridis')
        st.plotly_chart(figc, use_container_width=True)
    with col2:
        st.subheader("Top 10 Produtos")
        topp = df_filtrado.groupby('Artigo')['V Líquido'].sum().nlargest(10)
        figp = px.bar(x=topp.values, y=topp.index, orientation='h', color=topp.values,
                      color_continuous_scale='Plasma')
        st.plotly_chart(figp, use_container_width=True)

with t4:
    st.subheader("Tabela de Dados")
    ord = st.selectbox("Ordenar por", ['Data','V Líquido','Nome','Artigo'])
    asc = st.checkbox("Crescente", False)
    lim = st.slider("Linhas", 10, 1000, 100, 50)
    tab = df_filtrado[['Data','Nome','Artigo','Quantidade','V Líquido','PM','Comercial','Mês','Ano']] \
          .sort_values(ord, ascending=asc).head(lim)
    st.dataframe(tab.style.format({'V Líquido':'€{:,.2f}','PM':'€{:,.2f}'}), use_container_width=True, height=600)

    st.subheader("Exportar")
    c1,c2 = st.columns(2)
    csv_bytes = df_filtrado.to_csv(index=False).encode()
    c1.download_button("CSV Completo", data=csv_bytes, file_name="vendas_filtradas.csv", mime="text/csv")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl'):
        df_filtrado.to_excel(buffer, sheet_name='Dados', index=False)
        pd.DataFrame([kpi]).to_excel(buffer, sheet_name='KPIs', index=False)
    c2.download_button("Excel + KPIs", data=buffer.getvalue(),
                       file_name="relatorio_compras.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown(f"<small>Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</small>", unsafe_allow_html=True)
