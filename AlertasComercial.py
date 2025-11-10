# pages/AlertasComercial.py
import streamlit as st
import pandas as pd
import plotly.express as px
import re
from datetime import datetime

st.set_page_config(page_title="Alertas de Compras", page_icon="Alert", layout="wide")

# ---------- CSS ----------
st.markdown(
    """
<style>
    .main-header {font-size:2.5rem; color:#1f77b4; text-align:center; margin:2rem 0; font-weight:700;}
    .section-header {font-size:1.6rem; color:#2c3e50; margin:2rem 0 1rem; padding-bottom:0.5rem;
                     border-bottom:3px solid #3498db; font-weight:600;}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown("<h1 class='main-header'>Alertas de Compras</h1>", unsafe_allow_html=True)

# ---------- Voltar ----------
if st.button("Voltar ao Dashboard Principal"):
    st.switch_page("Dashboard_Principal.py")

# ---------- Dados ----------
if "df_filtrado" not in st.session_state:
    st.error("Volte ao Dashboard Principal para carregar os dados.")
    st.stop()

df = st.session_state.df_filtrado

# ---------- Padronizar Mês/Ano ----------
meses = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "10": 10, "11": 11, "12": 12,
}

def norm_mes(x):
    x = re.sub(r"\D", "", str(x).lower())
    return f"{meses.get(x, 0):02d}" if meses.get(x) else None

def norm_ano(x):
    x = re.sub(r"\D", "", str(x))
    if len(x) == 4: return x
    if len(x) == 2: return f"20{x}" if int(x) < 50 else f"19{x}"
    return None

df["Mes"] = df["Mes"].apply(norm_mes)
df["Ano"] = df["Ano"].apply(norm_ano)
df = df.dropna(subset=["Mes", "Ano"]).copy()
df["Periodo"] = df["Ano"] + "-" + df["Mes"]

mes_nome = {f"{i:02d}": m for i, m in enumerate("Jan Fev Mar Abr Mai Jun Jul Ago Set Out Nov Dez".split(), 1)}
df["Mes_Nome"] = df["Mes"].map(mes_nome)

# ---------- Análise ----------
if df["Periodo"].nunique() < 2:
    st.warning("São necessários pelo menos 2 períodos.")
    st.stop()

agg = df.groupby(["Cliente", "Periodo"])["Qtd"].sum().reset_index()
periodos = sorted(agg["Periodo"].unique())
atual, anterior = periodos[-1], periodos[-2]

pivot = agg.pivot(index="Cliente", columns="Periodo", values="Qtd").fillna(0)
pivot["Atual"] = pivot[atual]
pivot["Anterior"] = pivot[anterior]
pivot["Var_%"] = ((pivot["Atual"] - pivot["Anterior"]) / pivot["Anterior"].replace(0, 1)) * 100

subidas  = pivot[pivot["Var_%"] > 20].copy()
descidas = pivot[pivot["Var_%"] < -20].copy()
inativos = pivot[(pivot["Anterior"] > 0) & (pivot["Atual"] == 0)].copy()

subidas  = subidas.sort_values("Var_%", ascending=False)[["Anterior", "Atual", "Var_%"]]
descidas = descidas.sort_values("Var_%")[["Anterior", "Atual", "Var_%"]]
inativos = inativos.sort_values("Anterior", ascending=False)[["Anterior", "Atual"]]

subidas  = subidas.reset_index()
descidas = descidas.reset_index()
inativos = inativos.reset_index()
inativos["Var_%"] = -100   # <-- correção aqui

# ---------- UI ----------
st.markdown("<div class='section-header'>Análise de Tendências</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Subidas", len(subidas))
c2.metric("Descidas", len(descidas))
c3.metric("Inativos", len(inativos))

t1, t2, t3 = st.tabs(
    [f"Subidas ({len(subidas)})", f"Descidas ({len(descidas)})", f"Inativos ({len(inativos)})"]
)

with t1:
    if not subidas.empty:
        st.dataframe(subidas, use_container_width=True)
        fig = px.bar(subidas.head(10), x="Var_%", y="Cliente", orientation="h",
                     title="Top 10 Subidas", color="Var_%")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("Nenhum cliente com subida > 20%")

with t2:
    if not descidas.empty:
        st.dataframe(descidas, use_container_width=True)
        fig = px.bar(descidas.head(10), x="Var_%", y="Cliente", orientation="h",
                     title="Top 10 Descidas", color="Var_%")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("Nenhum cliente com descida > 20%")

with t3:
    if not inativos.empty:
        st.dataframe(inativos, use_container_width=True)
        fig = px.bar(inativos.head(10), x="Anterior", y="Cliente", orientation="h",
                     title="Top 10 Volumes Perdidos", color="Anterior")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("Nenhum cliente parou de comprar")

# ---------- Footer ----------
st.markdown("---")
st.caption(f"Atualizado em: {datetime.now():%d/%m/%Y %H:%M}")
