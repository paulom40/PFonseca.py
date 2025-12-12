import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import io

import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage

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

    if pd.isna(data_min) or pd.isna(data_max):
        st.sidebar.error("Datas inválidas no dataset.")
        return df

    data_min = data_min.date()
    data_max = data_max.date()

    data_inicio, data_fim = st.sidebar.date_input(
        "Período",
        value=(data_min, data_max)
    )

    if isinstance(data_inicio, datetime):
        data_inicio = data_inicio.date()
    if isinstance(data_fim, datetime):
        data_fim = data_fim.date()

    mask_data = (df["Data"].dt.date >= data_inicio) & (df["Data"].dt.date <= data_fim)
    df_filt = df[mask_data].copy()

    comerciais = sorted(df_filt["Comercial"].dropna().unique())
    sel_com = st.sidebar.multiselect("Comercial", options=comerciais, default=comerciais)
    if sel_com:
        df_filt = df_filt[df_filt["Comercial"].isin(sel_com)]

    artigos = sorted(df_filt["Artigo"].dropna().unique())
    sel_art = st.sidebar.multiselect("Artigo", options=artigos, default=artigos)
    if sel_art:
        df_filt = df_filt[df_filt["Artigo"].isin(sel_art)]

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
            "trans": 0, "ticket": 0, "ticket_cliente": 0,
            "venda_dia": 0, "valor_unidade": 0,
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
    ticket_medio_cliente = total_vendas / clientes if clientes else 0
    venda_media_dia = total_vendas / dias_com_venda if dias_com_venda else 0
    valor_medio_unidade = total_vendas / qtd_total if qtd_total else 0

    return {
        "total_vendas": total_vendas,
        "qtd": qtd_total,
        "clientes": clientes,
        "produtos": produtos,
        "trans": transacoes,
        "ticket": ticket_medio,
        "ticket_cliente": ticket_medio_cliente,
        "venda_dia": venda_media_dia,
        "valor_unidade": valor_medio_unidade,
        "periodo": periodo
    }


# ====================== ALERTAS E THRESHOLDS ======================
def obter_thresholds_globais():
    return {
        "ticket_comercial": 1000,
        "ticket_cliente": 1500,
        "venda_dia": 2000,
        "valor_unidade": 2,
        "total_vendas": 50000
    }


def mostrar_alerta(label: str, valor: float, limite: float):
    if limite is None:
        st.info(f"{label}: {valor:,.2f}")
        return

    if valor >= limite:
        st.success(f"{label}: {valor:,.2f} (acima do esperado)")
    elif valor >= limite * 0.7:
        st.warning(f"{label}: {valor:,.2f} (atenção)")
    else:
        st.error(f"{label}: {valor:,.2f} (abaixo do esperado)")


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
    c6.metric("Ticket Médio Comercial (€)", f"{kpis['ticket']:,.2f}")
    c7.metric("Ticket Médio Cliente (€)", f"{kpis['ticket_cliente']:,.2f}")
    c8.metric("Valor Médio por Unidade (€)", f"{kpis['valor_unidade']:,.4f}")

    st.info(f"Período em análise: {kpis['periodo']}")

    st.subheader("Ticket Médio por Comercial")
    if df_ticket_com.empty:
        st.warning("Sem dados de comercial.")
    else:
        df_show = df_ticket_com.copy()
        df_show["Total_Vendas"] = df_show["Total_Vendas"].map(lambda x: f"{x:,.2f}")
        df_show["Ticket_Medio"] = df_show["Ticket_Medio"].map(lambda x: f"{x:,.2f}")
        df_show["Valor_Medio_Unidade"] = df_show["Valor_Medio_Unidade"].map(lambda x: f"{x:,.4f}")
        st.dataframe(df_show, use_container_width=True)

    st.subheader("Alertas de Desempenho (Globais)")
    thresholds = obter_thresholds_globais()
    mostrar_alerta("Ticket Médio Comercial (€)", kpis["ticket"], thresholds["ticket_comercial"])
    mostrar_alerta("Ticket Médio Cliente (€)", kpis["ticket_cliente"], thresholds["ticket_cliente"])
    mostrar_alerta("Venda Média por Dia (€)", kpis["venda_dia"], thresholds["venda_dia"])
    mostrar_alerta("Valor Médio por Unidade (€)", kpis["valor_unidade"], thresholds["valor_unidade"])
    mostrar_alerta("Total de Vendas (€)", kpis["total_vendas"], thresholds["total_vendas"])


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
# ====================== ALERTAS POR COMERCIAL ======================
def alertas_por_comercial(df: pd.DataFrame):
    st.subheader("Alertas por Comercial")

    if df.empty:
        st.warning("Sem dados para análise de comerciais.")
        return

    thresholds = obter_thresholds_globais()

    grp = df.groupby("Comercial").agg(
        Total_Vendas=("V Líquido", "sum"),
        Transacoes=("V Líquido", "count"),
        Quantidade=("Quantidade", "sum"),
        Clientes=("Nome", "nunique")
    ).reset_index()

    grp["Ticket_Medio_Comercial"] = grp["Total_Vendas"] / grp["Transacoes"]
    grp["Ticket_Medio_Cliente"] = grp["Total_Vendas"] / grp["Clientes"]

    for _, row in grp.iterrows():
        st.markdown(f"### Comercial: **{row['Comercial']}**")
        mostrar_alerta(
            "Ticket Médio Comercial (€)",
            row["Ticket_Medio_Comercial"],
            thresholds["ticket_comercial"]
        )
        mostrar_alerta(
            "Ticket Médio Cliente (€)",
            row["Ticket_Medio_Cliente"],
            thresholds["ticket_cliente"]
        )
        mostrar_alerta(
            "Total de Vendas (€)",
            row["Total_Vendas"],
            thresholds["total_vendas"]
        )
        st.markdown("---")


# ====================== ALERTAS POR CLIENTE ======================
def alertas_por_cliente(df: pd.DataFrame, limite_min_venda: float = 0):
    st.subheader("Alertas por Cliente (Top 20 por Vendas)")

    if df.empty:
        st.warning("Sem dados para análise de clientes.")
        return

    thresholds = obter_thresholds_globais()

    grp = df.groupby("Nome").agg(
        Total_Vendas=("V Líquido", "sum"),
        Transacoes=("V Líquido", "count"),
        Quantidade=("Quantidade", "sum")
    ).reset_index()

    grp["Ticket_Medio_Cliente"] = grp["Total_Vendas"] / grp["Transacoes"]
    grp = grp.sort_values("Total_Vendas", ascending=False).head(20)

    for _, row in grp.iterrows():
        if row["Total_Vendas"] < limite_min_venda:
            continue

        st.markdown(f"### Cliente: **{row['Nome']}**")
        mostrar_alerta(
            "Total de Vendas (€)",
            row["Total_Vendas"],
            thresholds["total_vendas"]
        )
        mostrar_alerta(
            "Ticket Médio por Transação (€)",
            row["Ticket_Medio_Cliente"],
            thresholds["ticket_cliente"]
        )
        st.markdown("---")


# ====================== ALERTAS POR PRODUTO ======================
def alertas_por_produto(df: pd.DataFrame, limite_min_venda: float = 0):
    st.subheader("Alertas por Produto (Top 20 por Vendas)")

    if df.empty:
        st.warning("Sem dados para análise de produtos.")
        return

    thresholds = obter_thresholds_globais()

    grp = df.groupby("Artigo").agg(
        Total_Vendas=("V Líquido", "sum"),
        Quantidade=("Quantidade", "sum"),
        Transacoes=("V Líquido", "count")
    ).reset_index()

    grp["Ticket_Medio_Produto"] = grp["Total_Vendas"] / grp["Transacoes"]
    grp["Valor_Medio_Unidade"] = grp["Total_Vendas"] / grp["Quantidade"]
    grp = grp.sort_values("Total_Vendas", ascending=False).head(20)

    for _, row in grp.iterrows():
        if row["Total_Vendas"] < limite_min_venda:
            continue

        st.markdown(f"### Produto: **{row['Artigo']}**")
        mostrar_alerta(
            "Total de Vendas (€)",
            row["Total_Vendas"],
            thresholds["total_vendas"]
        )
        mostrar_alerta(
            "Ticket Médio por Transação (€)",
            row["Ticket_Medio_Produto"],
            thresholds["ticket_comercial"]
        )
        mostrar_alerta(
            "Valor Médio por Unidade (€)",
            row["Valor_Medio_Unidade"],
            thresholds["valor_unidade"]
        )
        st.markdown("---")


# ====================== GRÁFICO SEMÁFORO TICKET COMERCIAL ======================
def grafico_semaforo_ticket_comercial(df: pd.DataFrame):
    st.subheader("Semáforo Ticket Médio por Comercial")

    if df.empty:
        st.warning("Sem dados.")
        return

    thresholds = obter_thresholds_globais()

    grp = df.groupby("Comercial").agg(
        Total_Vendas=("V Líquido", "sum"),
        Transacoes=("V Líquido", "count")
    ).reset_index()

    grp["Ticket_Medio"] = grp["Total_Vendas"] / grp["Transacoes"]

    def classificar(valor):
        if valor >= thresholds["ticket_comercial"]:
            return "Acima"
        elif valor >= thresholds["ticket_comercial"] * 0.7:
            return "Atenção"
        else:
            return "Abaixo"

    grp["Status"] = grp["Ticket_Medio"].apply(classificar)

    color_map = {"Acima": "green", "Atenção": "orange", "Abaixo": "red"}
    colors = grp["Status"].map(color_map)

    fig = px.bar(
        grp,
        x="Comercial",
        y="Ticket_Medio",
        color="Status",
        color_discrete_map=color_map,
        title="Ticket Médio por Comercial (Semáforo)"
    )
    st.plotly_chart(fig, use_container_width=True)


# ====================== EXPORTAÇÃO COMPLETA PARA EXCEL ======================
def tabela_dados_export(df: pd.DataFrame, kpis: dict):
    st.subheader("Exportar Relatório Completo")

    if df.empty:
        st.warning("Sem dados para exportar.")
        return

    df_dados = df.copy()
    df_kpis = pd.DataFrame([kpis])

    df_hist = df.groupby("AnoMes").agg(
        Total_Vendas=("V Líquido", "sum"),
        Quantidade=("Quantidade", "sum"),
        Transacoes=("V Líquido", "count")
    ).reset_index()

    df_rank_com = df.groupby("Comercial").agg(
        Total_Vendas=("V Líquido", "sum"),
        Transacoes=("V Líquido", "count"),
        Quantidade=("Quantidade", "sum"),
        Clientes=("Nome", "nunique")
    ).reset_index()
    df_rank_com["Ticket_Medio"] = df_rank_com["Total_Vendas"] / df_rank_com["Transacoes"]
    df_rank_com = df_rank_com.sort_values("Total_Vendas", ascending=False)

    df_clientes = df.groupby("Nome").agg(
        Total_Vendas=("V Líquido", "sum"),
        Transacoes=("V Líquido", "count"),
        Quantidade=("Quantidade", "sum")
    ).reset_index()
    df_clientes["Ticket_Medio"] = df_clientes["Total_Vendas"] / df_clientes["Transacoes"]
    df_clientes = df_clientes.sort_values("Total_Vendas", ascending=False).head(10)

    df_produtos = df.groupby("Artigo").agg(
        Total_Vendas=("V Líquido", "sum"),
        Quantidade=("Quantidade", "sum"),
        Transacoes=("V Líquido", "count")
    ).reset_index()
    df_produtos["Ticket_Medio"] = df_produtos["Total_Vendas"] / df_produtos["Transacoes"]
    df_produtos["Valor_Medio_Unidade"] = df_produtos["Total_Vendas"] / df_produtos["Quantidade"]
    df_produtos = df_produtos.sort_values("Total_Vendas", ascending=False).head(10)

    thresholds = obter_thresholds_globais()
    df_alertas = pd.DataFrame([
        {"KPI": "Ticket Médio Comercial", "Valor": kpis["ticket"], "Limite": thresholds["ticket_comercial"]},
        {"KPI": "Ticket Médio Cliente", "Valor": kpis["ticket_cliente"], "Limite": thresholds["ticket_cliente"]},
        {"KPI": "Venda Média por Dia", "Valor": kpis["venda_dia"], "Limite": thresholds["venda_dia"]},
        {"KPI": "Valor Médio por Unidade", "Valor": kpis["valor_unidade"], "Limite": thresholds["valor_unidade"]},
        {"KPI": "Total de Vendas", "Valor": kpis["total_vendas"], "Limite": thresholds["total_vendas"]},
    ])

    buffer = io.BytesIO()
    wb = Workbook()

    def add_sheet(name, df_sheet):
        ws = wb.create_sheet(name)
        for col_num, col_name in enumerate(df_sheet.columns, 1):
            ws.cell(row=1, column=col_num, value=col_name)
        for row_num, row in enumerate(df_sheet.values, 2):
            for col_num, value in enumerate(row, 1):
                ws.cell(row=row_num, column=col_num, value=value)

    def add_plot_to_sheet(sheet_name, fig):
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
        img_buffer.seek(0)
        ws = wb[sheet_name]
        img = XLImage(img_buffer)
        img.anchor = "H2"
        ws.add_image(img)

    add_sheet("Dados", df_dados)
    add_sheet("KPIs_Globais", df_kpis)
    add_sheet("Historico_Mensal", df_hist)
    add_sheet("Ranking_Comerciais", df_rank_com)
    add_sheet("Clientes", df_clientes)
    add_sheet("Produtos", df_produtos)
    add_sheet("Alertas_Globais", df_alertas)

    # Gráfico evolução mensal
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(df_hist["AnoMes"], df_hist["Total_Vendas"], marker="o")
    ax1.set_title("Evolução Mensal de Vendas")
    ax1.set_xlabel("Ano-Mês")
    ax1.set_ylabel("Vendas (€)")
    plt.xticks(rotation=45)
    add_plot_to_sheet("Historico_Mensal", fig1)

    # Gráfico ranking comerciais
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(df_rank_com["Comercial"], df_rank_com["Total_Vendas"])
    ax2.set_title("Ranking de Comerciais")
    ax2.set_ylabel("Total de Vendas (€)")
    plt.xticks(rotation=45)
    add_plot_to_sheet("Ranking_Comerciais", fig2)

    # Gráfico top clientes
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.barh(df_clientes["Nome"], df_clientes["Total_Vendas"], color="steelblue")
    ax3.set_title("Top 10 Clientes por Vendas")
    ax3.set_xlabel("Total de Vendas (€)")
    ax3.invert_yaxis()
    plt.tight_layout()
    add_plot_to_sheet("Clientes", fig3)

    # Gráfico top produtos
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    ax4.barh(df_produtos["Artigo"], df_produtos["Total_Vendas"], color="purple")
    ax4.set_title("Top 10 Produtos por Vendas")
    ax4.set_xlabel("Total de Vendas (€)")
    ax4.invert_yaxis()
    plt.tight_layout()
    add_plot_to_sheet("Produtos", fig4)

    # Gráfico semáforo comerciais
    fig5, ax5 = plt.subplots(figsize=(8, 4))
    df_rank_com["Status"] = df_rank_com["Ticket_Medio"].apply(
        lambda x: "Acima" if x >= thresholds["ticket_comercial"]
        else "Atenção" if x >= thresholds["ticket_comercial"] * 0.7
        else "Abaixo"
    )
    color_map = {"Acima": "green", "Atenção": "orange", "Abaixo": "red"}
    colors = df_rank_com["Status"].map(color_map)
    ax5.bar(df_rank_com["Comercial"], df_rank_com["Ticket_Medio"], color=colors)
    ax5.set_title("Semáforo — Ticket Médio por Comercial")
    ax5.set_ylabel("Ticket Médio (€)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    add_plot_to_sheet("Ranking_Comerciais", fig5)

    # Exportação individual — comercial
    for comercial in df["Comercial"].unique():
        df_c = df[df["Comercial"] == comercial].copy()
        sheet_name = f"Com_{comercial[:25]}"
        add_sheet(sheet_name, df_c)

        df_c_hist = df_c.groupby("AnoMes")["V Líquido"].sum().reset_index()

        figC1, axC1 = plt.subplots(figsize=(8, 4))
        axC1.plot(df_c_hist["AnoMes"], df_c_hist["V Líquido"], marker="o")
        axC1.set_title(f"Evolução Mensal — {comercial}")
        axC1.set_xlabel("Ano-Mês")
        axC1.set_ylabel("Vendas (€)")
        plt.xticks(rotation=45)
        add_plot_to_sheet(sheet_name, figC1)

        figC2, axC2 = plt.subplots(figsize=(8, 4))
        axC2.bar(["Total"], [df_c["V Líquido"].sum()], color="blue")
        axC2.set_title(f"Total de Vendas — {comercial}")
        axC2.set_ylabel("Vendas (€)")
        add_plot_to_sheet(sheet_name, figC2)

        figC3, axC3 = plt.subplots(figsize=(8, 4))
        ticket_c = df_c["V Líquido"].sum() / len(df_c)
        axC3.bar(["Ticket Médio"], [ticket_c], color="green")
        axC3.set_title(f"Ticket Médio — {comercial}")
        axC3.set_ylabel("€")
        add_plot_to_sheet(sheet_name, figC3)

    # Exportação individual — cliente
    for cliente in df["Nome"].unique():
        df_cli = df[df["Nome"] == cliente].copy()
        sheet_name = f"Cli_{cliente[:25]}"
        add_sheet(sheet_name, df_cli)

        df_cli_hist = df_cli.groupby("AnoMes")["V Líquido"].sum().reset_index()

        figCl1, axCl1 = plt.subplots(figsize=(8, 4))
        axCl1.plot(df_cli_hist["AnoMes"], df_cli_hist["V Líquido"], marker="o")
        axCl1.set_title(f"Evolução Mensal — {cliente}")
        axCl1.set_xlabel("Ano-Mês")
        axCl1.set_ylabel("Vendas (€)")
        plt.xticks(rotation=45)
        add_plot_to_sheet(sheet_name, figCl1)

        figCl2, axCl2 = plt.subplots(figsize=(8, 4))
        axCl2.bar(["Total"], [df_cli["V Líquido"].sum()], color="purple")
        axCl2.set_title(f"Total de Vendas — {cliente}")
        axCl2.set_ylabel("Vendas (€)")
        add_plot_to_sheet(sheet_name, figCl2)

        figCl3, axCl3 = plt.subplots(figsize=(8, 4))
        ticket_cl = df_cli["V Líquido"].sum() / len(df_cli)
        axCl3.bar(["Ticket Médio"], [ticket_cl], color="orange")
        axCl3.set_title(f"Ticket Médio — {cliente}")
        axCl3.set_ylabel("€")
        add_plot_to_sheet(sheet_name, figCl3)

    # Exportação individual — produto
    for produto in df["Artigo"].unique():
        df_p = df[df["Artigo"] == produto].copy()
        sheet_name = f"Prod_{produto[:25]}"
        add_sheet(sheet_name, df_p)

        df_p_hist = df_p.groupby("AnoMes")["V Líquido"].sum().reset_index()

        figP1, axP1 = plt.subplots(figsize=(8, 4))
        axP1.plot(df_p_hist["AnoMes"], df_p_hist["V Líquido"], marker="o")
        axP1.set_title(f"Evolução Mensal — {produto}")
        axP1.set_xlabel("Ano-Mês")
        axP1.set_ylabel("Vendas (€)")
        plt.xticks(rotation=45)
        add_plot_to_sheet(sheet_name, figP1)

        figP2, axP2 = plt.subplots(figsize=(8, 4))
        axP2.bar(["Total"], [df_p["V Líquido"].sum()], color="red")
        axP2.set_title(f"Total de Vendas — {produto}")
        axP2.set_ylabel("Vendas (€)")
        add_plot_to_sheet(sheet_name, figP2)

        figP3, axP3 = plt.subplots(figsize=(8, 4))
        ticket_p = df_p["V Líquido"].sum() / len(df_p)
        axP3.bar(["Ticket Médio"], [ticket_p], color="teal")
        axP3.set_title(f"Ticket Médio — {produto}")
        axP3.set_ylabel("€")
        add_plot_to_sheet(sheet_name, figP3)

    wb.remove(wb["Sheet"])
    wb.save(buffer)

    st.download_button(
        "📥 Download Excel Completo (com gráficos)",
        data=buffer.getvalue(),
        file_name="Relatorio_Completo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# ====================== EXPORTAÇÃO AUTOMÁTICA MENSAL ======================
def gerar_excel_completo(df_mes: pd.DataFrame, kpis_mes: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    wb = Workbook()

    def add_sheet(name, df_sheet):
        ws = wb.create_sheet(name)
        for col_num, col_name in enumerate(df_sheet.columns, 1):
            ws.cell(row=1, column=col_num, value=col_name)
        for row_num, row in enumerate(df_sheet.values, 2):
            for col_num, value in enumerate(row, 1):
                ws.cell(row=row_num, column=col_num, value=value)

    def add_plot_to_sheet(sheet_name, fig):
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
        img_buffer.seek(0)
        ws = wb[sheet_name]
        img = XLImage(img_buffer)
        img.anchor = "H2"
        ws.add_image(img)

    add_sheet("Dados", df_mes)
    add_sheet("KPIs", pd.DataFrame([kpis_mes]))

    df_hist = df_mes.groupby("AnoMes")["V Líquido"].sum().reset_index()
    add_sheet("Historico", df_hist)

    df_rank = df_mes.groupby("Comercial").agg(
        Total_Vendas=("V Líquido", "sum"),
        Transacoes=("V Líquido", "count")
    ).reset_index()
    df_rank["Ticket_Medio"] = df_rank["Total_Vendas"] / df_rank["Transacoes"]
    add_sheet("Comerciais", df_rank)

    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(df_rank["Comercial"], df_rank["Total_Vendas"])
    ax1.set_title("Ranking Comerciais")
    plt.xticks(rotation=45)
    add_plot_to_sheet("Comerciais", fig1)

    for comercial in df_mes["Comercial"].unique():
        df_c = df_mes[df_mes["Comercial"] == comercial]
        add_sheet(f"Com_{comercial[:25]}", df_c)

    for cliente in df_mes["Nome"].unique():
        df_cli = df_mes[df_mes["Nome"] == cliente]
        add_sheet(f"Cli_{cliente[:25]}", df_cli)

    for produto in df_mes["Artigo"].unique():
        df_p = df_mes[df_mes["Artigo"] == produto]
        add_sheet(f"Prod_{produto[:25]}", df_p)

    wb.remove(wb["Sheet"])
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def exportacao_mensal(df: pd.DataFrame):
    st.subheader("📦 Exportação Automática Mensal")

    if df.empty:
        st.warning("Sem dados para exportação mensal.")
        return

    meses = sorted(df["AnoMes"].unique())

    if st.button("Gerar Relatórios Mensais"):
        for mes in meses:
            df_mes = df[df["AnoMes"] == mes].copy()
            kpis_mes = calcular_kpis(df_mes)
            buffer = gerar_excel_completo(df_mes, kpis_mes)

            st.download_button(
                label=f"📥 Download Relatório {mes}",
                data=buffer.getvalue(),
                file_name=f"Relatorio_{mes}.xlsx",
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

    resumo["Total_Vendas"] = resumo["Total_Vendas"].map(lambda x: f"{x:,.2f}")
    resumo["Ticket_Medio"] = resumo["Ticket_Medio"].map(lambda x: f"{x:,.2f}")
    resumo["Valor_Medio_Unidade"] = resumo["Valor_Medio_Unidade"].map(lambda x: f"{x:,.4f}")

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

    tab1, tab2, tab3 = st.tabs(["📊 KPIs", "📈 Gráficos & Alertas", "📄 Tabelas & Export"])

    with tab1:
        desenhar_kpis(kpis, df_ticket_com)
        alertas_por_comercial(df_filt)
        alertas_por_cliente(df_filt, limite_min_venda=1000)

    with tab2:
        grafico_evolucao(df_filt)
        graficos_top10(df_filt)
        grafico_semaforo_ticket_comercial(df_filt)
        alertas_por_produto(df_filt, limite_min_venda=1000)

    with tab3:
        tabela_dados_export(df_filt, kpis)
        exportacao_mensal(df_filt)

    st.markdown("---")
    st.markdown("Desenvolvido por Paulo — Dashboard Comercial ✅")


if __name__ == "__main__":
    main()
