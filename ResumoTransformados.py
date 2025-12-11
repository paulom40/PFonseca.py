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
    st.error("Não foi possível carregar os dados. Verifique a URL do ficheiro.")
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

# Inicializar session state para filtros
if 'filtros_aplicados' not in st.session_state:
    st.session_state.filtros_aplicados = False

# === Sidebar com filtros interativos ===
with st.sidebar:
    st.header("🔍 Filtros Interativos")
    
    # Botão para recarregar dados
    if st.button("🔄 Atualizar dados do ficheiro"):
        st.cache_data.clear()
        st.rerun()
    
    # === Filtro por ANO ===
    anos_disponiveis = sorted(df["Ano"].unique())
    if anos_disponiveis:
        anos_selecionados = st.multiselect(
            "📅 Selecionar Ano(s)", 
            options=anos_disponiveis,
            default=anos_disponiveis[-1:] if anos_disponiveis else [],
            key="filtro_anos"
        )
    else:
        anos_selecionados = []
        st.warning("Não há anos disponíveis nos dados")
    
    # Se nenhum ano selecionado, usar todos
    if not anos_selecionados and anos_disponiveis:
        anos_selecionados = anos_disponiveis
    
    # === Filtro por MÊS ===
    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                   "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    meses_selecionados = st.multiselect(
        "🗓️ Selecionar Mês(es)", 
        options=meses_nomes,
        default=meses_nomes,
        key="filtro_meses"
    )
    
    # Se nenhum mês selecionado, usar todos
    if not meses_selecionados:
        meses_selecionados = meses_nomes
    
    # === Filtro por COMERCIAL ===
    comerciais_disponiveis = sorted(df["Comercial"].dropna().unique())
    if comerciais_disponiveis:
        comerciais_selecionados = st.multiselect(
            "👤 Selecionar Comercial(ais)", 
            options=comerciais_disponiveis,
            default=comerciais_disponiveis,
            key="filtro_comerciais"
        )
    else:
        comerciais_selecionados = []
        st.warning("Não há comerciais disponíveis nos dados")
    
    # Se nenhum comercial selecionado, usar todos
    if not comerciais_selecionados and comerciais_disponiveis:
        comerciais_selecionados = comerciais_disponiveis
    
    # === Filtro por CLIENTE ===
    clientes_disponiveis = sorted(df["Nome"].dropna().unique())
    if clientes_disponiveis:
        clientes_selecionados = st.multiselect(
            "🏢 Selecionar Cliente(s)", 
            options=clientes_disponiveis,
            default=clientes_disponiveis,
            key="filtro_clientes"
        )
    else:
        clientes_selecionados = []
        st.warning("Não há clientes disponíveis nos dados")
    
    # Se nenhum cliente selecionado, usar todos
    if not clientes_selecionados and clientes_disponiveis:
        clientes_selecionados = clientes_disponiveis
    
    # === Filtro por ARTIGO ===
    artigos_disponiveis = sorted(df["Artigo"].dropna().unique())
    if artigos_disponiveis:
        artigos_selecionados = st.multiselect(
            "📦 Selecionar Artigo(s)", 
            options=artigos_disponiveis,
            default=artigos_disponiveis,
            key="filtro_artigos"
        )
    else:
        artigos_selecionados = []
        st.warning("Não há artigos disponíveis nos dados")
    
    # Se nenhum artigo selecionado, usar todos
    if not artigos_selecionados and artigos_disponiveis:
        artigos_selecionados = artigos_disponiveis
    
    # Botão para aplicar filtros
    if st.button("✅ Aplicar Filtros", type="primary"):
        st.session_state.filtros_aplicados = True
        st.rerun()
    
    # Botão para limpar filtros
    if st.button("🗑️ Limpar Filtros"):
        st.session_state.filtros_aplicados = False
        st.rerun()

# === Aplicar filtros ao dataframe ===
df_filtrado = df.copy()

# Mostrar status dos filtros
if st.session_state.filtros_aplicados:
    st.success("✅ Filtros aplicados!")
else:
    st.info("ℹ️ Configure os filtros na sidebar e clique em 'Aplicar Filtros'")

# 1. Filtrar por ANO
if anos_selecionados:
    df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos_selecionados)]

# 2. Filtrar por MÊS
if meses_selecionados:
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
st.subheader("📋 Resumo dos Filtros Aplicados")

if st.session_state.filtros_aplicados:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Anos", len(anos_selecionados) if anos_selecionados else "Todos")
    
    with col2:
        st.metric("Meses", len(meses_selecionados) if meses_selecionados else "Todos")
    
    with col3:
        st.metric("Comerciais", len(comerciais_selecionados) if comerciais_selecionados else "Todos")
    
    with col4:
        st.metric("Clientes", len(clientes_selecionados) if clientes_selecionados else "Todos")
    
    with col5:
        st.metric("Artigos", len(artigos_selecionados) if artigos_selecionados else "Todos")
    
    # Mostrar valores selecionados
    with st.expander("📝 Ver valores selecionados"):
        if anos_selecionados:
            st.write(f"**Anos:** {', '.join(map(str, anos_selecionados))}")
        if meses_selecionados:
            st.write(f"**Meses:** {', '.join(meses_selecionados)}")
        if comerciais_selecionados:
            st.write(f"**Comerciais:** {', '.join(comerciais_selecionados[:10])}" + 
                    ("..." if len(comerciais_selecionados) > 10 else ""))
        if clientes_selecionados:
            st.write(f"**Clientes:** {', '.join(clientes_selecionados[:10])}" + 
                    ("..." if len(clientes_selecionados) > 10 else ""))
        if artigos_selecionados:
            st.write(f"**Artigos:** {', '.join(artigos_selecionados[:10])}" + 
                    ("..." if len(artigos_selecionados) > 10 else ""))

# === Verificação de dados filtrados ===
if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros aplicados. Tente ajustar os filtros.")
    
    # Mostrar estatísticas dos dados originais
    with st.expander("📊 Estatísticas dos dados originais"):
        st.write(f"**Total de registos:** {len(df):,}")
        st.write(f"**Anos disponíveis:** {sorted(df['Ano'].unique())}")
        st.write(f"**Número de clientes:** {df['Nome'].nunique():,}")
        st.write(f"**Número de artigos:** {df['Artigo'].nunique():,}")
        st.write(f"**Número de comerciais:** {df['Comercial'].nunique():,}")
        st.write(f"**Período dos dados:** {df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}")
    
    st.stop()

# === KPI 1 – Total de quantidade por cliente ===
st.subheader("📊 KPI 1 – Total de Quantidade Comprada por Cliente")

# Garantir que temos dados filtrados
if not df_filtrado.empty:
    kpi_cliente = (
        df_filtrado.groupby("Nome")["Quantidade"]
        .sum()
        .reset_index()
        .sort_values("Quantidade", ascending=False)
    )
    
    # Mostrar top 10
    top_n = min(10, len(kpi_cliente))
    kpi_cliente_top = kpi_cliente.head(top_n)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not kpi_cliente_top.empty:
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            
            # Criar gráfico de barras horizontais
            bars = ax1.barh(kpi_cliente_top["Nome"], kpi_cliente_top["Quantidade"], 
                           color=plt.cm.Blues(range(top_n)))
            
            ax1.set_xlabel("Quantidade Total", fontsize=12)
            ax1.set_title(f"Top {top_n} Clientes", fontsize=14, fontweight='bold')
            ax1.invert_yaxis()  # Maior no topo
            
            # Adicionar valores nas barras
            max_val = kpi_cliente_top["Quantidade"].max()
            for bar in bars:
                width = bar.get_width()
                ax1.text(width + max_val * 0.01, 
                        bar.get_y() + bar.get_height()/2,
                        f'{int(width):,}', 
                        ha='left', va='center',
                        fontweight='bold', fontsize=10)
            
            plt.tight_layout()
            st.pyplot(fig1)
    
    with col2:
        st.dataframe(
            kpi_cliente_top.style.format({"Quantidade": "{:,.0f}"})
            .background_gradient(subset=["Quantidade"], cmap="Blues"),
            height=400,
            use_container_width=True
        )
    
    # Estatísticas dos clientes
    st.subheader("📈 Estatísticas de Clientes")
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    total_clientes = len(kpi_cliente)
    quantidade_total = kpi_cliente["Quantidade"].sum()
    media_por_cliente = kpi_cliente["Quantidade"].mean() if total_clientes > 0 else 0
    
    with col_stat1:
        st.metric("Total Clientes", f"{total_clientes:,}")
    
    with col_stat2:
        st.metric("Média por Cliente", f"{media_por_cliente:,.0f}")
    
    with col_stat3:
        if total_clientes > 10:
            top_10_percent = kpi_cliente.head(max(1, int(total_clientes * 0.1)))["Quantidade"].sum() / quantidade_total * 100
            st.metric("Top 10% Clientes", f"{top_10_percent:.1f}%")
        else:
            st.metric("Top Cliente", f"{kpi_cliente_top.iloc[0]['Quantidade']:,.0f}")
    
    with col_stat4:
        st.metric("Quantidade Total", f"{quantidade_total:,.0f}")

# === KPI 2 – Percentagem de quantidade por artigo dentro de cada cliente ===
st.subheader("📊 KPI 2 – Distribuição Percentual por Artigo")

if not df_filtrado.empty and len(df_filtrado) > 0:
    # Criar cópia para cálculos
    df_perc = df_filtrado.copy()
    
    # Calcular totais por cliente
    total_por_cliente = df_perc.groupby("Nome")["Quantidade"].sum()
    
    # Função segura para calcular percentagem
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
    
    # Top artigos por cliente (máximo 3 artigos por cliente para melhor visualização)
    kpi_artigo_cliente_top = kpi_artigo_cliente.groupby("Nome").head(3)
    
    # Exibir tabela
    st.dataframe(
        kpi_artigo_cliente_top.style.format({
            "Quantidade": "{:,.0f}",
            "Percentagem": "{:.1f}%"
        }).background_gradient(subset=["Percentagem"], cmap="YlOrRd"),
        height=400,
        use_container_width=True
    )
    
    # Gráfico de barras para top clientes
    if len(kpi_artigo_cliente_top["Nome"].unique()) > 0:
        # Selecionar top 5 clientes para visualização
        top_clientes = kpi_cliente.head(5)["Nome"].tolist()
        dados_top = kpi_artigo_cliente_top[kpi_artigo_cliente_top["Nome"].isin(top_clientes)]
        
        if not dados_top.empty:
            # Criar pivot para gráfico
            pivot_artigos = dados_top.pivot_table(
                index="Nome",
                columns="Artigo",
                values="Percentagem",
                aggfunc="sum",
                fill_value=0
            )
            
            # Criar gráfico de barras agrupadas
            fig_artigos, ax_artigos = plt.subplots(figsize=(12, 6))
            pivot_artigos.plot(kind='bar', ax=ax_artigos, width=0.8)
            
            ax_artigos.set_title("Top Artigos por Cliente (Top 5 Clientes)", fontsize=14, fontweight='bold')
            ax_artigos.set_xlabel("Cliente", fontsize=12)
            ax_artigos.set_ylabel("Percentagem (%)", fontsize=12)
            ax_artigos.legend(title="Artigo", bbox_to_anchor=(1.05, 1), loc='upper left')
            ax_artigos.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig_artigos)

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
            }).background_gradient(subset=["Quantidade"], cmap="Greens"),
            height=300,
            use_container_width=True
        )
    
    with col_kpi2:
        if not kpi_comercial.empty:
            fig_comercial, ax_comercial = plt.subplots(figsize=(10, 5))
            
            # Criar gráfico de barras
            bars = ax_comercial.bar(kpi_comercial["Comercial"], kpi_comercial["Quantidade"], 
                                   color=plt.cm.Set3(range(len(kpi_comercial))))
            
            ax_comercial.set_title("Quantidade por Comercial", fontsize=14, fontweight='bold')
            ax_comercial.set_xlabel("Comercial", fontsize=12)
            ax_comercial.set_ylabel("Quantidade Total", fontsize=12)
            plt.xticks(rotation=45, ha='right')
            
            # Adicionar valores no topo das barras
            for bar in bars:
                height = bar.get_height()
                ax_comercial.text(bar.get_x() + bar.get_width()/2., height,
                                 f'{int(height):,}', ha='center', va='bottom', 
                                 fontsize=9, rotation=0, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig_comercial)

# === Exportar para Excel ===
st.subheader("📥 Exportar Resultados")

if not df_filtrado.empty:
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
        
        # Formatar largura das colunas
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column('A:Z', 20)
    
    # Botão de download
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button(
        label=f"⬇️ Download Relatório Excel",
        data=xls_buf.getvalue(),
        file_name=f"relatorio_compras_{timestamp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
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
        st.metric("Clientes Únicos", f"{clientes_unicos:,}")
    
    with col_res4:
        artigos_unicos = df_filtrado["Artigo"].nunique()
        st.metric("Artigos Únicos", f"{artigos_unicos:,}")
    
    # Distribuição por ano
    st.subheader("📅 Distribuição por Ano")
    distribuicao_ano = df_filtrado.groupby("Ano")["Quantidade"].sum().reset_index()
    
    if not distribuicao_ano.empty:
        col_dist1, col_dist2 = st.columns([1, 2])
        
        with col_dist1:
            st.dataframe(
                distribuicao_ano.style.format({"Quantidade": "{:,.0f}"})
                .background_gradient(subset=["Quantidade"], cmap="Purples"),
                height=200,
                use_container_width=True
            )
        
        with col_dist2:
            fig_dist, ax_dist = plt.subplots(figsize=(10, 4))
            ax_dist.bar(distribuicao_ano["Ano"].astype(str), 
                       distribuicao_ano["Quantidade"], 
                       color='#9b59b6')
            ax_dist.set_title("Distribuição por Ano", fontsize=14, fontweight='bold')
            ax_dist.set_xlabel("Ano", fontsize=12)
            ax_dist.set_ylabel("Quantidade", fontsize=12)
            
            # Adicionar valores no topo das barras
            for i, (ano, qtd) in enumerate(zip(distribuicao_ano["Ano"], distribuicao_ano["Quantidade"])):
                ax_dist.text(i, qtd + max(distribuicao_ano["Quantidade"]) * 0.01, 
                           f'{int(qtd):,}', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig_dist)

# === Instruções ===
with st.expander("📖 Instruções de Uso"):
    st.markdown("""
    ## 🎯 Como usar este dashboard
    
    ### 🔍 **Configurar Filtros (Sidebar)**
    1. **Selecione os valores** em cada filtro (todos são multiselect)
    2. Clique em **✅ Aplicar Filtros** para atualizar o dashboard
    3. Use **🗑️ Limpar Filtros** para recomeçar
    
    ### 📊 **KPIs Disponíveis**
    1. **KPI 1 - Clientes** - Ranking dos melhores clientes por volume
    2. **KPI 2 - Artigos** - Distribuição percentual de artigos por cliente
    3. **KPI 3 - Comerciais** - Performance por comercial
    
    ### 📥 **Exportar Dados**
    - Botão **⬇️ Download Relatório Excel** para exportar todos os dados filtrados
    - Inclui todas as análises em abas separadas
    
    ### 💡 **Dicas Importantes**
    - **Ctrl+Click** para selecionar múltiplos valores
    - **Clique no ❌** para remover itens selecionados
    - **🔄 Atualizar dados** recarrega do ficheiro original
    - Configure os filtros e clique em **Aplicar Filtros** para ver resultados
    
    ### 🔧 **Solução de Problemas**
    - Se não vir dados: verifique os filtros aplicados
    - Se houver erro: clique em "Atualizar dados do ficheiro"
    - Para ajuda: verifique as estatísticas dos dados originais
    """)

# === Debug (apenas para desenvolvimento) ===
with st.expander("🔧 Debug - Ver dados brutos"):
    st.write("**Primeiras 10 linhas dos dados originais:**")
    st.dataframe(df.head(10))
    st.write(f"**Total de registos:** {len(df)}")
    st.write(f"**Colunas disponíveis:** {list(df.columns)}")
    st.write(f"**Anos disponíveis:** {sorted(df['Ano'].unique())}")
    st.write(f"**Dados filtrados:** {len(df_filtrado)} registos")
