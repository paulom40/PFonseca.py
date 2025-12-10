import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="KPI Compras Clientes (YoY)", layout="wide")
st.title("📊 Dashboard de Compras – Clientes, Artigos e Comerciais")

# --- URL raw do ficheiro no GitHub ---
RAW_URL = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"

# === 1. Ler ficheiro diretamente ===
df = pd.read_excel(RAW_URL)

# === 2. Normalizar colunas ===
df = df.rename(columns={
    "Nome":"Nome",
    "Quantidade":"Quantidade",
    "Data":"Data",
    "Artigo":"Artigo",
    "Comercial":"Comercial"
})
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df = df.dropna(subset=["Data"])
df["Ano"] = df["Data"].dt.year
df["Mes"] = df["Data"].dt.month
df["Nome"] = df["Nome"].astype(str).str.strip()
df["Artigo"] = df["Artigo"].astype(str).str.strip()
df["Comercial"] = df["Comercial"].astype(str).str.strip()
df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)

# === 3. Agrupar KPI base ===
kpi = df.groupby(["Comercial","Nome","Artigo","Ano","Mes"], as_index=False)["Quantidade"].sum()
# === 4. Sidebar com filtros dinâmicos ===
with st.sidebar:
    st.header("Filtros")

    anos_disponiveis = sorted(kpi["Ano"].unique())
    ano_base = st.selectbox("Ano base", anos_disponiveis, index=max(0,len(anos_disponiveis)-2))
    ano_comp = st.selectbox("Ano comparação", anos_disponiveis, index=len(anos_disponiveis)-1)

    meses_nomes = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    meses_sel = st.multiselect("Selecionar meses", meses_nomes, default=meses_nomes)

    # Comerciais
    comerciais_opts = sorted(kpi["Comercial"].unique())
    select_all_comerciais = st.checkbox("Selecionar todos os comerciais", value=True)
    comerciais_sel = comerciais_opts if select_all_comerciais else st.multiselect("Selecionar comerciais", comerciais_opts)

    # Clientes
    clientes_opts = sorted(kpi["Nome"].unique())
    select_all_clientes = st.checkbox("Selecionar todos os clientes", value=True)
    clientes_sel = clientes_opts if select_all_clientes else st.multiselect("Selecionar clientes", clientes_opts)

    # Artigos
    artigos_opts = sorted(kpi["Artigo"].unique())
    select_all_artigos = st.checkbox("Selecionar todos os artigos", value=True)
    artigos_sel = artigos_opts if select_all_artigos else st.multiselect("Selecionar artigos", artigos_opts)

    if st.button("🔄 Limpar filtros"):
        st.experimental_rerun()

# Converter meses selecionados para números
meses_map = dict(zip(meses_nomes, range(1,13)))
meses_sel_num = [meses_map[m] for m in meses_sel]

# === 5. Aplicar filtros ===
kpi_view = kpi.copy()
if comerciais_sel:
    kpi_view = kpi_view[kpi_view["Comercial"].isin(comerciais_sel)]
if clientes_sel:
    kpi_view = kpi_view[kpi_view["Nome"].isin(clientes_sel)]
if artigos_sel:
    kpi_view = kpi_view[kpi_view["Artigo"].isin(artigos_sel)]
if meses_sel_num:
    kpi_view = kpi_view[kpi_view["Mes"].isin(meses_sel_num)]
# === 6. Pivot comparativo ===
pv = kpi_view.pivot_table(index=["Comercial","Nome","Artigo","Mes"], columns="Ano", values="Quantidade", aggfunc="sum")
for a in [ano_base, ano_comp]:
    if a not in pv.columns:
        pv[a] = 0
pv["Variação_%"] = ((pv[ano_comp] - pv[ano_base]) / pv[ano_base].replace(0, pd.NA)) * 100
pv = pv.reset_index().sort_values(["Comercial","Nome","Artigo","Mes"])
pv["Mês"] = pv["Mes"].apply(lambda m: meses_nomes[m-1] if 1<=m<=12 else str(m))
pv = pv[["Comercial","Nome","Artigo","Mês",ano_base,ano_comp,"Variação_%"]]

# === 7. Mostrar tabela ===
st.subheader("Tabela comparativa YoY por Comercial, Cliente, Artigo e Mês")
st.dataframe(
    pv.style
    .format({ano_base:"{:.0f}", ano_comp:"{:.0f}", "Variação_%":"{:.2f}"})
    .background_gradient(cmap="RdYlGn", subset=["Variação_%"])
)

# === 8. Exportar para Excel com formatação condicional e gráfico ===
st.subheader("Exportar resultados filtrados")

xls_buf = io.BytesIO()
with pd.ExcelWriter(xls_buf, engine="xlsxwriter") as writer:
    pv.to_excel(writer, sheet_name="KPI_YoY", index=False)
    ws = writer.sheets["KPI_YoY"]

    # Ajuste automático da largura das colunas
    for i, col in enumerate(pv.columns):
        width = max(12, min(30, int(pv[col].astype(str).str.len().mean()) + 4))
        ws.set_column(i, i, width)

    # Formatação condicional na coluna de Variação_%
    last_col = len(pv.columns) - 1
    ws.conditional_format(1, last_col, len(pv), last_col, {
        'type': 'cell',
        'criteria': '>',
        'value': 0,
        'format': writer.book.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    })
    ws.conditional_format(1, last_col, len(pv), last_col, {
        'type': 'cell',
        'criteria': '<',
        'value': 0,
        'format': writer.book.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    })

    # Gráfico automático global
    chart = writer.book.add_chart({'type': 'line'})
    chart.add_series({
        'name': f"Ano {ano_base}",
        'categories': ['KPI_YoY', 1, 3, len(pv), 3],  # coluna Mês
        'values':     ['KPI_YoY', 1, 4, len(pv), 4],  # coluna Ano Base
    })
    chart.add_series({
        'name': f"Ano {ano_comp}",
        'categories': ['KPI_YoY', 1, 3, len(pv), 3],
        'values':     ['KPI_YoY', 1, 5, len(pv), 5],  # coluna Ano Comparação
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
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
# === 9. KPI 1 – Total de quantidade por cliente ===
kpi_cliente = df.groupby("Nome")["Quantidade"].sum().reset_index().sort_values("Quantidade", ascending=False)
st.subheader("📊 KPI 1 – Total de Quantidade Comprada por Cliente")
st.dataframe(kpi_cliente.style.format({"Quantidade":"{:.0f}"}))

fig1, ax1 = plt.subplots(figsize=(8,4))
ax1.bar(kpi_cliente["Nome"], kpi_cliente["Quantidade"], color="steelblue")
ax1.set_title("Total Quantidade por Cliente")
ax1.set_ylabel("Quantidade")
st.pyplot(fig1)

# === 10. KPI 2 – Percentagem de quantidade por artigo dentro de cada cliente ===
total_por_cliente = df.groupby("Nome")["Quantidade"].sum()

# Corrigido: string fechada corretamente
df["Perc_Artigo"] = df.apply(
    lambda row: (row["Quantidade"] / total_por_cliente[row["Nome"]] * 100)
    if total_por_cliente[row["Nome"]] != 0 else 0,
    axis=1
)

kpi_artigo_cliente = (
    df.groupby(["Nome","Artigo"], as_index=False)["Perc_Artigo"]
      .sum()
      .sort_values(["Nome","Perc_Artigo"], ascending=[True, False])
)

st.subheader("📊 KPI 2 – Percentagem de Quantidade por Artigo e Cliente")
st.dataframe(kpi_artigo_cliente.style.format({"Perc_Artigo": "{:.2f}%"}))

# Gráfico stacked bar por cliente
pivot_perc = kpi_artigo_cliente.pivot(index="Nome", columns="Artigo", values="Perc_Artigo").fillna(0)

fig2, ax2 = plt.subplots(figsize=(10,6))
pivot_perc.plot(kind="bar", stacked=True, ax=ax2, colormap="tab20")
ax2.set_title("Distribuição Percentual por Artigo e Cliente")
ax2.set_ylabel("%")
st.pyplot(fig2)

