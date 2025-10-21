import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análise de Compras", layout="wide")
st.title("📊 Análise de Compras por Cliente")

# Fonte do Excel no GitHub
github_excel_url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas2025.xlsx"
df = pd.read_excel(github_excel_url)

# Normaliza os nomes das colunas
df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace("í", "i").str.replace("ç", "c").str.replace(".", "").str.lower()

# Verifica colunas esperadas
expected_cols = ["cliente", "nome_cliente", "total_liquido", "comercial", "mes", "ano"]
if all(col in df.columns for col in expected_cols):
    df["mes"] = df["mes"].astype(int)
    df["ano"] = df["ano"].astype(int)
    df["trimestre"] = pd.to_datetime(dict(year=df["ano"], month=df["mes"], day=1)).dt.to_period("Q")

    # Filtros
    clientes = st.multiselect("🧍 Clientes", df["nome_cliente"].unique())
    anos = st.multiselect("📅 Anos", sorted(df["ano"].unique()))
    comerciais = st.multiselect("🧑‍💼 Comerciais", df["comercial"].unique())

    df_filtrado = df.copy()
    if clientes: df_filtrado = df_filtrado[df_filtrado["nome_cliente"].isin(clientes)]
    if anos: df_filtrado = df_filtrado[df_filtrado["ano"].isin(anos)]
    if comerciais: df_filtrado = df_filtrado[df_filtrado["comercial"].isin(comerciais)]

    # Agrupamento mensal
    compras_mensais = df_filtrado.groupby(["ano", "mes", "nome_cliente"])["total_liquido"].sum().reset_index()

    # Gráfico de linhas
    st.subheader("📈 Evolução Mensal por Cliente")
    fig, ax = plt.subplots(figsize=(10, 5))
    for cliente in compras_mensais["nome_cliente"].unique():
        for ano in compras_mensais["ano"].unique():
            dados = compras_mensais[(compras_mensais["nome_cliente"] == cliente) & (compras_mensais["ano"] == ano)]
            ax.plot(dados["mes"], dados["total_liquido"], label=f"{cliente} - {ano}")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Total Líquido")
    ax.set_title("Comparação Anual por Cliente")
    ax.legend()
    st.pyplot(fig)

    # Tabela mensal
    st.subheader("📋 Tabela de Compras por Mês")
    tabela = compras_mensais.pivot_table(index=["nome_cliente", "ano"], columns="mes", values="total_liquido", fill_value=0)
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

    # Ranking de clientes
    st.subheader("🏆 Ranking de Clientes por Volume Total")
    ranking = df_filtrado.groupby("nome_cliente")["total_liquido"].sum().sort_values(ascending=False).reset_index()
    ranking.index += 1
    st.dataframe(ranking)

    # Alertas de queda
    st.subheader("⚠️ Alertas de Queda Mensal")
    alertas = compras_mensais.sort_values(["nome_cliente", "ano", "mes"])
    alertas["queda"] = alertas.groupby(["nome_cliente", "ano"])["total_liquido"].diff()
    alertas_queda = alertas[alertas["queda"] < 0]
    st.dataframe(alertas_queda[["nome_cliente", "ano", "mes", "total_liquido", "queda"]])

    # Exportação
    st.subheader("📤 Exportar Dados")
    csv = tabela.reset_index().to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar CSV", data=csv, file_name="compras_clientes.csv", mime="text/csv")
else:
    st.error("O arquivo precisa conter as colunas: Cliente, Nome Cliente, Total Liquido, Comercial, Mês, Ano.")
