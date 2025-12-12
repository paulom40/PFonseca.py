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
def load_data(path_or_file="ResumoTR.xlsx") -> pd.DataFrame:
    try:
        df = pd.read_excel(path_or_file)
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

    mask_data = (df["Data"].dt.date >= data_inicio) & (df["Data"].dt.date <= data_fim)
    df_filt = df[mask_data].copy()

    # Filtro Comercial
    comerciais = sorted(df_filt["Comercial"].dropna().unique())
    sel_com = st.sidebar.multiselect("Comercial", options=comerciais, default=comerciais)
    if sel_com:
        df_filt = df_filt[df_filt["Comercial"].isin(sel_com)]

    # Filtro Artigo
    artigos = sorted(df_filt["Artigo"].dropna().unique())
    sel_art = st.sidebar.multiselect("Artigo", options=artigos, default=artigos)
    if sel_art:
        df_filt = df_filt[df_filt["Artigo"].isin(sel_art)]

    # Filtro Nome entidade
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
# ====================== VISUALIZAÇÕES PRINCIPAIS ======================
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
        st.dataframe(df_show, width="stretch")

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

    st.plotly_chart(fig, width="stretch")


def graficos_top10(df: pd.DataFrame):
    col1, col2 = st.columns(2)

    # Top 10 Produtos (€)
    with col1:
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
            st.plotly_chart(figp, width="stretch")

    # Top 10 Clientes (€)
    with col2:
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
            st.plotly_chart(figc, width="stretch")

    st.divider()

    col3, col4 = st.columns(2)

    # Top 10 Produtos (Quantidade)
    with col3:
        st.subheader("Top 10 Produtos (Quantidade)")
        if df.empty:
            st.warning("Sem dados.")
        else:
            topp_q = df.groupby("Artigo")["Quantidade"].sum().nlargest(10)
            figpq = px.bar(
                x=topp_q.values, y=topp_q.index, orientation="h",
                color=topp_q.values, color_continuous_scale="Blues"
            )
            figpq.update_layout(height=500)
            st.plotly_chart(figpq, width="stretch")

    # Top 10 Clientes (Quantidade)
    with col4:
        st.subheader("Top 10 Clientes (Quantidade)")
        if df.empty:
            st.warning("Sem dados.")
        else:
            topc_q = df.groupby("Nome")["Quantidade"].sum().nlargest(10)
            figcq = px.bar(
                x=topc_q.values, y=topc_q.index, orientation="h",
                color=topc_q.values, color_continuous_scale="Greens"
            )
            figcq.update_layout(height=500)
            st.plotly_chart(figcq, width="stretch")
# ====================== COMPARAÇÃO ANO-A-ANO (DASHBOARD) ======================
def comparacao_ano_a_ano(df: pd.DataFrame):
    st.subheader("📆 Comparação do Mesmo Mês em Diferentes Anos")

    if df.empty:
        st.warning("Sem dados para comparar.")
        return

    df = df.copy()
    df["Mes_Num"] = df["Data"].dt.month
    df["Ano"] = df["Data"].dt.year

    meses_disponiveis = sorted(df["Mes_Num"].unique())

    mes_sel = st.selectbox(
        "Seleciona o mês para comparar entre anos:",
        options=meses_disponiveis,
        format_func=lambda m: datetime(2000, m, 1).strftime("%B")
    )

    df_mes = df[df["Mes_Num"] == mes_sel]

    if df_mes.empty:
        st.warning("Sem dados para este mês.")
        return

    df_comp = df_mes.groupby("Ano").agg(
        Total_Vendas=("V Líquido", "sum"),
        Quantidade=("Quantidade", "sum"),
        Transacoes=("V Líquido", "count"),
        Clientes=("Nome", "nunique")
    ).reset_index()

    fig = px.bar(
        df_comp,
        x="Ano",
        y="Total_Vendas",
        text="Total_Vendas",
        title=f"Vendas do mês de {datetime(2000, mes_sel, 1).strftime('%B')} — Comparação Ano-a-Ano",
        color="Total_Vendas",
        color_continuous_scale="Blues"
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(height=500)

    st.plotly_chart(fig, width="stretch")

    st.subheader("Resumo Ano-a-Ano")
    df_show = df_comp.copy()
    df_show["Total_Vendas"] = df_show["Total_Vendas"].map(lambda x: f"{x:,.2f}")
    df_show["Quantidade"] = df_show["Quantidade"].map(lambda x: f"{x:,.2f}")
    st.dataframe(df_show, width="stretch")
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

    fig = px.bar(
        grp,
        x="Comercial",
        y="Ticket_Medio",
        color="Status",
        color_discrete_map=color_map,
        title="Ticket Médio por Comercial (Semáforo)"
    )
    st.plotly_chart(fig, width="stretch")


# ====================== SANITIZAR NOMES DE FOLHAS EXCEL ======================
def sanitize_sheet_name(name: str, existing_names: set) -> str:
    invalid = [":", "\\", "/", "?", "*", "[", "]"]
    for ch in invalid:
        name = name.replace(ch, "")
    name = name.replace(" ", "_")
    name = name[:31]
    if not name.strip():
        name = "Sheet"
    base = name
    counter = 1
    while name in existing_names:
        suffix = f"_{counter}"
        name = base[:31 - len(suffix)] + suffix
        counter += 1
    existing_names.add(name)
    return name
# ====================== EXPORTAÇÃO COMPLETA OTIMIZADA PARA EXCEL ======================
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

    # ========== COMPARAÇÃO ANO-A-ANO PARA EXPORT ==========
    df_comp_aa = None
    mes_sel_export = None
    if not df.empty:
        df_tmp = df.copy()
        df_tmp["Mes_Num"] = df_tmp["Data"].dt.month
        df_tmp["Ano"] = df_tmp["Data"].dt.year

        meses_disponiveis = sorted(df_tmp["Mes_Num"].unique())
        if len(meses_disponiveis) > 0:
            mes_sel_export = meses_disponiveis[-1]  # último mês disponível
            df_mes = df_tmp[df_tmp["Mes_Num"] == mes_sel_export]
            if not df_mes.empty:
                df_comp_aa = df_mes.groupby("Ano").agg(
                    Total_Vendas=("V Líquido", "sum"),
                    Quantidade=("Quantidade", "sum"),
                    Transacoes=("V Líquido", "count"),
                    Clientes=("Nome", "nunique")
                ).reset_index()

    buffer = io.BytesIO()
    wb = Workbook()
    existing_sheet_names = set()

    def add_sheet(name, df_sheet):
        nonlocal existing_sheet_names
        name_real = sanitize_sheet_name(name, existing_sheet_names)
        ws = wb.create_sheet(name_real)
        for col_num, col_name in enumerate(df_sheet.columns, 1):
            ws.cell(row=1, column=col_num, value=col_name)
        for row_num, row in enumerate(df_sheet.values, 2):
            for col_num, value in enumerate(row, 1):
                ws.cell(row=row_num, column=col_num, value=value)
        return name_real
    def add_plot_to_sheet(sheet_name, fig, anchor="H2"):
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
        img_buffer.seek(0)
        ws = wb[sheet_name]
        img = XLImage(img_buffer)
        img.anchor = anchor
        ws.add_image(img)

    # Criar folhas na ordem pedida
    nome_dados   = add_sheet("Dados", df_dados)
    nome_kpis    = add_sheet("KPIs_Globais", df_kpis)
    nome_hist    = add_sheet("Historico_Mensal", df_hist)
    nome_rank    = add_sheet("Ranking_Comerciais", df_rank_com)
    nome_cli     = add_sheet("Clientes", df_clientes)
    nome_prod    = add_sheet("Produtos", df_produtos)
    nome_alertas = add_sheet("Alertas_Globais", df_alertas)

    nome_comp_aa = None
    if df_comp_aa is not None and not df_comp_aa.empty:
        nome_comp_aa = add_sheet("Comparacao_Ano_a_Ano", df_comp_aa)

    # Evolução mensal
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(df_hist["AnoMes"], df_hist["Total_Vendas"], marker="o")
    ax1.set_title("Evolução Mensal de Vendas")
    ax1.set_xlabel("Ano-Mês")
    ax1.set_ylabel("Vendas (€)")
    plt.xticks(rotation=45)
    add_plot_to_sheet(nome_hist, fig1, anchor="H2")

    # Ranking comerciais
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(df_rank_com["Comercial"], df_rank_com["Total_Vendas"])
    ax2.set_title("Ranking de Comerciais")
    ax2.set_ylabel("Total de Vendas (€)")
    plt.xticks(rotation=45)
    add_plot_to_sheet(nome_rank, fig2, anchor="H2")

    # Semáforo comerciais
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
    add_plot_to_sheet(nome_rank, fig5, anchor="H20")

    # Top produtos (€)
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.barh(df_produtos["Artigo"], df_produtos["Total_Vendas"], color="purple")
    ax3.set_title("Top 10 Produtos por Vendas (€)")
    ax3.set_xlabel("Total de Vendas (€)")
    ax3.invert_yaxis()
    plt.tight_layout()
    add_plot_to_sheet(nome_prod, fig3, anchor="H2")

    # Top produtos (Quantidade)
    fig6, ax6 = plt.subplots(figsize=(8, 4))
    topp_q = df.groupby("Artigo")["Quantidade"].sum().nlargest(10)
    ax6.barh(topp_q.index, topp_q.values, color="dodgerblue")
    ax6.set_title("Top 10 Produtos (Quantidade)")
    ax6.set_xlabel("Quantidade Total")
    ax6.invert_yaxis()
    plt.tight_layout()
    add_plot_to_sheet(nome_prod, fig6, anchor="H20")

    # Top clientes (€)
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    ax4.barh(df_clientes["Nome"], df_clientes["Total_Vendas"], color="steelblue")
    ax4.set_title("Top 10 Clientes por Vendas (€)")
    ax4.set_xlabel("Total de Vendas (€)")
    ax4.invert_yaxis()
    plt.tight_layout()
    add_plot_to_sheet(nome_cli, fig4, anchor="H2")

    # Top clientes (Quantidade)
    fig7, ax7 = plt.subplots(figsize=(8, 4))
    topc_q = df.groupby("Nome")["Quantidade"].sum().nlargest(10)
    ax7.barh(topc_q.index, topc_q.values, color="seagreen")
    ax7.set_title("Top 10 Clientes (Quantidade)")
    ax7.set_xlabel("Quantidade Total")
    ax7.invert_yaxis()
    plt.tight_layout()
    add_plot_to_sheet(nome_cli, fig7, anchor="H20")

    # Comparação Ano-a-Ano (se existir)
    if nome_comp_aa is not None and df_comp_aa is not None and not df_comp_aa.empty:
        fig8, ax8 = plt.subplots(figsize=(8, 4))
        ax8.bar(df_comp_aa["Ano"], df_comp_aa["Total_Vendas"], color="navy")
        if mes_sel_export is not None:
            nome_mes = datetime(2000, mes_sel_export, 1).strftime("%B")
            ax8.set_title(f"Comparação Ano-a-Ano — Mês de {nome_mes}")
        else:
            ax8.set_title("Comparação Ano-a-Ano")
        ax8.set_ylabel("Total de Vendas (€)")
        plt.xticks(rotation=0)
        plt.tight_layout()
        add_plot_to_sheet(nome_comp_aa, fig8, anchor="H2")

    if "Sheet" in wb.sheetnames and len(wb.sheetnames) > 1:
        std = wb["Sheet"]
        wb.remove(std)

    wb.save(buffer)
    buffer.seek(0)

    st.download_button(
        "📥 Download Excel Completo (com gráficos)",
        data=buffer.getvalue(),
        file_name="Relatorio_Completo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# ====================== EXPORTAÇÃO AUTOMÁTICA MENSAL (OTIMIZADA) ======================
def gerar_excel_completo(df_mes: pd.DataFrame, kpis_mes: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    wb = Workbook()
    existing_sheet_names = set()

    def add_sheet(name, df_sheet):
        nonlocal existing_sheet_names
        name_real = sanitize_sheet_name(name, existing_sheet_names)
        ws = wb.create_sheet(name_real)
        for col_num, col_name in enumerate(df_sheet.columns, 1):
            ws.cell(row=1, column=col_num, value=col_name)
        for row_num, row in enumerate(df_sheet.values, 2):
            for col_num, value in enumerate(row, 1):
                ws.cell(row=row_num, column=col_num, value=value)
        return name_real

    def add_plot_to_sheet(sheet_name, fig, anchor="H2"):
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
        img_buffer.seek(0)
        ws = wb[sheet_name]
        img = XLImage(img_buffer)
        img.anchor = anchor
        ws.add_image(img)

    nome_dados = add_sheet("Dados", df_mes)
    nome_kpis = add_sheet("KPIs", pd.DataFrame([kpis_mes]))

    df_hist = df_mes.groupby("AnoMes")["V Líquido"].sum().reset_index()
    nome_hist = add_sheet("Historico", df_hist)

    df_rank = df_mes.groupby("Comercial").agg(
        Total_Vendas=("V Líquido", "sum"),
        Transacoes=("V Líquido", "count")
    ).reset_index()
    df_rank["Ticket_Medio"] = df_rank["Total_Vendas"] / df_rank["Transacoes"]
    nome_rank = add_sheet("Comerciais", df_rank)

    # Gráfico ranking comerciais
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(df_rank["Comercial"], df_rank["Total_Vendas"])
    ax1.set_title("Ranking Comerciais")
    plt.xticks(rotation=45)
    add_plot_to_sheet(nome_rank, fig1, anchor="H2")

    # Gráfico vendas do mês
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(df_hist["AnoMes"], df_hist["V Líquido"])
    ax2.set_title("Vendas do Mês")
    plt.xticks(rotation=45)
    add_plot_to_sheet(nome_hist, fig2, anchor="H2")

    if "Sheet" in wb.sheetnames and len(wb.sheetnames) > 1:
        std = wb["Sheet"]
        wb.remove(std)

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

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 KPIs",
        "📈 Gráficos & Alertas",
        "📄 Tabelas & Export",
        "📆 Comparação Ano-a-Ano"
    ])

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

    with tab4:
        comparacao_ano_a_ano(df_filt)

    st.markdown("---")
    st.markdown("Desenvolvido por Paulo — Dashboard Comercial ✅")


if __name__ == "__main__":
    main()
