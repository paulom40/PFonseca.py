import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Dashboard Compras - KPIs + YoY", layout="wide")
st.title("Dashboard de Compras – KPIs + Comparativo com Ano Anterior")

# === CARREGAR DADOS ===
@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"
    df_raw = pd.read_excel(url)

    df = pd.DataFrame({
        "Data":       pd.to_datetime(df_raw.iloc[:, 0], errors="coerce"),
        "Cliente":    df_raw.iloc[:, 1].astype(str).str.strip(),
        "Artigo":     df_raw.iloc[:, 2].astype(str).str.strip(),
        "Quantidade": pd.to_numeric(df_raw.iloc[:, 3], errors="coerce").fillna(0),
        "Comercial":  df_raw.iloc[:, 8].astype(str).astype(str).str.strip(),
    })

    df = df.dropna(subset=["Data"])
    df = df[(df["Cliente"] != "nan") & (df["Comercial"] != "nan") & (df["Artigo"] != "nan")]
    df["Ano"] = df["Data"].dt.year
    df["Mes"] = df["Data"].dt.month
    df["MesNome"] = df["Data"].dt.strftime("%b")   # Jan, Feb, Mar…

    return df

df = load_data()

# === SIDEBAR – 4 FILTROS ===
st.sidebar.header("Filtros")

# Obter anos disponíveis em ordem decrescente
anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)
ano_atual = st.sidebar.selectbox("Ano a Analisar", options=anos_disponiveis)

# Verificar se existe ano anterior nos dados
ano_anterior = ano_atual - 1
tem_ano_anterior = ano_anterior in anos_disponiveis

# Comerciais
todos_com = st.sidebar.checkbox("Todos os Comerciais", value=True)
comerciais_sel = df["Comercial"].unique().tolist() if todos_com else st.sidebar.multiselect(
    "Selecionar Comerciais", sorted(df["Comercial"].unique()))

# Clientes
todos_cli = st.sidebar.checkbox("Todos os Clientes", value=True)
clientes_sel = df["Cliente"].unique().tolist() if todos_cli else st.sidebar.multiselect(
    "Selecionar Clientes", sorted(df["Cliente"].unique()))

# Artigos
todos_art = st.sidebar.checkbox("Todos os Artigos", value=True)
artigos_sel = df["Artigo"].unique().tolist() if todos_art else st.sidebar.multiselect(
    "Selecionar Artigos", sorted(df["Artigo"].unique()))

# === DADOS FILTRADOS ===
df_atual = df[
    (df["Ano"] == ano_atual) &
    (df["Comercial"].isin(comerciais_sel)) &
    (df["Cliente"].isin(clientes_sel)) &
    (df["Artigo"].isin(artigos_sel))
].copy()

# Inicializar df_anterior vazio se não houver ano anterior
if tem_ano_anterior:
    df_anterior = df[
        (df["Ano"] == ano_anterior) &
        (df["Comercial"].isin(comerciais_sel)) &
        (df["Cliente"].isin(clientes_sel)) &
        (df["Artigo"].isin(artigos_sel))
    ].copy()
else:
    df_anterior = pd.DataFrame(columns=df.columns)

# === CÁLCULO DOS KPIs ===
total_atual = df_atual["Quantidade"].sum()

if tem_ano_anterior:
    total_anterior = df_anterior["Quantidade"].sum()
    var_total = total_atual - total_anterior
    var_pct = (var_total / total_anterior * 100) if total_anterior > 0 else 0
else:
    total_anterior = 0
    var_total = 0
    var_pct = 0

n_clientes_atual = df_atual["Cliente"].nunique()

if tem_ano_anterior:
    n_clientes_anterior = df_anterior["Cliente"].nunique()
    var_clientes = n_clientes_atual - n_clientes_anterior
else:
    n_clientes_anterior = 0
    var_clientes = 0

n_artigos_atual = df_atual["Artigo"].nunique()
n_artigos_anterior = df_anterior["Artigo"].nunique() if tem_ano_anterior else 0

n_comerciais = df_atual["Comercial"].nunique()

ticket_atual = total_atual / len(df_atual) if len(df_atual) > 0 else 0

if tem_ano_anterior:
    ticket_anterior = total_anterior / len(df_anterior) if len(df_anterior) > 0 else 0
    var_ticket = ticket_atual - ticket_anterior
else:
    ticket_anterior = 0
    var_ticket = 0

top_cliente = df_atual.groupby("Cliente")["Quantidade"].sum().idxmax() if not df_atual.empty else "—"
top_qtd = df_atual.groupby("Cliente")["Quantidade"].sum().max() if not df_atual.empty else 0

# === 8 KPIs BONITOS NO TOPO ===
if tem_ano_anterior:
    st.markdown(f"### Resumo Executivo – {ano_atual} vs {ano_anterior}")
else:
    st.markdown(f"### Resumo Executivo – {ano_atual}")

c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

with c1:
    st.metric("Total Quantidade", f"{total_atual:,.0f}", f"{var_total:+,.0f}" if tem_ano_anterior else None)

with c2:
    if tem_ano_anterior:
        st.metric("Variação %", f"{var_pct:+.1f}%", delta_color="normal")
    else:
        st.metric("Variação %", "N/A")

with c3:
    st.metric("Clientes Únicos", n_clientes_atual, f"{var_clientes:+d}" if tem_ano_anterior else None)

with c4:
    if tem_ano_anterior:
        st.metric("Artigos Vendidos", n_artigos_atual, f"{n_artigos_atual - n_artigos_anterior:+d}")
    else:
        st.metric("Artigos Vendidos", n_artigos_atual)

with c5:
    st.metric("Comerciais Ativos", n_comerciais)

with c6:
    st.metric("Ticket Médio", f"{ticket_atual:,.0f}", f"{var_ticket:+.0f}" if tem_ano_anterior else None)

with c7:
    st.metric("Top Cliente", top_cliente)

with c8:
    st.metric("Qtd Top Cliente", f"{top_qtd:,.0f}")

st.divider()

# === EVOLUÇÃO MENSAL ===
if tem_ano_anterior:
    st.subheader(f"Evolução Mensal Comparativa – {ano_anterior} vs {ano_atual}")
else:
    st.subheader(f"Evolução Mensal – {ano_atual}")

meses = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

evol_atual = df_atual.groupby("MesNome")["Quantidade"].sum().reindex(meses, fill_value=0)

fig, ax = plt.subplots(figsize=(14,6))
ax.plot(meses, evol_atual.values, marker="o", linewidth=4, label=str(ano_atual), color="#2E86AB")

if tem_ano_anterior:
    evol_ant = df_anterior.groupby("MesNome")["Quantidade"].sum().reindex(meses, fill_value=0)
    ax.plot(meses, evol_ant.values, marker="o", linewidth=4, label=str(ano_anterior), color="#A23B72", alpha=0.7)
    ax.set_title(f"Evolução Mensal – {ano_anterior} vs {ano_atual}", fontsize=15, fontweight="bold")
else:
    ax.set_title(f"Evolução Mensal – {ano_atual}", fontsize=15, fontweight="bold")

ax.set_ylabel("Quantidade")
ax.legend()
ax.grid(alpha=0.3)
st.pyplot(fig)

st.divider()

# === TOP 10 CLIENTES YoY ===
if tem_ano_anterior:
    st.subheader(f"Top 10 Clientes – Comparativo {ano_anterior} vs {ano_atual}")
else:
    st.subheader(f"Top 10 Clientes – {ano_atual}")

if not df_atual.empty:
    top10 = df_atual.groupby("Cliente")["Quantidade"].sum().nlargest(10).index
    
    if tem_ano_anterior:
        comp = pd.DataFrame({
            str(ano_anterior): df_anterior.groupby("Cliente")["Quantidade"].sum(),
            str(ano_atual):    df_atual.groupby("Cliente")["Quantidade"].sum()
        }).fillna(0).loc[top10]

        comp["Variação"] = comp[str(ano_atual)] - comp[str(ano_anterior)]
        comp["Var %"] = (comp["Variação"] / comp[str(ano_anterior)].replace(0,1) * 100).round(1)
    else:
        comp = pd.DataFrame({
            str(ano_atual): df_atual.groupby("Cliente")["Quantidade"].sum()
        }).loc[top10]

    col1, col2 = st.columns([3,2])
    with col1:
        fig2, ax2 = plt.subplots(figsize=(10,6))
        if tem_ano_anterior:
            comp[[str(ano_anterior), str(ano_atual)]].plot(kind="barh", ax=ax2, color=["#A23B72", "#2E86AB"])
        else:
            comp[[str(ano_atual)]].plot(kind="barh", ax=ax2, color="#2E86AB")
        ax2.set_title("Top 10 Clientes")
        ax2.invert_yaxis()
        st.pyplot(fig2)
    
    with col2:
        disp = comp.copy()
        if tem_ano_anterior:
            for col in [str(ano_anterior), str(ano_atual), "Variação"]:
                disp[col] = disp[col].apply(lambda x: f"{x:,.0f}")
            disp["Var %"] = disp["Var %"].apply(lambda x: f"{x:+.1f}%")
        else:
            disp[str(ano_atual)] = disp[str(ano_atual)].apply(lambda x: f"{x:,.0f}")
        st.dataframe(disp, use_container_width=True)
else:
    st.info("Não há dados para o ano atual com os filtros selecionados.")

st.divider()

# === EXPORTAR EXCEL ===
st.subheader("Exportar Relatório")
output = io.BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    if not df_atual.empty:
        df_atual.groupby(["Comercial","Cliente","Artigo"])["Quantidade"].sum().reset_index().to_excel(
            writer, sheet_name="Detalhe Atual", index=False)
        
        if tem_ano_anterior and not df_anterior.empty:
            df_anterior.groupby(["Comercial","Cliente","Artigo"])["Quantidade"].sum().reset_index().to_excel(
                writer, sheet_name="Detalhe Anterior", index=False)

st.download_button(
    "Baixar Relatório Completo (Excel)",
    data=output.getvalue(),
    file_name=f"Dashboard_KPIs_{ano_atual}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success("Dashboard carregado com sucesso! Todos os filtros e KPIs funcionam perfeitamente.")
