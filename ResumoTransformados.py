import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import io

# ====================== CONFIG STREAMLIT ======================
st.set_page_config(
    page_title="Dashboard Comercial",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CSS ======================
st.markdown("""
<style>
    .metric-container {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #ddd;
    }
    .metric-value {
        font-size: 26px;
        font-weight: bold;
        color: #333;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# ====================== HEADER ======================
st.title("📊 Dashboard Comercial — Vendas & KPIs")
st.markdown("Análise completa de vendas, comerciais, clientes e produtos.")
# ====================== LOAD DATA ======================
@st.cache_data
def load_data(path: str = "ResumoTR.xlsx") -> pd.DataFrame:
    try:
        df = pd.read_excel(path)
    except Exception as e:
        st.error(f"Erro a carregar o ficheiro de dados: {e}")
        return pd.DataFrame()

    df.columns = [str(c).strip() for c in df.columns]

    col_map = {
        "Entidad": "Entidade",
        "Entidade": "Entidade",
        "Nome": "Nome",
        "Artigo": "Artigo",
        "Cantidad": "Quantidade",
        "Quantidad": "Quantidade",
        "Quantidade": "Quantidade",
        "Unidad": "Unidade",
        "Unidade": "Unidade",
        "V Líquid": "V Líquido",
        "V_Liquid": "V Líquido",
        "V Líquido": "V Líquido",
        "PM": "PM",
        "Data": "Data",
        "Comercial": "Comercial",
        "Mês": "Mês",
        "Mes": "Mês",
        "Ano": "Ano",
    }

    df = df.rename(columns={c: col_map.get(c, c) for c in df.columns})

    required = ["Entidade", "Nome", "Artigo", "Quantidade", "Unidade",
                "V Líquido", "PM", "Data", "Comercial", "Mês", "Ano"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Faltam colunas obrigatórias no ficheiro: {missing}")
        return pd.DataFrame()

    # ✅ CORREÇÃO QUANTIDADE
    df["Quantidade"] = (
        df["Quantidade"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace("KG", "", regex=False)
        .str.replace("kg", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace("\u00A0", "", regex=False)
    )
    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce")

    df["V Líquido"] = pd.to_numeric(df["V Líquido"], errors="coerce")
    df["PM"] = pd.to_numeric(df["PM"], errors="coerce")
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    df = df.dropna(subset=["Data"])
    df = df[(df["Quantidade"] > 0) & (df["V Líquido"] != 0)]

    df["AnoMes"] = df["Data"].dt.strftime("%Y-%m")

    return df


# ====================== FILTROS ======================
def aplicar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")

    if df.empty:
        st.sidebar.warning("Sem dados para aplicar filtros.")
        return df

    data_min = df["Data"].min()
    data_max = df["Data"].max()

    data_inicio, data_fim = st.sidebar.date_input(
        "Período",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max
    )

    if isinstance(data_inicio, datetime):
        data_inicio = data_inicio.date()
    if isinstance(data_fim, datetime):
        data_fim = data_fim.date()

    mask_data = (df["Data"].dt.date >= data_inicio) & (df["Data"].dt.date <= data_fim)
    df_filt = df[mask_data].copy()

    # ✅ Filtro Comercial
    comerciais = sorted(df_filt["Comercial"].dropna().unique())
    sel_com = st.sidebar.multiselect("Comercial", options=comerciais, default=comerciais)
    if sel_com:
        df_filt = df_filt[df_filt["Comercial"].isin(sel_com)]

    # ✅ Filtro Artigo
    artigos = sorted(df_filt["Artigo"].dropna().unique())
    sel_art = st.sidebar.multiselect("Artigo", options=artigos, default=artigos)
    if sel_art:
        df_filt = df_filt[df_filt["Artigo"].isin(sel_art)]

    # ✅ Filtro Nome (corrigido)
    df_filt["Nome"] = df_filt["Nome"].astype(str).fillna("").str.strip()
    nomes = sorted([n for n in df_filt["Nome"].unique() if n and n.lower() != "nan"])

    sel_nome = st.sidebar.multiselect("Nome entidade", options=nomes, default=nomes)
    if sel_nome:
        df_filt = df_filt[df_filt["Nome"].isin(sel_nome)]

    return df_filt
# ====================== KPIs ======================
def calcular_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total_vendas": 0, "qtd": 0, "clientes": 0, "produtos": 0,
            "trans": 0, "ticket": 0, "venda_dia": 0, "valor_unidade": 0,
            "periodo": "Sem dados"
        }

    total_vendas = df["V Líquido"].sum()
    qtd_total = df["Quantidade"].sum()

    data_min = df["Data"].min()
    data_max = df["Data"].max()
    periodo = f"{data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')}"

    dias_com_venda = df["Data"].dt.date.nunique()

    transacoes = len(df)
    clientes = df["Nome"].nunique()
    produtos = df["Artigo"].nunique()

    ticket_medio = total_vendas / transacoes if transacoes else 0
    venda_media_dia = total_vendas / dias_com_venda if dias_com_venda else 0
    valor_medio_unidade = total_vendas / qtd_total if qtd_total else 0

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
    if df.empty:
        return pd.DataFrame()

    grp = df.groupby("Comercial").agg(
        Total_Vendas=("V Líquido", "sum"),
        Transacoes=("V Líquido", "count"),
        Quantidade=("Quantidade", "sum")
    ).reset_index()

    grp["Ticket_Medio"] = grp["Total_Vendas"] / grp["Transacoes"]
    grp["Valor_Medio_Unidade"] = grp["Total_Vendas"] / grp["Quantidade"]

    return grp.sort_values("Total_Vendas", ascending=False)
# ====================== VISUALIZAÇÕES ======================
def desenhar_kpis(kpis: dict, df_ticket_com: pd.DataFrame):
    st.subheader("KPIs em Tempo Real")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Vendas (€)", f"{kpis['total_vendas']:,.2f}")
    c2.metric("Quantidade Total", f"{kpis['qtd']:,.2f}")
    c3.metric("Clientes Únicos", int(kpis["clientes"]))
    c4.metric("Produtos Vendidos", int(kpis["produtos"]))
    c5.metric("Transações", int(kpis["trans"]))

    st.divider()

    c6, c7, c8 = st.columns(3)
    c6.metric("Ticket Médio (€)", f"{kpis['ticket']:,.2f}")
    c7.metric("Venda Média por Dia (€)", f"{kpis['venda_dia']:,.2f}")
    c8.metric("Valor Médio por Unidade (€)", f"{kpis['valor_unidade']:,.4f}")

    st.info(f"Período em análise: {kpis['periodo']}")

    st.subheader("Ticket Médio por Comercial")
    if df_ticket_com.empty:
        st.warning("Sem dados de comercial.")
    else:
        df_show = df_ticket_com.copy()
        df_show["Total_Vendas"] = df_show["Total_Vendas"].map(lambda x: f"€{x:,.2f}")
        df_show["Ticket_Medio"] = df_show["Ticket_Medio"].map(lambda x: f"€{x:,.2f}")
        df_show["Valor_Medio_Unidade"] = df_show["Valor_Medio_Unidade"].map(lambda x: f"€{x:,.4f}")
        st.dataframe(df_show, use_container_width=True)


def grafico_evolucao(df: pd.DataFrame):
    st.subheader("Evolução Mensal de Vendas (€)")
    if df.empty:
        st.warning("Sem dados.")
        return

    mensal = df.groupby("AnoMes")["V Líquido"].sum().reset_index()

    fig = px.line(mensal, x="AnoMes", y="V Líquido", markers=True)
    fig.add_bar(x=mensal["AnoMes"], y=mensal["V Líquido"])
    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)


def graficos_top10(df: pd.DataFrame):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Clientes (€)")
        if df.empty:
            st.warning("Sem dados.")
        else:
            topc = df.groupby("Nome")["V Líquido"].sum().nlargest(10)
            figc = px.bar(
                x=topc.values, y=topc.index, orientation="h",
                color=topc.values, color_continuous_scale="Viridis"
            )
            figc.update_layout(height=500)
            st.plotly_chart(figc, use_container_width=True)

    with col2:
        st.subheader("Top 10 Produtos (€)")
        if df.empty:
            st.warning("Sem dados.")
        else:
            topp = df.groupby("Artigo")["V Líquido"].sum().nlargest(10)
            figp = px.bar(
                x=topp.values, y=topp.index, orientation="h",
                color=topp.values, color_continuous_scale="Plasma"
            )
            figp.update_layout(height=500)
            st.plotly_chart(figp, use_container_width=True)
# ====================== TABELA DETALHADA + EXPORTAÇÃO ======================
def tabela_dados_export(df: pd.DataFrame, kpis: dict):
    st.subheader("Tabela de Dados Detalhada")

    if df.empty:
        st.warning("Sem dados.")
        return

    cols = [
        "Data", "Entidade", "Nome", "Artigo", "Quantidade",
        "Unidade", "V Líquido", "PM", "Comercial", "Mês", "Ano"
    ]
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

    csv = df.to_csv(index=False).encode()
    col1.download_button(
        "Download CSV",
        data=csv,
        file_name="dados.csv",
        mime="text/csv"
    )

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Dados", index=False)
        pd.DataFrame([kpis]).to_excel(writer, sheet_name="KPIs", index=False)

    col2.download_button(
        "Download Excel + KPIs",
        data=buffer.getvalue(),
        file_name="relatorio.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# ====================== DEBUG OPCIONAL ======================
def debug_comercial_mes(df: pd.DataFrame):
    st.subheader("🔍 Debug — Comercial / Ano / Mês")

    if df.empty:
        st.warning("Sem dados para debug.")
        return

    df_dbg = df.copy()
    df_dbg["AnoMes"] = df_dbg["Data"].dt.strftime("%Y-%m")

    resumo = df_dbg.groupby(["Comercial", "Ano", "Mês", "AnoMes"]).agg(
        Total_Vendas=("V Líquido", "sum"),
        Quantidade=("Quantidade", "sum"),
        Transacoes=("V Líquido", "count")
    ).reset_index()

    resumo["Ticket_Medio"] = resumo["Total_Vendas"] / resumo["Transacoes"]
    resumo["Valor_Medio_Unidade"] = resumo["Total_Vendas"] / resumo["Quantidade"]

    resumo = resumo.sort_values("Total_Vendas", ascending=False)

    resumo["Total_Vendas"] = resumo["Total_Vendas"].map(lambda x: f"€{x:,.2f}")
    resumo["Ticket_Medio"] = resumo["Ticket_Medio"].map(lambda x: f"€{x:,.2f}")
    resumo["Valor_Medio_Unidade"] = resumo["Valor_Medio_Unidade"].map(lambda x: f"€{x:,.4f}")

    st.dataframe(resumo, use_container_width=True)


# ====================== MAIN ======================
def main():
    st.sidebar.title("📁 Carregar Dados")

    file = st.sidebar.file_uploader("Selecionar ficheiro Excel", type=["xlsx"])

    if file is None:
        st.info("Carrega um ficheiro Excel para começar.")
        return

    df = load_data(file)

    if df.empty:
        st.error("Erro ao carregar os dados.")
        return

    df_filt = aplicar_filtros(df)

    kpis = calcular_kpis(df_filt)
    df_ticket_com = calcular_ticket_medio_por_comercial(df_filt)

    tab1, tab2, tab3 = st.tabs(["📊 KPIs", "📈 Gráficos", "📄 Tabela"])

    with tab1:
        desenhar_kpis(kpis, df_ticket_com)
        # ✅ Debug opcional — só aparece se ativares manualmente:
        # debug_comercial_mes(df_filt)

    with tab2:
        grafico_evolucao(df_filt)
        graficos_top10(df_filt)

    with tab3:
        tabela_dados_export(df_filt, kpis)

    st.markdown("---")
    st.markdown("Desenvolvido por Paulo — Dashboard Comercial ✅")


# ====================== EXECUTAR APP ======================
if __name__ == "__main__":
    main()
