import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análise de Compras", layout="wide")
st.title("📊 Análise de Compras por Cliente")

# Upload do arquivo
uploaded_file = st.file_uploader("Carregue o arquivo Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Verificação de colunas esperadas
    expected_cols = ["Nome Cliente", "Data Compra", "Valor Compra"]
    if all(col in df.columns for col in expected_cols):
        df["Data Compra"] = pd.to_datetime(df["Data Compra"])
        df["Ano"] = df["Data Compra"].dt.year
        df["Mês"] = df["Data Compra"].dt.month

        # Filtros
        clientes = st.multiselect("Selecione os clientes", df["Nome Cliente"].unique())
        anos = st.multiselect("Selecione os anos", sorted(df["Ano"].unique()))

        df_filtrado = df.copy()
        if clientes:
            df_filtrado = df_filtrado[df_filtrado["Nome Cliente"].isin(clientes)]
        if anos:
            df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos)]

        # Agrupamento mensal
        compras_mensais = df_filtrado.groupby(["Ano", "Mês", "Nome Cliente"])["Valor Compra"].sum().reset_index()

        # Gráfico de linhas
        st.subheader("📉 Evolução Mensal das Compras")
        fig, ax = plt.subplots(figsize=(10, 5))
        for cliente in compras_mensais["Nome Cliente"].unique():
            for ano in compras_mensais["Ano"].unique():
                dados = compras_mensais[(compras_mensais["Nome Cliente"] == cliente) & (compras_mensais["Ano"] == ano)]
                ax.plot(dados["Mês"], dados["Valor Compra"], label=f"{cliente} - {ano}")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Valor das Compras")
        ax.set_title("Comparação Anual por Cliente")
        ax.legend()
        st.pyplot(fig)

        # Tabela mensal
        st.subheader("📋 Tabela de Compras por Mês")
        tabela = compras_mensais.pivot_table(index=["Nome Cliente", "Ano"], columns="Mês", values="Valor Compra", fill_value=0)
        st.dataframe(tabela)

        # Crescimento percentual
        st.subheader("📈 Crescimento Percentual Anual")
        crescimento = df_filtrado.groupby(["Nome Cliente", "Ano"])["Valor Compra"].sum().unstack()
        crescimento_pct = crescimento.pct_change(axis=1) * 100
        st.dataframe(crescimento_pct.round(2))

        # Média mensal
        st.subheader("📊 Média Mensal de Compras")
        media_mensal = compras_mensais.groupby(["Nome Cliente", "Ano"])["Valor Compra"].mean().unstack()
        st.dataframe(media_mensal.round(2))

        # Sazonalidade (desvio padrão)
        st.subheader("📉 Sazonalidade (Desvio Padrão Mensal)")
        sazonalidade = compras_mensais.groupby(["Nome Cliente", "Ano"])["Valor Compra"].std().unstack()
        st.dataframe(sazonalidade.round(2))

        # Alertas de queda
        st.subheader("⚠️ Alertas de Queda Mensal")
        alertas = compras_mensais.sort_values(["Nome Cliente", "Ano", "Mês"])
        alertas["Queda"] = alertas.groupby(["Nome Cliente", "Ano"])["Valor Compra"].diff()
        alertas_queda = alertas[alertas["Queda"] < 0]
        st.dataframe(alertas_queda[["Nome Cliente", "Ano", "Mês", "Valor Compra", "Queda"]])

        # Exportação
        st.subheader("📤 Exportar Dados")
        export_df = compras_mensais.pivot_table(index=["Nome Cliente", "Ano"], columns="Mês", values="Valor Compra", fill_value=0)
        csv = export_df.to_csv().encode("utf-8")
        st.download_button("📥 Baixar CSV", data=csv, file_name="compras_analise_completa.csv", mime="text/csv")
    else:
        st.error("O arquivo precisa conter as colunas: Nome Cliente, Data Compra, Valor Compra.")
