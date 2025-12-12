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
            st.plotly_chart(figp, use_container_width=True)

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
            st.plotly_chart(figc, use_container_width=True)

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
            st.plotly_chart(figpq, use_container_width=True)

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
            st.plotly_chart(figcq, use_container_width=True)
# ====================== COMPARAÇÃO ANO-A-ANO (GLOBAL) ======================
def comparacao_ano_a_ano(df: pd.DataFrame):
    st.subheader("📆 Comparação Ano-a-Ano — Global")

    if df.empty:
        st.warning("Sem dados para comparar.")
        return

    df = df.copy()
    df["Mes_Num"] = df["Data"].dt.month
    df["Ano"] = df["Data"].dt.year

    # Filtro de mês
    meses_disponiveis = sorted(df["Mes_Num"].unique())
    if not meses_disponiveis:
        st.warning("Sem meses disponíveis para comparação.")
        return

    mes_sel = st.selectbox(
        "Seleciona o mês para comparar entre anos (Global):",
        options=meses_disponiveis,
        format_func=lambda m: datetime(2000, m, 1).strftime("%B"),
        key="mes_ano_ano_global_selectbox_unico"
    )

    df_mes = df[df["Mes_Num"] == mes_sel]

    if df_mes.empty:
        st.warning("Sem dados para este mês.")
        return

    # Agrupamento
    df_comp = df_mes.groupby("Ano").agg(
        Total_Vendas=("V Líquido", "sum"),
        Quantidade=("Quantidade", "sum"),
        Transacoes=("V Líquido", "count"),
        Clientes=("Nome", "nunique")
    ).reset_index()

    if df_comp.empty:
        st.warning("Sem dados agregados para este mês.")
        return

    # Gráfico
    fig = px.bar(
        df_comp,
        x="Ano",
        y="Total_Vendas",
        text="Total_Vendas",
        title=f"Vendas no mês de {datetime(2000, mes_sel, 1).strftime('%B')} — Comparação Ano-a-Ano (Global)",
        color="Total_Vendas",
        color_continuous_scale="Blues"
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

    # Tabela
    st.subheader("Tabela Ano-a-Ano — Global")
    df_show = df_comp.copy()
    df_show["Total_Vendas"] = df_show["Total_Vendas"].map(lambda x: f"{x:,.2f}")
    df_show["Quantidade"] = df_show["Quantidade"].map(lambda x: f"{x:,.2f}")
    st.dataframe(df_show, use_container_width=True)


# ====================== COMPARAÇÃO ANO-A-ANO POR CLIENTE ======================
def comparacao_ano_a_ano_clientes(df: pd.DataFrame):
    st.subheader("👥 Comparação Ano-a-Ano — Clientes")

    if df.empty:
        st.warning("Sem dados para comparar.")
        return

    df = df.copy()
    df["Mes_Num"] = df["Data"].dt.month
    df["Ano"] = df["Data"].dt.year

    # Filtro de cliente
    clientes = sorted(df["Nome"].dropna().unique())
    if not clientes:
        st.warning("Sem clientes disponíveis para análise.")
        return

    cliente_sel = st.selectbox(
        "Seleciona o cliente a analisar:",
        options=clientes,
        key="cliente_ano_ano_selectbox_unico"
    )

    df = df[df["Nome"] == cliente_sel]

    if df.empty:
        st.warning("Sem dados para este cliente.")
        return

    # Filtro de mês
    meses_disponiveis = sorted(df["Mes_Num"].unique())
    if not meses_disponiveis:
        st.warning("Sem meses disponíveis para este cliente.")
        return

    mes_sel = st.selectbox(
        "Seleciona o mês para comparar entre anos (Clientes):",
        options=meses_disponiveis,
        format_func=lambda m: datetime(2000, m, 1).strftime("%B"),
        key="mes_ano_ano_cliente_selectbox_unico"
    )

    df_mes = df[df["Mes_Num"] == mes_sel]

    if df_mes.empty:
        st.warning("Sem dados para este mês.")
        return

    # Agrupamento
    df_comp = df_mes.groupby("Ano").agg(
        Total_Vendas=("V Líquido", "sum"),
        Quantidade=("Quantidade", "sum"),
        Transacoes=("V Líquido", "count")
    ).reset_index()

    if df_comp.empty:
        st.warning("Sem dados agregados para este cliente e mês.")
        return

    # Gráfico
    fig = px.bar(
        df_comp,
        x="Ano",
        y="Total_Vendas",
        text="Total_Vendas",
        title=f"{cliente_sel} — Vendas no mês de {datetime(2000, mes_sel, 1).strftime('%B')} (Ano-a-Ano)",
        color="Total_Vendas",
        color_continuous_scale="Blues"
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

    # Tabela
    st.subheader(f"Tabela Ano-a-Ano — {cliente_sel}")
    df_show = df_comp.copy()
    df_show["Total_Vendas"] = df_show["Total_Vendas"].map(lambda x: f"{x:,.2f}")
    df_show["Quantidade"] = df_show["Quantidade"].map(lambda x: f"{x:,.2f}")
    st.dataframe(df_show, use_container_width=True)
# ====================== AUXILIARES PARA EXPORTAÇÃO EXCEL ======================

def sanitize_sheet_name(name: str, existing_names: set) -> str:
    """
    Garante que o nome da folha é válido no Excel e único.
    """
    invalid_chars = ['\\', '/', '*', '?', ':', '[', ']']
    for ch in invalid_chars:
        name = name.replace(ch, '')

    name = name.strip()
    if len(name) > 31:
        name = name[:31]

    base = name
    counter = 1
    while name in existing_names:
        suffix = f"_{counter}"
        name = base[:31 - len(suffix)] + suffix
        counter += 1

    existing_names.add(name)
    return name


def criar_sheet(wb, name: str, existing_names: set):
    """
    Cria uma folha com nome validado e único.
    """
    name_real = sanitize_sheet_name(name, existing_names)
    ws = wb.create_sheet(title=name_real)
    return ws
# ====================== EXPORTAÇÃO EXCEL — RELATÓRIO COMPLETO ======================
def tabela_dados_export(df: pd.DataFrame, kpis: dict):
    st.subheader("📄 Exportação — Relatório Completo")

    if df.empty:
        st.warning("Sem dados para exportar.")
        return

    # Criar workbook
    wb = Workbook()
    ws0 = wb.active
    ws0.title = "Resumo"
    existing_names = {ws0.title}

    # ====================== Função interna para adicionar gráficos ======================
    def add_plot_to_sheet(sheet_name, fig, anchor="H2"):
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
        img_buffer.seek(0)

        ws = wb[sheet_name]
        img = XLImage(img_buffer)
        img.anchor = anchor
        ws.add_image(img)

    # ====================== Folha Resumo ======================
    ws0["A1"] = "Resumo Geral"
    ws0["A3"] = "Total Vendas (€)"
    ws0["B3"] = kpis["total_vendas"]
    ws0["A4"] = "Quantidade Total"
    ws0["B4"] = kpis["qtd"]
    ws0["A5"] = "Clientes Únicos"
    ws0["B5"] = kpis["clientes"]
    ws0["A6"] = "Produtos Vendidos"
    ws0["B6"] = kpis["produtos"]
    ws0["A7"] = "Transações"
    ws0["B7"] = kpis["trans"]
    ws0["A8"] = "Ticket Médio Comercial (€)"
    ws0["B8"] = kpis["ticket"]
    ws0["A9"] = "Ticket Médio Cliente (€)"
    ws0["B9"] = kpis["ticket_cliente"]
    ws0["A10"] = "Venda Média por Dia (€)"
    ws0["B10"] = kpis["venda_dia"]
    ws0["A11"] = "Valor Médio por Unidade (€)"
    ws0["B11"] = kpis["valor_unidade"]

    # ====================== Folha Dados ======================
    ws_dados = criar_sheet(wb, "Dados", existing_names)
    for col_num, col_name in enumerate(df.columns, 1):
        ws_dados.cell(row=1, column=col_num, value=col_name)

    for row_num, row in enumerate(df.itertuples(index=False), 2):
        for col_num, value in enumerate(row, 1):
            ws_dados.cell(row=row_num, column=col_num, value=value)

    # ====================== Folha Evolução Mensal ======================
    ws_hist = criar_sheet(wb, "Historico_Mensal", existing_names)

    mensal = df.groupby("AnoMes")["V Líquido"].sum().reset_index()
    fig = px.line(mensal, x="AnoMes", y="V Líquido", markers=True)
    fig.add_bar(x=mensal["AnoMes"], y=mensal["V Líquido"])
    fig.update_layout(height=500)

    add_plot_to_sheet("Historico_Mensal", fig)

    # ====================== Folha Ranking Comerciais ======================
    ws_rank = criar_sheet(wb, "Ranking_Comerciais", existing_names)

    rank = df.groupby("Comercial")["V Líquido"].sum().sort_values(ascending=False)
    fig = px.bar(
        x=rank.values, y=rank.index, orientation="h",
        color=rank.values, color_continuous_scale="Blues"
    )
    fig.update_layout(height=500)

    add_plot_to_sheet("Ranking_Comerciais", fig)

    # ====================== Folha Produtos ======================
    ws_prod = criar_sheet(wb, "Produtos", existing_names)

    top_prod = df.groupby("Artigo")["V Líquido"].sum().nlargest(10)
    fig = px.bar(
        x=top_prod.values, y=top_prod.index, orientation="h",
        color=top_prod.values, color_continuous_scale="Plasma"
    )
    fig.update_layout(height=500)

    add_plot_to_sheet("Produtos", fig)

    # ====================== Folha Clientes ======================
    ws_cli = criar_sheet(wb, "Clientes", existing_names)

    top_cli = df.groupby("Nome")["V Líquido"].sum().nlargest(10)
    fig = px.bar(
        x=top_cli.values, y=top_cli.index, orientation="h",
        color=top_cli.values, color_continuous_scale="Viridis"
    )
    fig.update_layout(height=500)

    add_plot_to_sheet("Clientes", fig)

    # ====================== Exportação ======================
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    st.download_button(
        label="📥 Download Relatório Completo (Excel)",
        data=buffer,
        file_name="Relatorio_Completo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# ====================== EXPORTAÇÃO EXCEL — RELATÓRIOS MENSAIS ======================
def gerar_excel_completo(df: pd.DataFrame):
    st.subheader("📄 Exportação — Relatórios Mensais")

    if df.empty:
        st.warning("Sem dados para exportar.")
        return

    meses = sorted(df["AnoMes"].unique())
    mes_sel = st.selectbox("Seleciona o mês para exportar:", meses)

    df_mes = df[df["AnoMes"] == mes_sel]
    if df_mes.empty:
        st.warning("Sem dados para este mês.")
        return

    wb = Workbook()
    ws0 = wb.active
    ws0.title = "Resumo"
    existing_names = {ws0.title}

    # ====================== Função interna para adicionar gráficos ======================
    def add_plot_to_sheet(sheet_name, fig, anchor="H2"):
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
        img_buffer.seek(0)

        ws = wb[sheet_name]
        img = XLImage(img_buffer)
        img.anchor = anchor
        ws.add_image(img)

    # ====================== Resumo ======================
    ws0["A1"] = f"Resumo — {mes_sel}"
    ws0["A3"] = "Total Vendas (€)"
    ws0["B3"] = df_mes["V Líquido"].sum()
    ws0["A4"] = "Quantidade Total"
    ws0["B4"] = df_mes["Quantidade"].sum()
    ws0["A5"] = "Clientes Únicos"
    ws0["B5"] = df_mes["Nome"].nunique()
    ws0["A6"] = "Produtos Vendidos"
    ws0["B6"] = df_mes["Artigo"].nunique()

    # ====================== Dados ======================
    ws_dados = criar_sheet(wb, "Dados", existing_names)
    for col_num, col_name in enumerate(df_mes.columns, 1):
        ws_dados.cell(row=1, column=col_num, value=col_name)

    for row_num, row in enumerate(df_mes.itertuples(index=False), 2):
        for col_num, value in enumerate(row, 1):
            ws_dados.cell(row=row_num, column=col_num, value=value)

    # ====================== Gráfico Mensal ======================
    ws_hist = criar_sheet(wb, "Historico", existing_names)

    diario = df_mes.groupby(df_mes["Data"].dt.strftime("%d"))["V Líquido"].sum().reset_index()
    fig = px.line(diario, x="Data", y="V Líquido", markers=True)
    fig.update_layout(height=500)

    add_plot_to_sheet("Historico", fig)

    # ====================== Exportação ======================
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    st.download_button(
        label=f"📥 Download Relatório {mes_sel}",
        data=buffer,
        file_name=f"Relatorio_{mes_sel}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# ====================== TABELAS & EXPORT ======================
def tabelas_export_interface(df: pd.DataFrame, kpis: dict):
    st.subheader("📄 Tabelas & Export")

    st.markdown("### 📥 Exportação Completa")
    tabela_dados_export(df, kpis)

    st.markdown("---")
    st.markdown("### 📥 Exportação Mensal")
    gerar_excel_completo(df)


# ====================== ABA PRINCIPAL — COMPARAÇÃO ANO-A-ANO ======================
def aba_comparacao_ano_ano(df: pd.DataFrame):
    st.header("📆 Comparação Ano-a-Ano")

    tab1, tab2 = st.tabs([
        "📆 Global",
        "👥 Clientes"
    ])

    with tab1:
        comparacao_ano_a_ano(df)

    with tab2:
        comparacao_ano_a_ano_clientes(df)
# ====================== ABA PRINCIPAL — DASHBOARD COMPLETO ======================
def aba_dashboard(df: pd.DataFrame):
    st.header("📊 Dashboard Geral")

    if df.empty:
        st.warning("Sem dados para apresentar.")
        return

    # ====================== KPIs ======================
    kpis = calcular_kpis(df)
    df_ticket_com = calcular_ticket_medio_por_comercial(df)

    desenhar_kpis(kpis, df_ticket_com)

    st.divider()

    # ====================== Evolução Mensal ======================
    grafico_evolucao(df)

    st.divider()

    # ====================== Top 10 ======================
    graficos_top10(df)

    st.divider()

    # ====================== Tabelas & Export ======================
    tabelas_export_interface(df, kpis)
# ====================== MAIN APP ======================
def main():
    st.sidebar.title("📁 Carregar Dados")

    uploaded_file = st.sidebar.file_uploader(
        "Seleciona o ficheiro Excel",
        type=["xlsx"]
    )

    if uploaded_file:
        df = load_data(uploaded_file)
    else:
        st.info("A usar o ficheiro padrão: ResumoTR.xlsx")
        df = load_data()

    if df.empty:
        st.error("Não foi possível carregar dados válidos.")
        return

    # Aplicar filtros
    df_filt = aplicar_filtros(df)

    # Tabs principais
    tab_dashboard, tab_ano = st.tabs([
        "📊 Dashboard Geral",
        "📆 Comparação Ano-a-Ano"
    ])

    with tab_dashboard:
        aba_dashboard(df_filt)

    with tab_ano:
        aba_comparacao_ano_ano(df_filt)


# Execução
if __name__ == "__main__":
    main()
