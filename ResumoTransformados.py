import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Dashboard Completo KPIs", layout="wide")
st.title("Dashboard Completo de Análise de Compras")

# URL do ficheiro
RAW_URL = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"

# === CARREGAR DADOS ===
@st.cache_data
def load_data():
    df_raw = pd.read_excel(RAW_URL)
    
    df = pd.DataFrame({
        "Cliente":   df_raw.iloc[:, 1],
        "Artigo":    df_raw.iloc[:, 2],
        "Comercial": df_raw.iloc[:, 8],
        "Data":      df_raw.iloc[:, 0],
        "Quantidade":df_raw.iloc[:, 3],
    })
    
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"])
    df["Ano"] = df["Data"].dt.year
    df["Mes"] = df["Data"].dt.month
    
    for col in ["Cliente", "Artigo", "Comercial"]:
        df[col] = df[col].astype(str).str.strip()
        df = df[df[col] != "nan"]
    
    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)
    
    return df

with st.spinner("A carregar dados..."):
    df = load_data()

# === SIDEBAR - FILTROS ===
st.sidebar.header("Filtros")

# Anos disponíveis
anos = sorted(df["Ano"].unique(), reverse=True)
st.sidebar.subheader("Período")
ano_comp = st.sidebar.selectbox("Ano Atual", anos, index=0)
ano_base = st.sidebar.selectbox("Ano Comparação", anos, index=min(1, len(anos)-1))

# Meses
st.sidebar.subheader("Meses")
meses_nomes = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
meses_sel = st.sidebar.multiselect("Selecionar Meses", meses_nomes, default=meses_nomes)

# Comerciais
st.sidebar.subheader("Comerciais")
lista_comerciais = sorted(df["Comercial"].unique())
todos_com = st.sidebar.checkbox("Todos os comerciais", value=True)
comerciais_sel = lista_comerciais if todos_com else st.sidebar.multiselect("Escolher comerciais", lista_comerciais, default=[])

# Clientes
st.sidebar.subheader("Clientes")
lista_clientes = sorted(df["Cliente"].unique())
todos_cli = st.sidebar.checkbox("Todos os clientes", value=True)
clientes_sel = lista_clientes if todos_cli else st.sidebar.multiselect("Escolher clientes", lista_clientes, default=[])

# Artigos
st.sidebar.subheader("Artigos")
lista_artigos = sorted(df["Artigo"].unique())
todos_art = st.sidebar.checkbox("Todos os artigos", value=True)
artigos_sel = lista_artigos if todos_art else st.sidebar.multiselect("Escolher artigos", lista_artigos, default=[])

# === FUNÇÃO PARA APLICAR TODOS OS FILTROS ===
def aplicar_filtros(df, anos_lista=None, meses_lista=None, comerciais=None, clientes=None, artigos=None):
    df_f = df.copy()
    
    if anos_lista:
        df_f = df_f[df_f["Ano"].isin(anos_lista)]
    if meses_lista:
        df_f = df_f[df_f["Mes"].isin(meses_lista)]
    if comerciais:
        df_f = df_f[df_f["Comercial"].isin(comerciais)]
    if clientes:
        df_f = df_f[df_f["Cliente"].isin(clientes)]
    if artigos:
        df_f = df_f[df_f["Artigo"].isin(artigos)]
    
    return df_f

# Mapear meses selecionados para números
meses_map = {nome: num+1 for num, nome in enumerate(meses_nomes)}
meses_num = [meses_map[m] for m in meses_sel if m in meses_map]

# Dados com todos os filtros aplicados (para resumo geral)
df_filtered = aplicar_filtros(
    df,
    anos_lista=[ano_base, ano_comp],
    meses_lista=meses_num or None,
    comerciais=comerciais_sel or None,
    clientes=clientes_sel or None,
    artigos=artigos_sel or None
)

# Dados apenas do ano atual e comparação (para YoY)
df_atual = aplicar_filtros(df, anos_lista=[ano_comp], meses_lista=meses_num or None,
                          comerciais=comerciais_sel, clientes=clientes_sel, artigos=artigos_sel)
df_anterior = aplicar_filtros(df, anos_lista=[ano_base], meses_lista=meses_num or None,
                             comerciais=comerciais_sel, clientes=clientes_sel, artigos=artigos_sel)

# === MÉTRICAS RESUMO ===
st.header("Resumo Executivo")

total_base = df_anterior["Quantidade"].sum()
total_comp = df_atual["Quantidade"].sum()
variacao_pct = ((total_comp - total_base) / total_base * 100) if total_base > 0 else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1: st.metric(f"{ano_base} (Base)", f"{total_base:,.0f}")
with col2: st.metric(f"{ano_comp} (Atual)", f"{total_comp:,.0f}")
with col3: st.metric("Variação %", f"{variacao_pct:+.1f}%", delta=f"{variacao_pct:+.1f}%")
with col4: st.metric("Comerciais", len(comerciais_sel))
with col5: st.metric("Clientes", len(clientes_sel))
with col6: st.metric("Artigos", len(artigos_sel))

st.divider()

# === TABELA COMPARATIVA YOY ===
st.header("Tabela Comparativa YoY (Mês a Mês)")

# Dados para a tabela YoY
df_yoy = aplicar_filtros(df, anos_lista=[ano_base, ano_comp], meses_lista=meses_num or None,
                        comerciais=comerciais_sel, clientes=clientes_sel, artigos=artigos_sel)

kpi = df_yoy.groupby(["Comercial","Cliente","Artigo","Ano","Mes"], as_index=False)["Quantidade"].sum()

pivot = kpi.pivot_table(
    index=["Comercial","Cliente","Artigo","Mes"],
    columns="Ano",
    values="Quantidade",
    fill_value=0
).reset_index()

# Garantir colunas
for a in [ano_base, ano_comp]:
    if a not in pivot.columns:
        pivot[a] = 0

pivot["Variação"] = pivot[ano_comp] - pivot[ano_base]
pivot["Variação_%"] = pivot.apply(
    lambda r: (r["Variação"] / r[ano_base] * 100) if r[ano_base] > 0 else (100 if r[ano_comp] > 0 else 0), axis=1
)
pivot["Mês"] = pivot["Mes"].apply(lambda m: meses_nomes[int(m)-1])

cols = ["Comercial","Cliente","Artigo","Mês", ano_base, ano_comp, "Variação", "Variação_%"]
tabela = pivot[cols].sort_values(["Comercial","Cliente","Artigo","Mês"]).reset_index(drop=True)

if len(tabela) > 0:
    tab_display = tabela.copy()
    for col in [ano_base, ano_comp, "Variação"]:
        tab_display[col] = tab_display[col].apply(lambda x: f"{x:,.0f}")
    tab_display["Variação_%"] = tab_display["Variação_%"].apply(lambda x: f"{x:+.1f}%")

    def highlight_var(val):
        try:
            v = float(val.replace("%", "").replace("+", ""))
            color = "#d4edda" if v > 0 else "#f8d7da" if v < 0 else ""
            return f'background-color: {color}; font-weight: bold'
        except:
            return ''
    
    st.dataframe(tab_display.style.applymap(highlight_var, subset=["Variação_%"]), 
                 use_container_width=True, height=500)
else:
    st.info("Nenhum dado com os filtros aplicados.")

# === GRÁFICOS COM FILTROS CORRETOS ===
st.divider()

col1, col2 = st.columns([3, 2])

# KPI 1: Top Clientes (com filtros aplicados)
with col1:
    st.subheader("Top 20 Clientes (Total Filtrado)")
    kpi1 = df_filtered.groupby("Cliente")["Quantidade"].sum().sort_values(ascending=False).head(20).reset_index()
    if len(kpi1) > 0:
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(kpi1["Cliente"], kpi1["Quantidade"], color="steelblue")
        ax.set_xlabel("Quantidade Total")
        ax.set_title("Top 20 Clientes")
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)

with col2:
    kpi1_disp = kpi1.copy()
    kpi1_disp["Quantidade"] = kpi1_disp["Quantidade"].apply(lambda x: f"{x:,.0f}")
    kpi1_disp.index = range(1, len(kpi1_disp)+1)
    st.dataframe(kpi1_disp, use_container_width=True)

st.divider()

# Evolução Mensal Comparativa (respeitando todos os filtros)
st.header("Evolução Mensal Comparativa")
evol = aplicar_filtros(df, anos_lista=[ano_base, ano_comp], meses_lista=meses_num or None,
                      comerciais=comerciais_sel, clientes=clientes_sel, artigos=artigos_sel)
evol = evol.groupby(["Ano", "Mes"])["Quantidade"].sum().reset_index()
evol["Mês"] = evolu["Mes"].apply(lambda x: meses_nomes[x-1])

fig3, ax3 = plt.subplots(figsize=(14, 6))
for ano in [ano_base, ano_comp]:
    dados_ano = evol[evol["Ano"] == ano].sort_values("Mes")
    if len(dados_ano) > 0:
        ax3.plot(dados_ano["Mês"], dados_ano["Quantidade"], marker='o', label=str(ano), linewidth=3, markersize=8)

ax3.set_title(f"Evolução Mensal: {ano_base} vs {ano_comp}", fontweight="bold")
ax3.set_ylabel("Quantidade")
ax3.legend()
ax3.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig3)

st.divider()

# Performance por Comercial (com filtros)
st.header("Performance por Comercial")
col1, col2 = st.columns(2)

with col1:
    com_tot = df_filtered.groupby("Comercial")["Quantidade"].sum().sort_values(ascending=False)
    fig4, ax4 = plt.subplots()
    ax4.barh(com_tot.index, com_tot.values, color="coral")
    ax4.set_title("Total por Comercial")
    ax4.invert_yaxis()
    st.pyplot(fig4)

with col2:
    com_base = df_anterior.groupby("Comercial")["Quantidade"].sum()
    com_atual = df_atual.groupby("Comercial")["Quantidade"].sum()
    com_yoy = pd.DataFrame({"Base": com_base, "Atual": com_atual}).fillna(0)
    com_yoy["Var_%"] = ((com_yoy["Atual"] - com_yoy["Base"]) / com_yoy["Base"].replace(0,1)) * 100
    com_yoy = com_yoy.sort_values("Var_%", ascending=False)
    com_yoy_disp = com_yoy.copy()
    for c in ["Base", "Atual"]:
        com_yoy_disp[c] = com_yoy_disp[c].apply(lambda x: f"{x:,.0f}")
    com_yoy_disp["Var_%"] = com_yoy_disp["Var_%"].apply(lambda x: f"{x:+.1f}%")
    st.dataframe(com_yoy_disp, use_container_width=True)

st.divider()

# Top Artigos do Ano Atual (com filtros)
st.header("Top 15 Artigos")
top_art = df_atual.groupby("Artigo")["Quantidade"].sum().sort_values(ascending=False).head(15)
fig5, ax5 = plt.subplots(figsize=(10, 6))
ax5.barh(top_art.index, top_art.values, color="seagreen")
ax5.set_title(f"Top 15 Artigos em {ano_comp}")
ax5.invert_yaxis()
plt.tight_layout()
st.pyplot(fig5)

# === EXPORTAR EXCEL ===
st.header("Exportar para Excel")
if len(df_filtered) > 0:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        tabela.to_excel(writer, sheet_name='YoY Detalhado', index=False)
        df_filtered.groupby("Cliente")["Quantidade"].sum().reset_index().to_excel(writer, sheet_name='Top Clientes', index=False)
        com_yoy.to_excel(writer, sheet_name='Performance Comercial', index=False)
    
    st.download_button(
        label="Download Relatório Completo Excel",
        data=output.getvalue(),
        file_name=f"Relatorio_KPIs_{ano_comp}_vs_{ano_base}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.success("Dashboard 100% interativo e com todos os filtros aplicados corretamente!")
