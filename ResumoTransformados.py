import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Dashboard Compras YoY", layout="wide")
st.title("📊 Dashboard de Compras – Análise Year-over-Year")

# --- URL do ficheiro ---
RAW_URL = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"

# === Carregar dados ===
@st.cache_data
def load_data():
    df_raw = pd.read_excel(RAW_URL)
    
    df = pd.DataFrame({
        "Cliente":   df_raw.iloc[:, 1],   # Coluna B
        "Artigo":    df_raw.iloc[:, 2],   # Coluna C
        "Comercial": df_raw.iloc[:, 8],   # Coluna I
        "Data":      df_raw.iloc[:, 0],   # Coluna A
        "Quantidade":df_raw.iloc[:, 3],   # Coluna D
    })
    
    # Limpar e converter dados
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"])
    
    df["Ano"] = df["Data"].dt.year
    df["Mes"] = df["Data"].dt.month
    df["MesNome"] = df["Data"].dt.strftime("%b")
    
    # Filtrar anos válidos
    df = df[(df["Ano"] >= 2000) & (df["Ano"] <= 2030)]
    
    # Limpar strings
    for col in ["Cliente", "Artigo", "Comercial"]:
        df[col] = df[col].astype(str).str.strip()
        df = df[df[col] != "nan"]
    
    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)
    
    return df

df = load_data()

# === SIDEBAR - FILTROS ===
st.sidebar.header("🎯 Filtros")

# Anos para comparação
anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)
st.sidebar.subheader("📅 Período")
ano_comp = st.sidebar.selectbox("Ano Atual", anos_disponiveis, index=0)
ano_base = st.sidebar.selectbox("Ano Anterior", anos_disponiveis, index=min(1, len(anos_disponiveis)-1))

# Meses
st.sidebar.subheader("📆 Meses")
todos_meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
meses_sel = st.sidebar.multiselect("Selecionar meses", todos_meses, default=todos_meses)

# Comerciais
st.sidebar.subheader("👔 Filtrar por Comercial")
todos_comerciais = ["Todos"] + sorted(df["Comercial"].unique().tolist())
comercial_sel = st.sidebar.selectbox("Comercial", todos_comerciais)

# Clientes
st.sidebar.subheader("🏢 Filtrar por Cliente")
todos_clientes = ["Todos"] + sorted(df["Cliente"].unique().tolist())
cliente_sel = st.sidebar.selectbox("Cliente", todos_clientes)

# Artigos
st.sidebar.subheader("📦 Filtrar por Artigo")
todos_artigos = ["Todos"] + sorted(df["Artigo"].unique().tolist())
artigo_sel = st.sidebar.selectbox("Artigo", todos_artigos)

# === APLICAR FILTROS ===
df_filtered = df.copy()

# Filtro de meses
meses_map = {m: i+1 for i, m in enumerate(todos_meses)}
meses_num = [meses_map[m] for m in meses_sel if m in meses_map]
if meses_num:
    df_filtered = df_filtered[df_filtered["Mes"].isin(meses_num)]

# Filtros específicos
if comercial_sel != "Todos":
    df_filtered = df_filtered[df_filtered["Comercial"] == comercial_sel]
if cliente_sel != "Todos":
    df_filtered = df_filtered[df_filtered["Cliente"] == cliente_sel]
if artigo_sel != "Todos":
    df_filtered = df_filtered[df_filtered["Artigo"] == artigo_sel]

# === MÉTRICAS RESUMO ===
st.subheader(f"📈 Comparativo {ano_base} vs {ano_comp}")

dados_base = df_filtered[df_filtered["Ano"] == ano_base]["Quantidade"].sum()
dados_comp = df_filtered[df_filtered["Ano"] == ano_comp]["Quantidade"].sum()
variacao = ((dados_comp - dados_base) / dados_base * 100) if dados_base > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(f"Total {ano_base}", f"{dados_base:,.0f}", help="Quantidade total no ano base")
with col2:
    st.metric(f"Total {ano_comp}", f"{dados_comp:,.0f}", help="Quantidade total no ano comparação")
with col3:
    st.metric("Variação", f"{variacao:+.1f}%", delta=f"{dados_comp - dados_base:,.0f}")
with col4:
    registros = len(df_filtered)
    st.metric("Registros", f"{registros:,}")

# === TABELA DETALHADA ===
st.subheader("📋 Análise Detalhada por Cliente, Artigo e Mês")

# Criar pivot table
pivot_data = df_filtered.groupby(["Comercial", "Cliente", "Artigo", "Ano", "Mes"]).agg({
    "Quantidade": "sum"
}).reset_index()

# Criar tabela comparativa
tabela = pivot_data.pivot_table(
    index=["Comercial", "Cliente", "Artigo", "Mes"],
    columns="Ano",
    values="Quantidade",
    fill_value=0
).reset_index()

# Adicionar colunas necessárias
if ano_base not in tabela.columns:
    tabela[ano_base] = 0
if ano_comp not in tabela.columns:
    tabela[ano_comp] = 0

tabela["Variação"] = tabela[ano_comp] - tabela[ano_base]
tabela["Variação_%"] = tabela.apply(
    lambda row: (row["Variação"] / row[ano_base] * 100) if row[ano_base] > 0 else 0,
    axis=1
)

# Adicionar nome do mês
tabela["Mês"] = tabela["Mes"].apply(lambda m: todos_meses[int(m)-1] if 1 <= int(m) <= 12 else str(m))

# Ordenar e selecionar colunas
tabela = tabela.sort_values(["Comercial", "Cliente", "Artigo", "Mes"])
colunas_exibir = ["Comercial", "Cliente", "Artigo", "Mês", ano_base, ano_comp, "Variação", "Variação_%"]
tabela_final = tabela[colunas_exibir].reset_index(drop=True)

# Exibir tabela
if len(tabela_final) > 0:
    # Formatação com cores
    def highlight_variacao(val):
        try:
            if val > 0:
                return 'background-color: #d4edda; color: #155724'
            elif val < 0:
                return 'background-color: #f8d7da; color: #721c24'
            return ''
        except:
            return ''
    
    tabela_display = tabela_final.copy()
    tabela_display[ano_base] = tabela_display[ano_base].apply(lambda x: f"{x:,.0f}")
    tabela_display[ano_comp] = tabela_display[ano_comp].apply(lambda x: f"{x:,.0f}")
    tabela_display["Variação"] = tabela_display["Variação"].apply(lambda x: f"{x:+,.0f}")
    tabela_display["Variação_%"] = tabela_display["Variação_%"].apply(lambda x: f"{x:+.1f}%")
    
    styled = tabela_display.style.applymap(
        lambda x: highlight_variacao(float(x.replace('%','').replace(',','').replace('+',''))) if '%' in str(x) else '',
        subset=["Variação_%"]
    )
    
    st.dataframe(styled, use_container_width=True, height=400)
else:
    st.info("⚠️ Nenhum dado disponível para os filtros selecionados")

# === GRÁFICO EVOLUÇÃO MENSAL ===
st.subheader("📊 Evolução Mensal")

if len(df_filtered) > 0:
    evolucao = df_filtered.groupby(["Ano", "Mes"]).agg({"Quantidade": "sum"}).reset_index()
    evolucao["MesNome"] = evolucao["Mes"].apply(lambda m: todos_meses[m-1] if 1 <= m <= 12 else str(m))
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    for ano in [ano_base, ano_comp]:
        dados_ano = evolucao[evolucao["Ano"] == ano].sort_values("Mes")
        if len(dados_ano) > 0:
            ax.plot(dados_ano["MesNome"], dados_ano["Quantidade"], marker='o', label=str(ano), linewidth=2)
    
    ax.set_xlabel("Mês")
    ax.set_ylabel("Quantidade")
    ax.set_title(f"Comparativo Mensal {ano_base} vs {ano_comp}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# === TOP CLIENTES ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 10 Clientes")
    top_clientes = df_filtered[df_filtered["Ano"] == ano_comp].groupby("Cliente").agg({
        "Quantidade": "sum"
    }).sort_values("Quantidade", ascending=False).head(10).reset_index()
    
    if len(top_clientes) > 0:
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        ax1.barh(top_clientes["Cliente"], top_clientes["Quantidade"], color="steelblue")
        ax1.set_xlabel("Quantidade")
        ax1.set_title(f"Top 10 Clientes - {ano_comp}")
        ax1.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig1)

with col2:
    st.subheader("📦 Top 10 Artigos")
    top_artigos = df_filtered[df_filtered["Ano"] == ano_comp].groupby("Artigo").agg({
        "Quantidade": "sum"
    }).sort_values("Quantidade", ascending=False).head(10).reset_index()
    
    if len(top_artigos) > 0:
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.barh(top_artigos["Artigo"], top_artigos["Quantidade"], color="coral")
        ax2.set_xlabel("Quantidade")
        ax2.set_title(f"Top 10 Artigos - {ano_comp}")
        ax2.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig2)

# === EXPORTAR PARA EXCEL ===
st.subheader("💾 Exportar Dados")

if len(tabela_final) > 0:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("📥 Exporte os dados filtrados para análise em Excel")
    
    with col2:
        # Criar Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Sheet principal
            tabela_final.to_excel(writer, sheet_name='Comparativo YoY', index=False)
            
            # Sheet resumo
            resumo = pd.DataFrame({
                'Métrica': ['Total ' + str(ano_base), 'Total ' + str(ano_comp), 'Variação', 'Variação %'],
                'Valor': [dados_base, dados_comp, dados_comp - dados_base, variacao]
            })
            resumo.to_excel(writer, sheet_name='Resumo', index=False)
            
            # Formatação
            workbook = writer.book
            worksheet = writer.sheets['Comparativo YoY']
            
            # Auto-ajustar colunas
            for i, col in enumerate(tabela_final.columns):
                max_len = max(tabela_final[col].astype(str).str.len().max(), len(col)) + 2
                worksheet.set_column(i, i, min(max_len, 30))
        
        st.download_button(
            label="📥 Download Excel",
            data=output.getvalue(),
            file_name=f"Relatorio_YoY_{ano_base}_vs_{ano_comp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
else:
    st.warning("⚠️ Sem dados para exportar")
