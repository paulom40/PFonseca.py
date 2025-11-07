import streamlit as st
import pandas as pd
import plotly.express as px
import json, re
from pathlib import Path

st.set_page_config("Vendas Globais", "Chart", "wide")
st.markdown("<h1 style='text-align:center;color:#1f77b4'>Dashboard Vendas</h1>", True)

# -------------------------------------------------
# DADOS
# -------------------------------------------------
@st.cache_data
def load():
    df = pd.read_excel(
        "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx",
        dtype=str, thousands=".", decimal=","
    )
    df.columns = df.columns.str.strip()
    df.rename(columns={
        "Código": "Codigo", "Qtd.": "Qtd", "V. Líquido": "V_Liquido",
        "Mês": "Mes"
    }, inplace=True)

    # NUMÉRICAS (apenas Qtd, V_Liquido, PM)
    for c in ["Qtd", "V_Liquido", "PM"]:
        if c in df:
            df[c] = (df[c].astype(str)
                     .str.replace(r'\.', '', regex=True)
                     .str.replace(',', '.', regex=False)
                     .replace('', '0'))
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

    # CATEGÓRICAS
    for c in ["Cliente","Artigo","Comercial","Categoria","Mes","Ano","UN"]:
        if c in df: df[c] = df[c].astype(str).str.strip()

    return df.dropna(subset=["V_Liquido","Qtd"], how="all")

df = load()

# -------------------------------------------------
# PRESETS
# -------------------------------------------------
p = Path("diagnosticos/presets_filtros.json"); p.parent.mkdir(exist_ok=True)
presets = json.loads(p.read_text()) if p.exists() else {}

def save(n, f): presets[n] = f; p.write_text(json.dumps(presets, indent=2, ensure_ascii=False))

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown("### Filtros")
    sel = st.selectbox("Preset", [""] + list(presets))
    f = presets.get(sel, {}) if sel else {}

    ms = lambda l, c, d=[]: st.multiselect(l, sorted(df[c].unique().astype(str)), [x for x in (d or []) if x in df[c].astype(str).values])
    clientes   = ms("Cliente",   "Cliente",   f.get("Cliente"))
    artigos    = ms("Artigo",    "Artigo",    f.get("Artigo"))
    comerciais = ms("Comercial", "Comercial", f.get("Comercial"))
    categorias = ms("Categoria", "Categoria", f.get("Categoria"))
    meses      = ms("Mês",       "Mes",       f.get("Mes"))
    anos       = ms("Ano",       "Ano",       f.get("Ano"))

    st.markdown("---")
    nome = st.text_input("Salvar preset")
    if st.button("Salvar") and nome:
        save(nome, {k:v for k,v in locals().items() if k in ["clientes","artigos","comerciais","categorias","meses","anos"]})
        st.success(f"**{nome}** salvo!")

    st.markdown(f"**Linhas:** {len(df):,} | **Artigos:** {df['Artigo'].nunique():,}")

# -------------------------------------------------
# FILTRO
# -------------------------------------------------
d = df.copy()
for col, vals in zip(
    ["Cliente","Artigo","Comercial","Categoria","Mes","Ano"],
    [clientes,artigos,comerciais,categorias,meses,anos]
):
    if vals: d = d[d[col].astype(str).isin(vals)]

# -------------------------------------------------
# UI
# -------------------------------------------------
if d.empty:
    st.warning("Nenhum dado com os filtros.")
else:
    st.success(f"**{len(d):,}** registros")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Vendas", f"€ {d['V_Liquido'].sum():,.0f}")
    c2.metric("Qtd", f"{d['Qtd'].sum():,.0f}")
    c3.metric("Clientes", d['Cliente'].nunique())
    c4.metric("Artigos", d['Artigo'].nunique())

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(d.groupby("Cliente")["V_Liquido"].sum().nlargest(10).reset_index(),
                     x="V_Liquido", y="Cliente", orientation='h', title="Top 10 Clientes")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(d.groupby("Artigo")["V_Liquido"].sum().nlargest(10).reset_index(),
                     x="V_Liquido", y="Artigo", orientation='h', title="Top 10 Artigos")
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(d.astype(str), use_container_width=True)

st.caption(f"Atualizado: {pd.Timestamp.now():%d/%m/%Y %H:%M}")
