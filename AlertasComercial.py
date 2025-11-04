# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from unidecode import unidecode

st.set_page_config(page_title="Vendas", layout="wide")
st.title("Dashboard Vendas – VGlob2425")

# -------------------------------------------------
# 1. LOAD FROM GITHUB
# -------------------------------------------------
@st.cache_data(ttl=3600)
def load():
    url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/VGlob2425.xlsx"
    try:
        df = pd.read_excel(url, sheet_name="Sheet1")
    except Exception as e:
        st.error(f"Erro ao carregar Excel: {e}")
        st.stop()

    # Verificar número de colunas
    if df.shape[1] < 11:
        st.error(f"Arquivo tem apenas {df.shape[1]} colunas. Esperado: 11.")
        st.stop()

    # Renomear apenas as primeiras 11 colunas
    cols = ["Código","Cliente","Qtd.","UN","PM","V. Líquido",
            "Artigo","Comercial","Categoria","Mês","Ano"]
    df = df.iloc[:, :11].copy()
    df.columns = cols

    df = df.dropna(subset=["Cliente","Comercial","Artigo","Mês","Ano"])

    # Normalizar mês
    df["Mês"] = df["Mês"].astype(str).str.strip().str.lower().apply(unidecode)\
                .str.replace(r"[^a-z]","",regex=True)
    meses = {m:i for i,m in enumerate("janeiro fevereiro marco abril maio junho julho agosto setembro outubro novembro dezembro".split(),1)}
    df["Mês_Num"] = df["Mês"].map(meses)

    if df["Mês_Num"].isna().any():
        bad = df[df["Mês_Num"].isna()]["Mês"].unique()
        st.error(f"Meses inválidos: {', '.join(sorted(bad))}")
        st.stop()

    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")
    if df["Ano"].isna().any():
        st.error("Ano inválido encontrado.")
        st.stop()
    df["Ano"] = df["Ano"].astype(int)
    df = df[df["Ano"].between(2000, 2100)]

    # Data correta: year, month, day
    df["Data"] = pd.to_datetime(df[["Ano", "Mês_Num"]].assign(day=1)[["Ano", "Mês_Num", "day"]])

    df["V. Líquido"] = pd.to_numeric(df["V. Líquido"], errors="coerce").fillna(0)
    return df

df = load()

# -------------------------------------------------
# 2. FILTROS
# -------------------------------------------------
st.sidebar.header("Filtros")
anos = sorted(df["Ano"].unique())
ano_sel = st.sidebar.multiselect("Ano", anos, default=anos[-2:] if len(anos)>=2 else anos)
df = df[df["Ano"].isin(ano_sel)]

mes_sel = st.sidebar.multiselect("Mês", sorted(df["Mês"].str.capitalize().unique()), default=[])
if mes_sel: df = df[df["Mês"].str.capitalize().isin(mes_sel)]

com_sel = st.sidebar.multiselect("Comercial", sorted(df["Comercial"].unique()), default=[])
if com_sel: df = df[df["Comercial"].isin(com_sel)]

cli_sel = st.sidebar.multiselect("Cliente", sorted(df["Cliente"].unique()), default=[])
if cli_sel: df = df[df["Cliente"].isin(cli_sel)]

# -------------------------------------------------
# 3. COMPARATIVO
# -------------------------------------------------
cur = df["Ano"].max()
df_cur = df[df["Ano"]==cur]
df_prev = df[df["Ano"]==cur-1] if cur-1 in df["Ano"].values else pd.DataFrame()

v_cur, v_prev = df_cur["V. Líquido"].sum(), df_prev["V. Líquido"].sum()
c_cur, c_prev = df_cur["Cliente"].nunique(), df_prev["Cliente"].nunique()

# -------------------------------------------------
# 4. KPIs
# -------------------------------------------------
c1,c2,c3,c4 = st.columns(4)
c1.metric("Vendas", f"€{v_cur:,.0f}", f"{(v_cur-v_prev)/v_prev*100:+.1f}%" if v_prev else None)
c2.metric("Clientes", c_cur, f"{(c_cur-c_prev)/c_prev*100:+.1f}%" if c_prev else None)
c3.metric("Artigos", df_cur["Artigo"].nunique())
c4.metric("Média", f"€{v_cur/c_cur:,.0f}" if c_cur else "€0")

# -------------------------------------------------
# 5. GRÁFICO
# -------------------------------------------------
st.subheader(f"{cur} vs {cur-1}")
meses = "Janeiro Fevereiro Março Abril Maio Junho Julho Agosto Setembro Outubro Novembro Dezembro".split()
fig = go.Figure()
for d,n,clr,dash in [(df_cur,str(cur),"blue","solid"), (df_prev,str(cur-1),"orange","dot")]:
    if not d.empty:
        m = d.groupby("Mês_Num")["V. Líquido"].sum().reindex(range(1,13),fill_value=0)
        fig.add_trace(go.Scatter(x=meses,y=m,name=n,line=dict(color=clr,dash=dash)))
fig.update_layout(hovermode="x unified", xaxis_title="Mês", yaxis_title="Vendas (€)")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# 6. QUEDA >30%
# -------------------------------------------------
if not df_prev.empty:
    comp = df_cur.groupby("Cliente")["V. Líquido"].sum().to_frame("Atual")
    comp["Anterior"] = df_prev.groupby("Cliente")["V. Líquido"].sum()
    comp = comp[comp["Anterior"]>0].fillna(0)
    comp["Var%"] = (comp["Atual"]/comp["Anterior"]-1)*100
    q = comp[comp["Var%"]<=-30]
    if not q.empty:
        st.error(f"{len(q)} cliente(s) com queda >30%")
        st.dataframe(q.style.format({"Atual":"€{:.0f}","Anterior":"€{:.0f}","Var%":"{:+.1f}%"})
                     .background_gradient(cmap="Reds"))
    else:
        st.success("Nenhum cliente com queda >30%")

# -------------------------------------------------
# 7. DOWNLOAD
# -------------------------------------------------
st.download_button("Baixar CSV", df.to_csv(index=False).encode(), "vendas.csv", "text/csv")
