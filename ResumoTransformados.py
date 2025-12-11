import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Dashboard Compras Completo", layout="wide")
st.title("📊 Dashboard Completo de Compras – YoY Analysis")

# --- URL do ficheiro ---
RAW_URL = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"

# === Carregar dados ===
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
    
    df = df[(df["Ano"] >= 2000) & (df["Ano"] <= 2030)]
    
    for col in ["Cliente", "Artigo", "Comercial"]:
        df[col] = df[col].astype(str).str.strip()
        df = df[df[col] != "nan"]
    
    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)
    
    return df

df = load_data()

# === SIDEBAR FILTROS ===
st.sidebar.header("🎯 Filtros Interativos")

# Anos
anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)
st.sidebar.subheader("📅 Período")
ano_comp = st.sidebar.selectbox("Ano Atual", anos_disponiveis, index=0)
ano_base = st.sidebar.selectbox("Ano Base", anos_disponiveis, index=min(1, len(anos_disponiveis)-1))

# Meses
st.sidebar.subheader("📆 Meses")
todos_meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
meses_sel = st.sidebar.multiselect("Meses", todos_meses, default=todos_meses)

st.sidebar.divider()

# === FILTRO INTERATIVO 1: COMERCIAIS ===
st.sidebar.subheader("👔 Comerciais")
lista_comerciais = sorted(df["Comercial"].unique().tolist())

# Checkbox "Todos"
todos_comerciais = st.sidebar.checkbox("Selecionar todos comerciais", value=True, key="check_comerciais")

if todos_comerciais:
    comerciais_sel = lista_comerciais
    st.sidebar.info(f"✓ {len(lista_comerciais)} comerciais selecionados")
else:
    comerciais_sel = st.sidebar.multiselect(
        "Escolha os comerciais:",
        lista_comerciais,
        default=[],
        key="select_comerciais"
    )
    st.sidebar.caption(f"{len(comerciais_sel)}/{len(lista_comerciais)} selecionados")

st.sidebar.divider()

# === FILTRO INTERATIVO 2: CLIENTES ===
st.sidebar.subheader("🏢 Clientes")
lista_clientes = sorted(df["Cliente"].unique().tolist())

todos_clientes = st.sidebar.checkbox("Selecionar todos clientes", value=True, key="check_clientes")

if todos_clientes:
    clientes_sel = lista_clientes
    st.sidebar.info(f"✓ {len(lista_clientes)} clientes selecionados")
else:
    clientes_sel = st.sidebar.multiselect(
        "Escolha os clientes:",
        lista_clientes,
        default=[],
        key="select_clientes"
    )
    st.sidebar.caption(f"{len(clientes_sel)}/{len(lista_clientes)} selecionados")

st.sidebar.divider()

# === FILTRO INTERATIVO 3: ARTIGOS ===
st.sidebar.subheader("📦 Artigos")
lista_artigos = sorted(df["Artigo"].unique().tolist())

todos_artigos = st.sidebar.checkbox("Selecionar todos artigos", value=True, key="check_artigos")

if todos_artigos:
    artigos_sel = lista_artigos
    st.sidebar.info(f"✓ {len(lista_artigos)} artigos selecionados")
else:
    artigos_sel = st.sidebar.multiselect(
        "Escolha os artigos:",
        lista_artigos,
        default=[],
        key="select_artigos"
    )
    st.sidebar.caption(f"{len(artigos_sel)}/{len(lista_artigos)} selecionados")

# === APLICAR FILTROS ===
df_filtered = df.copy()

# Filtro de meses
meses_map = {m: i+1 for i, m in enumerate(todos_meses)}
meses_num = [meses_map[m] for m in meses_sel if m in meses_map]
if meses_num:
    df_filtered = df_filtered[df_filtered["Mes"].isin(meses_num)]

# Aplicar filtros
if comerciais_sel:
    df_filtered = df_filtered[df_filtered["Comercial"].isin(comerciais_sel)]
if clientes_sel:
    df_filtered = df_filtered[df_filtered["Cliente"].isin(clientes_sel)]
if artigos_sel:
    df_filtered = df_filtered[df_filtered["Artigo"].isin(artigos_sel)]

# === MÉTRICAS GERAIS ===
st.subheader(f"📊 Visão Geral: {ano_base} vs {ano_comp}")

dados_base = df_filtered[df_filtered["Ano"] == ano_base]["Quantidade"].sum()
dados_comp = df_filtered[df_filtered["Ano"] == ano_comp]["Quantidade"].sum()
variacao = ((dados_comp - dados_base) / dados_base * 100) if dados_base > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(f"📅 {ano_base}", f"{dados_base:,.0f}")
with col2:
    st.metric(f"📅 {ano_comp}", f"{dados_comp:,.0f}")
with col3:
    st.metric("📈 Variação", f"{variacao:+.1f}%")
with col4:
    st.metric("👥 Comerciais", len(comerciais_sel))
with col5:
    st.metric("📋 Registros", f"{len(df_filtered):,}")

# === TABELA COMPARATIVA YoY ===
st.subheader("📋 Tabela Comparativa YoY por Comercial, Cliente, Artigo e Mês")

# Preparar dados
pivot_data = df_filtered.groupby(["Comercial", "Cliente", "Artigo", "Ano", "Mes"]).agg({
    "Quantidade": "sum"
}).reset_index()

tabela = pivot_data.pivot_table(
    index=["Comercial", "Cliente", "Artigo", "Mes"],
    columns="Ano",
    values="Quantidade",
    fill_value=0
).reset_index()

if ano_base not in tabela.columns:
    tabela[ano_base] = 0
if ano_comp not in tabela.columns:
    tabela[ano_comp] = 0

tabela["Variação"] = tabela[ano_comp] - tabela[ano_base]
tabela["Variação_%"] = tabela.apply(
    lambda row: (row["Variação"] / row[ano_base] * 100) if row[ano_base] > 0 else 0,
    axis=1
)

tabela["Mês"] = tabela["Mes"].apply(lambda m: todos_meses[int(m)-1] if 1 <= int(m) <= 12 else str(m))
tabela = tabela.sort_values(["Comercial", "Cliente", "Artigo", "Mes"])

colunas = ["Comercial", "Cliente", "Artigo", "Mês", ano_base, ano_comp, "Variação", "Variação_%"]
tabela_final = tabela[colunas].reset_index(drop=True)

if len(tabela_final) > 0:
    # Formatação visual
    def color_row(row):
        try:
            var = row["Variação_%"]
            if var > 0:
                return [''] * 4 + [''] * 2 + ['background-color: #d4edda'] + ['background-color: #d4edda; font-weight: bold']
            elif var < 0:
                return [''] * 4 + [''] * 2 + ['background-color: #f8d7da'] + ['background-color: #f8d7da; font-weight: bold']
            return [''] * 8
        except:
            return [''] * 8
    
    tabela_display = tabela_final.copy()
    tabela_display[ano_base] = tabela_display[ano_base].apply(lambda x: f"{x:,.0f}")
    tabela_display[ano_comp] = tabela_display[ano_comp].apply(lambda x: f"{x:,.0f}")
    tabela_display["Variação"] = tabela_display["Variação"].apply(lambda x: f"{x:+,.0f}")
    tabela_display["Variação_%"] = tabela_display["Variação_%"].apply(lambda x: f"{x:+.1f}%")
    
    styled = tabela_display.style.apply(color_row, axis=1)
    st.dataframe(styled, use_container_width=True, height=400)
else:
    st.warning("⚠️ Nenhum dado disponível com os filtros atuais")

# === KPI 1: TOTAL POR CLIENTE ===
st.subheader("📊 KPI 1 – Total de Quantidade por Cliente")

col1, col2 = st.columns([2, 1])

with col1:
    kpi_cliente = df_filtered.groupby("Cliente")["Quantidade"].sum().reset_index()
    kpi_cliente = kpi_cliente.sort_values("Quantidade", ascending=False).head(15)
    
    if len(kpi_cliente) > 0:
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        ax1.barh(kpi_cliente["Cliente"], kpi_cliente["Quantidade"], color="steelblue")
        ax1.set_xlabel("Quantidade Total")
        ax1.set_title("Top 15 Clientes por Quantidade")
        ax1.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig1)

with col2:
    if len(kpi_cliente) > 0:
        kpi_display = kpi_cliente.copy()
        kpi_display["Quantidade"] = kpi_display["Quantidade"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(kpi_display, use_container_width=True, height=400)

# === KPI 2: PERCENTAGEM POR ARTIGO DENTRO DE CADA CLIENTE ===
st.subheader("📊 KPI 2 – Distribuição Percentual de Artigos por Cliente")

if len(df_filtered) > 0:
    total_por_cliente = df_filtered.groupby("Cliente")["Quantidade"].sum()
    
    df_perc = df_filtered.copy()
    df_perc["Perc_Artigo"] = df_perc.apply(
        lambda row: (row["Quantidade"] / total_por_cliente[row["Cliente"]] * 100) 
        if total_por_cliente[row["Cliente"]] > 0 else 0,
        axis=1
    )
    
    kpi_artigo = df_perc.groupby(["Cliente", "Artigo"])["Perc_Artigo"].sum().reset_index()
    kpi_artigo = kpi_artigo.sort_values(["Cliente", "Perc_Artigo"], ascending=[True, False])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico stacked bar
        pivot_perc = kpi_artigo.pivot(index="Cliente", columns="Artigo", values="Perc_Artigo").fillna(0)
        
        # Pegar só os top clientes para não sobrecarregar o gráfico
        top_clientes = df_filtered.groupby("Cliente")["Quantidade"].sum().nlargest(10).index
        pivot_perc_top = pivot_perc.loc[pivot_perc.index.isin(top_clientes)]
        
        if len(pivot_perc_top) > 0:
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            pivot_perc_top.plot(kind="bar", stacked=True, ax=ax2, colormap="tab20", legend=False)
            ax2.set_title("Distribuição Percentual de Artigos (Top 10 Clientes)")
            ax2.set_ylabel("Percentagem (%)")
            ax2.set_xlabel("Cliente")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig2)
    
    with col2:
        # Tabela com percentagens
        kpi_display2 = kpi_artigo.copy()
        kpi_display2["Perc_Artigo"] = kpi_display2["Perc_Artigo"].apply(lambda x: f"{x:.2f}%")
        st.dataframe(kpi_display2.head(20), use_container_width=True, height=400)

# === KPI 3: EVOLUÇÃO MENSAL ===
st.subheader("📊 KPI 3 – Evolução Mensal Comparativa")

evolucao = df_filtered.groupby(["Ano", "Mes"])["Quantidade"].sum().reset_index()
evolucao["MesNome"] = evolucao["Mes"].apply(lambda m: todos_meses[m-1] if 1 <= m <= 12 else str(m))

fig3, ax3 = plt.subplots(figsize=(14, 6))

for ano in [ano_base, ano_comp]:
    dados_ano = evolucao[evolucao["Ano"] == ano].sort_values("Mes")
    if len(dados_ano) > 0:
        ax3.plot(dados_ano["MesNome"], dados_ano["Quantidade"], 
                marker='o', label=str(ano), linewidth=2.5, markersize=8)

ax3.set_xlabel("Mês", fontsize=12)
ax3.set_ylabel("Quantidade", fontsize=12)
ax3.set_title(f"Comparativo Mensal {ano_base} vs {ano_comp}", fontsize=14, fontweight='bold')
ax3.legend(fontsize=11)
ax3.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig3)

# === KPI 4: TOP COMERCIAIS ===
st.subheader("📊 KPI 4 – Performance por Comercial")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🏆 Ranking Comerciais")
    comerciais_ranking = df_filtered.groupby("Comercial")["Quantidade"].sum().reset_index()
    comerciais_ranking = comerciais_ranking.sort_values("Quantidade", ascending=False)
    
    if len(comerciais_ranking) > 0:
        fig4, ax4 = plt.subplots(figsize=(8, 6))
        ax4.barh(comerciais_ranking["Comercial"], comerciais_ranking["Quantidade"], color="coral")
        ax4.set_xlabel("Quantidade Total")
        ax4.set_title("Performance por Comercial")
        ax4.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig4)

with col2:
    st.markdown("#### 📈 Variação YoY por Comercial")
    
    comercial_base = df_filtered[df_filtered["Ano"] == ano_base].groupby("Comercial")["Quantidade"].sum()
    comercial_comp = df_filtered[df_filtered["Ano"] == ano_comp].groupby("Comercial")["Quantidade"].sum()
    
    comercial_yoy = pd.DataFrame({
        ano_base: comercial_base,
        ano_comp: comercial_comp
    }).fillna(0)
    
    comercial_yoy["Variação_%"] = comercial_yoy.apply(
        lambda row: ((row[ano_comp] - row[ano_base]) / row[ano_base] * 100) 
        if row[ano_base] > 0 else 0,
        axis=1
    )
    
    comercial_yoy = comercial_yoy.reset_index().sort_values("Variação_%", ascending=False)
    
    comercial_display = comercial_yoy.copy()
    comercial_display[ano_base] = comercial_display[ano_base].apply(lambda x: f"{x:,.0f}")
    comercial_display[ano_comp] = comercial_display[ano_comp].apply(lambda x: f"{x:,.0f}")
    comercial_display["Variação_%"] = comercial_display["Variação_%"].apply(lambda x: f"{x:+.1f}%")
    
    st.dataframe(comercial_display, use_container_width=True)

# === EXPORTAR EXCEL ===
st.subheader("💾 Exportar Relatório Completo")

if len(tabela_final) > 0:
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: Tabela Comparativa
        tabela_final.to_excel(writer, sheet_name='Comparativo YoY', index=False)
        
        # Sheet 2: KPI Clientes
        kpi_cliente_full = df_filtered.groupby("Cliente")["Quantidade"].sum().reset_index()
        kpi_cliente_full = kpi_cliente_full.sort_values("Quantidade", ascending=False)
        kpi_cliente_full.to_excel(writer, sheet_name='KPI Clientes', index=False)
        
        # Sheet 3: KPI Artigos
        kpi_artigo.to_excel(writer, sheet_name='KPI Artigos', index=False)
        
        # Sheet 4: KPI Comerciais
        comercial_yoy.to_excel(writer, sheet_name='KPI Comerciais', index=False)
        
        # Sheet 5: Resumo
        resumo = pd.DataFrame({
            'Métrica': [
                f'Total {ano_base}',
                f'Total {ano_comp}',
                'Variação Absoluta',
                'Variação %',
                'Comerciais Filtrados',
                'Clientes Filtrados',
                'Artigos Filtrados',
                'Total Registros'
            ],
            'Valor': [
                f"{dados_base:,.0f}",
                f"{dados_comp:,.0f}",
                f"{dados_comp - dados_base:+,.0f}",
                f"{variacao:+.2f}%",
                len(comerciais_sel),
                len(clientes_sel),
                len(artigos_sel),
                len(df_filtered)
            ]
        })
        resumo.to_excel(writer, sheet_name='Resumo', index=False)
        
        # Formatação
        workbook = writer.book
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for i, col in enumerate(writer.sheets[sheet_name].table.keys() if hasattr(writer.sheets[sheet_name], 'table') else []):
                worksheet.set_column(i, i, 15)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.download_button(
            label="📥 Download Excel Completo",
            data=output.getvalue(),
            file_name=f"Dashboard_Completo_{ano_base}_vs_{ano_comp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
else:
    st.warning("⚠️ Sem dados para exportar")
