import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Dashboard Compras - KPIs", layout="wide")
st.title("Dashboard de Compras – KPIs + Comparativo YoY")

# === CARREGAR DADOS ===
@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"
    df_raw = pd.read_excel(url)

    df = pd.DataFrame({
        "Data":       pd.to_datetime(df_raw.iloc[:, 0], errors="coerce"),
        "Cliente":    df_raw.iloc[:, 1].astype(str).str.strip(),
        "Artigo":     df_raw.iloc[:, 2].astype(str).str.strip(),
        "Quantidade": pd.to_numeric(df_raw.iloc[:, 3], errors="coerce="coerce").fillna(0),
        "Comercial":  df_raw.iloc[:, 8].astype(str).str.strip(),
    })

    df = df.dropna(subset=["Data"])
    df = df[(df["Cliente"] != "nan") & (df["Comercial"] != "nan") & (df["Artigo"] != "nan")]
    df["Ano"] = df["Data"].dt.year
    df["Mes"] = df["Data"].dt.month
    df["MesNome"] = df["Data"].dt.strftime("%b")

    return df

df = load_data()

# === SIDEBAR - 4 FILTROS ===
st.sidebar.header("Filtros")

ano_atual = st.sidebar.selectbox("Ano a Analisar", options=sorted(df["Ano"].unique(), reverse=True))
ano_anterior = ano_atual - 1

if ano_anterior not in df["Ano"].unique():
    st.error("Ano anterior não disponível.")
    st.stop()

# Filtros
todos_com = st.sidebar.checkbox("Todos Comerciais", value=True)
comerciais_sel = df["Comercial"].unique().tolist() if todos_com else st.sidebar.multiselect("Comerciais", sorted(df["Comercial"].unique()))

todos_cli = st.sidebar.checkbox("Todos Clientes", value=True)
clientes_sel = df["Cliente"].unique().tolist() if todos_cli else st.sidebar.multiselect("Clientes", sorted(df["Cliente"].unique()))

todos_art = st.sidebar.checkbox("Todos Artigos", value=True)
artigos_sel = df["Artigo"].unique().tolist() if todos_art else st.sidebar.multiselect("Artigos", sorted(df["Artigo"].unique()))

# === DADOS FILTRADOS ===
df_atual = df[(df["Ano"] == ano_atual) & (df["Comercial"].isin(comerciais_sel)) & (df["Cliente"].isin(clientes_sel)) & (df["Artigo"].isin(artigos_sel))]
df_anterior = df[(df["Ano"] == ano_anterior) & (df["Comercial"].isin(comerciais_sel)) & (df["Cliente"].isin(clientes_sel)) & (df["Artigo"].isin(artigos_sel))]

# === CÁLCULO DOS 8 KPIs PRINCIPAIS ===
total_atual = df_atual["Quantidade"].sum()
total_anterior = df_anterior["Quantidade"].sum()
var_total = total_atual - total_anterior
var_pct = (var_total / total_anterior * 100) if total_anterior > 0 else 0

clientes_atual = df_atual["Cliente"].nunique()
clientes_anterior = df_anterior["Cliente"].nunique()
var_clientes = clientes_atual - clientes_anterior

artigos_atual = df_atual["Artigo"].nunique()
artigos_anterior = df_anterior["Artigo"].nunique()

comerciais_atual = df_atual["Comercial"].nunique()

ticket_medio_atual = total_atual / len(df_atual) if len(df_atual) > 0 else 0
ticket_medio_anterior = total_anterior / len(df_anterior) if len(df_anterior) > 0 else 0
var_ticket = ticket_medio_atual - ticket_medio_anterior

top_cliente_atual = df_atual.groupby("Cliente")["Quantidade"].sum().idxmax() if not df_atual.empty else "-"
qtd_top_cliente = df_atual.groupby("Cliente")["Quantidade"].sum().max() if not df_atual.empty else 0

# === 8 KPIs NO TOPO - BONITOS E CLAROS ===
st.markdown(f"### Resumo Executivo – {ano_atual} vs {ano_anterior}")

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6, kpi7, kpi8 = st.columns(8)

with kpi1:
    st.metric("Total Quantidade", f"{total_atual:,.0f}", f"{var_total:+,.0f}", delta_color="normal")

with kpi2:
    st.metric("Variação %", f"{var_pct:+.1f}%", delta=f"{var_pct:+.1f}%", delta_color="normal")

with kpi3:
    st.metric("Nº Clientes", clientes_atual, f"{var_clientes:+d}")

with kpi4:
    st.metric("Nº Artigos", art_atual, f"{artigos_anterior:+d}" if artigos_anterior > 0 else None)

with kpi5:
    st.metric("Comerciais Ativos", comerciais_atual)

with kpi6:
    st.metric("Ticket Médio", f"{ticket_medio_atual:,.0f}", f"{var_ticket:+.0f}")

with kpi7:
    st.metric("Top Cliente", top_cliente_atual, help="Cliente com mais quantidade")

with kpi8:
    st.metric("Qtd Top Cliente", f"{qtd_top_cliente:,.0f}")

st.divider()

# === GRÁFICO EVOLUÇÃO MENSAL ===
st.subheader(f"Evolução Mensal – {ano_anterior} vs {ano_atual}")

meses = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
evol_atual = df_atual.groupby("MesNome")["Quantidade"].sum().reindex(meses, fill_value=0)
evol_anterior = df_anterior.groupby("MesNome")["Quantidade"].sum().reindex(meses, fill_value=0)

fig, ax = plt.subplots(figsize=(14,6))
ax.plot(meses, evol_atual.values, marker='o', linewidth=4, label=ano_atual, color="#1f77b4")
ax.plot(meses, evol_anterior.values, marker='o', linewidth=4, label=ano_anterior, color="#ff7f0e", alpha=0.8)
ax.set_title("Evolução Mensal Comparativa", fontsize=16, fontweight="bold")
ax.set_ylabel("Quantidade")
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)

st.divider()

# === TOP 10 CLIENTES COM VARIAÇÃO ===
st.subheader("Top 10 Clientes – Comparativo YoY")
top10 = df_atual.groupby("Cliente")["Quantidade"].sum().nlargest(10).index
comp = pd.DataFrame({
    ano_anterior: df_anterior.groupby("Cliente")["Quantidade"].sum(),
    ano_atual: df_atual.groupby("Cliente")["Quantidade"].sum()
}).fillna(0).loc[top10]

comp["Variação"] = comp[ano_atual] - comp[ano_anterior]
comp["Var %"] = (comp["Variação"] / comp[ano_anterior].replace(0,1) * 100).round(1)

col1, col2 = st.columns([3,2])
with col1:
    fig, ax = plt.subplots(figsize=(10,6))
    comp[[ano_anterior, ano_atual]].plot(kind='barh', ax=ax, color=['#ff7f0e', '#1f77b4'])
    ax.set_title("Top 10 Clientes")
    ax.invert_yaxis()
    st.pyplot(fig)

with col2:
    disp = comp.copy()
    disp[ano_anterior] = disp[ano_anterior].apply(lambda x: f"{x:,.0f}")
    disp[ano_atual] = disp[ano_atual].apply(lambda x: f"{x:,.0f}")
    disp["Variação"] = disp["Variação"].apply(lambda x: f"{x:+,.0f}")
    disp["Var %"] = disp["Var %"].apply(lambda x: f"{x:+.1f}%")
    st.dataframe(disp, use_container_width=True)

st.divider()

# === EXPORTAR ===
st.subheader("Exportar Relatório")
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    comp.to_excel(writer, sheet_name='Top Clientes YoY')
    df_atual.groupby(["Comercial","Cliente","Artigo"])["Quantidade"].sum().reset_index().to_excel(writer, sheet_name='Detalhe Atual', index=False)

st.download_button("Download Excel Completo", 
                   data=output.getvalue(),
                   file_name=f"KPIs_{ano_atual}_vs_{ano_anterior}.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.success("Dashboard com KPIs completos e todos os filtros a funcionar perfeitamente!")
