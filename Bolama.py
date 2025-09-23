import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

# 🚀 Configuração da página
st.set_page_config(page_title="Bolama Dashboard", layout="wide", page_icon="📊")

# 🔒 Ocultar elementos padrão
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 📥 Carregar dados
@st.cache_data
def load_data():
    df = pd.read_excel("Bolama_Vendas.xlsx")
    df["Data"] = pd.to_datetime(df["Data"])
    df["Mês"] = df["Data"].dt.strftime("%Y-%m")
    return df

df = load_data()

# 🔐 Controle de sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 🔐 Login
st.sidebar.title("🔐 Login")
if not st.session_state.logged_in:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        if username == "pedro" and password == "pedro":
            st.session_state.logged_in = True
            st.success("✅ Login bem-sucedido")
        else:
            st.error("❌ Credenciais inválidas")
else:
    # 📦 Filtros
    st.sidebar.title("📦 Filtros")
    selected_artigo = st.sidebar.multiselect("Artigo", options=sorted(df["Artigo"].unique()))
    selected_mes = st.sidebar.multiselect("Mês", options=sorted(df["Mês"].unique()))

    filtered_df = df.copy()
    if selected_artigo:
        filtered_df = filtered_df[filtered_df["Artigo"].isin(selected_artigo)]
    if selected_mes:
        filtered_df = filtered_df[filtered_df["Mês"].isin(selected_mes)]

    # 🧮 KPIs
    st.title("📊 Bolama Vendas Dashboard")
    st.markdown("### Indicadores por Mês")

    kpi_df = filtered_df.groupby("Mês").agg({
        "Quantidade": "sum",
        "V Líquido": "sum"
    }).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Quantidade", f"{kpi_df['Quantidade'].sum():,.2f} KG")
    with col2:
        st.metric("Total Vendas Líquidas", f"€ {kpi_df['V Líquido'].sum():,.2f}")

    # 🏆 Top Artigos
    st.markdown("### 🏆 Top 10 Artigos por Mês")
    top_artigos = (
        filtered_df.groupby(["Mês", "Artigo"])
        .agg({"Quantidade": "sum", "V Líquido": "sum"})
        .sort_values(by="V Líquido", ascending=False)
        .groupby("Mês")
        .head(10)
        .reset_index()
    )

    # 📋 Tabelas
    st.markdown("### 📋 Resultados Filtrados")
    st.dataframe(
        filtered_df.style.background_gradient(cmap="YlGnBu").format({
            "Quantidade": "{:.2f}",
            "V Líquido": "€ {:.2f}"
        }),
        use_container_width=True
    )

    st.markdown("### 📌 Top Artigos")
    st.dataframe(
        top_artigos.style.background_gradient(cmap="OrRd").format({
            "Quantidade": "{:.2f}",
            "V Líquido": "€ {:.2f}"
        }),
        use_container_width=True
    )

    # 📈 Aba de Crescimento
    tab1, tab2 = st.tabs(["📊 Dashboard Principal", "📈 Crescimento por Artigo (2024 vs 2025)"])

    with tab2:
        st.markdown("### 📈 Percentagem de Crescimento por Artigo entre 2024 e 2025")

        df_growth = df[df["Data"].dt.year.isin([2024, 2025])].copy()
        df_growth["Ano"] = df_growth["Data"].dt.year
        df_growth["Mês"] = df_growth["Data"].dt.strftime("%m")

        grouped = df_growth.groupby(["Artigo", "Mês", "Ano"]).agg({
            "Quantidade": "sum",
            "V Líquido": "sum"
        }).reset_index()

        pivot_qtd = grouped.pivot(index=["Artigo", "Mês"], columns="Ano", values="Quantidade").reset_index()
        pivot_vl = grouped.pivot(index=["Artigo", "Mês"], columns="Ano", values="V Líquido").reset_index()

        pivot_qtd = pivot_qtd.rename(columns={2024: "Qtd 2024", 2025: "Qtd 2025"})
        pivot_vl = pivot_vl.rename(columns={2024: "Vendas 2024", 2025: "Vendas 2025"})

        crescimento_df = pd.merge(pivot_qtd, pivot_vl, on=["Artigo", "Mês"])

        crescimento_df["Crescimento Qtd (%)"] = crescimento_df.apply(
            lambda row: ((row["Qtd 2025"] - row["Qtd 2024"]) / row["Qtd 2024"] * 100)
            if pd.notnull(row["Qtd 2024"]) and row["Qtd 2024"] != 0 else None,
            axis=1
        )
        crescimento_df["Crescimento Vendas (%)"] = crescimento_df.apply(
            lambda row: ((row["Vendas 2025"] - row["Vendas 2024"]) / row["Vendas 2024"] * 100)
            if pd.notnull(row["Vendas 2024"]) and row["Vendas 2024"] != 0 else None,
            axis=1
        )

        crescimento_df["Crescimento Qtd (%)"] = crescimento_df["Crescimento Qtd (%)"].round(2).replace(np.nan, "Sem dados")
        crescimento_df["Crescimento Vendas (%)"] = crescimento_df["Crescimento Vendas (%)"].round(2).replace(np.nan, "Sem dados")

        st.dataframe(crescimento_df, use_container_width=True)

        # 📤 Exportar para Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Planilhas principais
            filtered_df.to_excel(writer, index=False, sheet_name='Dados Filtrados')
            top_artigos.to_excel(writer, index=False, sheet_name='Top Artigos')
            crescimento_df.to_excel(writer, index=False, sheet_name='Crescimento')

            # Planilha de resumo
            total_qtd = filtered_df["Quantidade"].sum()
            total_vl = filtered_df["V Líquido"].sum()
            total_2024 = df[df["Data"].dt.year == 2024]["V Líquido"].sum()
            total_2025 = df[df["Data"].dt.year == 2025]["V Líquido"].sum()
            crescimento_total = ((total_2025 - total_2024) / total_2024 * 100) if total_2024 else None

            resumo_df = pd.DataFrame({
                "Indicador": [
                    "Total Quantidade Filtrada",
                    "Total Vendas Líquidas Filtradas",
                    "Vendas 2024",
                    "Vendas 2025",
                    "Crescimento Total (%)",
                    "Data de Exportação"
                ],
                "Valor": [
                    f"{total_qtd:,.2f} KG",
                    f"€ {total_vl:,.2f}",
                    f"€ {total_2024:,.2f}",
                    f"€ {total_2025:,.2f}",
                    f"{crescimento_total:.2f}%" if crescimento_total is not None else "Sem dados",
                    datetime.now().strftime("%d/%m/%Y %H:%M")
                ]
            })
            resumo_df.to_excel(writer, index=False, sheet_name='Resumo')

            # Estilização
            for sheet_name in ['Dados Filtrados', 'Top Artigos', 'Crescimento', 'Resumo']:
                ws = writer.sheets[sheet_name]
                ws.set_column('A:Z', 18)
                ws.autofilter(0, 0, 1 + len(df), len(df.columns) - 1)

            ws3 = writer.sheets['Crescimento']
            format_up = writer.book.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
            format_down = writer.book.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
            format_na = writer.book.add_format({'bg_color': '#D9D9D9', 'font_color': '#404040', 'italic': True})

