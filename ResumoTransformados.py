import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io
from datetime import datetime

st.set_page_config(page_title="KPI Compras Clientes (YoY)", layout="wide")
st.title("📊 Dashboard de Compras – Clientes, Artigos e Comerciais")

# --- URL raw do ficheiro no GitHub ---
RAW_URL = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"

# === 1. Ler ficheiro diretamente ===
@st.cache_data(ttl=3600)
def load_data():
    try:
        df_raw = pd.read_excel(RAW_URL)
        return df_raw
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df_raw = load_data()

if df_raw.empty:
    st.stop()

# === 2. Mapear colunas por índice conforme especificado ===
IDX_NOME = 1       # Coluna B
IDX_ARTIGO = 2     # Coluna C
IDX_COMERCIAL = 8  # Coluna I
IDX_DATA = 0       # Coluna A (ajustar se necessário)
IDX_QTD = 3        # Coluna D (ajustar se necessário)
IDX_ANO = 10       # Coluna K

# Construir dataframe canónico
df = pd.DataFrame({
    "Nome": df_raw.iloc[:, IDX_NOME],
    "Artigo": df_raw.iloc[:, IDX_ARTIGO],
    "Comercial": df_raw.iloc[:, IDX_COMERCIAL],
    "Data": df_raw.iloc[:, IDX_DATA],
    "Quantidade": df_raw.iloc[:, IDX_QTD],
    "Ano": df_raw.iloc[:, IDX_ANO]  # Coluna K
})

# === 3. Normalização ===
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

# Remover dados inválidos
df = df[df["Data"].notna()]
df = df[df["Data"].dt.year >= 2000]

# Se a coluna Ano não estiver preenchida, extrair do Data
if df["Ano"].isna().any():
    df["Ano"] = df["Data"].dt.year

df["Mes"] = df["Data"].dt.month

df["Nome"] = df["Nome"].astype(str).str.strip()
df["Artigo"] = df["Artigo"].astype(str).str.strip()
df["Comercial"] = df["Comercial"].astype(str).str.strip()
df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)
df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").fillna(0).astype(int)

# === Sidebar com filtros interativos ===
with st.sidebar:
    st.header("🔍 Filtros Interativos")
    
    if st.button("🔄 Atualizar todos os dados"):
        st.cache_data.clear()
        st.rerun()
    
    # Filtro por Ano (Coluna K)
    anos_disponiveis = sorted(df["Ano"].unique())
    ano_base = st.selectbox("📅 Ano base", anos_disponiveis, 
                          index=len(anos_disponiveis)-2 if len(anos_disponiveis) >= 2 else 0)
    ano_comp = st.selectbox("📅 Ano comparação", anos_disponiveis, 
                          index=len(anos_disponiveis)-1 if len(anos_disponiveis) >= 1 else 0)
    
    # Filtro por Mês
    meses_nomes = ["Jan","Fev","Mar","Abr","Mai","Jun",
                   "Jul","Ago","Set","Out","Nov","Dez"]
    meses_sel = st.multiselect("🗓️ Selecionar meses", meses_nomes, default=meses_nomes)
    
    # Filtro por Comercial (Coluna I)
    comerciais_opts = ["Todos"] + sorted(df["Comercial"].dropna().unique().tolist())
    comercial_sel = st.selectbox("👤 Comercial", comerciais_opts)
    
    # Filtro por Cliente (Coluna B)
    if comercial_sel != "Todos":
        clientes_filtrados = sorted(df[df["Comercial"] == comercial_sel]["Nome"].dropna().unique())
    else:
        clientes_filtrados = sorted(df["Nome"].dropna().unique())
    
    clientes_opts = ["Todos"] + clientes_filtrados
    cliente_sel = st.selectbox("🏢 Cliente", clientes_opts)
    
    # Filtro por Artigo (Coluna C)
    if cliente_sel != "Todos":
        artigos_filtrados = sorted(df[df["Nome"] == cliente_sel]["Artigo"].dropna().unique())
    elif comercial_sel != "Todos":
        artigos_filtrados = sorted(df[df["Comercial"] == comercial_sel]["Artigo"].dropna().unique())
    else:
        artigos_filtrados = sorted(df["Artigo"].dropna().unique())
    
    artigos_opts = ["Todos"] + artigos_filtrados
    artigo_sel = st.selectbox("📦 Artigo", artigos_opts)
    
    if st.button("🗑️ Limpar filtros"):
        st.rerun()

# === Aplicar filtros ao dataframe ===
df_filtrado = df.copy()

# Filtro por Ano
df_filtrado = df_filtrado[df_filtrado["Ano"].isin([ano_base, ano_comp])]

# Filtro por Mês
meses_map = dict(zip(meses_nomes, range(1, 13)))
meses_sel_num = [meses_map[m] for m in meses_sel]
df_filtrado = df_filtrado[df_filtrado["Mes"].isin(meses_sel_num)]

# Filtro por Comercial
if comercial_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Comercial"] == comercial_sel]

# Filtro por Cliente
if cliente_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Nome"] == cliente_sel]

# Filtro por Artigo
if artigo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Artigo"] == artigo_sel]

# === KPI agregado ===
kpi = df_filtrado.groupby(
    ["Comercial", "Nome", "Artigo", "Ano", "Mes"],
    as_index=False
)["Quantidade"].sum()

# === Tabela comparativa YoY ===
st.subheader("📈 Comparativo Ano a Ano (YoY)")

# Criar pivot table
pv = kpi.pivot_table(
    index=["Comercial", "Nome", "Artigo", "Mes"],
    columns="Ano",
    values="Quantidade",
    aggfunc="sum",
    fill_value=0
).reset_index()

# Adicionar coluna de variação
if ano_base in pv.columns and ano_comp in pv.columns:
    pv["Variação_%"] = pv.apply(
        lambda row: ((row[ano_comp] - row[ano_base]) / row[ano_base] * 100) 
        if row[ano_base] != 0 else (100 if row[ano_comp] > 0 else 0),
        axis=1
    )
    
    # Formatar a exibição
    pv["Mês"] = pv["Mes"].apply(lambda m: meses_nomes[m-1] if 1 <= m <= 12 else str(m))
    
    # Reordenar colunas
    cols_order = ["Comercial", "Nome", "Artigo", "Mês", ano_base, ano_comp, "Variação_%"]
    pv = pv[[col for col in cols_order if col in pv.columns]]
    
    # Exibir tabela formatada
    st.dataframe(
        pv.style.format({
            ano_base: "{:,.0f}",
            ano_comp: "{:,.0f}",
            "Variação_%": "{:+.2f}%"
        }).bar(subset=["Variação_%"], align='mid', color=['#FF6B6B', '#51CF66'])
    )
else:
    st.warning("Não há dados para os anos selecionados")

# === KPI 1 – Total de quantidade por cliente ===
st.subheader("📊 KPI 1 – Total de Quantidade Comprada por Cliente")

kpi_cliente = (
    df_filtrado.groupby("Nome")["Quantidade"]
    .sum()
    .reset_index()
    .sort_values("Quantidade", ascending=False)
    .head(10)  # Mostrar apenas top 10
)

col1, col2 = st.columns([2, 1])

with col1:
    if not kpi_cliente.empty:
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        bars = ax1.barh(kpi_cliente["Nome"], kpi_cliente["Quantidade"], color="steelblue")
        ax1.set_xlabel("Quantidade Total")
        ax1.set_title(f"Top 10 Clientes ({ano_base} vs {ano_comp})")
        ax1.invert_yaxis()  # Maior no topo
        
        # Adicionar valores nas barras
        for bar in bars:
            width = bar.get_width()
            ax1.text(width + max(kpi_cliente["Quantidade"]) * 0.01, 
                    bar.get_y() + bar.get_height()/2,
                    f'{int(width):,}', 
                    ha='left', va='center')
        
        st.pyplot(fig1)

with col2:
    st.dataframe(
        kpi_cliente.style.format({"Quantidade": "{:,.0f}"})
        .bar(subset=["Quantidade"], color='#51CF66')
    )

# === KPI 2 – Percentagem de quantidade por artigo dentro de cada cliente ===
st.subheader("📊 KPI 2 – Distribuição Percentual por Artigo")

# Calcular totais por cliente
total_por_cliente = df_filtrado.groupby("Nome")["Quantidade"].sum()

# Criar DataFrame para percentagens
df_perc = df_filtrado.copy()
df_perc["Percentagem"] = df_perc.apply(
    lambda row: (row["Quantidade"] / total_por_cliente[row["Nome"]] * 100) 
    if total_por_cliente[row["Nome"]] != 0 else 0,
    axis=1
)

kpi_artigo_cliente = (
    df_perc.groupby(["Nome", "Artigo"], as_index=False)["Percentagem"]
    .sum()
    .sort_values(["Nome", "Percentagem"], ascending=[True, False])
    .head(20)  # Limitar para melhor visualização
)

# Exibir tabela
st.dataframe(
    kpi_artigo_cliente.style.format({"Percentagem": "{:.1f}%"})
    .bar(subset=["Percentagem"], color='#FFA726')
)

# Gráfico de distribuição (apenas se houver dados razoáveis)
if len(kpi_artigo_cliente["Nome"].unique()) <= 15:
    pivot_perc = kpi_artigo_cliente.pivot(
        index="Nome", 
        columns="Artigo", 
        values="Percentagem"
    ).fillna(0)
    
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    pivot_perc.plot(kind="bar", stacked=True, ax=ax2, colormap="tab20c")
    ax2.set_title("Distribuição Percentual por Artigo")
    ax2.set_ylabel("%")
    ax2.set_xlabel("Cliente")
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig2)

# === Exportar para Excel ===
st.subheader("📥 Exportar Resultados")

if st.button("💾 Gerar Relatório Excel"):
    # Criar Excel com múltiplas abas
    xls_buf = io.BytesIO()
    with pd.ExcelWriter(xls_buf, engine='xlsxwriter') as writer:
        # Aba 1: Dados filtrados
        df_filtrado.to_excel(writer, sheet_name='Dados_Filtrados', index=False)
        
        # Aba 2: Comparativo YoY
        if 'pv' in locals():
            pv.to_excel(writer, sheet_name='Comparativo_YoY', index=False)
        
        # Aba 3: KPI Clientes
        kpi_cliente.to_excel(writer, sheet_name='KPI_Clientes', index=False)
        
        # Aba 4: Distribuição por Artigo
        kpi_artigo_cliente.to_excel(writer, sheet_name='Distrib_Artigo', index=False)
        
        # Formatar largura das colunas
        for sheet in writer.sheets:
            worksheet = writer.sheets[sheet]
            for i, col in enumerate(df_filtrado.columns):
                column_len = max(
                    df_filtrado[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet.set_column(i, i, min(column_len, 30))
    
    # Botão de download
    st.download_button(
        label="⬇️ Download do Relatório Excel",
        data=xls_buf.getvalue(),
        file_name=f"relatorio_compras_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# === Métricas de resumo ===
st.subheader("📈 Métricas de Resumo")

if not df_filtrado.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    total_ano_base = df_filtrado[df_filtrado["Ano"] == ano_base]["Quantidade"].sum()
    total_ano_comp = df_filtrado[df_filtrado["Ano"] == ano_comp]["Quantidade"].sum()
    variacao_total = ((total_ano_comp - total_ano_base) / total_ano_base * 100) if total_ano_base != 0 else 0
    
    with col1:
        st.metric(f"Total {ano_base}", f"{total_ano_base:,.0f}")
    
    with col2:
        st.metric(f"Total {ano_comp}", f"{total_ano_comp:,.0f}")
    
    with col3:
        st.metric("Variação", f"{variacao_total:+.1f}%")
    
    with col4:
        clientes_unicos = df_filtrado["Nome"].nunique()
        st.metric("Clientes Únicos", clientes_unicos)

# === Instruções ===
with st.expander("ℹ️ Instruções de uso"):
    st.markdown("""
    **Como usar este dashboard:**
    
    1. **Filtros (sidebar à esquerda):**
       - 📅 **Ano base/comparação**: Selecione os anos para comparação
       - 🗓️ **Meses**: Selecione os meses a incluir na análise
       - 👤 **Comercial**: Filtre por comercial específico
       - 🏢 **Cliente**: Filtre por cliente específico
       - 📦 **Artigo**: Filtre por artigo específico
    
    2. **Visualizações principais:**
       - 📈 **Comparativo YoY**: Tabela interativa com variação percentual
       - 📊 **KPI Clientes**: Gráfico dos principais clientes
       - 📊 **Distribuição por Artigo**: Análise percentual por artigo
    
    3. **Exportação:**
       - 💾 **Botão de exportação**: Gera relatório Excel com todas as análises
    
    **Notas:**
    - Os filtros são aplicados sequencialmente
    - A coluna K (Índice 10) é usada para o ano
    - Use "Limpar filtros" para recomeçar
    """)
