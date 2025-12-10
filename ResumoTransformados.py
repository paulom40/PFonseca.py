import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="KPI Compras Clientes (YoY)", layout="wide")
st.title("📊 Dashboard de Compras – Clientes, Artigos e Comerciais")

# --- URL raw do ficheiro no GitHub ---
RAW_URL = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"

# === 1. Ler ficheiro diretamente ===
@st.cache_data
def load_data():
    df_raw = pd.read_excel(RAW_URL)
    
    # === 2. Mapear colunas por índice ===
    # Construir dataframe canónico
    df = pd.DataFrame({
        "Nome":      df_raw.iloc[:, 1],   # Coluna B
        "Artigo":    df_raw.iloc[:, 2],   # Coluna C
        "Comercial": df_raw.iloc[:, 8],   # Coluna I
        "Data":      df_raw.iloc[:, 0],   # Coluna A
        "Quantidade":df_raw.iloc[:, 3],   # Coluna D
    })
    
    # === 3. Normalização ===
    # Converter Data - tentar múltiplos formatos
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    
    # Se ainda houver problemas, tentar formato específico
    mask_invalid = df["Data"].isna()
    if mask_invalid.any():
        df.loc[mask_invalid, "Data"] = pd.to_datetime(
            df_raw.iloc[:, 0][mask_invalid], 
            format='%d/%m/%Y', 
            errors="coerce"
        )
    
    # Remover linhas onde Data é inválida
    df = df.dropna(subset=["Data"])
    
    # Extrair ano e mês
    df["Ano"] = df["Data"].dt.year
    df["Mes"] = df["Data"].dt.month
    
    # Filtrar apenas anos válidos (2000 em diante)
    df = df[(df["Ano"] >= 2000) & (df["Ano"] <= 2030)]
    
    # Limpar strings
    df["Nome"] = df["Nome"].astype(str).str.strip()
    df["Artigo"] = df["Artigo"].astype(str).str.strip()
    df["Comercial"] = df["Comercial"].astype(str).str.strip()
    
    # Remover valores 'nan' como string
    df = df[df["Nome"] != "nan"]
    df = df[df["Artigo"] != "nan"]
    df = df[df["Comercial"] != "nan"]
    
    # Converter quantidade para numérico
    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)
    
    return df

# Carregar dados
df = load_data()

# === 4. Base KPI ===
kpi = df.groupby(["Comercial","Nome","Artigo","Ano","Mes"], as_index=False)["Quantidade"].sum()

# === Sidebar com filtros dinâmicos ===
with st.sidebar:
    st.header("🔍 Filtros")
    
    # Filtros de Ano
    st.subheader("📅 Período")
    anos_disponiveis = sorted(df["Ano"].unique())
    
    if len(anos_disponiveis) >= 2:
        ano_base = st.selectbox("Ano base", anos_disponiveis, index=len(anos_disponiveis)-2)
        ano_comp = st.selectbox("Ano comparação", anos_disponiveis, index=len(anos_disponiveis)-1)
    else:
        ano_base = st.selectbox("Ano base", anos_disponiveis, index=0)
        ano_comp = st.selectbox("Ano comparação", anos_disponiveis, index=0)

    # Filtro de Meses
    meses_nomes = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    meses_sel = st.multiselect("Selecionar meses", meses_nomes, default=meses_nomes)
    
    st.divider()
    
    # === FILTRO 1: COMERCIAIS ===
    st.subheader("👔 Comerciais")
    comerciais_opts = sorted([c for c in df["Comercial"].unique() if c and str(c).strip()])
    
    # Botões para selecionar todos/nenhum
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✓ Todos", key="btn_todos_comerciais", use_container_width=True):
            # Cria um novo widget com todos selecionados
            st.session_state.comerciais_sel = comerciais_opts
    with col_btn2:
        if st.button("✗ Nenhum", key="btn_nenhum_comerciais", use_container_width=True):
            st.session_state.comerciais_sel = []
    
    # Inicializar se não existir
    if "comerciais_sel" not in st.session_state:
        st.session_state.comerciais_sel = comerciais_opts
    
    # Widget multiselect
    comerciais_selecionados = st.multiselect(
        "Escolher comerciais",
        comerciais_opts,
        default=st.session_state.comerciais_sel,
        key="comerciais_multiselect"
    )
    
    # Atualizar session state
    st.session_state.comerciais_sel = comerciais_selecionados
    
    st.caption(f"{len(comerciais_selecionados)} de {len(comerciais_opts)} selecionados")
    
    st.divider()
    
    # === FILTRO 2: CLIENTES ===
    st.subheader("🏢 Clientes")
    clientes_opts = sorted([c for c in df["Nome"].unique() if c and str(c).strip()])
    
    col_btn3, col_btn4 = st.columns(2)
    with col_btn3:
        if st.button("✓ Todos", key="btn_todos_clientes", use_container_width=True):
            st.session_state.clientes_sel = clientes_opts
    with col_btn4:
        if st.button("✗ Nenhum", key="btn_nenhum_clientes", use_container_width=True):
            st.session_state.clientes_sel = []
    
    if "clientes_sel" not in st.session_state:
        st.session_state.clientes_sel = clientes_opts
    
    clientes_selecionados = st.multiselect(
        "Escolher clientes",
        clientes_opts,
        default=st.session_state.clientes_sel,
        key="clientes_multiselect"
    )
    
    st.session_state.clientes_sel = clientes_selecionados
    
    st.caption(f"{len(clientes_selecionados)} de {len(clientes_opts)} selecionados")
    
    st.divider()
    
    # === FILTRO 3: ARTIGOS ===
    st.subheader("📦 Artigos")
    artigos_opts = sorted([c for c in df["Artigo"].unique() if c and str(c).strip()])
    
    col_btn5, col_btn6 = st.columns(2)
    with col_btn5:
        if st.button("✓ Todos", key="btn_todos_artigos", use_container_width=True):
            st.session_state.artigos_sel = artigos_opts
    with col_btn6:
        if st.button("✗ Nenhum", key="btn_nenhum_artigos", use_container_width=True):
            st.session_state.artigos_sel = []
    
    if "artigos_sel" not in st.session_state:
        st.session_state.artigos_sel = artigos_opts
    
    artigos_selecionados = st.multiselect(
        "Escolher artigos",
        artigos_opts,
        default=st.session_state.artigos_sel,
        key="artigos_multiselect"
    )
    
    st.session_state.artigos_sel = artigos_selecionados
    
    st.caption(f"{len(artigos_selecionados)} de {len(artigos_opts)} selecionados")
    
    st.divider()
    
    # Botão para resetar todos os filtros
    if st.button("🔄 Resetar todos os filtros", use_container_width=True):
        st.session_state.comerciais_sel = comerciais_opts
        st.session_state.clientes_sel = clientes_opts
        st.session_state.artigos_sel = artigos_opts
        st.rerun()

# Converter meses selecionados para números
meses_map = dict(zip(meses_nomes, range(1,13)))
meses_sel_num = [meses_map[m] for m in meses_sel] if meses_sel else []

# Aplicar filtros DINAMICAMENTE
kpi_view = kpi.copy()

# Usar valores atuais dos filtros
comerciais_ativos = st.session_state.comerciais_sel if hasattr(st.session_state, 'comerciais_sel') else []
clientes_ativos = st.session_state.clientes_sel if hasattr(st.session_state, 'clientes_sel') else []
artigos_ativos = st.session_state.artigos_sel if hasattr(st.session_state, 'artigos_sel') else []

if comerciais_ativos:
    kpi_view = kpi_view[kpi_view["Comercial"].isin(comerciais_ativos)]
    
if clientes_ativos:
    kpi_view = kpi_view[kpi_view["Nome"].isin(clientes_ativos)]
    
if artigos_ativos:
    kpi_view = kpi_view[kpi_view["Artigo"].isin(artigos_ativos)]
    
if meses_sel_num:
    kpi_view = kpi_view[kpi_view["Mes"].isin(meses_sel_num)]

# Mostrar resumo dos filtros aplicados
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Comerciais", len(comerciais_ativos))
with col2:
    st.metric("Clientes", len(clientes_ativos))
with col3:
    st.metric("Artigos", len(artigos_ativos))
with col4:
    st.metric("Registos", len(kpi_view))

# === Pivot comparativo ===
if len(kpi_view) == 0:
    st.warning("⚠️ Nenhum dado disponível para os filtros selecionados.")
    pv = pd.DataFrame()
else:
    # Garantir agregação antes do pivot
    kpi_agg = kpi_view.groupby(["Comercial","Nome","Artigo","Ano","Mes"], as_index=False)["Quantidade"].sum()
    
    # Criar pivot
    pv = kpi_agg.pivot_table(
        index=["Comercial","Nome","Artigo","Mes"], 
        columns="Ano", 
        values="Quantidade", 
        aggfunc="sum", 
        fill_value=0
    )
    
    # Resetar index
    pv = pv.reset_index()
    
    # Garantir que os anos existem
    if ano_base not in pv.columns:
        pv[ano_base] = 0
    if ano_comp not in pv.columns:
        pv[ano_comp] = 0
    
    # Adicionar nome do mês
    pv["Mês"] = pv["Mes"].apply(lambda m: meses_nomes[int(m)-1] if 1<=int(m)<=12 else str(m))
    
    # Calcular variação
    pv["Variação_%"] = pv.apply(
        lambda row: ((row[ano_comp] - row[ano_base]) / row[ano_base] * 100) 
        if row[ano_base] != 0 else (100 if row[ano_comp] > 0 else 0),
        axis=1
    )
    
    # Ordenar
    pv = pv.sort_values(["Comercial","Nome","Artigo","Mes"]).reset_index(drop=True)
    
    # Selecionar colunas finais
    pv = pv[["Comercial","Nome","Artigo","Mês",ano_base,ano_comp,"Variação_%"]]

# === Mostrar tabela ===
st.subheader("Tabela comparativa YoY por Comercial, Cliente, Artigo e Mês")

if len(pv) == 0:
    st.info("Sem dados para apresentar. Ajuste os filtros.")
else:
    # Formatar sem styling complexo para evitar erros
    pv_display = pv.copy()
    pv_display[ano_base] = pv_display[ano_base].apply(lambda x: f"{x:.0f}")
    pv_display[ano_comp] = pv_display[ano_comp].apply(lambda x: f"{x:.0f}")
    pv_display["Variação_%"] = pv_display["Variação_%"].apply(lambda x: f"{x:.2f}%")
    
    # Colorir apenas a coluna de variação manualmente
    def color_variation(val):
        try:
            num = float(val.replace('%',''))
            if num > 0:
                return 'background-color: #C6EFCE; color: #006100'
            elif num < 0:
                return 'background-color: #FFC7CE; color: #9C0006'
            else:
                return ''
        except:
            return ''
    
    styled = pv_display.style.applymap(color_variation, subset=["Variação_%"])
    st.dataframe(styled, use_container_width=True)

# === Exportar para Excel ===
st.subheader("Exportar resultados filtrados")

if len(pv) > 0:
    xls_buf = io.BytesIO()
    with pd.ExcelWriter(xls_buf, engine="xlsxwriter") as writer:
        pv.to_excel(writer, sheet_name="KPI_YoY", index=False)
        ws = writer.sheets["KPI_YoY"]

        # Ajuste automático da largura das colunas
        for i, col in enumerate(pv.columns):
            max_len = max(
                pv[col].astype(str).str.len().max(),
                len(str(col))
            )
            ws.set_column(i, i, min(max_len + 2, 30))

        # Formatação condicional
        if "Variação_%" in pv.columns:
            var_col_idx = pv.columns.get_loc("Variação_%")
            ws.conditional_format(1, var_col_idx, len(pv), var_col_idx, {
                'type': 'cell','criteria': '>', 'value': 0,
                'format': writer.book.add_format({'bg_color': '#C6EFCE','font_color': '#006100'})
            })
            ws.conditional_format(1, var_col_idx, len(pv), var_col_idx, {
                'type': 'cell','criteria': '<', 'value': 0,
                'format': writer.book.add_format({'bg_color': '#FFC7CE','font_color': '#9C0006'})
            })

    st.download_button(
        label="📥 Exportar para Excel",
        data=xls_buf.getvalue(),
        file_name=f"KPI_YoY_{ano_base}_vs_{ano_comp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
else:
    st.info("Sem dados para exportar. Ajuste os filtros.")

# Aplicar os mesmos filtros ao df original para os KPIs
df_filtered = df.copy()
if comerciais_ativos:
    df_filtered = df_filtered[df_filtered["Comercial"].isin(comerciais_ativos)]
if clientes_ativos:
    df_filtered = df_filtered[df_filtered["Nome"].isin(clientes_ativos)]
if artigos_ativos:
    df_filtered = df_filtered[df_filtered["Artigo"].isin(artigos_ativos)]

# === KPI 1 – Total de quantidade por cliente ===
kpi_cliente = (
    df_filtered.groupby("Nome")["Quantidade"]
      .sum()
      .reset_index()
      .sort_values("Quantidade", ascending=False)
)

st.subheader("📊 KPI 1 – Total de Quantidade Comprada por Cliente")

if len(kpi_cliente) > 0:
    # Formatação simples
    kpi_cliente_display = kpi_cliente.copy()
    kpi_cliente_display["Quantidade"] = kpi_cliente_display["Quantidade"].apply(lambda x: f"{x:.0f}")
    st.dataframe(kpi_cliente_display, use_container_width=True)

    fig1, ax1 = plt.subplots(figsize=(10,5))
    ax1.bar(kpi_cliente["Nome"], kpi_cliente["Quantidade"], color="steelblue")
    ax1.set_title("Total Quantidade por Cliente")
    ax1.set_ylabel("Quantidade")
    ax1.set_xticklabels(kpi_cliente["Nome"], rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig1)
else:
    st.info("Sem dados para apresentar no KPI 1.")

# === KPI 2 – Percentagem de quantidade por artigo dentro de cada cliente ===
if len(df_filtered) > 0:
    total_por_cliente = df_filtered.groupby("Nome")["Quantidade"].sum()

    df_filtered_copy = df_filtered.copy()
    df_filtered_copy["Perc_Artigo"] = df_filtered_copy.apply(
        lambda row: (row["Quantidade"] / total_por_cliente[row["Nome"]] * 100)
        if total_por_cliente[row["Nome"]] != 0 else 0,
        axis=1
    )

    kpi_artigo_cliente = (
        df_filtered_copy.groupby(["Nome","Artigo"], as_index=False)["Perc_Artigo"]
          .sum()
          .sort_values(["Nome","Perc_Artigo"], ascending=[True, False])
    )

    st.subheader("📊 KPI 2 – Percentagem de Quantidade por Artigo e Cliente")
    
    if len(kpi_artigo_cliente) > 0:
        kpi_artigo_display = kpi_artigo_cliente.copy()
        kpi_artigo_display["Perc_Artigo"] = kpi_artigo_display["Perc_Artigo"].apply(lambda x: f"{x:.2f}%")
        st.dataframe(kpi_artigo_display, use_container_width=True)

        pivot_perc = kpi_artigo_cliente.pivot(index="Nome", columns="Artigo", values="Perc_Artigo").fillna(0)

        if len(pivot_perc) > 0:
            fig2, ax2 = plt.subplots(figsize=(12,6))
            pivot_perc.plot(kind="bar", stacked=True, ax=ax2, colormap="tab20")
            ax2.set_title("Distribuição Percentual por Artigo e Cliente")
            ax2.set_ylabel("%")
            ax2.legend(ncol=2, bbox_to_anchor=(1.02, 1), borderaxespad=0)
            plt.tight_layout()
            st.pyplot(fig2)
    else:
        st.info("Sem dados para apresentar no KPI 2.")
else:
    st.info("Sem dados filtrados para KPI 2.")
