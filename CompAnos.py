import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análise de Compras", layout="wide")
st.title("📊 Análise de Compras por Cliente")

# Fonte do Excel no GitHub
github_excel_url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas2025.xlsx"
df = pd.read_excel(github_excel_url)

# Verificação das colunas reais
expected_cols = ["N° Cliente", "Nome Cliente", "Total Líq.", "Comercial", "Mês", "Ano"]
if all(col in df.columns for col in expected_cols):
    df["Mês"] = df["Mês"].astype(int)
    df["Ano"] = df["Ano"].astype(int)
    df["Trimestre"] = pd.to_datetime(dict(year=df["Ano"], month=df["Mês"], day=1)).dt.to_period("Q")

    # Filtros interativos
    clientes = st.multiselect("🧍 Clientes", df["Nome Cliente"].unique())
    anos = st.multiselect("📅 Anos", sorted(df["Ano"].unique()))
    comerciais = st.multiselect("🧑‍💼 Comerciais", df["Comercial"].unique())

    df_filtrado = df.copy()
    if clientes: df_filtrado = df_filtrado[df_filtrado["Nome Cliente"].isin(clientes)]
    if anos: df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos)]
    if comerciais: df_filtrado = df_filtrado[df_filtrado["Comercial"].isin(comerciais)]

    # Agrupamento mensal
    compras_mensais = df_filtrado.groupby(["Ano", "Mês", "Nome Cliente"])["Total Líq."].sum().reset_index()

    # Gráfico de linhas por cliente
    st.subheader("📈 Evolução Mensal por Cliente")
    fig, ax = plt.subplots(figsize=(10, 5))
    for cliente in compras_mensais["Nome Cliente"].unique():
        for ano in compras_mensais["Ano"].unique():
            dados = compras_mensais[(compras_mensais["Nome Cliente"] == cliente) & (compras_mensais["Ano"] == ano)]
            ax.plot(dados["Mês"], dados["Total Líq."], label=f"{cliente} - {ano}")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Total Líquido")
    ax.set_title("Comparação Anual por Cliente")
    ax.legend()
    st.pyplot(fig)

    # Tabela mensal
    st.subheader("📋 Tabela de Compras por Mês")
    tabela = compras_mensais.pivot_table(index=["Nome Cliente", "Ano"], columns="Mês", values="Total Líq.", fill_value=0)
    st.dataframe(tabela)

    # Tabela trimestral
    st.subheader("📆 Compras por Trimestre")
    compras_trimestrais = df_filtrado.groupby(["Trimestre", "Nome Cliente"])["Total Líq."].sum().reset_index()
    tabela_tri = compras_trimestrais.pivot_table(index="Nome Cliente", columns="Trimestre", values="Total Líq.", fill_value=0)
    st.dataframe(tabela_tri)

    # Indicadores analíticos
    st.subheader("📊 Indicadores de Desempenho")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Crescimento Percentual**")
        crescimento = df_filtrado.groupby(["Nome Cliente", "Ano"])["Total Líq."].sum().unstack()
        crescimento_pct = crescimento.pct_change(axis=1) * 100
        st.dataframe(crescimento_pct.round(2))

    with col2:
        st.markdown("**Média Mensal**")
        media_mensal = compras_mensais.groupby(["Nome Cliente", "Ano"])["Total Líq."].mean().unstack()
        st.dataframe(media_mensal.round(2))

    with col3:
        st.markdown("**Sazonalidade (Desvio Padrão)**")
        sazonalidade = compras_mensais.groupby(["Nome Cliente", "Ano"])["Total Líq."].std().unstack()
        st.dataframe(sazonalidade.round(2))

    # Ticket médio por comercial
    st.subheader("💼 Ticket Médio por Comercial")
    ticket_medio = df_filtrado.groupby("Comercial")["Total Líq."].mean().reset_index()
    st.dataframe(ticket_medio.round(2))

    # Alertas de queda
    st.subheader("⚠️ Alertas de Queda Mensal")
    alertas = compras_mensais.sort_values(["Nome Cliente", "Ano", "Mês"])
    alertas["Queda"] = alertas.groupby(["Nome Cliente", "Ano"])["Total Líq."].diff()
    alertas_queda = alertas[alertas["Queda"] < 0]
    st.dataframe(alertas_queda[["Nome Cliente", "Ano", "Mês", "Total Líq.", "Queda"]])

    # Exportação
    st.subheader("📤 Exportar Dados")
    csv = tabela.reset_index().to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar CSV", data=csv, file_name="compras_clientes.csv", mime="text/csv")
else:
    st.error("O arquivo precisa conter as colunas: N° Cliente, Nome Cliente, Total Líq., Comercial, Mês, Ano.")
