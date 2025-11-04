# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from unidecode import unidecode

st.set_page_config(page_title="Vendas", layout="wide")
st.title("Dashboard Vendas – VGlob2425 (GitHub)")

# -------------------------------------------------
# 1. LOAD FROM GITHUB
# -------------------------------------------------
@st.cache_data(ttl=3600)
def load():
    url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/VGlob2425.xlsx"
    df = pd.read_excel(url, sheet_name="Sheet1")
    df.columns = ["Código","Cliente","Qtd.","UN","PM","V. Líquido",
                  "Artigo","Comercial","Categoria","Mês","Ano"]
    df = df.dropna(subset=["Cliente","Comercial","Artigo","Mês","Ano"])

    # mês → número (case/acento-insensitive)
    df["Mês"] = df["Mês"].astype(str).str.strip().str.lower().apply(unidecode)\
                .str.replace(r"[^a-z]","",regex=True)
    meses = {m:i for i,m in enumerate(
        "janeiro fevereiro marco abril maio junho julho agosto setembro outubro novembro dezembro".split(),1)}
    df["Mês_Num"] = df["Mês"].map(meses)
    if df["Mês_Num"].isna().any():
        st.error(f"Meses inválidos: {sorted(df[df['Mês_Num'].isna()]['Mês'].unique())}"); st.stop()

    df["Ano"] = pd.to_numeric(df["Ano"],errors="coerce").astype(int)
    df = df[df["Ano"].between(2000,2100)]

    # year, month, day  (ordem correta)
    df["Data"] = pd.to_datetime(df[["Ano","Mês_Num"]].assign(day=1)[["Ano","Mês_Num","day"]])
    df["V. Líquido"] = pd.to_numeric(df["V. Líquido"],errors="coerce").fillna(0)
    return df

df = load()

# -------------------------------------------------
# 2. FILTROS
# -------------------------------------------------
st.sidebar.header("Filtros")
ano = st.sidebar.multiselect("Ano", sorted(df["Ano"].unique()), default=sorted(df["Ano"].unique())[-2:])
df = df[df["Ano"].isin(ano)]

mes = st.sidebar.multiselect("Mês", sorted(df["Mês"].str.capitalize().unique()), default=[])
if mes: df = df[df["Mês"].str.capitalize().isin(mes)]

com = st.sidebar.multiselect("Comercial", sorted(df["Comercial"].unique()), default=[])
if com: df = df[df["Comercial"].isin(com)]

cli = st.sidebar.multiselect("Cliente", sorted(df["Cliente"].unique()), default=[])
if cli: df = df[df["Cliente"].isin(cli)]

# -------------------------------------------------
# 3. ANO ATUAL / ANTERIOR
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
c4.metric("Média/Cliente", f"€{v_cur/c_cur:,.0f}" if c_cur else "€0")

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
fig.update_layout(hovermode="x unified",xaxis_title="Mês",yaxis_title="Vendas (€)")
st.plotly_chart(fig,use_container_width=True)

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
st.download_button("Baixar CSV", df.to_csv(index=False).encode(),"vendas.csv","text/csv")
