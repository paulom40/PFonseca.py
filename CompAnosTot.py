import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime
import xlsxwriter.utility


st.set_page_config(page_title="Análise de Compras", layout="wide")
st.title("📊 Análise de Compras por Cliente")

# Fonte do Excel
github_excel_url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/VGlob2425.xlsx"
df = pd.read_excel(github_excel_url)

# Normaliza colunas
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df["nome_cliente"] = df["nome_cliente"].astype(str).str.strip()
df["comercial"] = df["comercial"].astype(str).str.strip()

# Mapeia meses
mes_map = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
}
df["mês"] = df["mês"].astype(str).str.strip().str.lower().map(mes_map)
df["ano"] = pd.to_numeric(df["ano"], errors="coerce").fillna(0).astype(int)
df["trimestre"] = pd.to_datetime(dict(year=df["ano"], month=df["mês"], day=1)).dt.to_period("Q")

# Filtros
st.sidebar.header("🎚️ Filtros")
clientes = st.sidebar.multiselect("🧍 Nome Cliente", sorted(df["nome_cliente"].dropna().unique()))
comerciais = st.sidebar.multiselect("💼 Comercial", sorted(df["comercial"].dropna().unique()))
meses = st.sidebar.multiselect("📆 Mês", sorted(df["mês"].dropna().unique()))
anos = st.sidebar.multiselect("📅 Ano", sorted(df["ano"].dropna().unique()))

df_filtrado = df.copy()
if clientes:
    df_filtrado = df_filtrado[df_filtrado["nome_cliente"].isin(clientes)]
if comerciais:
    df_filtrado = df_filtrado[df_filtrado["comercial"].isin(comerciais)]
if meses:
    df_filtrado = df_filtrado[df_filtrado["mês"].isin(meses)]
if anos:
    df_filtrado = df_filtrado[df_filtrado["ano"].isin(anos)]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# Agrupamentos principais
compras_mensais = df_filtrado.groupby(["ano", "mês", "nome_cliente"])["total_liquido"].sum().reset_index()
compras_trimestrais = df_filtrado.groupby(["trimestre", "nome_cliente"])["total_liquido"].sum().reset_index()
ticket_medio = df_filtrado.groupby("comercial")["total_liquido"].mean().reset_index()
ticket_cliente = df_filtrado.groupby("nome_cliente")["total_liquido"].mean().reset_index()
ranking = df_filtrado.groupby("nome_cliente")["total_liquido"].sum().sort_values(ascending=False).reset_index()
ranking.index += 1
# Indicadores adicionais
crescimento = df_filtrado.groupby(["nome_cliente", "ano"])["total_liquido"].sum().unstack()
crescimento_pct = crescimento.pct_change(axis=1, fill_method=None) * 100
media_mensal = compras_mensais.groupby(["nome_cliente", "ano"])["total_liquido"].mean().unstack()
sazonalidade = compras_mensais.groupby(["nome_cliente", "ano"])["total_liquido"].std().unstack()

# Alertas
alertas = compras_mensais.sort_values(["nome_cliente", "ano", "mês"])
alertas["queda"] = alertas.groupby(["nome_cliente", "ano"])["total_liquido"].diff()
alertas_queda = alertas[alertas["queda"] < 0]

df_filtrado["data_compra"] = pd.to_datetime(dict(year=df_filtrado["ano"], month=df_filtrado["mês"], day=1))
ultimas_compras = df_filtrado.groupby("nome_cliente")["data_compra"].max().reset_index()
ultimas_compras["dias_sem_compra"] = (datetime.today() - ultimas_compras["data_compra"]).dt.days
alertas_inativos = ultimas_compras[ultimas_compras["dias_sem_compra"] > 60].copy()
alertas_inativos["status"] = "🔴 Inativo"
alertas_inativos = alertas_inativos.sort_values("dias_sem_compra", ascending=False)

# Resumo mensal geral
resumo_mensal = df_filtrado.groupby(["ano", "mês"])["total_liquido"].sum().reset_index()
resumo_mensal["mês_nome"] = resumo_mensal["mês"].map(mes_map)
resumo_mensal = resumo_mensal.sort_values(["ano", "mês"])
resumo_mensal = resumo_mensal[["ano", "mês_nome", "total_liquido"]].rename(columns={
    "ano": "Ano", "mês_nome": "Mês", "total_liquido": "Total Compras"
})

# Resumo mensal por comercial
resumo_comercial = df_filtrado.groupby(["ano", "mês", "comercial"])["total_liquido"].sum().reset_index()
resumo_comercial["mês_nome"] = resumo_comercial["mês"].map(mes_map)
resumo_comercial["periodo"] = resumo_comercial["ano"].astype(str) + "-" + resumo_comercial["mês"].astype(str).str.zfill(2)
resumo_comercial = resumo_comercial.sort_values(["ano", "mês", "comercial"])
resumo_comercial = resumo_comercial[["periodo", "comercial", "total_liquido"]].rename(columns={
    "periodo": "Período", "comercial": "Comercial", "total_liquido": "Total Compras"
})

# Gráfico de linhas por comercial
st.subheader("📈 Evolução Mensal por Comercial")
pivot = resumo_comercial.pivot(index="Período", columns="Comercial", values="Total Compras")
fig, ax = plt.subplots(figsize=(10, 5))
pivot.plot(ax=ax)
plt.title("Total de Compras por Comercial ao Longo do Tempo")
plt.xlabel("Período")
plt.ylabel("Total Compras (€)")
plt.xticks(rotation=45)
plt.legend(title="Comercial")
st.pyplot(fig)
# Exibição visual
st.subheader("📋 Dados Filtrados")
st.dataframe(df_filtrado)

st.subheader("🏆 Ranking de Clientes")
st.dataframe(ranking.style.format({"total_liquido": "€ {:,.2f}"}))

st.subheader("📆 Compras Mensais")
st.dataframe(compras_mensais.style.format({"total_liquido": "€ {:,.2f}"}))

st.subheader("💼 Ticket Médio por Comercial")
st.dataframe(ticket_medio.style.format({"total_liquido": "€ {:,.2f}"}))

st.subheader("🧾 Ticket Médio por Cliente")
st.dataframe(ticket_cliente.style.format({"total_liquido": "€ {:,.2f}"}))

st.subheader("⚠️ Alertas de Queda Mensal")
st.dataframe(alertas_queda[["nome_cliente", "ano", "mês", "total_liquido", "queda"]].style.format({
    "total_liquido": "€ {:,.2f}", "queda": "€ {:,.2f}"
}))

st.subheader("🚨 Clientes sem compras há mais de 60 dias")
def colorir_linha(row):
    if row["dias_sem_compra"] > 120:
        return ["background-color: #ffcccc"] * len(row)
    elif row["dias_sem_compra"] > 90:
        return ["background-color: #ffe5b4"] * len(row)
    else:
        return ["background-color: #ffffcc"] * len(row)
st.dataframe(alertas_inativos.style.apply(colorir_linha, axis=1))

st.subheader("📅 Resumo Mensal de Compras por Ano")
st.dataframe(resumo_mensal.style.format({"Total Compras": "€ {:,.2f}"}))

st.subheader("📊 Resumo Mensal por Comercial")
st.dataframe(resumo_comercial.style.format({"Total Compras": "€ {:,.2f}"}))

# Exportação para Excel
st.subheader("📤 Exportar Dados para Excel")
output = io.BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    compras_mensais.to_excel(writer, index=False, sheet_name="Compras Mensais")
    compras_trimestrais.to_excel(writer, index=False, sheet_name
