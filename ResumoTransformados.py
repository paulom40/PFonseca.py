import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# === Configuração da página ===
st.set_page_config(page_title="KPI Compras Clientes (YoY)", layout="wide")

# === CSS customizado ===
st.markdown("""
    <style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
        padding: 20px;
        border-right: 2px solid #ccc;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #2c3e50;
    }
    /* Dataframe styling */
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 8px;
        overflow: hidden;
    }
    /* Title styling */
    h1 {
        color: #1a5276;
    }
    h2 {
        color: #21618c;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 KPI de Compras por Cliente e Artigo (YoY)")

# --- URL raw do ficheiro no GitHub ---
RAW_URL = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"

# === 1. Ler ficheiro diretamente ===
df = pd.read_excel(RAW_URL)

# === 2. Normalizar colunas ===
df = df.rename(columns={"Nome":"Nome","Quantidade":"Quantidade","Data":"Data","Artigo":"Artigo"})
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df = df.dropna(subset=["Data"])
df["Ano"] = df["Data"].dt.year
df["Mes"] = df["Data"].dt.month
df["Nome"] = df["Nome"].astype(str).str.strip()
df["Artigo"] = df["Artigo"].astype(str).str.strip()
df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)

# === 3. Agrupar KPI ===
kpi = df.groupby(["Nome","Artigo","Ano","Mes"], as_index=False)["Quantidade"].sum()

# === 4. Sidebar com filtros dinâmicos ===
with st.sidebar:
    st.header("Filtros")
    anos_disponiveis = sorted(kpi["Ano"].unique())
    ano_base = st.selectbox("Ano base", anos_disponiveis, index=max(0,len(anos_disponiveis)-2))
    ano_comp = st.selectbox("Ano comparação", anos_disponiveis, index=len(anos_disponiveis)-1)

    meses_nomes = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    meses_sel = st.multiselect("Selecionar meses", meses_nomes, default=meses_nomes)

    clientes_opts = sorted(kpi["Nome"].unique())
    clientes_sel = st.multiselect("Selecionar clientes", clientes_opts)

    artigos_opts = sorted(kpi["Artigo"].unique())
    artigos_sel = st.multiselect("Selecionar artigos", artigos_opts)

# Converter meses selecionados para números
meses_map = dict(zip(meses_nomes, range(1,13)))
meses_sel_num = [meses_map[m] for m in meses_sel]

# === 5. Aplicar filtros ===
kpi_view = kpi.copy()
if clientes_sel:
    kpi_view = kpi_view[kpi_view["Nome"].isin(clientes_sel)]
if artigos_sel:
    kpi_view = kpi_view[kpi_view["Artigo"].isin(artigos_sel)]
if meses_sel_num:
    kpi_view = kpi_view[kpi_view["Mes"].isin(meses_sel_num)]

# === 6. Pivot comparativo ===
pv = kpi_view.pivot_table(index=["Nome","Artigo","Mes"], columns="Ano", values="Quantidade", aggfunc="sum")
for a in [ano_base, ano_comp]:
    if a not in pv.columns:
        pv[a] = 0
pv["Variação_%"] = ((pv[ano_comp] - pv[ano_base]) / pv[ano_base].replace(0, pd.NA)) * 100
pv = pv.reset_index().sort_values(["Nome","Artigo","Mes"])
pv["Mês"] = pv["Mes"].apply(lambda m: meses_nomes[m-1] if 1<=m<=12 else str(m))
pv = pv[["Nome","Artigo","Mês",ano_base,ano_comp,"Variação_%"]]

# === 7. Mostrar tabela ===
st.subheader("Tabela comparativa YoY por Cliente, Artigo e Mês")
st.dataframe(
    pv.style
    .format({ano_base:"{:.0f}", ano_comp:"{:.0f}", "Variação_%":"{:.2f}"})
    .background_gradient(cmap="RdYlGn", subset=["Variação_%"])
)

# === 8. Gráfico por cliente/artigo ===
st.subheader("Evolução mensal por Cliente e Artigo")
clientes = sorted(pv["Nome"].unique())
artigos = sorted(pv["Artigo"].unique())
cliente_sel = st.selectbox("Selecionar cliente", clientes)
artigo_sel = st.selectbox("Selecionar artigo", artigos)

if cliente_sel and artigo_sel:
    base = kpi_view[(kpi_view["Nome"]==cliente_sel) & (kpi_view["Artigo"]==artigo_sel) & (kpi_view["Ano"]==ano_base)].sort_values("Mes")
    comp = kpi_view[(kpi_view["Nome"]==cliente_sel) & (kpi_view["Artigo"]==artigo_sel) & (kpi_view["Ano"]==ano_comp)].sort_values("Mes")

    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(base["Mes"], base["Quantidade"], marker="o", label=str(ano_base))
    ax.plot(comp["Mes"], comp["Quantidade"], marker="o", label=str(ano_comp))
    ax.set_xticks(range(1,13))
    ax.set_xticklabels(meses_nomes)
    ax.set_xlabel("Mês")
    ax.set_ylabel("Quantidade")
    ax.set_title(f"Evolução mensal – {cliente_sel} / {artigo_sel}")
    ax.legend()
    st.pyplot(fig)
