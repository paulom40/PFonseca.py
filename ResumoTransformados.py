import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Dashboard Completo KPIs", layout="wide")
st.title("📊 Dashboard Completo de Análise de Compras")

# URL do ficheiro
RAW_URL = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"

# === CARREGAR DADOS ===
@st.cache_data
def load_data():
    df_raw = pd.read_excel(RAW_URL)
    
    # Mapear colunas
    df = pd.DataFrame({
        "Cliente":   df_raw.iloc[:, 1],   # Coluna B
        "Artigo":    df_raw.iloc[:, 2],   # Coluna C
        "Comercial": df_raw.iloc[:, 8],   # Coluna I
        "Data":      df_raw.iloc[:, 0],   # Coluna A
        "Quantidade":df_raw.iloc[:, 3],   # Coluna D
    })
    
    # Limpar dados
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"])
    df["Ano"] = df["Data"].dt.year
    df["Mes"] = df["Data"].dt.month
    df = df[(df["Ano"] >= 2000) & (df["Ano"] <= 2030)]
    
    for col in ["Cliente", "Artigo", "Comercial"]:
        df[col] = df[col].astype(str).str.strip()
        df = df[df[col] != "nan"]
    
    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)
    
    return df

with st.spinner("🔄 A carregar dados..."):
    df = load_data()

# === SIDEBAR - FILTROS ===
st.sidebar.header("🎯 Filtros")

# Anos
anos = sorted(df["Ano"].unique(), reverse=True)
st.sidebar.subheader("📅 Período")
ano_comp = st.sidebar.selectbox("Ano Atual", anos, index=0)
ano_base = st.sidebar.selectbox("Ano Comparação", anos, index=min(1, len(anos)-1))

# Meses
st.sidebar.subheader("📆 Meses")
meses_nomes = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
meses_sel = st.sidebar.multiselect("Meses", meses_nomes, default=meses_nomes)

st.sidebar.divider()

# Filtro Comerciais
st.sidebar.subheader("👔 Comerciais")
lista_comerciais = sorted(df["Comercial"].unique())
todos_com = st.sidebar.checkbox("Todos comerciais", value=True)
if todos_com:
    comerciais_sel = lista_comerciais
    st.sidebar.success(f"✓ {len(lista_comerciais)} selecionados")
else:
    comerciais_sel = st.sidebar.multiselect("Escolher", lista_comerciais, default=[])

st.sidebar.divider()

# Filtro Clientes
st.sidebar.subheader("🏢 Clientes")
lista_clientes = sorted(df["Cliente"].unique())
todos_cli = st.sidebar.checkbox("Todos clientes", value=True)
if todos_cli:
    clientes_sel = lista_clientes
    st.sidebar.success(f"✓ {len(lista_clientes)} selecionados")
else:
    clientes_sel = st.sidebar.multiselect("Escolher", lista_clientes, default=[])

st.sidebar.divider()

# Filtro Artigos
st.sidebar.subheader("📦 Artigos")
lista_artigos = sorted(df["Artigo"].unique())
todos_art = st.sidebar.checkbox("Todos artigos", value=True)
if todos_art:
    artigos_sel = lista_artigos
    st.sidebar.success(f"✓ {len(lista_artigos)} selecionados")
else:
    artigos_sel = st.sidebar.multiselect("Escolher", lista_artigos, default=[])

# === APLICAR FILTROS ===
df_filtered = df.copy()

meses_map = {m: i+1 for i, m in enumerate(meses_nomes)}
meses_num = [meses_map[m] for m in meses_sel if m in meses_map]
if meses_num:
    df_filtered = df_filtered[df_filtered["Mes"].isin(meses_num)]

if comerciais_sel:
    df_filtered = df_filtered[df_filtered["Comercial"].isin(comerciais_sel)]
if clientes_sel:
    df_filtered = df_filtered[df_filtered["Cliente"].isin(clientes_sel)]
if artigos_sel:
    df_filtered = df_filtered[df_filtered["Artigo"].isin(artigos_sel)]

# === MÉTRICAS RESUMO ===
st.header("📈 Resumo Executivo")

total_base = df_filtered[df_filtered["Ano"] == ano_base]["Quantidade"].sum()
total_comp = df_filtered[df_filtered["Ano"] == ano_comp]["Quantidade"].sum()
variacao_pct = ((total_comp - total_base) / total_base * 100) if total_base > 0 else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric(f"📅 {ano_base}", f"{total_base:,.0f}")
with col2:
    st.metric(f"📅 {ano_comp}", f"{total_comp:,.0f}")
with col3:
    st.metric("📊 Variação", f"{variacao_pct:+.1f}%")
with col4:
    st.metric("👔 Comerciais", len(comerciais_sel))
with col5:
    st.metric("🏢 Clientes", len(clientes_sel))
with col6:
    st.metric("📦 Artigos", len(artigos_sel))

st.divider()

# === TABELA COMPARATIVA YOY ===
st.header("📋 Tabela Comparativa YoY")

kpi = df_filtered.groupby(["Comercial","Cliente","Artigo","Ano","Mes"], as_index=False)["Quantidade"].sum()

pivot = kpi.pivot_table(
    index=["Comercial","Cliente","Artigo","Mes"],
    columns="Ano",
    values="Quantidade",
    fill_value=0
).reset_index()

if ano_base not in pivot.columns:
    pivot[ano_base] = 0
if ano_comp not in pivot.columns:
    pivot[ano_comp] = 0

pivot["Variação"] = pivot[ano_comp] - pivot[ano_base]
pivot["Variação_%"] = pivot.apply(
    lambda r: (r["Variação"] / r[ano_base] * 100) if r[ano_base] > 0 else 0, axis=1
)
pivot["Mês"] = pivot["Mes"].apply(lambda m: meses_nomes[int(m)-1] if 1<=int(m)<=12 else str(m))
pivot = pivot.sort_values(["Comercial","Cliente","Artigo","Mes"]).reset_index(drop=True)

cols = ["Comercial","Cliente","Artigo","Mês",ano_base,ano_comp,"Variação","Variação_%"]
tabela = pivot[cols]

if len(tabela) > 0:
    tab_display = tabela.copy()
    tab_display[ano_base] = tab_display[ano_base].apply(lambda x: f"{x:,.0f}")
    tab_display[ano_comp] = tab_display[ano_comp].apply(lambda x: f"{x:,.0f}")
    tab_display["Variação"] = tab_display["Variação"].apply(lambda x: f"{x:+,.0f}")
    tab_display["Variação_%"] = tab_display["Variação_%"].apply(lambda x: f"{x:+.1f}%")
    
    def color_var(val):
        try:
            num = float(val.replace('%','').replace('+',''))
            if num > 0: return 'background-color: #d4edda; color: #155724; font-weight: bold'
            elif num < 0: return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            return ''
        except: return ''
    
    styled = tab_display.style.applymap(color_var, subset=["Variação_%"])
    st.dataframe(styled, use_container_width=True, height=400)
else:
    st.warning("⚠️ Sem dados para mostrar")

st.divider()

# === KPI 1: TOTAL POR CLIENTE ===
st.header("📊 KPI 1 – Total de Quantidade por Cliente")

col1, col2 = st.columns([3, 2])

with col1:
    kpi1 = df_filtered.groupby("Cliente")["Quantidade"].sum().reset_index()
    kpi1 = kpi1.sort_values("Quantidade", ascending=False).head(20)
    
    if len(kpi1) > 0:
        fig1, ax1 = plt.subplots(figsize=(10, 8))
        ax1.barh(kpi1["Cliente"], kpi1["Quantidade"], color="steelblue")
        ax1.set_xlabel("Quantidade Total", fontsize=11)
        ax1.set_title("Top 20 Clientes por Quantidade", fontsize=13, fontweight="bold")
        ax1.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig1)

with col2:
    if len(kpi1) > 0:
        kpi1_display = kpi1.copy()
        kpi1_display["Quantidade"] = kpi1_display["Quantidade"].apply(lambda x: f"{x:,.0f}")
        kpi1_display.index = range(1, len(kpi1_display)+1)
        st.dataframe(kpi1_display, use_container_width=True, height=550)

st.divider()

# === KPI 2: PERCENTAGEM POR ARTIGO DENTRO DE CADA CLIENTE ===
st.header("📊 KPI 2 – Distribuição % de Artigos por Cliente")

total_cliente = df_filtered.groupby("Cliente")["Quantidade"].sum()
df_perc = df_filtered.copy()
df_perc["Perc"] = df_perc.apply(
    lambda r: (r["Quantidade"]/total_cliente[r["Cliente"]]*100) if total_cliente[r["Cliente"]]>0 else 0, axis=1
)

kpi2 = df_perc.groupby(["Cliente","Artigo"])["Perc"].sum().reset_index()
kpi2 = kpi2.sort_values(["Cliente","Perc"], ascending=[True,False])

col1, col2 = st.columns([3, 2])

with col1:
    # Gráfico stacked - top 10 clientes
    pivot_perc = kpi2.pivot(index="Cliente", columns="Artigo", values="Perc").fillna(0)
    top10_clientes = df_filtered.groupby("Cliente")["Quantidade"].sum().nlargest(10).index
    pivot_top = pivot_perc.loc[pivot_perc.index.isin(top10_clientes)]
    
    if len(pivot_top) > 0:
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        pivot_top.plot(kind="bar", stacked=True, ax=ax2, colormap="tab20")
        ax2.set_title("Distribuição % de Artigos (Top 10 Clientes)", fontsize=13, fontweight="bold")
        ax2.set_ylabel("Percentagem (%)", fontsize=11)
        ax2.set_xlabel("Cliente", fontsize=11)
        ax2.legend(title="Artigos", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig2)

with col2:
    kpi2_display = kpi2.head(30).copy()
    kpi2_display["Perc"] = kpi2_display["Perc"].apply(lambda x: f"{x:.2f}%")
    kpi2_display.index = range(1, len(kpi2_display)+1)
    st.dataframe(kpi2_display, use_container_width=True, height=450)

st.divider()

# === GRÁFICO EVOLUÇÃO MENSAL ===
st.header("📈 Evolução Mensal Comparativa")

evolucao = df_filtered.groupby(["Ano","Mes"])["Quantidade"].sum().reset_index()
evolucao["MesNome"] = evolucao["Mes"].apply(lambda m: meses_nomes[m-1] if 1<=m<=12 else str(m))

fig3, ax3 = plt.subplots(figsize=(14, 6))
for ano in [ano_base, ano_comp]:
    dados = evolucao[evolucao["Ano"]==ano].sort_values("Mes")
    if len(dados) > 0:
        ax3.plot(dados["MesNome"], dados["Quantidade"], marker='o', label=str(ano), linewidth=3, markersize=8)

ax3.set_xlabel("Mês", fontsize=12)
ax3.set_ylabel("Quantidade", fontsize=12)
ax3.set_title(f"Comparativo Mensal {ano_base} vs {ano_comp}", fontsize=14, fontweight="bold")
ax3.legend(fontsize=12)
ax3.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig3)

st.divider()

# === TOP COMERCIAIS ===
st.header("🏆 Performance por Comercial")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Total por Comercial")
    comerciais = df_filtered.groupby("Comercial")["Quantidade"].sum().reset_index()
    comerciais = comerciais.sort_values("Quantidade", ascending=False)
    
    if len(comerciais) > 0:
        fig4, ax4 = plt.subplots(figsize=(8, 6))
        ax4.barh(comerciais["Comercial"], comerciais["Quantidade"], color="coral")
        ax4.set_xlabel("Quantidade Total")
        ax4.set_title("Ranking de Comerciais")
        ax4.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig4)

with col2:
    st.subheader("Variação YoY por Comercial")
    
    com_base = df_filtered[df_filtered["Ano"]==ano_base].groupby("Comercial")["Quantidade"].sum()
    com_comp = df_filtered[df_filtered["Ano"]==ano_comp].groupby("Comercial")["Quantidade"].sum()
    
    com_yoy = pd.DataFrame({ano_base: com_base, ano_comp: com_comp}).fillna(0)
    com_yoy["Var_%"] = com_yoy.apply(
        lambda r: ((r[ano_comp]-r[ano_base])/r[ano_base]*100) if r[ano_base]>0 else 0, axis=1
    )
    com_yoy = com_yoy.reset_index().sort_values("Var_%", ascending=False)
    
    com_display = com_yoy.copy()
    com_display[ano_base] = com_display[ano_base].apply(lambda x: f"{x:,.0f}")
    com_display[ano_comp] = com_display[ano_comp].apply(lambda x: f"{x:,.0f}")
    com_display["Var_%"] = com_display["Var_%"].apply(lambda x: f"{x:+.1f}%")
    
    st.dataframe(com_display, use_container_width=True, height=400)

st.divider()

# === TOP ARTIGOS ===
st.header("📦 Top Artigos")

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Top 15 Artigos - {ano_comp}")
    top_art = df_filtered[df_filtered["Ano"]==ano_comp].groupby("Artigo")["Quantidade"].sum()
    top_art = top_art.sort_values(ascending=False).head(15).reset_index()
    
    if len(top_art) > 0:
        fig5, ax5 = plt.subplots(figsize=(8, 6))
        ax5.barh(top_art["Artigo"], top_art["Quantidade"], color="seagreen")
        ax5.set_xlabel("Quantidade")
        ax5.set_title(f"Top 15 Artigos {ano_comp}")
        ax5.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig5)

with col2:
    st.subheader("Comparativo Artigos")
    top_art_display = top_art.copy()
    top_art_display["Quantidade"] = top_art_display["Quantidade"].apply(lambda x: f"{x:,.0f}")
    top_art_display.index = range(1, len(top_art_display)+1)
    st.dataframe(top_art_display, use_container_width=True, height=400)

st.divider()

# === EXPORTAR EXCEL ===
st.header("💾 Exportar para Excel")

if len(tabela) > 0:
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: Comparativo YoY
        tabela.to_excel(writer, sheet_name='Comparativo YoY', index=False)
        
        # Sheet 2: KPI Clientes
        kpi1_full = df_filtered.groupby("Cliente")["Quantidade"].sum().sort_values(ascending=False).reset_index()
        kpi1_full.to_excel(writer, sheet_name='KPI Clientes', index=False)
        
        # Sheet 3: KPI Artigos
        kpi2.to_excel(writer, sheet_name='KPI Artigos-Cliente', index=False)
        
        # Sheet 4: KPI Comerciais
        com_yoy.to_excel(writer, sheet_name='KPI Comerciais', index=False)
        
        # Sheet 5: Resumo
        resumo = pd.DataFrame({
            'Indicador': [
                f'Total {ano_base}', f'Total {ano_comp}', 'Variação', 'Variação %',
                'Comerciais', 'Clientes', 'Artigos', 'Registros'
            ],
            'Valor': [
                total_base, total_comp, total_comp-total_base, variacao_pct,
                len(comerciais_sel), len(clientes_sel), len(artigos_sel), len(df_filtered)
            ]
        })
        resumo.to_excel(writer, sheet_name='Resumo', index=False)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.download_button(
            label="📥 Download Excel Completo",
            data=output.getvalue(),
            file_name=f"Dashboard_KPIs_{ano_base}_vs_{ano_comp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

st.success("✅ Dashboard completo com todos os KPIs carregado!")
