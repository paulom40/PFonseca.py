import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io
from datetime import datetime

st.set_page_config(page_title="KPI Compras Clientes", layout="wide")
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
IDX_DATA = 0       # Coluna A
IDX_QTD = 3        # Coluna D
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
df["Mes_Nome"] = df["Mes"].map({
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
})

df["Nome"] = df["Nome"].astype(str).str.strip()
df["Artigo"] = df["Artigo"].astype(str).str.strip()
df["Comercial"] = df["Comercial"].astype(str).str.strip()
df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)
df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").fillna(0).astype(int)

# Resetar índice para evitar problemas
df = df.reset_index(drop=True)

# === Sidebar com filtros interativos MULTISELECT ===
with st.sidebar:
    st.header("🔍 Filtros Interativos")
    
    if st.button("🔄 Atualizar todos os dados"):
        st.cache_data.clear()
        st.rerun()
    
    # === Filtro por ANO (multiselect) ===
    anos_disponiveis = sorted(df["Ano"].unique())
    anos_selecionados = st.multiselect(
        "📅 Selecionar Ano(s)", 
        anos_disponiveis,
        default=anos_disponiveis[-1:] if anos_disponiveis else [],
        key="ano_filter"
    )
    
    # Se nenhum ano selecionado, usar todos
    if not anos_selecionados:
        anos_selecionados = anos_disponiveis
        st.info("ℹ️ Mostrando todos os anos disponíveis")
    
    # === Filtro por MÊS (multiselect) ===
    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                   "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    meses_selecionados = st.multiselect(
        "🗓️ Selecionar Mês(es)", 
        meses_nomes,
        default=meses_nomes,
        key="mes_filter"
    )
    
    # === Filtro por COMERCIAL (multiselect) ===
    comerciais_disponiveis = sorted(df["Comercial"].dropna().unique())
    comerciais_selecionados = st.multiselect(
        "👤 Selecionar Comercial(ais)", 
        comerciais_disponiveis,
        default=comerciais_disponiveis,
        key="comercial_filter"
    )
    
    # === Filtro por CLIENTE (multiselect) ===
    clientes_disponiveis = sorted(df["Nome"].dropna().unique())
    clientes_selecionados = st.multiselect(
        "🏢 Selecionar Cliente(s)", 
        clientes_disponiveis,
        default=clientes_disponiveis,
        key="cliente_filter"
    )
    
    # === Filtro por ARTIGO (multiselect) ===
    artigos_disponiveis = sorted(df["Artigo"].dropna().unique())
    artigos_selecionados = st.multiselect(
        "📦 Selecionar Artigo(s)", 
        artigos_disponiveis,
        default=artigos_disponiveis,
        key="artigo_filter"
    )
    
    if st.button("🗑️ Limpar todos os filtros"):
        st.rerun()
    
    # Mostrar estatísticas dos filtros
    with st.expander("📊 Estatísticas dos Filtros"):
        st.write(f"**Anos selecionados:** {len(anos_selecionados)} de {len(anos_disponiveis)}")
        st.write(f"**Meses selecionados:** {len(meses_selecionados)} de 12")
        st.write(f"**Comerciais selecionados:** {len(comerciais_selecionados)} de {len(comerciais_disponiveis)}")
        st.write(f"**Clientes selecionados:** {len(clientes_selecionados)} de {len(clientes_disponiveis)}")
        st.write(f"**Artigos selecionados:** {len(artigos_selecionados)} de {len(artigos_disponiveis)}")

# === Aplicar filtros ao dataframe ===
df_filtrado = df.copy()

# 1. Filtrar por ANO
df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos_selecionados)]

# 2. Filtrar por MÊS
meses_map = dict(zip(meses_nomes, range(1, 13)))
meses_num_selecionados = [meses_map[m] for m in meses_selecionados]
df_filtrado = df_filtrado[df_filtrado["Mes"].isin(meses_num_selecionados)]

# 3. Filtrar por COMERCIAL
if comerciais_selecionados:
    df_filtrado = df_filtrado[df_filtrado["Comercial"].isin(comerciais_selecionados)]

# 4. Filtrar por CLIENTE
if clientes_selecionados:
    df_filtrado = df_filtrado[df_filtrado["Nome"].isin(clientes_selecionados)]

# 5. Filtrar por ARTIGO
if artigos_selecionados:
    df_filtrado = df_filtrado[df_filtrado["Artigo"].isin(artigos_selecionados)]

# === Mostrar informações sobre os filtros aplicados ===
st.subheader("ℹ️ Filtros Aplicados")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Anos", len(anos_selecionados))
with col2:
    st.metric("Meses", len(meses_selecionados))
with col3:
    st.metric("Comerciais", len(comerciais_selecionados) if comerciais_selecionados else "Todos")
with col4:
    st.metric("Clientes", len(clientes_selecionados) if clientes_selecionados else "Todos")
with col5:
    st.metric("Artigos", len(artigos_selecionados) if artigos_selecionados else "Todos")

# === Análise por Ano (comparação entre anos selecionados) ===
if len(anos_selecionados) > 1:
    st.subheader("📈 Comparativo Entre Anos")
    
    # Agrupar por ano e mês
    comparativo_ano = df_filtrado.groupby(["Ano", "Mes_Nome", "Mes"])["Quantidade"].sum().reset_index()
    comparativo_ano = comparativo_ano.sort_values(["Ano", "Mes"])
    
    # Pivot table para comparação
    pivot_comparativo = comparativo_ano.pivot_table(
        index=["Mes_Nome", "Mes"],
        columns="Ano",
        values="Quantidade",
        aggfunc="sum",
        fill_value=0
    ).reset_index()
    
    # Ordenar por mês
    pivot_comparativo = pivot_comparativo.sort_values("Mes")
    
    # Calcular variações se tiver mais de um ano
    if len(anos_selecionados) == 2:
        ano1, ano2 = sorted(anos_selecionados)
        if ano1 in pivot_comparativo.columns and ano2 in pivot_comparativo.columns:
            pivot_comparativo["Variação_%"] = (
                (pivot_comparativo[ano2] - pivot_comparativo[ano1]) / 
                pivot_comparativo[ano1].replace(0, pd.NA)
            ) * 100
            
            # Exibir tabela formatada
            st.dataframe(
                pivot_comparativo[["Mes_Nome", ano1, ano2, "Variação_%"]]
                .style.format({
                    str(ano1): "{:,.0f}",
                    str(ano2): "{:,.0f}",
                    "Variação_%": "{:+.1f}%"
                }).applymap(
                    lambda x: 'background-color: #FF6B6B' if isinstance(x, (int, float)) and x < 0 else 
                             ('background-color: #51CF66' if isinstance(x, (int, float)) and x > 0 else ''),
                    subset=["Variação_%"]
                ),
                height=400
            )
            
            # Gráfico de linha comparativo
            fig_comparativo, ax_comparativo = plt.subplots(figsize=(12, 6))
            for ano in sorted(anos_selecionados):
                dados_ano = pivot_comparativo.sort_values("Mes")
                ax_comparativo.plot(
                    dados_ano["Mes_Nome"], 
                    dados_ano[ano], 
                    marker='o', 
                    label=f"Ano {ano}"
                )
            
            ax_comparativo.set_title(f"Comparativo Mensal: {min(anos_selecionados)} vs {max(anos_selecionados)}")
            ax_comparativo.set_xlabel("Mês")
            ax_comparativo.set_ylabel("Quantidade")
            ax_comparativo.legend()
            ax_comparativo.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig_comparativo)
    else:
        # Mostrar tabela simples para múltiplos anos
        st.dataframe(
            pivot_comparativo.drop(columns=["Mes"]).style.format({
                str(ano): "{:,.0f}" for ano in anos_selecionados if ano in pivot_comparativo.columns
            }),
            height=400
        )

# === KPI 1 – Total de quantidade por cliente ===
st.subheader("📊 KPI 1 – Total de Quantidade Comprada por Cliente")

if not df_filtrado.empty:
    kpi_cliente = (
        df_filtrado.groupby("Nome")["Quantidade"]
        .sum()
        .reset_index()
        .sort_values("Quantidade", ascending=False)
    )
    
    # Mostrar top 15
    top_n = min(15, len(kpi_cliente))
    kpi_cliente_top = kpi_cliente.head(top_n)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not kpi_cliente_top.empty:
            fig1, ax1 = plt.subplots(figsize=(12, 6))
            bars = ax1.barh(kpi_cliente_top["Nome"], kpi_cliente_top["Quantidade"], 
                           color=plt.cm.viridis(range(top_n)))
            ax1.set_xlabel("Quantidade Total")
            ax1.set_title(f"Top {top_n} Clientes")
            ax1.invert_yaxis()
            
            # Adicionar valores nas barras
            max_val = kpi_cliente_top["Quantidade"].max()
            for bar in bars:
                width = bar.get_width()
                ax1.text(width + max_val * 0.01, 
                        bar.get_y() + bar.get_height()/2,
                        f'{int(width):,}', 
                        ha='left', va='center',
                        fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig1)
    
    with col2:
        st.dataframe(
            kpi_cliente_top.style.format({"Quantidade": "{:,.0f}"})
            .background_gradient(subset=["Quantidade"], cmap="viridis"),
            height=500
        )
    
    # Estatísticas dos clientes
    st.subheader("📈 Estatísticas de Clientes")
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        total_clientes = len(kpi_cliente)
        st.metric("Total Clientes", total_clientes)
    
    with col_stat2:
        media_por_cliente = kpi_cliente["Quantidade"].mean()
        st.metric("Média por Cliente", f"{media_por_cliente:,.0f}")
    
    with col_stat3:
        top_10_percent = kpi_cliente.head(max(1, int(len(kpi_cliente) * 0.1)))["Quantidade"].sum() / kpi_cliente["Quantidade"].sum() * 100
        st.metric("Top 10%", f"{top_10_percent:.1f}%")
    
    with col_stat4:
        quantidade_total = kpi_cliente["Quantidade"].sum()
        st.metric("Quantidade Total", f"{quantidade_total:,.0f}")

# === KPI 2 – Percentagem de quantidade por artigo dentro de cada cliente ===
st.subheader("📊 KPI 2 – Distribuição Percentual por Artigo")

if not df_filtrado.empty and len(df_filtrado) > 0:
    # Calcular percentagens de forma segura
    df_perc = df_filtrado.copy()
    
    # Calcular totais por cliente
    total_por_cliente = df_perc.groupby("Nome")["Quantidade"].sum()
    
    # Função para calcular percentagem
    def calcular_percentagem(row):
        try:
            cliente = row["Nome"]
            quantidade = row["Quantidade"]
            total_cliente = total_por_cliente.get(cliente, 0)
            return (quantidade / total_cliente * 100) if total_cliente > 0 else 0
        except:
            return 0
    
    # Aplicar função
    df_perc["Percentagem"] = df_perc.apply(calcular_percentagem, axis=1)
    
    # Agrupar por cliente e artigo
    kpi_artigo_cliente = (
        df_perc.groupby(["Nome", "Artigo"], as_index=False)
        .agg({"Quantidade": "sum", "Percentagem": "sum"})
        .sort_values(["Nome", "Percentagem"], ascending=[True, False])
    )
    
    # Top artigos por cliente (máximo 5 artigos por cliente para melhor visualização)
    kpi_artigo_cliente_top = kpi_artigo_cliente.groupby("Nome").head(5)
    
    # Exibir tabela
    st.dataframe(
        kpi_artigo_cliente_top.style.format({
            "Quantidade": "{:,.0f}",
            "Percentagem": "{:.1f}%"
        }).background_gradient(subset=["Percentagem"], cmap="YlOrRd"),
        height=500
    )
    
    # Gráfico de heatmap para top clientes
    if len(kpi_artigo_cliente_top["Nome"].unique()) > 0:
        # Selecionar top 10 clientes para visualização
        top_clientes = kpi_cliente.head(10)["Nome"].tolist()
        dados_top = kpi_artigo_cliente_top[kpi_artigo_cliente_top["Nome"].isin(top_clientes)]
        
        if not dados_top.empty:
            # Criar pivot para heatmap
            pivot_heatmap = dados_top.pivot_table(
                index="Nome",
                columns="Artigo",
                values="Percentagem",
                aggfunc="sum",
                fill_value=0
            )
            
            # Ordenar por total de percentagem
            pivot_heatmap = pivot_heatmap.loc[top_clientes]
            
            # Criar heatmap
            fig_heatmap, ax_heatmap = plt.subplots(figsize=(14, 8))
            im = ax_heatmap.imshow(pivot_heatmap.values, aspect='auto', cmap='YlOrRd')
            
            # Configurar eixos
            ax_heatmap.set_xticks(range(len(pivot_heatmap.columns)))
            ax_heatmap.set_yticks(range(len(pivot_heatmap.index)))
            ax_heatmap.set_xticklabels(pivot_heatmap.columns, rotation=45, ha='right')
            ax_heatmap.set_yticklabels(pivot_heatmap.index)
            
            # Adicionar barra de cores
            plt.colorbar(im, ax=ax_heatmap, label='Percentagem (%)')
            ax_heatmap.set_title("Heatmap - Distribuição de Artigos por Cliente (Top 10)")
            plt.tight_layout()
            st.pyplot(fig_heatmap)

# === KPI 3 – Análise por Comercial ===
st.subheader("👤 KPI 3 – Desempenho por Comercial")

if not df_filtrado.empty:
    # Análise por comercial
    kpi_comercial = (
        df_filtrado.groupby("Comercial")
        .agg({
            "Quantidade": "sum",
            "Nome": "nunique",
            "Artigo": "nunique"
        })
        .reset_index()
        .rename(columns={
            "Nome": "Clientes_Unicos",
            "Artigo": "Artigos_Unicos"
        })
        .sort_values("Quantidade", ascending=False)
    )
    
    col_kpi1, col_kpi2 = st.columns(2)
    
    with col_kpi1:
        st.dataframe(
            kpi_comercial.style.format({
                "Quantidade": "{:,.0f}",
                "Clientes_Unicos": "{:,.0f}",
                "Artigos_Unicos": "{:,.0f}"
            }).background_gradient(subset=["Quantidade"], cmap="Blues"),
            height=400
        )
    
    with col_kpi2:
        if not kpi_comercial.empty:
            fig_comercial, ax_comercial = plt.subplots(figsize=(10, 6))
            bars = ax_comercial.bar(kpi_comercial["Comercial"], kpi_comercial["Quantidade"], 
                                   color=plt.cm.Set3(range(len(kpi_comercial))))
            ax_comercial.set_title("Quantidade por Comercial")
            ax_comercial.set_xlabel("Comercial")
            ax_comercial.set_ylabel("Quantidade Total")
            plt.xticks(rotation=45, ha='right')
            
            # Adicionar valores no topo das barras
            for bar in bars:
                height = bar.get_height()
                ax_comercial.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                                 f'{int(height):,}', ha='center', va='bottom', 
                                 fontsize=9, rotation=0)
            
            plt.tight_layout()
            st.pyplot(fig_comercial)

# === Exportar para Excel ===
st.subheader("📥 Exportar Resultados")

if not df_filtrado.empty:
    if st.button("💾 Gerar Relatório Excel Completo"):
        # Criar Excel com múltiplas abas
        xls_buf = io.BytesIO()
        with pd.ExcelWriter(xls_buf, engine='xlsxwriter') as writer:
            # Aba 1: Dados filtrados
            df_filtrado.to_excel(writer, sheet_name='Dados_Filtrados', index=False)
            
            # Aba 2: KPI Clientes
            if 'kpi_cliente' in locals() and not kpi_cliente.empty:
                kpi_cliente.to_excel(writer, sheet_name='KPI_Clientes', index=False)
            
            # Aba 3: Distribuição por Artigo
            if 'kpi_artigo_cliente_top' in locals() and not kpi_artigo_cliente_top.empty:
                kpi_artigo_cliente_top.to_excel(writer, sheet_name='Distrib_Artigo', index=False)
            
            # Aba 4: KPI Comercial
            if 'kpi_comercial' in locals() and not kpi_comercial.empty:
                kpi_comercial.to_excel(writer, sheet_name='KPI_Comercial', index=False)
            
            # Aba 5: Resumo de Filtros
            resumo_filtros = pd.DataFrame({
                'Filtro': ['Anos', 'Meses', 'Comerciais', 'Clientes', 'Artigos'],
                'Selecionados': [
                    ', '.join(map(str, anos_selecionados)),
                    ', '.join(meses_selecionados),
                    str(len(comerciais_selecionados)) if comerciais_selecionados else 'Todos',
                    str(len(clientes_selecionados)) if clientes_selecionados else 'Todos',
                    str(len(artigos_selecionados)) if artigos_selecionados else 'Todos'
                ]
            })
            resumo_filtros.to_excel(writer, sheet_name='Resumo_Filtros', index=False)
            
            # Formatar largura das colunas
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                worksheet.set_column('A:Z', 20)
        
        # Botão de download
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label=f"⬇️ Download do Relatório Excel ({timestamp})",
            data=xls_buf.getvalue(),
            file_name=f"relatorio_compras_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("Não há dados filtrados para exportar")

# === Resumo Geral ===
st.subheader("📊 Resumo Geral")

if not df_filtrado.empty:
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    
    with col_res1:
        total_quantidade = df_filtrado["Quantidade"].sum()
        st.metric("Quantidade Total", f"{total_quantidade:,.0f}")
    
    with col_res2:
        total_registos = len(df_filtrado)
        st.metric("Registos Totais", f"{total_registos:,}")
    
    with col_res3:
        clientes_unicos = df_filtrado["Nome"].nunique()
        st.metric("Clientes Únicos", clientes_unicos)
    
    with col_res4:
        artigos_unicos = df_filtrado["Artigo"].nunique()
        st.metric("Artigos Únicos", artigos_unicos)
    
    # Distribuição por ano
    st.subheader("📅 Distribuição por Ano")
    distribuicao_ano = df_filtrado.groupby("Ano")["Quantidade"].sum().reset_index()
    
    col_dist1, col_dist2 = st.columns([1, 2])
    
    with col_dist1:
        st.dataframe(
            distribuicao_ano.style.format({"Quantidade": "{:,.0f}"})
            .background_gradient(subset=["Quantidade"], cmap="Greens"),
            height=200
        )
    
    with col_dist2:
        if len(distribuicao_ano) > 0:
            fig_dist, ax_dist = plt.subplots(figsize=(10, 4))
            ax_dist.bar(distribuicao_ano["Ano"].astype(str), 
                       distribuicao_ano["Quantidade"], 
                       color='#2ecc71')
            ax_dist.set_title("Distribuição por Ano")
            ax_dist.set_xlabel("Ano")
            ax_dist.set_ylabel("Quantidade")
            
            # Adicionar valores no topo das barras
            for i, (ano, qtd) in enumerate(zip(distribuicao_ano["Ano"], distribuicao_ano["Quantidade"])):
                ax_dist.text(i, qtd + max(distribuicao_ano["Quantidade"]) * 0.01, 
                           f'{int(qtd):,}', ha='center', va='bottom')
            
            plt.tight_layout()
            st.pyplot(fig_dist)

# === Instruções ===
with st.expander("ℹ️ Instruções de Uso"):
    st.markdown("""
    ## 📋 Como usar este dashboard
    
    ### 🔍 Filtros Interativos (Sidebar)
    Todos os filtros são **multiselect** - pode selecionar múltiplos valores:
    
    1. **📅 Ano(s)** - Selecione um ou mais anos para análise
    2. **🗓️ Mês(es)** - Selecione os meses a incluir
    3. **👤 Comercial(ais)** - Filtre por um ou mais comerciais
    4. **🏢 Cliente(s)** - Filtre por um ou mais clientes
    5. **📦 Artigo(s)** - Filtre por um ou mais artigos
    
    ### 📊 KPIs Principais
    1. **KPI 1 - Clientes** - Top clientes por volume de compras
    2. **KPI 2 - Artigos** - Distribuição percentual de artigos por cliente
    3. **KPI 3 - Comerciais** - Desempenho por comercial
    
    ### 📥 Exportação
    - **Gerar Relatório Excel** - Exporta todos os dados filtrados e análises para Excel
    - Inclui múltiplas abas com todos os KPIs
    
    ### 💡 Dicas
    - Use **Ctrl+Click** para selecionar múltiplos itens nos filtros
    - Clique no **❌** ao lado dos itens selecionados para removê-los
    - **🔄 Atualizar dados** recarrega do ficheiro original
    - **🗑️ Limpar filtros** remove todas as seleções
    
    ### 📍 Mapeamento de Colunas
    - Coluna B (Índice 1): **Nome do Cliente**
    - Coluna C (Índice 2): **Artigo**
    - Coluna I (Índice 8): **Comercial**
    - Coluna K (Índice 10): **Ano**
    """)
