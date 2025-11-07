import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import json
from datetime import datetime

# -------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------------------------
st.set_page_config(page_title="Dashboard Vendas", page_icon="Chart", layout="wide")
st.markdown(
    """
    <style>
    .main-header {font-size:2.5rem; color:#1f77b4; text-align:center; font-weight:700; margin-bottom:2rem}
    .metric-card {background:linear-gradient(135deg,#667eea,#764ba2); padding:1.2rem;
                  border-radius:12px; color:#fff; box-shadow:0 4px 6px rgba(0,0,0,.1)}
    .section-header {font-size:1.5rem; color:#2c3e50; margin:2rem 0 .5rem; border-bottom:3px solid #3498db}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# CARREGAMENTO DOS DADOS
# -------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    try:
        df = pd.read_excel(url, dtype=str, thousands=".", decimal=",")
        df.columns = [c.strip() for c in df.columns]                # remove espaços
        rename = {
            "Código": "Codigo", "Cliente": "Cliente", "Qtd.": "Qtd", "UN": "UN",
            "PM": "PM", "V. Líquido": "V_Liquido", "Artigo": "Artigo",
            "Comercial": "Comercial", "Categoria": "Categoria",
            "Mês": "Mes", "Ano": "Ano"
        }
        df = df.rename(columns=rename)

        # converte números (Qtd, V_Liquido, PM)
        for col in ("Qtd", "V_Liquido", "PM"):
            if col in df.columns:
                df[col] = (
                    df[col]
                    .str.replace(r"\.", "", regex=True)   # milhar
                    .str.replace(",", ".", regex=False)   # decimal
                    .astype(float)
                )

        # colunas categóricas → string limpa
        cat = ("Cliente", "Artigo", "Comercial", "Categoria", "Mes", "Ano", "UN")
        for c in cat:
            if c in df.columns:
                df[c] = df[c].astype(str).str.strip()

        df = df.dropna(subset=["V_Liquido", "Qtd"], how="all")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar: {e}")
        return pd.DataFrame()


df = load_data()

# -------------------------------------------------
# PRESETS
# -------------------------------------------------
preset_path = Path("diagnosticos/presets_filtros.json")
preset_path.parent.mkdir(exist_ok=True)

def load_presets(): return json.loads(preset_path.read_text(encoding="utf-8")) if preset_path.exists() else {}
def save_preset(name, filt): 
    p = load_presets(); p[name] = filt
    preset_path.write_text(json.dumps(p, indent=2, ensure_ascii=False), encoding="utf-8")

# -------------------------------------------------
# SIDEBAR – CONTROLES
# -------------------------------------------------
with st.sidebar:
    st.markdown("<div class='metric-card'><h4>Controle</h4></div>", unsafe_allow_html=True)
    presets = load_presets()
    sel = st.selectbox("Preset", [""] + list(presets.keys()))
    filt = presets.get(sel, {}) if sel else {}

    def ms(label, col, default=None):
        opts = sorted(df[col].dropna().astype(str).unique()) if col in df.columns and not df.empty else []
        return st.multiselect(label, opts, default=[v for v in (default or []) if v in opts])

    clientes   = ms("Clientes",   "Cliente",   filt.get("Cliente"))
    artigos    = ms("Artigos",    "Artigo",    filt.get("Artigo"))
    comerciais = ms("Comerciais", "Comercial", filt.get("Comercial"))
    categorias = ms("Categorias", "Categoria", filt.get("Categoria"))
    meses      = ms("Meses",      "Mes",       filt.get("Mes"))
    anos       = ms("Anos",       "Ano",       filt.get("Ano"))

    st.markdown("---")
    nome = st.text_input("Nome do preset")
    if st.button("Salvar") and nome:
        save_preset(nome, {"Cliente":clientes,"Artigo":artigos,"Comercial":comerciais,
                           "Categoria":categorias,"Mes":meses,"Ano":anos})
        st.success(f"Preset **{nome}** salvo!")

    st.markdown("---")
    st.markdown("### Estatísticas")
    if not df.empty:
        st.write(f"**Linhas:** {len(df):,}")
        st.write(f"**Artigos únicos:** {df['Artigo'].nunique():,}")
        st.write(f"**Clientes únicos:** {df['Cliente'].nunique():,}")

# -------------------------------------------------
# APLICAÇÃO DOS FILTROS
# -------------------------------------------------
df_f = df.copy()
if clientes:   df_f = df_f[df_f["Cliente"].astype(str).isin(clientes)]
if artigos:    df_f = df_f[df_f["Artigo"].astype(str).isin(artigos)]
if comerciais: df_f = df_f[df_f["Comercial"].astype(str).isin(comerciais)]
if categorias: df_f = df_f[df_f["Categoria"].astype(str).isin(categorias)]
if meses:      df_f = df_f[df_f["Mes"].astype(str).isin(meses)]
if anos:       df_f = df_f[df_f["Ano"].astype(str).isin(anos)]

# -------------------------------------------------
# UI PRINCIPAL
# -------------------------------------------------
st.markdown("<h1 class='main-header'>Dashboard de Vendas</h1>", unsafe_allow_html=True)

if df_f.empty:
    st.warning("Nenhum registro com os filtros aplicados.")
else:
    st.success(f"**{len(df_f):,}** registros encontrados")

    # Métricas
    st.markdown("<div class='section-header'>Métricas Principais</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    c1.metric("Total Vendas", f"€ {df_f['V_Liquido'].sum():,.2f}")
    c1.markdown("</div>", unsafe_allow_html=True)

    c2.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    c2.metric("Quantidade", f"{df_f['Qtd'].sum():,.0f}")
    c2.markdown("</div>", unsafe_allow_html=True)

    c3.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    c3.metric("Clientes", f"{df_f['Cliente'].nunique():,}")
    c3.markdown("</div>", unsafe_allow_html=True)

    c4.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    c4.metric("Artigos", f"{df_f['Artigo'].nunique():,}")
    c4.markdown("</div>", unsafe_allow_html=True)

    # Gráficos
    st.markdown("<div class='section-header'>Visualizações</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        top_c = df_f.groupby("Cliente")["V_Liquido"].sum().nlargest(10)
        if not top_c.empty:
            fig = px.bar(top_c, x=top_c.values, y=top_c.index, orientation="h",
                         title="Top 10 Clientes", labels={"x":"Vendas (€)","y":""})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        top_a = df_f.groupby("Artigo")["V_Liquido"].sum().nlargest(10)
        if not top_a.empty:
            fig = px.bar(top_a, x=top_a.values, y=top_a.index, orientation="h",
                         title="Top 10 Artigos", labels={"x":"Vendas (€)","y":""})
            st.plotly_chart(fig, use_container_width=True)

    # Tabela
    st.markdown("<div class='section-header'>Dados Filtrados</div>", unsafe_allow_html=True)
    st.dataframe(df_f.astype(str), use_container_width=True)

st.markdown("---")
st.caption(f"Atualizado em {datetime.now():%d/%m/%Y %H:%M}")
