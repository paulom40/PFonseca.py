import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="KPI Compras Clientes (YoY)", layout="wide")
st.title("📊 KPI de Compras por Cliente (YoY)")

# --- URL raw do ficheiro no GitHub ---
RAW_URL = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"

# === 1. Ler ficheiro diretamente ===
df = pd.read_excel(RAW_URL)

# === 2. Normalizar colunas ===
df = df.rename(columns={"Nome":"Nome","Quantidade":"Quantidade","Data":"Data"})
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df = df.dropna(subset=["Data"])
df["Ano"] = df["Data"].dt.year
df["Mes"] = df["Data"].dt.month
df["Nome"] = df["Nome"].astype(str).str.strip()
df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)

# === 3. Agrupar KPI ===
kpi = df.groupby(["Nome","Ano","Mes"], as_index=False)["Quantidade"].sum()

# === 4. Seleção de anos ===
anos_disponiveis = sorted(kpi["Ano"].unique())
ano_base = st.selectbox("Ano base", anos_disponiveis, index=max(0,len(anos_disponiveis)-2))
ano_comp = st.selectbox("Ano comparação", anos_disponiveis, index=len(anos_disponiveis)-1)

# === 5. Pivot comparativo ===
pv = kpi.pivot_table(index=["Nome","Mes"], columns="Ano", values="Quantidade", aggfunc="sum")
for a in [ano_base, ano_comp]:
    if a not in pv.columns:
        pv[a] = 0
pv["Variação_%"] = ((pv[ano_comp] - pv[ano_base]) / pv[ano_base].replace(0, pd.NA)) * 100
pv = pv.reset_index().sort_values(["Nome","Mes"])

# === 6. Nome dos meses ===
meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
pv["Mês"] = pv["Mes"].apply(lambda m: meses[m-1] if 1<=m<=12 else str(m))
pv = pv[["Nome","Mês",ano_base,ano_comp,"Variação_%"]]

# === 7. Mostrar tabela ===
st.subheader("Tabela comparativa YoY por Cliente e Mês")
st.dataframe(
    pv.style
    .format({ano_base:"{:.0f}", ano_comp:"{:.0f}", "Variação_%":"{:.2f}"})
    .background_gradient(cmap="RdYlGn", subset=["Variação_%"])
)

# === 8. Gráfico por cliente ===
st.subheader("Evolução mensal por cliente")
clientes = sorted(pv["Nome"].unique())
cliente_sel = st.selectbox("Selecionar cliente", clientes)
if cliente_sel:
    base = kpi[(kpi["Nome"]==cliente_sel) & (kpi["Ano"]==ano_base)].sort_values("Mes")
    comp = kpi[(kpi["Nome"]==cliente_sel) & (kpi["Ano"]==ano_comp)].sort_values("Mes")

    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(base["Mes"], base["Quantidade"], marker="o", label=str(ano_base))
    ax.plot(comp["Mes"], comp["Quantidade"], marker="o", label=str(ano_comp))
    ax.set_xticks(range(1,13))
    ax.set_xticklabels(meses)
    ax.set_xlabel("Mês")
    ax.set_ylabel("Quantidade")
    ax.set_title(f"Evolução mensal – {cliente_sel}")
    ax.legend()
    st.pyplot(fig)
