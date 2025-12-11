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

# === Sidebar com filtros interativos ===
with st.sidebar:
    st.header("🔍 Filtros Interativos")
    
    if st.button("🔄 Atualizar todos os dados"):
        st.cache_data.clear()
        st.rerun()
    
    # Filtro por Ano (Coluna K)
    anos_disponiveis = sorted(df["Ano"].unique())
    if len(anos_disponiveis) >= 2:
        ano_base_default = anos_disponiveis[-2]
        ano_comp_default = anos_disponiveis[-1]
    elif len(anos_disponiveis) == 1:
        ano_base_default = anos_disponiveis[0]
        ano_comp_default = anos_disponiveis[0]
    else:
        ano_base_default = 2023
        ano_comp_default = 2024
    
    ano_base = st.selectbox("📅 Ano base", anos_disponiveis, 
                          index=anos_disponiveis.index(ano_base_default) if ano_base_default in anos_disponiveis else 0)
    ano_comp = st.selectbox("📅 Ano comparação", anos_disponiveis, 
                          index=anos_disponiveis.index(ano_comp_default) if ano_comp_default in anos_disponiveis else 0)
    
    # Filtro por Mês
    meses_nomes = ["Jan","Fev","Mar","Abr","Mai","Jun",
                   "Jul","Ago","Set","Out","Nov","Dez"]
    meses_sel = st.multiselect("🗓️ Selecionar meses", meses_nomes, default=meses_nomes)
    
    # Filtro por Comercial (Coluna I)
    comerciais_opts = sorted(df["Comercial"].dropna().unique())
    comercial_sel = st.multiselect("👤 Comercial(s)", comerciais_opts, default=comerciais_opts)
    
    # Filtro por Cliente (Coluna B)
    clientes_opts = sorted(df["Nome"].dropna().unique())
    cliente_sel = st.multiselect("🏢 Cliente(s)", clientes_opts, default=clientes_opts)
    
    # Filtro por Artigo (Coluna C)
    artigos_opts = sorted(df["Artigo"].dropna().unique())
    artigo_sel = st.multiselect("📦 Artigo(s)", artigos_opts, default=artigos_opts)
    
    if st.button("🗑️ Limpar todos os filtros"):
        st.rerun()

# === Aplicar filtros ao dataframe ===
df_filtrado = df.copy()

# Filtro por Ano
df_filtrado = df_filtrado[df_filtrado["Ano"].isin([ano_base, ano_comp])]

# Filtro por Mês
meses_map = dict(zip(meses_nomes, range(1, 13)))
meses_sel_num = [meses_map[m] for m in meses_sel]
if meses_sel_num:
    df_filtrado = df_filtrado[df_filtrado["Mes"].isin(meses_sel_num)]

# Filtro por Comercial
if comercial_sel:
    df_filtrado = df_filtrado[df_filtrado["Comercial"].isin(comercial_sel)]

# Filtro por Cliente
if cliente_sel:
    df_filtrado = df_filtrado[df_filtrado["Nome"].isin(cliente_sel)]

# Filtro por Artigo
if artigo_sel:
    df_filtrado = df_filtrado[df_filtrado["Artigo"].isin(artigo_sel)]

# === Tabela comparativa YoY ===
st.subheader("📈 Comparativo Ano a Ano (YoY)")

if not df_filtrado.empty:
    # Agrupar dados
    kpi_grouped = df_filtrado.groupby(
        ["Comercial", "Nome", "Artigo", "Mes_Nome", "Mes", "Ano"],
        as_index=False
    )["Quantidade"].sum()
    
    # Criar pivot table
    pv = kpi_grouped.pivot_table(
        index=["Comercial", "Nome", "Artigo", "Mes_Nome", "Mes"],
        columns="Ano",
        values="Quantidade",
        aggfunc="sum",
        fill_value=0
    ).reset_index()
    
    # Ordenar por mês
    pv = pv.sort_values(["Comercial", "Nome", "Artigo", "Mes"])
    
    # Adicionar coluna de variação
    if ano_base in pv.columns and ano_comp in pv.columns:
        pv["Variação_%"] = pv.apply(
            lambda row: ((row[ano_comp] - row[ano_base]) / row[ano_base] * 100) 
            if row[ano_base] != 0 else (100 if row[ano_comp] > 0 else 0),
            axis=1
        )
        
        # Reordenar colunas
        cols_order = ["Comercial", "Nome", "Artigo", "Mes_Nome", ano_base, ano_comp, "Variação_%"]
        pv = pv[[col for col in cols_order if col in pv.columns]]
        
        # Exibir tabela formatada
        st.dataframe(
            pv.style.format({
                str(ano_base): "{:,.0f}",
                str(ano_comp): "{:,.0f}",
                "Variação_%": "{:+.2f}%"
            }).applymap(
                lambda x: 'background-color: #FF6B6B' if isinstance(x, (int, float)) and x < 0 else 
                         ('background-color: #51CF66' if isinstance(x, (int, float)) and x > 0 else ''),
                subset=["Variação_%"]
            ),
            height=400
        )
    else:
        st.warning("Não há dados para os anos selecionados")
else:
    st.warning("Não há dados para os filtros aplicados")

# === KPI 1 – Total de quantidade por cliente ===
st.subheader("📊 KPI 1 – Total de Quantidade Comprada por Cliente")

if not df_filtrado.empty:
    kpi_cliente = (
        df_filtrado.groupby("Nome")["Quantidade"]
        .sum()
        .reset_index()
        .sort_values("Quantidade", ascending=False)
    )
    
    # Mostrar top 10 ou menos se não houver muitos
    kpi_cliente_top = kpi_cliente.head(min(10, len(kpi_cliente)))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not kpi_cliente_top.empty:
            fig1, ax1 = plt.subplots(figsize=(10, 5))
            bars = ax1.barh(kpi_cliente_top["Nome"], kpi_cliente_top["Quantidade"], color="steelblue")
            ax1.set_xlabel("Quantidade Total")
            ax1.set_title(f"Top Clientes ({ano_base} vs {ano_comp})")
            ax1.invert_yaxis()  # Maior no topo
            
            # Adicionar valores nas barras
            if len(kpi_cliente_top) > 0:
                max_val = kpi_cliente_top["Quantidade"].max()
                for bar in bars:
                    width = bar.get_width()
                    ax1.text(width + max_val * 0.01, 
                            bar.get_y() + bar.get_height()/2,
                            f'{int(width):,}', 
                            ha='left', va='center')
            
            st.pyplot(fig1)
    
    with col2:
        st.dataframe(
            kpi_cliente_top.style.format({"Quantidade": "{:,.0f}"})
            .bar(subset=["Quantidade"], color='#51CF66'),
            height=400
        )
else:
    st.warning("Não há dados para calcular KPI de clientes")

# === KPI 2 – Percentagem de quantidade por artigo dentro de cada cliente ===
st.subheader("📊 KPI 2 – Distribuição Percentual por Artigo")

if not df_filtrado.empty and len(df_filtrado) > 0:
    # Criar uma cópia para evitar problemas de índice
    df_perc_calc = df_filtrado.copy()
    
    # Calcular totais por cliente
    total_por_cliente = df_perc_calc.groupby("Nome")["Quantidade"].sum()
    
    # Adicionar percentagem de forma segura
    def calcular_percentagem(row):
        cliente = row["Nome"]
        quantidade = row["Quantidade"]
        total_cliente = total_por_cliente.get(cliente, 0)
        if total_cliente > 0:
            return (quantidade / total_cliente) * 100
        return 0
    
    df_perc_calc["Percentagem"] = df_perc_calc.apply(calcular_percentagem, axis=1)
    
    # Agrupar por cliente e artigo
    kpi_artigo_cliente = (
        df_perc_calc.groupby(["Nome", "Artigo"], as_index=False)
        .agg({"Quantidade": "sum", "Percentagem": "sum"})
        .sort_values(["Nome", "Percentagem"], ascending=[True, False])
    )
    
    # Limitar para melhor visualização
    kpi_artigo_cliente_display = kpi_artigo_cliente.head(20)
    
    # Exibir tabela
    st.dataframe(
        kpi_artigo_cliente_display.style.format({
            "Quantidade": "{:,.0f}",
            "Percentagem": "{:.1f}%"
        }).bar(subset=["Percentagem"], color='#FFA726'),
        height=400
    )
    
    # Gráfico de distribuição (apenas se houver dados razoáveis)
    clientes_unicos = kpi_artigo_cliente_display["Nome"].nunique()
    if clientes_unicos <= 10 and clientes_unicos > 0:
        pivot_perc = kpi_artigo_cliente_display.pivot(
            index="Nome", 
            columns="Artigo", 
            values="Percentagem"
        ).fillna(0)
        
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        pivot_perc.plot(kind="bar", stacked=True, ax=ax2, colormap="tab20c")
        ax2.set_title("Distribuição Percentual por Artigo")
        ax2.set_ylabel("%")
        ax2.set_xlabel("Cliente")
        ax2.legend(title="Artigo", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        st.pyplot(fig2)
    elif clientes_unicos > 10:
        st.info(f"Muitos clientes para mostrar no gráfico ({clientes_unicos}). Use filtros para reduzir.")
else:
    st.warning("Não há dados para calcular distribuição percentual")

# === Exportar para Excel ===
st.subheader("📥 Exportar Resultados")

if not df_filtrado.empty:
    if st.button("💾 Gerar Relatório Excel"):
        # Criar Excel com múltiplas abas
        xls_buf = io.BytesIO()
        with pd.ExcelWriter(xls_buf, engine='xlsxwriter') as writer:
            # Aba 1: Dados filtrados
            df_filtrado.to_excel(writer, sheet_name='Dados_Filtrados', index=False)
            
            # Aba 2: Comparativo YoY
            if 'pv' in locals() and not pv.empty:
                pv.to_excel(writer, sheet_name='Comparativo_YoY', index=False)
            
            # Aba 3: KPI Clientes
            if 'kpi_cliente' in locals() and not kpi_cliente.empty:
                kpi_cliente.to_excel(writer, sheet_name='KPI_Clientes', index=False)
            
            # Aba 4: Distribuição por Artigo
            if 'kpi_artigo_cliente' in locals() and not kpi_artigo_cliente.empty:
                kpi_artigo_cliente.to_excel(writer, sheet_name='Distrib_Artigo', index=False)
            
            # Formatar largura das colunas
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                # Ajustar largura das colunas
                for i, col in enumerate(df_filtrado.columns):
                    if col in df_filtrado.columns:
                        column_len = max(
                            df_filtrado[col].astype(str).str.len().max(),
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
else:
    st.warning("Não há dados filtrados para exportar")

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
        st.metric("Variação Total", f"{variacao_total:+.1f}%", 
                 delta=f"{variacao_total:+.1f}%")
    
    with col4:
        clientes_unicos = df_filtrado["Nome"].nunique()
        st.metric("Clientes Únicos", clientes_unicos)
        
    # Métricas adicionais
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        artigos_unicos = df_filtrado["Artigo"].nunique()
        st.metric("Artigos Únicos", artigos_unicos)
    
    with col6:
        comerciais_unicos = df_filtrado["Comercial"].nunique()
        st.metric("Comerciais", comerciais_unicos)
    
    with col7:
        registos_totais = len(df_filtrado)
        st.metric("Registos Totais", registos_totais)
    
    with col8:
        media_por_cliente = total_ano_comp / clientes_unicos if clientes_unicos > 0 else 0
        st.metric(f"Média/{ano_comp}", f"{media_por_cliente:,.0f}")
else:
    st.warning("Não há dados para mostrar métricas")

# === Instruções ===
with st.expander("ℹ️ Instruções de uso"):
    st.markdown("""
    **Como usar este dashboard:**
    
    1. **Filtros (sidebar à esquerda):**
       - 📅 **Ano base/comparação**: Selecione os anos para comparação
       - 🗓️ **Meses**: Selecione os meses a incluir na análise (multiseleção)
       - 👤 **Comercial**: Filtre por comercial(s) específico(s) (multiseleção)
       - 🏢 **Cliente**: Filtre por cliente(s) específico(s) (multiseleção)
       - 📦 **Artigo**: Filtre por artigo(s) específico(s) (multiseleção)
    
    2. **Visualizações principais:**
       - 📈 **Comparativo YoY**: Tabela interativa com variação percentual ano a ano
       - 📊 **KPI Clientes**: Gráfico dos principais clientes por volume
       - 📊 **Distribuição por Artigo**: Análise percentual de artigos por cliente
    
    3. **Exportação:**
       - 💾 **Gerar Relatório Excel**: Cria Excel com todas as análises filtradas
    
    4. **Métricas de Resumo:**
       - Visualização rápida dos principais indicadores
    
    **Colunas mapeadas do Excel:**
    - Coluna B (Índice 1): Nome do Cliente
    - Coluna C (Índice 2): Artigo
    - Coluna I (Índice 8): Comercial
    - Coluna K (Índice 10): Ano
    
    **Dicas:**
    - Use `Atualizar todos os dados` para recarregar do ficheiro original
    - Use `Limpar todos os filtros` para recomeçar a análise
    - Os filtros são cumulativos (todos aplicados em conjunto)
    """)
