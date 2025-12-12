import pandas as pd
import streamlit as st
import plotly.express as px
import io
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ====================== CONFIGURAÇÃO ======================
st.set_page_config(
    page_title="Dashboard Compras - Premium",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="chart_with_upwards_trend"
)

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
    'unidade': 'Unidade',
    'v líquido': 'V Líquido',
    'v liquido': 'V Líquido',
    'pm': 'PM',
    'data': 'Data',
    'comercial': 'Comercial',
    'mês': 'Mês',
    'mes': 'Mês',
    'ano': 'Ano'
}

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

        # Padronizar nomes de colunas
        df.columns = [COL_MAP.get(str(c).lower().strip(), c) for c in df.columns]

        col_obrig = ["Entidade", "Nome", "Artigo", "Quantidade", "V Líquido", "Data"]
        faltam = [c for c in col_obrig if c not in df.columns]
        if faltam:
            st.error(
                "As seguintes colunas obrigatórias estão em falta no ficheiro: "
                + ", ".join(faltam)
            )
            return pd.DataFrame()

        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        df = df.dropna(subset=["Data"]).copy()

        df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)
        df["V Líquido"] = pd.to_numeric(df["V Líquido"], errors="coerce").fillna(0)

        # Remover linhas sem quantidade ou sem valor
        df = df[(df["Quantidade"] > 0) & (df["V Líquido"] != 0)].copy()

        if "Ano" not in df.columns:
            df["Ano"] = df["Data"].dt.year
        if "Mês" not in df.columns:
            df["Mês"] = df["Data"].dt.month

        df["AnoMes"] = df["Data"].dt.strftime("%Y-%m")

        return df.sort_values("Data").reset_index(drop=True)

    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return pd.DataFrame()

# ====================== FILTROS ======================
def aplicar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    st.sidebar.markdown("### Filtros Dinâmicos")

    # Ano
    anos = sorted(df["Ano"].unique(), reverse=True)
    ano_sel = st.sidebar.multiselect("Ano", options=anos, default=anos[:2])
    if ano_sel:
        df = df[df["Ano"].isin(ano_sel)]

    # Mês (a partir da coluna Data)
    if not df.empty:
        meses_num = sorted(df["Data"].dt.month.unique())
        meses_opcoes = [MESES_NOME[m - 1] for m in meses_num]
        mes_sel = st.sidebar.multiselect(
            "Mês",
            options=meses_opcoes,
            default=meses_opcoes[-3:] if len(meses_opcoes) >= 3 else meses_opcoes
        )
        meses_sel_num = [MESES_NOME.index(m) + 1 for m in mes_sel]
        if meses_sel_num:
            df = df[df["Data"].dt.month.isin(meses_sel_num)]

    # Comercial
    if not df.empty and "Comercial" in df.columns:
        comerciais = sorted(df["Comercial"].dropna().unique())
        com_sel = st.sidebar.multiselect(
            "Comercial",
            options=comerciais,
            default=comerciais[:3] if len(comerciais) >= 3 else comerciais
        )
        if com_sel:
            df = df[df["Comercial"].isin(com_sel)]

    # Cliente
    if not df.empty:
        clientes = sorted(df["Nome"].dropna().unique())
        cli_sel = st.sidebar.multiselect(
            "Cliente",
            options=clientes,
            default=clientes[:5] if len(clientes) >= 5 else clientes
        )
        if cli_sel:
            df = df[df["Nome"].isin(cli_sel)]

    # Produto
    if not df.empty:
        produtos = sorted(df["Artigo"].dropna().unique())
        prod_sel = st.sidebar.multiselect(
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
            "total_vendas": 0,
            "qtd": 0,
            "clientes": 0,
            "produtos": 0,
            "trans": 0,
            "ticket": 0,
            "venda_dia": 0,
            "valor_unidade": 0,
            "periodo": "Sem dados"
        }

    total_vendas = df["V Líquido"].sum()
    qtd_total = df["Quantidade"].sum()

    data_min = df["Data"].min()
    data_max = df["Data"].max()
    periodo = f"{data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')}"

    # ✅ Dias com vendas reais (corrigido)
    dias_com_venda = df["Data"].dt.date.nunique()

    transacoes = len(df)
    clientes = df["Nome"].nunique()
    produtos = df["Artigo"].nunique()

    ticket_medio = total_vendas / transacoes if transacoes > 0 else 0
    venda_media_dia = total_vendas / dias_com_venda if dias_com_venda > 0 else 0
    valor_medio_unidade = total_vendas / qtd_total if qtd_total > 0 else 0

    return {
        "total_vendas": total_vendas,
        "qtd": qtd_total,
        "clientes": clientes,
        "produtos": produtos,
        "trans": transacoes,
        "ticket": ticket_medio,
        "venda_dia": venda_media_dia,
        "valor_unidade": valor_medio_unidade,
        "periodo": periodo
    }


# ====================== TICKET MÉDIO POR COMERCIAL ======================
def calcular_ticket_medio_por_comercial(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "Comercial" not in df.columns:
        return pd.DataFrame()

    grp = df.groupby("Comercial").agg(
        Total_Vendas=("V Líquido", "sum"),
        Transacoes=("V Líquido", "count"),
        Quantidade=("Quantidade", "sum")
    ).reset_index()

    grp["Ticket_Medio"] = grp["Total_Vendas"] / grp["Transacoes"]
    grp["Valor_Medio_Unidade"] = grp["Total_Vendas"] / grp["Quantidade"]

    return grp.sort_values("Ticket_Medio", ascending=False)
# ====================== VISUALIZAÇÕES ======================
def desenhar_kpis(kpis: dict, df_ticket_com: pd.DataFrame):
    st.subheader("KPIs em Tempo Real")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Vendas (€)", f"{kpis['total_vendas']:,.2f}")
    c2.metric("Quantidade Total", f"{kpis['qtd']:,.2f}")
    c3.metric("Clientes Únicos", int(kpis["clientes"]))
    c4.metric("Produtos Vendidos", int(kpis["produtos"]))
    c5.metric("Transações (linhas)", int(kpis["trans"]))

    st.divider()

    c6, c7, c8 = st.columns(3)
    c6.metric("Ticket Médio por Transação (€)", f"{kpis['ticket']:,.2f}")
    c7.metric("Venda Média por Dia (€)", f"{kpis['venda_dia']:,.2f}")
    c8.metric("Valor Médio por Unidade (€)", f"{kpis['valor_unidade']:,.4f}")

    st.info(f"Período em análise: {kpis['periodo']}")

    st.subheader("Ticket Médio por Comercial")
    if df_ticket_com.empty:
        st.warning("Sem dados de comercial para o período/filtros atuais.")
    else:
        df_show = df_ticket_com.copy()
        df_show["Total_Vendas"] = df_show["Total_Vendas"].map(lambda x: f"€{x:,.2f}")
        df_show["Ticket_Medio"] = df_show["Ticket_Medio"].map(lambda x: f"€{x:,.2f}")
        df_show["Valor_Medio_Unidade"] = df_show["Valor_Medio_Unidade"].map(lambda x: f"€{x:,.4f}")
        st.dataframe(df_show, width="stretch")


def grafico_evolucao(df: pd.DataFrame):
    st.subheader("Evolução Mensal de Vendas (€)")
    if df.empty:
        st.warning("Nenhum dado com os filtros atuais.")
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
    st.plotly_chart(fig, use_container_width=True)


def graficos_top10(df: pd.DataFrame):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Clientes por Vendas (€)")
        if df.empty:
            st.warning("Sem dados para o período/filtros atuais.")
        else:
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
            st.plotly_chart(figc, use_container_width=True)

    with col2:
        st.subheader("Top 10 Produtos por Vendas (€)")
        if df.empty:
            st.warning("Sem dados para o período/filtros atuais.")
        else:
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
            st.plotly_chart(figp, use_container_width=True)
# ====================== TABELA DETALHADA + EXPORTAÇÃO ======================
def tabela_dados_export(df: pd.DataFrame, kpis: dict):
    st.subheader("Tabela de Dados Detalhada")
    if df.empty:
        st.warning("Nenhum dado para apresentar na tabela com os filtros atuais.")
        return

    cols = ["Data", "Entidade", "Nome", "Artigo", "Quantidade",
            "Unidade", "V Líquido", "PM", "Comercial", "Mês", "Ano"]
    cols_existentes = [c for c in cols if c in df.columns]

    display_df = df[cols_existentes].copy()
    display_df["Data"] = display_df["Data"].dt.strftime("%d/%m/%Y")

    st.dataframe(
        display_df.style.format({
            "V Líquido": "€{:,.2f}",
            "PM": "€{:,.2f}"
        }),
        use_container_width=True,
        height=600
    )

    st.subheader("Exportar Dados e KPIs")
    col1, col2 = st.columns(2)

    # ✅ Exportar CSV
    csv = df.to_csv(index=False).encode()
    col1.download_button(
        "Download CSV",
        data=csv,
        file_name="dados.csv",
        mime="text/csv",
        help="Exportar dados filtrados em formato CSV.",
        key="btn_csv"
    )

    # ✅ Exportar Excel com KPIs
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
