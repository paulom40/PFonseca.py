import pandas as pd
import streamlit as st
import plotly.express as px
import io
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ====================== CONSTANTES ======================
MESES_NOME = [
    "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
    "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"
]

COL_MAP = {
    'entidade': 'Entidade',
    'nome': 'Nome',
    'artigo': 'Artigo',
    'quantidade': 'Quantidade',
    'v líquido': 'V Líquido',
    'v liquido': 'V Líquido',
    'pm': 'PM',
    'data': 'Data',
    'comercial': 'Comercial'
}

# ====================== CONFIGURAÇÃO ======================
st.set_page_config(
    page_title="Dashboard Compras - Premium",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="chart_with_upwards_trend"
)

# ====================== CSS ======================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102,126,234,0.3);
    }
    .stMetric {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .sidebar-section {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ====================== HEADER ======================
st.markdown("""
<div class="main-header">
    <h1>DASHBOARD DE COMPRAS</h1>
    <p>Análise em Tempo Real • Filtros Dinâmicos • KPIs Atualizados Instantaneamente</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "- Utilize os filtros à esquerda para selecionar período, comerciais, clientes e produtos.\n"
    "- Os KPIs refletem sempre o período filtrado.\n"
    "- Navegue pelas abas para ver evolução temporal, Top 10 e dados detalhados."
)

# ====================== CARREGAR DADOS ======================
@st.cache_data(show_spinner="Carregando ResumoTR.xlsx...", ttl=600)
def load_data(path: str = "ResumoTR.xlsx") -> pd.DataFrame:
    try:
        df = pd.read_excel(path)

        # Padronizar colunas
        df.columns = [COL_MAP.get(c.lower().strip(), c) for c in df.columns]

        # Verificação básica de schema
        col_obrig = ["Data", "Quantidade", "V Líquido", "Nome", "Artigo"]
        faltam = [c for c in col_obrig if c not in df.columns]
        if faltam:
            st.error(f"As seguintes colunas obrigatórias estão em falta no ficheiro: {', '.join(faltam)}")
            return pd.DataFrame()

        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        df = df.dropna(subset=["Data"]).copy()

        df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)
        df["V Líquido"] = pd.to_numeric(df["V Líquido"], errors="coerce").fillna(0)
        df = df[(df["Quantidade"] > 0) & (df["V Líquido"] > 0)].copy()

        df["Ano"] = df["Data"].dt.year
        df["Mes_Numero"] = df["Data"].dt.month
        df["Mês"] = df["Data"].dt.strftime("%B")
        df["AnoMes"] = df["Data"].dt.strftime("%Y-%m")

        return df.sort_values("Data").reset_index(drop=True)
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return pd.DataFrame()

# ====================== FILTROS ======================
def aplicar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    st.sidebar.markdown("### FILTROS DINÂMICOS")

    # Filtros de período
    with st.sidebar.expander("Período", expanded=True):
        anos = sorted(df["Ano"].unique(), reverse=True)
        ano_sel = st.multiselect("Ano", options=anos, default=anos[:2])
        if ano_sel:
            df = df[df["Ano"].isin(ano_sel)]

        if not df.empty:
            meses_num = sorted(df["Mes_Numero"].unique())
            meses_opcoes = [MESES_NOME[m - 1] for m in meses_num]
            mes_sel = st.multiselect(
                "Mês",
                options=meses_opcoes,
                default=meses_opcoes[-3:] if len(meses_opcoes) >= 3 else meses_opcoes
            )
            meses_sel_num = [MESES_NOME.index(m) + 1 for m in mes_sel]
            if meses_sel_num:
                df = df[df["Mes_Numero"].isin(meses_sel_num)]

    # Filtros de dimensão
    with st.sidebar.expander("Comercial / Cliente / Produto", expanded=False):
        if not df.empty:
            # Comercial
            if "Comercial" in df.columns:
                comerciais = sorted(df["Comercial"].dropna().unique())
                com_sel = st.multiselect(
                    "Comercial",
                    options=comerciais,
                    default=comerciais[:3] if len(comerciais) >= 3 else comerciais
                )
                if com_sel:
                    df = df[df["Comercial"].isin(com_sel)]

            # Cliente
            if not df.empty:
                clientes = sorted(df["Nome"].dropna().unique())
                cli_sel = st.multiselect(
                    "Cliente",
                    options=clientes,
                    default=clientes[:5] if len(clientes) >= 5 else clientes
                )
                if cli_sel:
                    df = df[df["Nome"].isin(cli_sel)]

            # Produto
            if not df.empty:
                produtos = sorted(df["Artigo"].dropna().unique())
                prod_sel = st.multiselect(
                    "Produto",
                    options=produtos,
                    default=produtos[:10] if len(produtos) >= 10 else produtos
                )
                if prod_sel:
                    df = df[df["Artigo"].isin(prod_sel)]

    return df

# ====================== KPIs ======================
def calcular_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            k: 0 for k in [
                "total_vendas","qtd","clientes","produtos",
                "trans","ticket","venda_dia","valor_unidade",
                "periodo","total_vendas_prev","delta_vendas"
            ]
        }

    total = df["V Líquido"].sum()
    qtd = df["Quantidade"].sum()
    # média por dia de calendário no período
    dias_periodo = (df["Data"].max() - df["Data"].min()).days + 1

    periodo = f"{df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}"

    return {
        "total_vendas": total,
        "qtd": qtd,
        "clientes": df["Nome"].nunique(),
        "produtos": df["Artigo"].nunique(),
        "trans": len(df),
        "ticket": total / len(df) if len(df) > 0 else 0,        # ticket por transação
        "venda_dia": total / dias_periodo if dias_periodo > 0 else 0,
        "valor_unidade": total / qtd if qtd > 0 else 0,
        "periodo": periodo,
        "total_vendas_prev": None,
        "delta_vendas": None,
    }

def calcular_delta_periodo(df_total: pd.DataFrame, df_filt: pd.DataFrame, kpis: dict) -> dict:
    if df_filt.empty:
        return kpis

    data_min = df_filt["Data"].min()
    data_max = df_filt["Data"].max()
    periodo_dias = (data_max - data_min).days + 1

    if periodo_dias <= 0:
        return kpis

    inicio_prev = data_min - pd.Timedelta(days=periodo_dias)
    fim_prev = data_min - pd.Timedelta(days=1)

    df_prev = df_total[(df_total["Data"] >= inicio_prev) & (df_total["Data"] <= fim_prev)].copy()

    if df_prev.empty:
        return kpis

    total_prev = df_prev["V Líquido"].sum()
    kpis["total_vendas_prev"] = total_prev

    if total_prev != 0:
        kpis["delta_vendas"] = (kpis["total_vendas"] - total_prev) / total_prev * 100
    else:
        kpis["delta_vendas"] = None

    return kpis

def calcular_ticket_medio_por_comercial(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ticket médio por comercial = total de vendas do comercial / nº de transações (linhas) do comercial no período filtrado.
    """
    if df.empty or "Comercial" not in df.columns:
        return pd.DataFrame()

    grp = df.groupby("Comercial").agg(
        Total_Vendas=("V Líquido", "sum"),
        Transacoes=("V Líquido", "count")
    ).reset_index()

    grp["Ticket_Medio"] = grp["Total_Vendas"] / grp["Transacoes"]
    return grp.sort_values("Total_Vendas", ascending=False)

# ====================== VISUALIZAÇÕES ======================
def desenhar_kpis(kpis: dict, df_ticket_com: pd.DataFrame):
    st.subheader("KPIs em Tempo Real")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(
        "Total Vendas (€)",
        f"{kpis['total_vendas']:,.0f}",
        delta=f"{kpis['delta_vendas']:.1f}%" if kpis.get("delta_vendas") is not None else None
    )
    c2.metric("Quantidade Total", f"{kpis['qtd']:,.0f}")
    c3.metric("Clientes Únicos", kpis["clientes"])
    c4.metric("Produtos Vendidos", kpis["produtos"])
    c5.metric("Transações", f"{kpis['trans']:,}")

    st.divider()

    c6, c7, c8 = st.columns(3)
    c6.metric("Ticket Médio por Transação (€)", f"{kpis['ticket']:,.0f}")
    c7.metric("Venda Média / Dia de Calendário (€)", f"{kpis['venda_dia']:,.0f}")
    c8.metric("Valor Médio / Unidade (€)", f"{kpis['valor_unidade']:,.2f}")

    st.info(f"**Período em análise:** {kpis['periodo']}")

    # Tabela de Ticket Médio por Comercial
    st.subheader("Ticket Médio por Comercial")
    if df_ticket_com.empty:
        st.warning("Sem dados de comercial para o período/filtros atuais.")
    else:
        df_show = df_ticket_com.copy()
        df_show["Total_Vendas"] = df_show["Total_Vendas"].map(lambda x: f"€{x:,.2f}")
        df_show["Ticket_Medio"] = df_show["Ticket_Medio"].map(lambda x: f"€{x:,.2f}")
        st.dataframe(df_show, width="stretch")

def grafico_evolucao(df: pd.DataFrame):
    st.subheader("Evolução Mensal de Vendas (€)")
    if df.empty:
        st.warning("Nenhum dado com os filtros atuais")
        return

    mensal = df.groupby("AnoMes")["V Líquido"].sum().reset_index()
    fig = px.line(
        mensal,
        x="AnoMes",
        y="V Líquido",
        markers=True,
        title="Vendas por Mês (Ano-Mês)"
    )
    fig.add_bar(x=mensal["AnoMes"], y=mensal["V Líquido"], name="Vendas (€)")
    fig.update_layout(
        xaxis_title="Período (Ano-Mês)",
        yaxis_title="Vendas (€)",
        height=500
    )
    st.plotly_chart(fig, width="stretch")

def graficos_top10(df: pd.DataFrame):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Clientes por Vendas (€)")
        if not df.empty:
            topc = df.groupby("Nome")["V Líquido"].sum().nlargest(10)
            figc = px.bar(
                x=topc.values,
                y=topc.index,
                orientation="h",
                color=topc.values,
                color_continuous_scale="Viridis",
                labels={"x": "Vendas (€)", "y": "Cliente"}
            )
            figc.update_layout(
                height=500,
                yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(figc, width="stretch")

    with col2:
        st.subheader("Top 10 Produtos por Vendas (€)")
        if not df.empty:
            topp = df.groupby("Artigo")["V Líquido"].sum().nlargest(10)
            figp = px.bar(
                x=topp.values,
                y=topp.index,
                orientation="h",
                color=topp.values,
                color_continuous_scale="Plasma",
                labels={"x": "Vendas (€)", "y": "Produto"}
            )
            figp.update_layout(
                height=500,
                yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(figp, width="stretch")

def tabela_dados_export(df: pd.DataFrame, kpis: dict):
    st.subheader("Tabela de Dados Detalhada")
    if df.empty:
        st.warning("Nenhum dado para apresentar na tabela com os filtros atuais.")
        return

    cols = ["Data", "Nome", "Artigo", "Quantidade", "V Líquido", "PM", "Comercial"]
    cols_existentes = [c for c in cols if c in df.columns]

    display_df = df[cols_existentes].copy()
    display_df["Data"] = display_df["Data"].dt.strftime("%d/%m/%Y")

    st.dataframe(
        display_df.style.format({"V Líquido": "€{:,.2f}", "PM": "€{:,.2f}"}),
        width="stretch",
        height=600
    )

    st.subheader("Exportar Dados e KPIs")
    col1, col2 = st.columns(2)

    csv = df.to_csv(index=False).encode()
    col1.download_button(
        "Download CSV",
        data=csv,
        file_name="dados.csv",
        mime="text/csv",
        help="Exportar dados filtrados em formato CSV.",
        key="btn_csv",
        type="primary"
    )

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Dados", index=False)
        pd.DataFrame([kpis]).to_excel(writer, sheet_name="KPIs", index=False)

    col2.download_button(
        "Download Excel + KPIs",
        data=buffer.getvalue(),
        file_name="relatorio.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Exportar dados filtrados e KPIs em ficheiro Excel.",
        key="btn_excel"
    )

# ====================== MAIN ======================
df_original = load_data()
if df_original.empty:
    st.stop()

df_filt = aplicar_filtros(df_original.copy())

kpis = calcular_kpis(df_filt)
kpis = calcular_delta_periodo(df_original, df_filt, kpis)

# Ticket médio por comercial (com base no df_filt)
df_ticket_com = calcular_ticket_medio_por_comercial(df_filt)

tab1, tab2, tab3, tab4 = st.tabs(["KPIs PRINCIPAIS", "EVOLUÇÃO", "TOP 10", "DADOS"])

with tab1:
    desenhar_kpis(kpis, df_ticket_com)

with tab2:
    grafico_evolucao(df_filt)

with tab3:
    graficos_top10(df_filt)

with tab4:
    tabela_dados_export(df_filt, kpis)

# ====================== FOOTER ======================
st.markdown("---")
st.markdown(
    f"<small style='text-align:center;display:block;color:#666'>Dashboard atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</small>",
    unsafe_allow_html=True
)
