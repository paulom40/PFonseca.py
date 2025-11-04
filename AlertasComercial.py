# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Vendas", layout="wide")
st.title("Dashboard de Vendas - Comparativo Anual")

# === CARREGAR DADOS ===
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Vendas_Globais.xlsx", sheet_name="Sheet1")
    except:
        st.error("Arquivo 'Vendas_Globais.xlsx' não encontrado.")
        st.stop()

    df.columns = ["Código", "Cliente", "Qtd.", "UN", "PM", "V. Líquido", "Artigo", "Comercial", "Categoria", "Mês", "Ano"]
    df = df.dropna(subset=["Cliente", "Comercial", "Artigo", "Mês", "Ano"])

    # Normalizar mês (case-insensitive)
    df["Mês"] = df["Mês"].astype(str).str.strip().str.lower()
    meses_map = {m.lower(): i for i, m in enumerate([
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ], 1)}
    df["Mês_Num"] = df["Mês"].map(meses_map)

    if df["Mês_Num"].isna().any():
        invalid = df[df["Mês_Num"].isna()]["Mês"].unique()
        st.error(f"Meses inválidos: {', '.join(invalid)}. Corrija no Excel.")
        st.stop()

    df["Ano"] = pd.to_numeric(df["Ano"], errors='coerce').fillna(0).astype(int)
    df = df[df["Ano"].between(2000, 2100)]
    df["Data"] = pd.to_datetime(df[["Ano", "Mês_Num"]].assign(day=1))
    df["V. Líquido"] = pd.to_numeric(df["V. Líquido"], errors='coerce').fillna(0)
    df["Qtd."] = pd.to_numeric(df["Qtd."], errors='coerce').fillna(0)

    return df

df = load_data()

# === FILTROS ===
st.sidebar.header("Filtros")
anos = sorted(df["Ano"].unique())
ano_sel = st.sidebar.multiselect("Ano", anos, default=anos[-2:] if len(anos) >= 2 else anos)
df = df[df["Ano"].isin(ano_sel)]

meses = sorted(df["Mês"].str.capitalize().unique())
mes_sel = st.sidebar.multiselect("Mês", meses, default=meses)
df = df[df["Mês"].str.capitalize().isin(mes_sel)]

comerciais = st.sidebar.multiselect("Comercial", sorted(df["Comercial"].unique()), default=[])
if comerciais:
    df = df[df["Comercial"].isin(comerciais)]

clientes = st.sidebar.multiselect("Cliente", sorted(df["Cliente"].unique()), default=df["Cliente"].unique()[:10])
if clientes:
    df = df[df["Cliente"].isin(clientes)]

# === ANO ATUAL E ANTERIOR ===
ano_atual = df["Ano"].max()
ano_anterior = ano_atual - 1
df_atual = df[df["Ano"] == ano_atual]
df_ant = df[df["Ano"] == ano_anterior] if ano_anterior in df["Ano"].values else pd.DataFrame()

# === KPIs ===
v_atual = df_atual["V. Líquido"].sum()
v_ant = df_ant["V. Líquido"].sum()
c_atual = df_atual["Cliente"].nunique()
c_ant = df_ant["Cliente"].nunique()

var_v = (v_atual - v_ant) / v_ant * 100 if v_ant > 0 else 0
var_c = (c_atual - c_ant) / c_ant * 100 if c_ant > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Vendas Totais", f"€{v_atual:,.0f}", f"{var_v:+.1f}%" if v_ant > 0 else None)
col2.metric("Clientes Únicos", c_atual, f"{var_c:+.1f}%" if c_ant > 0 else None)
col3.metric("Artigos Vendidos", df_atual["Artigo"].nunique())
col4.metric("Média por Cliente", f"€{v_atual/c_atual:,.0f}" if c_atual > 0 else "€0")

# === GRÁFICO EVOLUÇÃO ===
st.subheader(f"Vendas Mensais: {ano_atual} vs {ano_anterior}")

fig = go.Figure()

if not df_atual.empty:
    mensal = df_atual.groupby("Mês_Num")["V. Líquido"].sum().reindex(range(1,13), fill_value=0)
    meses_ordem = [m.capitalize() for m in [
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ]]
    fig.add_trace(go.Scatter(x=meses_ordem, y=mensal, mode='lines+markers', name=str(ano_atual), line=dict(width=3)))

if not df_ant.empty:
    mensal_ant = df_ant.groupby("Mês_Num")["V. Líquido"].sum().reindex(range(1,13), fill_value=0)
    fig.add_trace(go.Scatter(x=meses_ordem, y=mensal_ant, mode='lines+markers', name=str(ano_anterior), line=dict(dash='dot')))

fig.update_layout(title=f"{ano_atual} vs {ano_anterior}", xaxis_title="Mês", yaxis_title="Vendas (€)", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# === ALERTA: QUEDA >30% ===
st.subheader("Clientes com Queda >30%")

if not df_ant.empty:
    vendas_cli = df_atual.groupby("Cliente")["V. Líquido"].sum()
    vendas_ant = df_ant.groupby("Cliente")["V. Líquido"].sum()
    comp = pd.DataFrame({"Atual": vendas_cli, "Anterior": vendas_ant}).fillna(0)
    comp = comp[comp["Anterior"] > 0]
    comp["Variação (%)"] = (comp["Atual"] - comp["Anterior"]) / comp["Anterior"] * 100
    queda = comp[comp["Variação (%)"] <= -30].round(0)

    if not queda.empty:
        st.error(f"{len(queda)} cliente(s) com queda >30%")
        st.dataframe(queda.style.format({"Atual": "€{:.0f}", "Anterior": "€{:.0f}", "Variação (%)": "{:.1f}%"})
                     .background_gradient(subset=["Variação (%)"], cmap="Reds"))
    else:
        st.success("Nenhum cliente com queda >30%")

# === RESUMO POR CLIENTE ===
st.subheader("Resumo por Cliente")

resumo = df_atual.groupby("Cliente").agg({
    "V. Líquido": "sum",
    "Qtd.": "sum",
    "Artigo": "nunique"
}).round(0)

if not df_ant.empty:
    resumo["Anterior"] = df_ant.groupby("Cliente")["V. Líquido"].sum().round(0)
    resumo["Variação (%)"] = ((resumo["V. Líquido"] - resumo["Anterior"]) / resumo["Anterior"] * 100).round(1)
else:
    resumo["Anterior"] = 0
    resumo["Variação (%)"] = 0

resumo = resumo.rename(columns={
    "V. Líquido": "Vendas (€)",
    "Qtd.": "Qtd",
    "Artigo": "Artigos"
}).sort_values("Vendas (€)", ascending=False)

st.dataframe(resumo.style.format({
    "Vendas (€)": "€{:.0f}",
    "Anterior": "€{:.0f}",
    "Variação (%)": "{:.1f}%"
}).background_gradient(subset=["Variação (%)"], cmap="RdYlGn"), use_container_width=True)

# === DOWNLOAD ===
st.download_button(
    "Baixar Dados Filtrados (CSV)",
    df.to_csv(index=False).encode('utf-8'),
    f"vendas_{ano_atual}.csv",
    "text/csv"
)
