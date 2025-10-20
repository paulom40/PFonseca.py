import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análise de Compras", layout="wide")
st.title("📊 Análise de Compras por Cliente")

# Fonte do Excel no GitHub
github_excel_url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas2025.xlsx"
df = pd.read_excel(github_excel_url)

# Verificação de colunas disponíveis
expected_cols = ["N° Cliente", "Nome Cliente", "Total Líq.", "Comercial", "Mês", "Ano"]
if all(col in df.columns for col in expected_cols):
    df["Mês"] = df["Mês"].astype(int)
    df["Ano"] = df["Ano"].astype(int)

    # Filtros
    clientes = st.multiselect("🧍 Clientes", df["Nome Cliente"].unique())
    anos = st.multiselect("📅 Anos", sorted(df["Ano"].unique()))
    comerciais = st.multiselect("🧑‍💼 Comerciais", df["Comercial"].unique())

    df_filtrado = df.copy()
    if clientes: df_filtrado = df_filtrado[df_filtrado["Nome Cliente"].isin(clientes)]
    if anos: df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos)]
    if comerciais: df_filtrado = df_filtrado[df_filtrado["Comercial"].isin(comerciais)]

    # Agrupamento mensal
    compras_mensais = df_filtrado.groupby(["Ano", "Mês", "Nome Cliente"])["Total Líq."].sum().reset_index()

    # Gráfico de linhas
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

    # Exportação
    st.subheader("📤 Exportar Dados")
    csv = tabela.reset_index().to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar CSV", data=csv, file_name="compras_clientes.csv", mime="text/csv")
else:
    st.error("O arquivo precisa conter as colunas: N° Cliente, Nome Cliente, Total Líq., Comercial, Mês, Ano.")
