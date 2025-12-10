import io
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="KPI Compras Clientes (YoY)", layout="wide")
st.title("📊 KPI de Compras por Cliente (YoY)")

# --- Config ---
RAW_URL_DEFAULT = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"

@st.cache_data(show_spinner=False)
def load_excel_from_bytes(data: bytes) -> pd.DataFrame:
    return pd.read_excel(io.BytesIO(data))

@st.cache_data(show_spinner=False)
def load_excel_from_url(url: str) -> pd.DataFrame:
    return pd.read_excel(url)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Tenta mapear nomes comuns para as colunas esperadas
    cols = {c.lower(): c for c in df.columns}
    # Esperados: Data, Nome, Quantidade
    data_col = None
    for cand in ["data", "date", "dt", "emissão", "emissao"]:
        if cand in cols:
            data_col = cols[cand]; break
    nome_col = None
    for cand in ["nome", "cliente", "client"]:
        if cand in cols:
            nome_col = cols[cand]; break
    qty_col = None
    for cand in ["quantidade", "qty", "qtd", "quant", "qt"]:
        if cand in cols:
            qty_col = cols[cand]; break

    missing = [lbl for lbl, col in [("Data", data_col), ("Nome", nome_col), ("Quantidade", qty_col)] if col is None]
    if missing:
        st.error(f"Colunas em falta: {', '.join(missing)}. Atualiza o ficheiro ou ajusta o mapeamento.")
        st.stop()

    df = df.rename(columns={data_col: "Data", nome_col: "Nome", qty_col: "Quantidade"})
    return df

def prepare_kpi(df: pd.DataFrame) -> pd.DataFrame:
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"])
    df["Ano"] = df["Data"].dt.year
    df["Mes"] = df["Data"].dt.month
    kpi = df.groupby(["Nome", "Ano", "Mes"], as_index=False)["Quantidade"].sum()
    return kpi

def compute_yoy_pivot(kpi: pd.DataFrame, ano_base: int, ano_comp: int) -> pd.DataFrame:
    pv = kpi.pivot_table(index=["Nome", "Mes"], columns="Ano", values="Quantidade", aggfunc="sum")
    # Garante colunas dos anos
    for a in [ano_base, ano_comp]:
        if a not in pv.columns:
            pv[a] = 0
    pv["Variação_%"] = ((pv[ano_comp] - pv[ano_base]) / pv[ano_base].replace(0, pd.NA)) * 100
    pv = pv.reset_index().sort_values(["Nome", "Mes"])
    return pv

def month_name_pt(m):
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    return meses[m-1] if 1 <= m <= 12 else str(m)

# --- Data input ---
with st.sidebar:
    st.header("Dados")
    mode = st.radio("Fonte de dados", ["Upload", "GitHub (raw)"], index=1)
    url = st.text_input("URL do ficheiro (raw)", RAW_URL_DEFAULT)
    uploaded = st.file_uploader("Upload Excel", type=["xlsx"])

# Carregar
df = None
if mode == "Upload":
    if uploaded:
        df = load_excel_from_bytes(uploaded.read())
    else:
        st.info("Carrega o ficheiro Excel para continuar.")
else:
    try:
        df = load_excel_from_url(url)
    except Exception as e:
        st.error(f"Falha ao ler do URL: {e}")
        st.stop()

if df is not None:
    df = normalize_columns(df)
    kpi = prepare_kpi(df)

    anos_disponiveis = sorted(kpi["Ano"].unique())
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        ano_base = st.selectbox("Ano base", anos_disponiveis, index=max(0, len(anos_disponiveis)-2))
    with col2:
        ano_comp = st.selectbox("Ano comparação", anos_disponiveis, index=len(anos_disponiveis)-1)
    with col3:
        cliente_filter = st.multiselect("Filtrar clientes", sorted(kpi["Nome"].unique()))

    kpi_view = kpi.copy()
    if cliente_filter:
        kpi_view = kpi_view[kpi_view["Nome"].isin(cliente_filter)]

    pv = compute_yoy_pivot(kpi_view, ano_base, ano_comp)
    pv["MesNome"] = pv["Mes"].apply(month_name_pt)
    cols_order = ["Nome", "MesNome", ano_base, ano_comp, "Variação_%"]
    pv = pv[cols_order].rename(columns={"MesNome": "Mês"})

    st.subheader("Tabela comparativa YoY por Cliente e Mês")
    st.dataframe(
        pv.style
        .format({ano_base: "{:.0f}", ano_comp: "{:.0f}", "Variação_%": "{:.2f}"})
        .background_gradient(cmap="RdYlGn", subset=["Variação_%"])
    )

    # Exportação
    colA, colB = st.columns(2)
    with colA:
        csv = pv.to_csv(index=False).encode("utf-8-sig")
        st.download_button("💾 Exportar CSV", csv, file_name=f"KPI_YoY_{ano_base}_vs_{ano_comp}.csv", mime="text/csv")
    with colB:
        # Exportar Excel com formatação básica via pandas (sem cores); cores podem ser adicionadas offline se necessário
        xls_buf = io.BytesIO()
        with pd.ExcelWriter(xls_buf, engine="xlsxwriter") as writer:
            pv.to_excel(writer, sheet_name="KPI_YoY", index=False)
            ws = writer.sheets["KPI_YoY"]
            # Ajuste de largura de colunas
            for i, col in enumerate(pv.columns):
                width = max(12, min(30, int(pv[col].astype(str).str.len().mean()) + 4))
                ws.set_column(i, i, width)
        st.download_button("📥 Exportar Excel", xls_buf.getvalue(), file_name=f"KPI_YoY_{ano_base}_vs_{ano_comp}.xlsx")

    # Gráfico por cliente
    st.subheader("Evolução mensal por cliente")
    clientes = sorted(pv["Nome"].unique())
    cliente_sel = st.selectbox("Selecionar cliente", clientes if clientes else ["—"], index=0)
    if cliente_sel and cliente_sel != "—":
        base = kpi[(kpi["Nome"] == cliente_sel) & (kpi["Ano"] == ano_base)].sort_values("Mes")
        comp = kpi[(kpi["Nome"] == cliente_sel) & (kpi["Ano"] == ano_comp)].sort_values("Mes")

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(base["Mes"], base["Quantidade"], marker="o", label=str(ano_base))
        ax.plot(comp["Mes"], comp["Quantidade"], marker="o", label=str(ano_comp))
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels([month_name_pt(m) for m in range(1, 13)])
        ax.set_xlabel("Mês")
        ax.set_ylabel("Quantidade")
        ax.set_title(f"Evolução mensal – {cliente_sel}")
        ax.legend()
        st.pyplot(fig)

    # Resumo rápido
    st.markdown("> Dica: usa o filtro de clientes para focar nos principais e exporta o Excel para partilha.")
