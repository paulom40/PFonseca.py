import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime

st.set_page_config(page_title="Análise de Compras", layout="wide")
st.title("📊 Análise de Compras por Cliente")

# Fonte do Excel
github_excel_url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas2025.xlsx"
df = pd.read_excel(github_excel_url)

# Normaliza colunas
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Mapeia nomes de meses para números
mes_map = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
}
df["mês"] = df["mês"].astype(str).str.strip().str.lower().map(mes_map)
df["ano"] = pd.to_numeric(df["ano"], errors="coerce").fillna(0).astype(int)
df["trimestre"] = pd.to_datetime(dict(year=df["ano"], month=df["mês"], day=1)).dt.to_period("Q")

# Filtros na sidebar
st.sidebar.header("🎚️ Filtros")
clientes = st.sidebar.multiselect("🧍 Nome Cliente", df["nome_cliente"].unique())
comerciais = st.sidebar.multiselect("💼 Comercial", df["comercial"].unique())
meses = st.sidebar.multiselect("📆 Mês", sorted(df["mês"].dropna().unique()))
anos = st.sidebar.multiselect("📅 Ano", sorted(df["ano"].dropna().unique()))

# Aplica filtros
df_filtrado = df.copy()
if clientes: df_filtrado = df_filtrado[df_filtrado["nome_cliente"].isin(clientes)]
if comerciais: df_filtrado = df_filtrado[df_filtrado["comercial"].isin(comerciais)]
if meses: df_filtrado = df_filtrado[df_filtrado["mês"].isin(meses)]
if anos: df_filtrado = df_filtrado[df_filtrado["ano"].isin(anos)]

# Agrupamento mensal
compras_mensais = df_filtrado.groupby(["ano", "mês", "nome_cliente"])["total_liquido"].sum().reset_index()

# Gráfico com rótulos
st.subheader("📈 Comparação Mensal por Cliente e Ano")
fig, ax = plt.subplots(figsize=(10, 6))
for cliente in compras_mensais["nome_cliente"].unique():
    for ano in compras_mensais["ano"].unique():
        dados = compras_mensais[(compras_mensais["nome_cliente"] == cliente) & (compras_mensais["ano"] == ano)]
        if not dados.empty:
            ax.plot(dados["mês"], dados["total_liquido"], marker="o", label=f"{cliente} - {ano}")
            for i in range(len(dados)):
                x = dados["mês"].iloc[i]
                y = dados["total_liquido"].iloc[i]
                ax.text(x, y, f"{y:.0f}", ha="center", va="bottom", fontsize=8)
ax.set_xticks(range(1, 13))
ax.set_xticklabels(["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
ax.set_xlabel("Mês")
ax.set_ylabel("Total Líquido")
ax.set_title("Comparação Mensal com Rótulos")
ax.legend()
st.pyplot(fig)

# Tabela mensal
st.subheader("📋 Tabela de Compras por Mês")
tabela = compras_mensais.pivot_table(index=["nome_cliente", "ano"], columns="mês", values="total_liquido", fill_value=0)
st.dataframe(tabela)

# Tabela trimestral
st.subheader("📆 Compras por Trimestre")
compras_trimestrais = df_filtrado.groupby(["trimestre", "nome_cliente"])["total_liquido"].sum().reset_index()
tabela_tri = compras_trimestrais.pivot_table(index="nome_cliente", columns="trimestre", values="total_liquido", fill_value=0)
st.dataframe(tabela_tri)

# Indicadores
st.subheader("📊 Indicadores de Desempenho")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Crescimento Percentual**")
    crescimento = df_filtrado.groupby(["nome_cliente", "ano"])["total_liquido"].sum().unstack()
    crescimento_pct = crescimento.pct_change(axis=1) * 100
    st.dataframe(crescimento_pct.round(2))

with col2:
    st.markdown("**Média Mensal**")
    media_mensal = compras_mensais.groupby(["nome_cliente", "ano"])["total_liquido"].mean().unstack()
    st.dataframe(media_mensal.round(2))

with col3:
    st.markdown("**Sazonalidade (Desvio Padrão)**")
    sazonalidade = compras_mensais.groupby(["nome_cliente", "ano"])["total_liquido"].std().unstack()
    st.dataframe(sazonalidade.round(2))

# Ticket médio por comercial
st.subheader("💼 Ticket Médio por Comercial")
ticket_medio = df_filtrado.groupby("comercial")["total_liquido"].mean().reset_index()
st.dataframe(ticket_medio.round(2))

# Ticket médio por cliente
st.subheader("🧾 Ticket Médio por Cliente")
ticket_cliente = df_filtrado.groupby("nome_cliente")["total_liquido"].mean().reset_index()
st.dataframe(ticket_cliente.round(2))

# Ranking de clientes
st.subheader("🏆 Ranking de Clientes por Volume Total")
ranking = df_filtrado.groupby("nome_cliente")["total_liquido"].sum().sort_values(ascending=False).reset_index()
ranking.index += 1
st.dataframe(ranking)

# Alertas de queda
st.subheader("⚠️ Alertas de Queda Mensal")
alertas = compras_mensais.sort_values(["nome_cliente", "ano", "mês"])
alertas["queda"] = alertas.groupby(["nome_cliente", "ano"])["total_liquido"].diff()
alertas_queda = alertas[alertas["queda"] < 0]
st.dataframe(alertas_queda[["nome_cliente", "ano", "mês", "total_liquido", "queda"]])

# Clientes inativos
st.subheader("🚨 Clientes sem compras há mais de 60 dias")
df_filtrado["data_compra"] = pd.to_datetime(dict(year=df_filtrado["ano"], month=df_filtrado["mês"], day=1))
ultimas_compras = df_filtrado.groupby("nome_cliente")["data_compra"].max().reset_index()
ultimas_compras["dias_sem_compra"] = (datetime.today() - ultimas_compras["data_compra"]).dt.days
alertas_inativos = ultimas_compras[ultimas_compras["dias_sem_compra"] > 60].copy()
alertas_inativos["status"] = "🔴 Inativo"
alertas_inativos = alertas_inativos.sort_values("dias_sem_compra", ascending=False)

def colorir_linha(row):
    if row["dias_sem_compra"] > 120:
        return ["background-color: #ffcccc"] * len(row)
    elif row["dias_sem_compra"] > 90:
        return ["background-color: #ffe5b4"] * len(row)
    else:
        return ["background-color: #ffffcc"] * len(row)

st.dataframe(alertas_inativos.style.apply(colorir_linha, axis=1))

# Resumo mensal por ano
resumo_mensal = df_filtrado.groupby(["ano", "mês"])["total_liquido"].sum().reset_index()
resumo_mensal["mês_nome"] = resumo_mensal["mês"].map({
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
})
resumo_mensal = resumo_mensal.sort_values(["ano", "mês"])
resumo_mensal = resumo_mensal[["ano", "mês_nome", "total_liquido"]].rename(columns={
    "ano":
