# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from unidecode import unidecode

# Configuração da página
st.set_page_config(page_title="Dashboard Vendas", layout="wide", page_icon="📊")

# CSS personalizado moderno
st.markdown("""
<style>
    /* Estilos gerais */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Cards de métricas */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: none;
    }
    
    .metric-card-success {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-warning {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-danger {
        background: linear-gradient(135deg, #ff5858 0%, #f09819 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Botões modernos */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .download-btn {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%) !important;
    }
    
    /* Alertas */
    .alert-box {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        border-left: 5px solid #ff0000;
    }
    
    .success-box {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        border-left: 5px solid #00ff00;
    }
    
    /* Filtros */
    .filter-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Títulos das seções */
    .section-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1.5rem 0 1rem 0;
        font-weight: 600;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Container principal */
    .main-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.5rem;">📊 DASHBOARD VENDAS GLOBAIS</h1>
    <p style="margin:0; opacity: 0.9; font-size: 1.1rem;">Análise Comparativa de Vendas - VGlob2425</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 1. LOAD FROM GITHUB
# -------------------------------------------------
@st.cache_data(ttl=3600)
def load():
    url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/VGlob2425.xlsx"
    try:
        df = pd.read_excel(url, sheet_name="Sheet1")
        st.success("✅ Dados carregados com sucesso do GitHub")
    except Exception as e:
        st.error(f"❌ Erro ao carregar Excel: {e}")
        st.stop()

    # Verificar número de colunas
    if df.shape[1] < 11:
        st.error(f"⚠️ Arquivo tem apenas {df.shape[1]} colunas. Esperado: 11.")
        st.stop()

    # Renomear apenas as primeiras 11 colunas
    cols = ["Código","Cliente","Qtd.","UN","PM","V. Líquido",
            "Artigo","Comercial","Categoria","Mês","Ano"]
    df = df.iloc[:, :11].copy()
    df.columns = cols

    df = df.dropna(subset=["Cliente","Comercial","Artigo","Mês","Ano"])

    # Normalizar mês
    df["Mês"] = df["Mês"].astype(str).str.strip().str.lower().apply(unidecode)\
                .str.replace(r"[^a-z]","",regex=True)
    meses = {m:i for i,m in enumerate("janeiro fevereiro marco abril maio junho julho agosto setembro outubro novembro dezembro".split(),1)}
    df["Mês_Num"] = df["Mês"].map(meses)

    if df["Mês_Num"].isna().any():
        bad = df[df["Mês_Num"].isna()]["Mês"].unique()
        st.error(f"❌ Meses inválidos: {', '.join(sorted(bad))}")
        st.stop()

    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")
    if df["Ano"].isna().any():
        st.error("❌ Ano inválido encontrado.")
        st.stop()
    df["Ano"] = df["Ano"].astype(int)
    df = df[df["Ano"].between(2000, 2100)]

    # Data correta: year, month, day
    df["Data"] = pd.to_datetime(df[["Ano", "Mês_Num"]].assign(day=1)[["Ano", "Mês_Num", "day"]])

    df["V. Líquido"] = pd.to_numeric(df["V. Líquido"], errors="coerce").fillna(0)
    
    st.success(f"📊 {len(df)} registros processados com sucesso")
    return df

df = load()

# Container principal
with st.container():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<div class="section-title">🔍 FILTROS DE ANÁLISE</div>', unsafe_allow_html=True)
    
    with col2:
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

# -------------------------------------------------
# 2. FILTROS
# -------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ FILTROS</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="filter-section">📅 Filtros Temporais</div>', unsafe_allow_html=True)
    anos = sorted(df["Ano"].unique())
    ano_sel = st.multiselect("**Selecione o Ano:**", anos, default=anos[-2:] if len(anos)>=2 else anos)
    
    if ano_sel:
        df = df[df["Ano"].isin(ano_sel)]
        mes_sel = st.multiselect("**Selecione o Mês:**", sorted(df["Mês"].str.capitalize().unique()), default=[])
        if mes_sel: 
            df = df[df["Mês"].str.capitalize().isin(mes_sel)]
    
    st.markdown('<div class="filter-section">👥 Filtros de Pessoas</div>', unsafe_allow_html=True)
    com_sel = st.multiselect("**Selecione o Comercial:**", sorted(df["Comercial"].unique()), default=[])
    if com_sel: 
        df = df[df["Comercial"].isin(com_sel)]
    
    cli_sel = st.multiselect("**Selecione o Cliente:**", sorted(df["Cliente"].unique()), default=[])
    if cli_sel: 
        df = df[df["Cliente"].isin(cli_sel)]
    
    # Estatísticas rápidas na sidebar
    st.markdown("---")
    st.markdown("### 📈 Estatísticas Rápidas")
    if len(df) > 0:
        total_vendas = df["V. Líquido"].sum()
        total_clientes = df["Cliente"].nunique()
        total_comerciais = df["Comercial"].nunique()
        
        st.metric("💰 Vendas Filtradas", f"€{total_vendas:,.0f}")
        st.metric("👥 Clientes", total_clientes)
        st.metric("👨‍💼 Comerciais", total_comerciais)

# -------------------------------------------------
# 3. COMPARATIVO
# -------------------------------------------------
cur = df["Ano"].max()
df_cur = df[df["Ano"]==cur]
df_prev = df[df["Ano"]==cur-1] if cur-1 in df["Ano"].values else pd.DataFrame()

v_cur, v_prev = df_cur["V. Líquido"].sum(), df_prev["V. Líquido"].sum()
c_cur, c_prev = df_cur["Cliente"].nunique(), df_prev["Cliente"].nunique()

# -------------------------------------------------
# 4. KPIs
# -------------------------------------------------
st.markdown('<div class="section-title">📊 MÉTRICAS PRINCIPAIS</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_vendas = f"{(v_cur-v_prev)/v_prev*100:+.1f}%" if v_prev and v_prev > 0 else None
    st.markdown(f"""
    <div class="metric-card-success">
        <h3 style="margin:0; font-size: 0.9rem;">💰 Total Vendas</h3>
        <p style="margin:0; font-size: 1.5rem; font-weight: bold;">€{v_cur:,.0f}</p>
        <p style="margin:0; font-size: 0.8rem;">{delta_vendas if delta_vendas else 'Sem comparação'}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    delta_clientes = f"{(c_cur-c_prev)/c_prev*100:+.1f}%" if c_prev and c_prev > 0 else None
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin:0; font-size: 0.9rem;">👥 Clientes Ativos</h3>
        <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{c_cur}</p>
        <p style="margin:0; font-size: 0.8rem;">{delta_clientes if delta_clientes else 'Sem comparação'}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    artigos_unicos = df_cur["Artigo"].nunique()
    st.markdown(f"""
    <div class="metric-card-warning">
        <h3 style="margin:0; font-size: 0.9rem;">📦 Artigos Vendidos</h3>
        <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{artigos_unicos}</p>
        <p style="margin:0; font-size: 0.8rem;">Tipos diferentes</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    ticket_medio = v_cur/c_cur if c_cur > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin:0; font-size: 0.9rem;">🎯 Ticket Médio</h3>
        <p style="margin:0; font-size: 1.5rem; font-weight: bold;">€{ticket_medio:,.0f}</p>
        <p style="margin:0; font-size: 0.8rem;">Por cliente</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# 5. GRÁFICO
# -------------------------------------------------
st.markdown(f'<div class="section-title">📈 EVOLUÇÃO DE VENDAS - {cur} vs {cur-1}</div>', unsafe_allow_html=True)

meses = "Janeiro Fevereiro Março Abril Maio Junho Julho Agosto Setembro Outubro Novembro Dezembro".split()
fig = go.Figure()

# Adicionar traço do ano atual
if not df_cur.empty:
    m_cur = df_cur.groupby("Mês_Num")["V. Líquido"].sum().reindex(range(1,13),fill_value=0)
    fig.add_trace(go.Scatter(
        x=meses, 
        y=m_cur, 
        name=str(cur), 
        line=dict(color="#667eea", width=4),
        mode='lines+markers',
        marker=dict(size=8)
    ))

# Adicionar traço do ano anterior
if not df_prev.empty:
    m_prev = df_prev.groupby("Mês_Num")["V. Líquido"].sum().reindex(range(1,13),fill_value=0)
    fig.add_trace(go.Scatter(
        x=meses, 
        y=m_prev, 
        name=str(cur-1), 
        line=dict(color="#f093fb", width=3, dash='dot'),
        mode='lines+markers',
        marker=dict(size=6)
    ))

fig.update_layout(
    hovermode="x unified", 
    xaxis_title="Mês", 
    yaxis_title="Vendas (€)",
    template="plotly_white",
    height=500,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# 6. QUEDA >30%
# -------------------------------------------------
st.markdown('<div class="section-title">🚨 ALERTAS - CLIENTES COM QUEDA >30%</div>', unsafe_allow_html=True)

if not df_prev.empty and not df_cur.empty:
    comp = df_cur.groupby("Cliente")["V. Líquido"].sum().to_frame("Atual")
    comp["Anterior"] = df_prev.groupby("Cliente")["V. Líquido"].sum()
    comp = comp[comp["Anterior"]>0].fillna(0)
    comp["Var%"] = (comp["Atual"]/comp["Anterior"]-1)*100
    q = comp[comp["Var%"]<=-30]
    
    if not q.empty:
        st.markdown(f"""
        <div class="alert-box">
            <h4 style="margin:0; color: white;">⚠️ ALERTA: {len(q)} CLIENTE(S) COM QUEDA SUPERIOR A 30%</h4>
            <p style="margin:0; font-size: 0.9rem;">Clientes que precisam de atenção especial</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Formatar a tabela
        q_display = q.copy()
        q_display["Atual"] = q_display["Atual"].apply(lambda x: f"€{x:,.0f}")
        q_display["Anterior"] = q_display["Anterior"].apply(lambda x: f"€{x:,.0f}")
        q_display["Var%"] = q_display["Var%"].apply(lambda x: f"{x:+.1f}%")
        
        st.dataframe(
            q_display,
            use_container_width=True,
            height=min(400, len(q) * 35 + 38)
        )
    else:
        st.markdown("""
        <div class="success-box">
            <h4 style="margin:0; color: white;">✅ SITUAÇÃO ESTÁVEL</h4>
            <p style="margin:0; font-size: 0.9rem;">Nenhum cliente com queda superior a 30%</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("ℹ️ Dados insuficientes para comparação anual")

# -------------------------------------------------
# 7. DOWNLOAD
# -------------------------------------------------
st.markdown('<div class="section-title">📁 EXPORTAÇÃO DE DADOS</div>', unsafe_allow_html=True)

col_dl1, col_dl2, col_dl3 = st.columns([2, 1, 1])

with col_dl1:
    st.info(f"💾 Preparado para exportar {len(df)} registros filtrados")

with col_dl2:
    st.download_button(
        "📥 Baixar CSV", 
        df.to_csv(index=False).encode(), 
        "vendas_filtradas.csv", 
        "text/csv",
        use_container_width=True
    )

with col_dl3:
    if st.button("🔄 Limpar Filtros", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "📊 Dashboard desenvolvido com Streamlit • "
    f"Última atualização: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}"
    "</div>", 
    unsafe_allow_html=True
)
