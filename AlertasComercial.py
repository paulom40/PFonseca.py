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
    <p style="margin:0; opacity: 0.9; font-size: 1.1rem;">Análise de Vendas - VGlob2425</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 1. LOAD FROM GITHUB - VERSÃO CORRIGIDA
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

    # VERIFICAR ESTRUTURA REAL DO ARQUIVO
    st.info(f"📋 Estrutura do arquivo: {df.shape[1]} colunas, {df.shape[0]} linhas")
    
    # Mostrar as colunas disponíveis
    st.write("🔍 **Colunas disponíveis no arquivo:**")
    for i, col in enumerate(df.columns):
        st.write(f"   {i+1}. {col}")
    
    # Verificar número de colunas e adaptar
    num_colunas = df.shape[1]
    
    if num_colunas == 6:
        st.warning("⚠️ Arquivo tem 6 colunas. Adaptando estrutura...")
        # Mapear as 6 colunas para nomes padrão baseado na estrutura típica
        # Assumindo a estrutura: Código, Cliente, Qtd, UN, V. Líquido, Artigo
        cols = ["Código", "Cliente", "Qtd.", "UN", "V. Líquido", "Artigo"]
        df = df.iloc[:, :6].copy()
        df.columns = cols
        
        # Adicionar colunas faltantes com valores padrão
        df["Comercial"] = "Não Especificado"
        df["Categoria"] = "Geral"
        df["Mês"] = "Julho"  # Valor padrão
        df["Ano"] = 2024     # Valor padrão
        
    elif num_colunas >= 11:
        # Usar estrutura completa se tiver 11+ colunas
        cols = ["Código","Cliente","Qtd.","UN","PM","V. Líquido",
                "Artigo","Comercial","Categoria","Mês","Ano"]
        df = df.iloc[:, :11].copy()
        df.columns = cols
    else:
        # Estrutura personalizada para outros casos
        st.warning(f"⚠️ Estrutura personalizada com {num_colunas} colunas")
        # Manter colunas originais e tentar mapear
        available_cols = list(df.columns)
        st.write("📝 **Mapeamento de colunas:**", available_cols)
        
        # Tentar identificar colunas chave
        col_mapping = {}
        for col in available_cols:
            col_lower = str(col).lower()
            if 'cliente' in col_lower:
                col_mapping[col] = 'Cliente'
            elif 'artigo' in col_lower or 'produto' in col_lower:
                col_mapping[col] = 'Artigo'
            elif 'comercial' in col_lower or 'vendedor' in col_lower:
                col_mapping[col] = 'Comercial'
            elif 'valor' in col_lower or 'líquido' in col_lower or 'preço' in col_lower:
                col_mapping[col] = 'V. Líquido'
            elif 'quant' in col_lower or 'qtd' in col_lower:
                col_mapping[col] = 'Qtd.'
            elif 'mês' in col_lower or 'mes' in col_lower:
                col_mapping[col] = 'Mês'
            elif 'ano' in col_lower:
                col_mapping[col] = 'Ano'
        
        # Renomear colunas identificadas
        df = df.rename(columns=col_mapping)
        
        # Adicionar colunas faltantes se necessário
        required_cols = ['Cliente', 'Artigo', 'V. Líquido', 'Mês', 'Ano']
        for col in required_cols:
            if col not in df.columns:
                if col == 'Mês':
                    df[col] = 'Julho'
                elif col == 'Ano':
                    df[col] = 2024
                elif col == 'Comercial':
                    df[col] = 'Não Especificado'
                elif col == 'Categoria':
                    df[col] = 'Geral'

    # Limpeza básica dos dados
    df = df.dropna(subset=["Cliente", "Artigo"])
    
    # Garantir que temos as colunas mínimas necessárias
    required_minimum = ['Cliente', 'Artigo', 'V. Líquido']
    missing_cols = [col for col in required_minimum if col not in df.columns]
    if missing_cols:
        st.error(f"❌ Colunas essenciais em falta: {missing_cols}")
        st.stop()

    # Processar Mês e Ano
    if 'Mês' not in df.columns:
        df['Mês'] = 'Julho'
    
    if 'Ano' not in df.columns:
        df['Ano'] = 2024

    # Normalizar mês
    df["Mês"] = df["Mês"].astype(str).str.strip().str.lower().apply(unidecode)\
                .str.replace(r"[^a-z]","",regex=True)
    
    meses = {m:i for i,m in enumerate("janeiro fevereiro marco abril maio junho julho agosto setembro outubro novembro dezembro".split(),1)}
    df["Mês_Num"] = df["Mês"].map(meses)

    # Se houver meses inválidos, usar valor padrão
    if df["Mês_Num"].isna().any():
        invalid_months = df[df["Mês_Num"].isna()]["Mês"].unique()
        st.warning(f"⚠️ Meses inválidos encontrados: {', '.join(sorted(invalid_months))}. Usando valor padrão.")
        df["Mês_Num"] = df["Mês_Num"].fillna(7)  # Julho como padrão

    # Processar Ano
    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")
    if df["Ano"].isna().any():
        st.warning("⚠️ Anos inválidos encontrados. Usando 2024 como padrão.")
        df["Ano"] = df["Ano"].fillna(2024)
    
    df["Ano"] = df["Ano"].astype(int)
    df = df[df["Ano"].between(2000, 2100)]

    # Criar data
    df["Data"] = pd.to_datetime(df[["Ano", "Mês_Num"]].assign(day=1)[["Ano", "Mês_Num", "day"]])

    # Processar valor líquido
    df["V. Líquido"] = pd.to_numeric(df["V. Líquido"], errors="coerce").fillna(0)
    
    st.success(f"✅ {len(df)} registros processados com sucesso")
    return df

# Carregar dados
df = load()

# Mostrar preview dos dados
with st.expander("🔍 Visualizar Dados Carregados"):
    st.dataframe(df.head(10), use_container_width=True)
    st.write(f"**Total de registros:** {len(df)}")
    st.write(f"**Colunas disponíveis:** {list(df.columns)}")

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
    ano_sel = st.multiselect("**Selecione o Ano:**", anos, default=anos)
    
    if ano_sel:
        df = df[df["Ano"].isin(ano_sel)]
        meses_disponiveis = sorted(df["Mês"].str.capitalize().unique())
        mes_sel = st.multiselect("**Selecione o Mês:**", meses_disponiveis, default=meses_disponiveis)
        if mes_sel: 
            df = df[df["Mês"].str.capitalize().isin(mes_sel)]
    
    st.markdown('<div class="filter-section">👥 Filtros de Pessoas</div>', unsafe_allow_html=True)
    
    if 'Comercial' in df.columns:
        comerciais = sorted(df["Comercial"].unique())
        com_sel = st.multiselect("**Selecione o Comercial:**", comerciais, default=comerciais)
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
        total_artigos = df["Artigo"].nunique()
        
        st.metric("💰 Vendas Filtradas", f"€{total_vendas:,.0f}")
        st.metric("👥 Clientes", total_clientes)
        st.metric("📦 Artigos", total_artigos)

# Verificar se temos dados após filtros
if len(df) == 0:
    st.error("❌ Nenhum dado encontrado com os filtros aplicados.")
    st.stop()

# -------------------------------------------------
# 3. COMPARATIVO ANUAL
# -------------------------------------------------
anos_disponiveis = sorted(df["Ano"].unique())
if len(anos_disponiveis) >= 1:
    cur = anos_disponiveis[-1]  # Ano mais recente
    df_cur = df[df["Ano"] == cur]
    
    # Tentar obter ano anterior para comparação
    if len(anos_disponiveis) >= 2:
        prev = anos_disponiveis[-2]
        df_prev = df[df["Ano"] == prev]
    else:
        df_prev = pd.DataFrame()
        st.info("ℹ️ Apenas um ano de dados disponível para análise")
else:
    st.error("❌ Nenhum ano de dados disponível")
    st.stop()

v_cur = df_cur["V. Líquido"].sum()
v_prev = df_prev["V. Líquido"].sum() if not df_prev.empty else 0

c_cur = df_cur["Cliente"].nunique()
c_prev = df_prev["Cliente"].nunique() if not df_prev.empty else 0

# -------------------------------------------------
# 4. KPIs
# -------------------------------------------------
st.markdown('<div class="section-title">📊 MÉTRICAS PRINCIPAIS</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_vendas = f"{(v_cur-v_prev)/v_prev*100:+.1f}%" if v_prev > 0 else "N/A"
    st.markdown(f"""
    <div class="metric-card-success">
        <h3 style="margin:0; font-size: 0.9rem;">💰 Total Vendas</h3>
        <p style="margin:0; font-size: 1.5rem; font-weight: bold;">€{v_cur:,.0f}</p>
        <p style="margin:0; font-size: 0.8rem;">{delta_vendas}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    delta_clientes = f"{(c_cur-c_prev)/c_prev*100:+.1f}%" if c_prev > 0 else "N/A"
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin:0; font-size: 0.9rem;">👥 Clientes Ativos</h3>
        <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{c_cur}</p>
        <p style="margin:0; font-size: 0.8rem;">{delta_clientes}</p>
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
# 5. GRÁFICO DE EVOLUÇÃO
# -------------------------------------------------
if len(anos_disponiveis) >= 2:
    st.markdown(f'<div class="section-title">📈 EVOLUÇÃO DE VENDAS - {cur} vs {prev}</div>', unsafe_allow_html=True)
    
    meses = "Janeiro Fevereiro Março Abril Maio Junho Julho Agosto Setembro Outubro Novembro Dezembro".split()
    fig = go.Figure()

    # Adicionar traço do ano atual
    m_cur = df_cur.groupby("Mês_Num")["V. Líquido"].sum().reindex(range(1,13), fill_value=0)
    fig.add_trace(go.Scatter(
        x=meses, 
        y=m_cur, 
        name=str(cur), 
        line=dict(color="#667eea", width=4),
        mode='lines+markers',
        marker=dict(size=8)
    ))

    # Adicionar traço do ano anterior
    m_prev = df_prev.groupby("Mês_Num")["V. Líquido"].sum().reindex(range(1,13), fill_value=0)
    fig.add_trace(go.Scatter(
        x=meses, 
        y=m_prev, 
        name=str(prev), 
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
else:
    st.info("📈 Gráfico de comparação anual disponível apenas com dados de pelo menos 2 anos")

# -------------------------------------------------
# 6. ANÁLISE DE CLIENTES
# -------------------------------------------------
st.markdown('<div class="section-title">🏆 TOP CLIENTES</div>', unsafe_allow_html=True)

# Top 10 clientes por valor
top_clientes = df_cur.groupby("Cliente")["V. Líquido"].sum().nlargest(10)
if len(top_clientes) > 0:
    col_clientes1, col_clientes2 = st.columns(2)
    
    with col_clientes1:
        st.dataframe(
            top_clientes.reset_index().rename(columns={"V. Líquido": "Total Vendas"}),
            use_container_width=True
        )
    
    with col_clientes2:
        fig_clientes = px.bar(
            top_clientes.reset_index(), 
            x='Cliente', 
            y='V. Líquido',
            title="Top 10 Clientes por Vendas",
            color='V. Líquido',
            color_continuous_scale='viridis'
        )
        fig_clientes.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_clientes, use_container_width=True)

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
        df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'), 
        "vendas_filtradas.csv", 
        "text/csv",
        use_container_width=True,
        key="download_csv"
    )

with col_dl3:
    if st.button("🔄 Limpar Filtros", use_container_width=True, key="clear_filters"):
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
