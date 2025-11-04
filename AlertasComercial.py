# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from unidecode import unidecode
import io

st.set_page_config(page_title="Dashboard Vendas", layout="wide")
st.title("Dashboard de Vendas – VGlob2425 (GitHub)")

# -------------------------------------------------
# 1. CARREGAR DADOS DO GITHUB
# -------------------------------------------------
@st.cache_data(ttl=3600)  # Atualiza a cada 1h
def load_data_from_github():
    url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/VGlob2425.xlsx"
    try:
        # Baixar e ler o Excel diretamente
        response = pd.read_excel(url, sheet_name="Sheet1")
        st.success("Dados carregados do GitHub com sucesso!")
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo do GitHub: {e}")
        st.stop()

    # Cabeçalhos
    response.columns = ["Código", "Cliente", "Qtd.", "UN", "PM", "V. Líquido",
                        "Artigo", "Comercial", "Categoria", "Mês", "Ano"]

    df = response.dropna(subset=["Cliente", "Comercial", "Artigo", "Mês", "Ano"])

    # Normalização do mês
    df["Mês"] = (
        df["Mês"]
        .astype(str)
        .str.strip()
        .str.lower()
        .apply(unidecode)
        .str.replace(r"[^a-z]", "", regex=True)
    )

    meses_map = {
        "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4,
        "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
        "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
    }
    df["Mês_Num"] = df["Mês"].map(meses_map)

    if df["Mês_Num"].isna().any():
        invalid = df[df["Mês_Num"].isna()]["Mês"].unique()
        st.error(f"Meses inválidos: {', '.join(sorted(invalid))}")
        st.stop()

    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype(int)
    df = df[df["Ano"].between(2000, 2100)]
    df["Data"] = pd.to_datetime(df[["Ano", "Mês_Num"]].assign(day=1))
    df["V. Líquido"] = pd.to_numeric(df["V. Líquido"], errors="coerce").fillna(0)
    df["Qtd."] = pd.to_numeric(df["Qtd."], errors="coerce").fillna(0)

    return df

df = load_data_from_github()

# -------------------------------------------------
# 2. FILTROS
# -------------------------------------------------
st.sidebar.header("Filtros")

anos = sorted(df["Ano"].unique())
ano_sel = st.sidebar.multiselect("Ano", anos, default=anos[-2:] if len(anos) >= 2 else anos)
df = df[df["Ano"].isin(ano_sel)]

meses_cap = sorted(df["Mês"].str.capitalize().unique())
mes_sel = st.sidebar.multiselect("Mês", meses_cap, default=[])
if mes_sel:
    df = df[df["Mês"].str.capitalize().isin(mes_sel)]

comerciais = st.sidebar.multiselect("Comercial", sorted(df["Comercial"].unique()), default=[])
if comerciais:
    df = df[df["Comercial"].isin(comerciais)]

clientes = st.sidebar.multiselect("Cliente", sorted(df["Cliente"].unique()), default=[])
if clientes:
    df = df[df["Cliente"].isin(clientes)]

# -------------------------------------------------
# 3. COMPARATIVO ANUAL
# -------------------------------------------------
ano_atual = df["Ano"].max()
df_atual = df[df["Ano"] == ano_atual]
df_ant = df[df["Ano"] == ano_atual - 1] if (ano_atual - 1) in df["Ano"].values else pd.DataFrame()

v_atual = df_atual["V. Líquido"].sum()
v_ant = df_ant["V. Líquido"].sum()
c_atual = df_atual["Cliente"].nunique()
c_ant = df_ant["Cliente"].nunique()

# -------------------------------------------------
# 4. KPIs
# -------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Vendas Totais", f"€{v_atual:,.0f}", f"{(v_atual-v_ant)/v_ant*100:+.1f}%" if v_ant else None)
col2.metric("Clientes Únicos", c_atual, f"{(c_atual-c_ant)/c_ant*100:+.1f}%" if c_ant else None)
col3.metric("Artigos Vendidos", df_atual["Artigo"].nunique())
col4.metric("Média/Cliente", f"€{v_atual/c_atual:,.0f}" if c_atual else "€0")

# -------------------------------------------------
# 5. GRÁFICO
# -------------------------------------------------
st.subheader(f"Evolução: {ano_atual} vs {ano_atual-1}")

meses = "Janeiro Fevereiro Março Abril Maio Junho Julho Agosto Setembro Outubro Novembro Dezembro".split()
fig = go.Figure()

for data, nome, cor, dash in [
    (df_atual, str(ano_atual), "blue", "solid"),
    (df_ant, str(ano_atual-1), "orange", "dot")
]:
    if not data.empty:
        mensal = data.groupby("Mês_Num")["V. Líquido"].sum().reindex(range(1,13), fill_value=0)
        fig.add_trace(go.Scatter(x=meses, y=mensal, name=nome, line=dict(color=cor, dash=dash)))

fig.update_layout(hovermode="x unified", xaxis_title="Mês", yaxis_title="Vendas (€)")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# 6. ALERTA QUEDA >30%
# -------------------------------------------------
if not df_ant.empty:
    comp = df_atual.groupby("Cliente")["V. Líquido"].sum().to_frame("Atual")
    comp["Anterior"] = df_ant.groupby("Cliente")["V. Líquido"].sum()
    comp = comp[comp["Anterior"] > 0].fillna(0)
    comp["Var (%)"] = (comp["Atual"] / comp["Anterior"] - 1) * 100
    queda = comp[comp["Var (%)"] <= -30]

    if not queda.empty:
        st.error(f"{len(queda)} cliente(s) com queda >30%")
        st.dataframe(queda.style.format({
            "Atual": "€{:.0f}", "Anterior": "€{:.0f}", "Var (%)": "{:+.1f}%"
        }).background_gradient(cmap="Reds"))
    else:
        st.success("Nenhum cliente com queda >30%")

# -------------------------------------------------
# 7. DOWNLOAD
# -------------------------------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Baixar CSV", csv, f"vendas_{ano_atual}.csv", "text/csv")
