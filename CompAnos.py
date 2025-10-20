import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análise Segmentada", layout="wide")
st.title("📊 Análise de Compras por Cliente com Segmentação")

# Fonte do Excel no GitHub
github_excel_url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas2025.xlsx"

# Leitura direta do Excel
df = pd.read_excel(github_excel_url)

# Verificação de colunas esperadas
expected_cols = ["Nome Cliente", "Data Compra", "Valor Compra", "Produto", "Canal", "Região"]
if all(col in df.columns for col in expected_cols):
    df["Data Compra"] = pd.to_datetime(df["Data Compra"])
    df["Ano"] = df["Data Compra"].dt.year
    df["Mês"] = df["Data Compra"].dt.month

    # Filtros interativos
    clientes = st.multiselect("🧍 Clientes", df["Nome Cliente"].unique())
    anos = st.multiselect("📅 Anos", sorted(df["Ano"].unique()))
    produtos = st.multiselect("📦 Produtos", df["Produto"].unique())
    canais = st.multiselect("🛒 Canais de Venda", df["Canal"].unique())
    regioes = st.multiselect("🌍 Regiões", df["Região"].unique())

    # Aplicar filtros
    df_filtrado = df.copy()
    if clientes: df_filtrado = df_filtrado[df_filtrado["Nome Cliente"].isin(clientes)]
    if anos: df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos)]
    if produtos: df_filtrado = df_filtrado[df_filtrado["Produto"].isin(produtos)]
    if canais: df_filtrado = df_filtrado[df_filtrado["Canal"].isin(canais)]
    if regioes: df_filtrado = df_filtrado[df_filtrado["Região"].isin(regioes)]

    # Agrupamento mensal
    compras_mensais = df_filtrado.groupby(["Ano", "Mês", "Nome Cliente"])["Valor Compra"].sum().reset_index()

    # Gráfico de linhas por cliente
    st.subheader("📈 Evolução Mensal por Cliente")
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

    # Gráficos por segmento
    st.subheader("📊 Gráficos por Segmento")

    def plot_segmento(coluna, titulo):
        agrupado = df_filtrado.groupby([coluna, "Ano"])["Valor Compra"].sum().unstack().fillna(0)
        fig, ax = plt.subplots(figsize=(8, 4))
        agrupado.plot(kind="bar", ax=ax)
        ax.set_title(titulo)
        ax.set_ylabel("Valor Total")
        st.pyplot(fig)

    plot_segmento("Produto", "Compras por Produto")
    plot_segmento("Canal", "Compras por Canal de Venda")
    plot_segmento("Região", "Compras por Região")

    # Indicadores
    st.subheader("📊 Indicadores de Desempenho")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Crescimento Percentual**")
        crescimento = df_filtrado.groupby(["Nome Cliente", "Ano"])["Valor Compra"].sum().unstack()
        crescimento_pct = crescimento.pct_change(axis=1) * 100
        st.dataframe(crescimento_pct.round(2))

    with col2:
        st.markdown("**Média Mensal**")
        media_mensal = compras_mensais.groupby(["Nome Cliente", "Ano"])["Valor Compra"].mean().unstack()
        st.dataframe(media_mensal.round(2))

    with col3:
        st.markdown("**Sazonalidade (Desvio Padrão)**")
        sazonalidade = compras_mensais.groupby(["Nome Cliente", "Ano"])["Valor Compra"].std().unstack()
        st.dataframe(sazonalidade.round(2))

    # Alertas de queda
    st.subheader("⚠️ Alertas de Queda Mensal")
    alertas = compras_mensais.sort_values(["Nome Cliente", "Ano", "Mês"])
    alertas["Queda"] = alertas.groupby(["Nome Cliente", "Ano"])["Valor Compra"].diff()
    alertas_queda = alertas[alertas["Queda"] < 0]
    st.dataframe(alertas_queda[["Nome Cliente", "Ano", "Mês", "Valor Compra", "Queda"]])

    # Exportação segmentada
    st.subheader("📤 Exportar Dados Segmentados")
    export_df = df_filtrado.groupby(["Nome Cliente", "Ano", "Mês", "Produto", "Canal", "Região"])["Valor Compra"].sum().reset_index()
    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar CSV Segmentado", data=csv, file_name="compras_segmentadas_completas.csv", mime="text/csv")
else:
    st.error("O arquivo precisa conter as colunas: Nome Cliente, Data Compra, Valor Compra, Produto, Canal, Região.")
