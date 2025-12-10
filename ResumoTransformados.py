import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="KPI Compras Clientes (YoY)", layout="wide")
st.title("📊 Dashboard de Compras – Clientes, Artigos e Comerciais")

# --- URL raw do ficheiro no GitHub ---
RAW_URL = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"

# === 1. Ler ficheiro diretamente ===
df_raw = pd.read_excel(RAW_URL)

# === 2. Mapear colunas por índice ===
IDX_NOME = 1       # Coluna B
IDX_ARTIGO = 2     # Coluna C
IDX_COMERCIAL = 8  # Coluna I
COL_DATA = 0       # Ajusta se necessário
COL_QTD = 3        # Ajusta se necessário

# Construir dataframe canónico
df = pd.DataFrame({
    "Nome":      df_raw.iloc[:, IDX_NOME],
    "Artigo":    df_raw.iloc[:, IDX_ARTIGO],
    "Comercial": df_raw.iloc[:, IDX_COMERCIAL],
    "Data":      df_raw.iloc[:, COL_DATA],
    "Quantidade":df_raw.iloc[:, COL_QTD],
})

# === 3. Normalização ===
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df = df.dropna(subset=["Data"])
df["Ano"] = df["Data"].dt.year
df["Mes"] = df["Data"].dt.month
df["Nome"] = df["Nome"].astype(str).str.strip()
df["Artigo"] = df["Artigo"].astype(str).str.strip()
df["Comercial"] = df["Comercial"].astype(str).str.strip()
df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)

# === 4. Base KPI ===
kpi = df.groupby(["Comercial","Nome","Artigo","Ano","Mes"], as_index=False)["Quantidade"].sum()

# === Sidebar com filtros dinâmicos ===
with st.sidebar:
    st.header("🔍 Filtros")
    
    # Filtros de Ano
    st.subheader("📅 Período")
    anos_disponiveis = sorted(kpi["Ano"].unique())
    ano_base = st.selectbox("Ano base", anos_disponiveis, index=max(0,len(anos_disponiveis)-2))
    ano_comp = st.selectbox("Ano comparação", anos_disponiveis, index=len(anos_disponiveis)-1)

    # Filtro de Meses
    meses_nomes = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    meses_sel = st.multiselect("Selecionar meses", meses_nomes, default=meses_nomes)
    
    st.divider()
    
    # === FILTRO 1: COMERCIAIS ===
    st.subheader("👔 Comerciais")
    comerciais_opts = sorted(df["Comercial"].dropna().unique())
    select_all_comerciais = st.checkbox("Todos os comerciais", value=True, key="chk_comerciais")
    
    if select_all_comerciais:
        comerciais_sel = comerciais_opts
        st.info(f"✓ {len(comerciais_opts)} comerciais selecionados")
    else:
        comerciais_sel = st.multiselect(
            "Escolher comerciais",
            comerciais_opts,
            default=[],
            key="multi_comerciais"
        )
        st.caption(f"{len(comerciais_sel)} de {len(comerciais_opts)} selecionados")
    
    st.divider()
    
    # === FILTRO 2: CLIENTES ===
    st.subheader("🏢 Clientes")
    clientes_opts = sorted(df["Nome"].dropna().unique())
    select_all_clientes = st.checkbox("Todos os clientes", value=True, key="chk_clientes")
    
    if select_all_clientes:
        clientes_sel = clientes_opts
        st.info(f"✓ {len(clientes_opts)} clientes selecionados")
    else:
        clientes_sel = st.multiselect(
            "Escolher clientes",
            clientes_opts,
            default=[],
            key="multi_clientes"
        )
        st.caption(f"{len(clientes_sel)} de {len(clientes_opts)} selecionados")
    
    st.divider()
    
    # === FILTRO 3: ARTIGOS ===
    st.subheader("📦 Artigos")
    artigos_opts = sorted(df["Artigo"].dropna().unique())
    select_all_artigos = st.checkbox("Todos os artigos", value=True, key="chk_artigos")
    
    if select_all_artigos:
        artigos_sel = artigos_opts
        st.info(f"✓ {len(artigos_opts)} artigos selecionados")
    else:
        artigos_sel = st.multiselect(
            "Escolher artigos",
            artigos_opts,
            default=[],
            key="multi_artigos"
        )
        st.caption(f"{len(artigos_sel)} de {len(artigos_opts)} selecionados")
    
    st.divider()
    
    # Botão limpar filtros
    if st.button("🔄 Limpar todos os filtros", use_container_width=True):
        st.rerun()

# Converter meses selecionados para números
meses_map = dict(zip(meses_nomes, range(1,13)))
meses_sel_num = [meses_map[m] for m in meses_sel]

# Aplicar filtros
kpi_view = kpi.copy()

if comerciais_sel:
    kpi_view = kpi_view[kpi_view["Comercial"].isin(comerciais_sel)]
else:
    st.warning("⚠️ Nenhum comercial selecionado")
    
if clientes_sel:
    kpi_view = kpi_view[kpi_view["Nome"].isin(clientes_sel)]
else:
    st.warning("⚠️ Nenhum cliente selecionado")
    
if artigos_sel:
    kpi_view = kpi_view[kpi_view["Artigo"].isin(artigos_sel)]
else:
    st.warning("⚠️ Nenhum artigo selecionado")
    
if meses_sel_num:
    kpi_view = kpi_view[kpi_view["Mes"].isin(meses_sel_num)]

# Mostrar resumo dos filtros aplicados
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Comerciais", len(comerciais_sel))
with col2:
    st.metric("Clientes", len(clientes_sel))
with col3:
    st.metric("Artigos", len(artigos_sel))

# === Pivot comparativo ===
if len(kpi_view) == 0:
    st.warning("⚠️ Nenhum dado disponível para os filtros selecionados.")
    pv = pd.DataFrame()
else:
    pv = kpi_view.pivot_table(index=["Comercial","Nome","Artigo","Mes"], columns="Ano", values="Quantidade", aggfunc="sum")
    
    # Garantir que os anos existem
    for a in [ano_base, ano_comp]:
        if a not in pv.columns:
            pv[a] = 0
    
    pv["Variação_%"] = ((pv[ano_comp] - pv[ano_base]) / pv[ano_base].replace(0, pd.NA)) * 100
    pv = pv.reset_index().sort_values(["Comercial","Nome","Artigo","Mes"])
    pv["Mês"] = pv["Mes"].apply(lambda m: meses_nomes[m-1] if 1<=m<=12 else str(m))
    pv = pv[["Comercial","Nome","Artigo","Mês",ano_base,ano_comp,"Variação_%"]]

# === Mostrar tabela ===
st.subheader("Tabela comparativa YoY por Comercial, Cliente, Artigo e Mês")

if len(pv) == 0:
    st.info("Sem dados para apresentar. Ajuste os filtros.")
else:
    pv = pv.rename(columns=lambda c: str(c).strip())
    
    # Verificar se as colunas existem antes de formatar
    format_dict = {}
    if ano_base in pv.columns:
        format_dict[ano_base] = "{:.0f}"
    if ano_comp in pv.columns:
        format_dict[ano_comp] = "{:.0f}"
    if "Variação_%" in pv.columns:
        format_dict["Variação_%"] = "{:.2f}"
    
    # Aplicar estilo apenas se houver colunas para formatar
    if format_dict:
        styled = pv.style.format(format_dict)
        if "Variação_%" in pv.columns:
            styled = styled.background_gradient(cmap="RdYlGn", subset=["Variação_%"])
        st.dataframe(styled, use_container_width=True)
    else:
        st.dataframe(pv, use_container_width=True)

# === Exportar para Excel ===
st.subheader("Exportar resultados filtrados")

xls_buf = io.BytesIO()
with pd.ExcelWriter(xls_buf, engine="xlsxwriter") as writer:
    pv.to_excel(writer, sheet_name="KPI_YoY", index=False)
    ws = writer.sheets["KPI_YoY"]

    # Ajuste automático da largura das colunas
    for i, col in enumerate(pv.columns):
        width = max(12, min(30, int(pv[col].astype(str).str.len().mean()) + 4))
        ws.set_column(i, i, width)

    # Formatação condicional
    last_col = len(pv.columns) - 1
    ws.conditional_format(1, last_col, len(pv), last_col, {
        'type': 'cell','criteria': '>', 'value': 0,
        'format': writer.book.add_format({'bg_color': '#C6EFCE','font_color': '#006100'})
    })
    ws.conditional_format(1, last_col, len(pv), last_col, {
        'type': 'cell','criteria': '<', 'value': 0,
        'format': writer.book.add_format({'bg_color': '#FFC7CE','font_color': '#9C0006'})
    })

    # Gráfico automático global
    chart = writer.book.add_chart({'type': 'line'})
    chart.add_series({
        'name': f"Ano {ano_base}",
        'categories': ['KPI_YoY', 1, 3, len(pv), 3],
        'values':     ['KPI_YoY', 1, 4, len(pv), 4],
    })
    chart.add_series({
        'name': f"Ano {ano_comp}",
        'categories': ['KPI_YoY', 1, 3, len(pv), 3],
        'values':     ['KPI_YoY', 1, 5, len(pv), 5],
    })
    chart.set_title({'name': 'Evolução Mensal Global'})
    chart.set_x_axis({'name': 'Mês'})
    chart.set_y_axis({'name': 'Quantidade'})
    chart.set_style(10)
    ws.insert_chart('H2', chart, {'x_scale': 1.5, 'y_scale': 1.5})

st.download_button(
    label="📥 Exportar para Excel",
    data=xls_buf.getvalue(),
    file_name=f"KPI_YoY_{ano_base}_vs_{ano_comp}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

# Aplicar os mesmos filtros ao df original para os KPIs
df_filtered = df.copy()
if comerciais_sel:
    df_filtered = df_filtered[df_filtered["Comercial"].isin(comerciais_sel)]
if clientes_sel:
    df_filtered = df_filtered[df_filtered["Nome"].isin(clientes_sel)]
if artigos_sel:
    df_filtered = df_filtered[df_filtered["Artigo"].isin(artigos_sel)]

# === KPI 1 – Total de quantidade por cliente ===
kpi_cliente = (
    df_filtered.groupby("Nome")["Quantidade"]
      .sum()
      .reset_index()
      .sort_values("Quantidade", ascending=False)
)

st.subheader("📊 KPI 1 – Total de Quantidade Comprada por Cliente")
st.dataframe(kpi_cliente.style.format({"Quantidade":"{:.0f}"}), use_container_width=True)

fig1, ax1 = plt.subplots(figsize=(10,5))
ax1.bar(kpi_cliente["Nome"], kpi_cliente["Quantidade"], color="steelblue")
ax1.set_title("Total Quantidade por Cliente")
ax1.set_ylabel("Quantidade")
ax1.set_xticklabels(kpi_cliente["Nome"], rotation=45, ha="right")
plt.tight_layout()
st.pyplot(fig1)

# === KPI 2 – Percentagem de quantidade por artigo dentro de cada cliente ===
total_por_cliente = df_filtered.groupby("Nome")["Quantidade"].sum()

df_filtered["Perc_Artigo"] = df_filtered.apply(
    lambda row: (row["Quantidade"] / total_por_cliente[row["Nome"]] * 100)
    if total_por_cliente[row["Nome"]] != 0 else 0,
    axis=1
)

kpi_artigo_cliente = (
    df_filtered.groupby(["Nome","Artigo"], as_index=False)["Perc_Artigo"]
      .sum()
      .sort_values(["Nome","Perc_Artigo"], ascending=[True, False])
)

st.subheader("📊 KPI 2 – Percentagem de Quantidade por Artigo e Cliente")
st.dataframe(kpi_artigo_cliente.style.format({"Perc_Artigo": "{:.2f}%"}), use_container_width=True)

pivot_perc = kpi_artigo_cliente.pivot(index="Nome", columns="Artigo", values="Perc_Artigo").fillna(0)

fig2, ax2 = plt.subplots(figsize=(12,6))
pivot_perc.plot(kind="bar", stacked=True, ax=ax2, colormap="tab20")
ax2.set_title("Distribuição Percentual por Artigo e Cliente")
ax2.set_ylabel("%")
ax2.legend(ncol=2, bbox_to_anchor=(1.02, 1), borderaxespad=0)
plt.tight_layout()
st.pyplot(fig2)
