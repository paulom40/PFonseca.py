# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuração da página
st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

# Título
st.title("Dashboard de Vendas Globais")
st.markdown("Análise comparativa por **Cliente**, **Comercial**, **Artigo**, **Mês** e **Ano** com **KPIs e Comparação com Ano Anterior**")

# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_excel("Vendas_Globais.xlsx", sheet_name="Sheet1")
    df.columns = ["Código", "Cliente", "Qtd.", "UN", "PM", "V. Líquido", "Artigo", "Comercial", "Categoria", "Mês", "Ano"]
    
    df = df.dropna(subset=["Cliente", "Comercial", "Artigo", "Mês", "Ano"])
    df["Mês"] = df["Mês"].str.strip().str.capitalize()
    df["Ano"] = df["Ano"].astype(int)
    
    meses_map = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }
    df["Mês_Num"] = df["Mês"].map(meses_map)
    df["Data"] = pd.to_datetime(df[["Ano", "Mês_Num"]].assign(day=1))
    
    df["V. Líquido"] = pd.to_numeric(df["V. Líquido"], errors='coerce').fillna(0)
    df["Qtd."] = pd.to_numeric(df["Qtd."], errors='coerce').fillna(0)
    
    return df

df = load_data()

# Sidebar - Filtros
st.sidebar.header("Filtros")

anos = sorted(df["Ano"].unique())
ano_selecionado = st.sidebar.multiselect("Ano", anos, default=anos)

meses_disponiveis = df[df["Ano"].isin(ano_selecionado)]["Mês"].unique()
mes_selecionado = st.sidebar.multiselect("Mês", meses_disponiveis, default=meses_disponiveis)

comerciais = sorted(df["Comercial"].dropna().unique())
comercial_selecionado = st.sidebar.multiselect("Comercial", comerciais, default=comerciais)

clientes = sorted(df["Cliente"].dropna().unique())
cliente_selecionado = st.sidebar.multiselect("Cliente", clientes, default=clientes[:10])

artigos = sorted(df["Artigo"].dropna().unique())
artigo_selecionado = st.sidebar.multiselect("Artigo", artigos, default=[])

# Aplicar filtros
df_filtrado = df.copy()
if ano_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Ano"].isin(ano_selecionado)]
if mes_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Mês"].isin(mes_selecionado)]
if comercial_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Comercial"].isin(comercial_selecionado)]
if cliente_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Cliente"].isin(cliente_selecionado)]
if artigo_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Artigo"].isin(artigo_selecionado)]

# === COMPARAÇÃO COM ANO ANTERIOR ===
anos_selecionados = sorted(df_filtrado["Ano"].unique())
if len(anos_selecionados) > 0:
    ano_atual = max(anos_selecionados)
    ano_anterior = ano_atual - 1
    
    # Dados do ano atual
    df_atual = df_filtrado[df_filtrado["Ano"] == ano_atual].copy()
    df_anterior = df_filtrado[df_filtrado["Ano"] == ano_anterior].copy() if ano_anterior in df["Ano"].values else pd.DataFrame()

    # KPIs Ano Atual
    vendas_atual = df_atual["V. Líquido"].sum()
    clientes_atual = df_atual["Cliente"].nunique()
    vendas_anterior = df_anterior["V. Líquido"].sum() if not df_anterior.empty else 0
    clientes_anterior = df_anterior["Cliente"].nunique() if not df_anterior.empty else 0

    var_vendas = ((vendas_atual - vendas_anterior) / vendas_anterior * 100) if vendas_anterior > 0 else 0
    var_clientes = ((clientes_atual - clientes_anterior) / clientes_anterior * 100) if clientes_anterior > 0 else 0

else:
    vendas_atual = clientes_atual = vendas_anterior = clientes_anterior = 0
    var_vendas = var_clientes = 0
    df_atual = df_anterior = pd.DataFrame()

# KPIs com variação
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Vendas Totais",
        value=f"€{vendas_atual:,.2f}",
        delta=f"{var_vendas:+.1f}%" if vendas_anterior > 0 else "N/A"
    )
with col2:
    st.metric(
        label="Clientes Únicos",
        value=clientes_atual,
        delta=f"{var_clientes:+.1f}%" if clientes_anterior > 0 else "N/A"
    )
with col3:
    st.metric("Artigos Vendidos", df_atual["Artigo"].nunique())
with col4:
    media_cliente = vendas_atual / clientes_atual if clientes_atual > 0 else 0
    st.metric("Média por Cliente", f"€{media_cliente:,.2f}")

# === GRÁFICO: Evolução com Ano Anterior ===
st.markdown("---")
st.subheader("Evolução das Vendas (Este Ano vs Ano Anterior)")

# Preparar dados mensais
if not df_atual.empty:
    mensal_atual = df_atual.groupby(["Mês", "Mês_Num"])["V. Líquido"].sum().reset_index()
    mensal_atual["Período"] = mensal_atual["Mês"] + " " + str(ano_atual)
    mensal_atual = mensal_atual.sort_values("Mês_Num")

if not df_anterior.empty:
    mensal_anterior = df_anterior.groupby(["Mês", "Mês_Num"])["V. Líquido"].sum().reset_index()
    mensal_anterior["Período"] = mensal_anterior["Mês"] + " " + str(ano_anterior)
    mensal_anterior = mensal_anterior.sort_values("Mês_Num")

# Criar gráfico
fig = go.Figure()

if not df_atual.empty:
    fig.add_trace(go.Scatter(
        x=mensal_atual["Período"],
        y=mensal_atual["V. Líquido"],
        mode='lines+markers',
        name=f"{ano_atual} (Atual)",
        line=dict(color="#1f77b4", width=3)
    ))

if not df_anterior.empty:
    fig.add_trace(go.Scatter(
        x=mensal_anterior["Período"],
        y=mensal_anterior["V. Líquido"],
        mode='lines+markers',
        name=f"{ano_anterior} (Anterior)",
        line=dict(color="#ff7f0e", width=3, dash='dot')
    ))

fig.update_layout(
    title=f"Vendas Mensais: {ano_atual} vs {ano_anterior}",
    xaxis_title="Mês",
    yaxis_title="Vendas (€)",
    legend=dict(x=0, y=1.1, orientation="h"),
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)

# === TABELA: Clientes com Queda > 30% ===
st.subheader("Clientes com Queda > 30% vs Ano Anterior")

if not df_anterior.empty:
    vendas_cliente_atual = df_atual.groupby("Cliente")["V. Líquido"].sum()
    vendas_cliente_anterior = df_anterior.groupby("Cliente")["V. Líquido"].sum()
    
    comparacao = pd.DataFrame({
        "Vendas Atual": vendas_cliente_atual,
        "Vendas Anterior": vendas_cliente_anterior
    }).fillna(0)
    
    comparacao["Variação (%)"] = ((comparacao["Vendas Atual"] - comparacao["Vendas Anterior"]) / comparacao["Vendas Anterior"] * 100).round(1)
    comparacao = comparacao[comparacao["Vendas Anterior"] > 0]
    comparacao = comparacao.sort_values("Variação (%)")
    
    # Clientes com queda > 30%
    queda_forte = comparacao[comparacao["Variação (%)"] <= -30]
    
    if not queda_forte.empty:
        st.error(f"{len(queda_forte)} cliente(s) com queda superior a 30%")
        st.dataframe(
            queda_forte.style.format({
                "Vendas Atual": "€{:.2f}",
                "Vendas Anterior": "€{:.2f}",
                "Variação (%)": "{:.1f}%"
            }).background_gradient(subset=["Variação (%)"], cmap="Reds"),
            use_container_width=True
        )
    else:
        st.success("Nenhum cliente com queda superior a 30%")

# === RESUMO POR CLIENTE (com variação) ===
st.subheader("Resumo por Cliente (Este Ano vs Anterior)")

resumo_atual = df_atual.groupby("Cliente").agg({
    "V. Líquido": "sum",
    "Qtd.": "sum",
    "Artigo": "nunique"
}).round(2)

if not df_anterior.empty:
    resumo_anterior = df_anterior.groupby("Cliente").agg({
        "V. Líquido": "sum"
    }).round(2)
    resumo_atual = resumo_atual.join(resumo_anterior, rsuffix=" (Ano Anterior)", how="left").fillna(0)
    resumo_atual["Variação (%)"] = ((resumo_atual["V. Líquido"] - resumo_atual["V. Líquido (Ano Anterior)"]) / resumo_atual["V. Líquido (Ano Anterior)"] * 100).round(1)
else:
    resumo_atual["V. Líquido (Ano Anterior)"] = 0
    resumo_atual["Variação (%)"] = 0

resumo_atual = resumo_atual.rename(columns={
    "V. Líquido": "Vendas Atual (€)",
    "Qtd.": "Qtd. Total",
    "Artigo": "Nº Artigos"
}).sort_values("Vendas Atual (€)", ascending=False)

st.dataframe(
    resumo_atual.style.format({
        "Vendas Atual (€)": "€{:.2f}",
        "V. Líquido (Ano Anterior)": "€{:.2f}",
        "Variação (%)": "{:.1f}%"
    }).background_gradient(subset=["Variação (%)"], cmap="RdYlGn"),
    use_container_width=True
)

# === ALERTA: Clientes que não compraram em algum mês ===
st.markdown("---")
st.subheader("Alerta: Clientes com Compras Interrompidas")

periodos = df_filtrado[["Ano", "Mês", "Mês_Num"]].drop_duplicates().sort_values(["Ano", "Mês_Num"])
clientes_todos = df_filtrado["Cliente"].unique()

if len(periodos) > 1:
    clientes_com_compra = []
    for _, row in periodos.iterrows():
        mask = (df_filtrado["Ano"] == row["Ano"]) & (df_filtrado["Mês"] == row["Mês"])
        clientes_periodo = df_filtrado[mask]["Cliente"].unique()
        clientes_com_compra.append(set(clientes_periodo))

    clientes_ativos = set().union(*clientes_com_compra)
    clientes_faltantes = {}

    for i, (idx, row) in enumerate(periodos.iterrows()):
        mes_ano = f"{row['Mês']} {row['Ano']}"
        clientes_no_mes = clientes_com_compra[i]
        faltantes = clientes_ativos - clientes_no_mes
        if faltantes:
            clientes_faltantes[mes_ano] = sorted(faltantes)

    if clientes_faltantes:
        for mes_ano, lista in clientes_faltantes.items():
            with st.expander(f"{mes_ano} - {len(lista)} cliente(s) ausente(s)"):
                st.write(", ".join(lista))
    else:
        st.success("Todos os clientes ativos compraram em todos os meses!")
else:
    st.info("Selecione pelo menos 2 meses para análise de continuidade.")

# === DOWNLOAD ===
st.markdown("---")
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Baixar Dados Filtrados (CSV)",
    data=csv,
    file_name=f"vendas_filtradas_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)
