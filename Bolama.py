import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

st.set_page_config(page_title="Bolama Dashboard", layout="wide", page_icon="📊")

@st.cache_data
def load_data_from_github():
    url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bolama_Vendas.xlsx"
    df_raw = pd.read_excel(url)

    # Corrige datas
    df_raw["Data"] = pd.to_datetime(df_raw["Data"], errors="coerce")

    # Diagnóstico: mostra datas inválidas
    linhas_invalidas = df_raw[df_raw["Data"].isna()]
    if not linhas_invalidas.empty:
        st.sidebar.markdown("### ⚠️ Linhas com Data inválida")
        st.sidebar.dataframe(linhas_invalidas)

    # Mantém apenas datas válidas
    df = df_raw[df_raw["Data"].notna()].copy()

    # Gera campo Mês
    df["Mês"] = df["Data"].dt.strftime("%Y-%m")

    # Diagnóstico: mostra meses únicos
    st.sidebar.markdown("### 📅 Meses detectados")
    st.sidebar.write(sorted(df["Mês"].unique()))

    return df

# Carregamento inicial
if "df" not in st.session_state:
    st.session_state.df = load_data_from_github()
df = st.session_state.df

# Validação dinâmica de meses esperados
meses_esperados = pd.date_range(start=df["Data"].min(), end=df["Data"].max(), freq="MS").strftime("%Y-%m").tolist()
meses_disponiveis = sorted(df["Mês"].unique())
meses_em_falta = sorted(set(meses_esperados) - set(meses_disponiveis))

if meses_em_falta:
    st.warning(f"⚠️ Os seguintes meses estão ausentes ou incompletos: {', '.join(meses_em_falta)}")
else:
    st.success("✅ Todos os meses esperados estão presentes nos dados.")
st.sidebar.title("📦 Filtros")
selected_artigo = st.sidebar.multiselect("Artigo", options=sorted(df["Artigo"].unique()))
selected_mes = st.sidebar.multiselect("Mês", options=sorted(df["Mês"].unique()))

filtered_df = df.copy()
if selected_artigo:
    filtered_df = filtered_df[filtered_df["Artigo"].isin(selected_artigo)]
if selected_mes:
    filtered_df = filtered_df[filtered_df["Mês"].isin(selected_mes)]

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

st.markdown("### 🏆 Top 10 Artigos por Mês")
top_artigos = (
    filtered_df.groupby(["Mês", "Artigo"])
    .agg({"Quantidade": "sum", "V Líquido": "sum"})
    .sort_values(by="V Líquido", ascending=False)
    .groupby("Mês")
    .head(10)
    .reset_index()
)

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

    crescimento_df["Crescimento Qtd (%)"] = crescimento_df["Crescimento Qtd (%)"].round(2)
    crescimento_df["Crescimento Vendas (%)"] = crescimento_df["Crescimento Vendas (%)"].round(2)

    def highlight_growth(val):
        if pd.isna(val):
            return "background-color: #D9D9D9; color: #404040; font-style: italic"
        elif val < 0:
            return "background-color: #FFC7CE; color: #9C0006"
        elif val == 0:
            return "background-color: #FFEB9C; color: #9C6500"
        else:
            return "background-color: #C6EFCE; color: #006100"

    styled_df = crescimento_df.style.format({
        "Qtd 2024": "{:.2f}",
        "Qtd 2025": "{:.2f}",
        "Vendas 2024": "€ {:.2f}",
        "Vendas 2025": "€ {:.2f}",
        "Crescimento Qtd (%)": "{:.2f}%",
        "Crescimento Vendas (%)": "{:.2f}%"
    }).applymap(highlight_growth, subset=["Crescimento Qtd (%)", "Crescimento Vendas (%)"])

    st.dataframe(styled_df, use_container_width=True)

    # 📤 Exportação Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Dados Filtrados')
        top_artigos.to_excel(writer, index=False, sheet_name='Top Artigos')
        crescimento_df.to_excel(writer, index=False, sheet_name='Crescimento')

        # Aba com meses ausentes
        if meses_em_falta:
            df_ausentes = pd.DataFrame({"Meses Ausentes": meses_em_falta})
            df_ausentes.to_excel(writer, index=False, sheet_name='Meses Ausentes')
            writer.sheets['Meses Ausentes'].set_column('A:A', 20)

        # Aba de resumo
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
        ws = writer.sheets['Resumo']
        ws.set_column('A:B', 30)

        # Formatação condicional
        workbook = writer.book
        format_verde = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
        format_vermelho = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
        format_amarelo = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})
        format_cinza = workbook.add_format({'bg_color': '#D9D9D9', 'font_color': '#404040', 'italic': True})

        ws.conditional_format('B5:B5', {'type': 'cell', 'criteria': '>=', 'value': 0.01, 'format': format_verde})
        ws.conditional_format('B5:B5', {'type': 'cell', 'criteria': '<', 'value': 0, 'format': format_vermelho})
        ws.conditional_format('B5:B5', {'type': 'cell', 'criteria': '==', 'value': 0, 'format': format_amarelo})
        ws.conditional_format('B5:B5', {'type': 'text', 'criteria': 'containing', 'value': 'Sem dados', 'format': format_cinza})

    # Botão de exportação com nome dinâmico
    if selected_mes:
        nome_meses = "_".join(selected_mes)
        nome_ficheiro = f"Relatorio_Bolama_{nome_meses}.xlsx"
    else:
        nome_ficheiro = f"Relatorio_Bolama_{datetime.now().strftime('%Y-%m-%d')}.xlsx"

    st.download_button(
        label="📤 Exportar Relatório Bolama",
        data=output.getvalue(),
        file_name=nome_ficheiro,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
