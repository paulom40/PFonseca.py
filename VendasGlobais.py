import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------- CUSTOM CSS --------------------
st.markdown("""
    <style>
    .main {background-color: #f7f9fc;}
    .sidebar .sidebar-content {
        background-color: #2c3e50;
        color: white;
    }
    h1, h2, h3 {
        color: #34495e;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #1abc9c;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- SIMPLE LOGIN --------------------
st.title("🔐 Login")
username = st.text_input("Usuário")
password = st.text_input("Senha", type="password")

if username == "paulo" and password == "teste":
    st.success("Login bem-sucedido! 👋")

    # -------------------- LOAD DATA --------------------
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    try:
        df = pd.read_excel(url)
    except Exception as e:
        st.error("❌ Erro ao carregar o ficheiro Excel.")
        st.stop()

    # -------------------- SIDEBAR FILTERS --------------------
    st.sidebar.header("🔎 Filtros")
    cliente = st.sidebar.selectbox("🧑 Cliente", df["Cliente"].unique())
    artigo = st.sidebar.selectbox("📦 Artigo", df["Artigo"].unique())
    comercial = st.sidebar.selectbox("💼 Comercial", df["Comercial"].unique())
    mes = st.sidebar.selectbox("🗓️ Mês", df["Mês"].unique())
    ano = st.sidebar.selectbox("📅 Ano", df["Ano"].unique())

    # -------------------- FILTERED DATA --------------------
    filtered_df = df[
        (df["Cliente"] == cliente) &
        (df["Artigo"] == artigo) &
        (df["Comercial"] == comercial) &
        (df["Ano"] == ano)
    ]

    monthly_summary = (
        filtered_df.groupby(["Ano", "Mês"])["Valor"]
        .sum()
        .reset_index()
        .sort_values(["Ano", "Mês"])
    )

    monthly_summary["Variação (%)"] = monthly_summary["Valor"].pct_change().round(2) * 100

    # -------------------- DISPLAY TABLE --------------------
    st.subheader("📈 Evolução Mensal do Artigo")
    st.dataframe(monthly_summary)

    # -------------------- INTERACTIVE CHART --------------------
    st.subheader("📊 Gráfico de Vendas Mensais")
    fig = px.line(monthly_summary, x="Mês", y="Valor", markers=True,
                  title=f"Vendas Mensais - {artigo} ({cliente})",
                  labels={"Valor": "Valor (€)", "Mês": "Mês"})
    st.plotly_chart(fig, use_container_width=True)

    # -------------------- EXPORT BUTTON --------------------
    st.subheader("📤 Exportar Dados")
    csv = monthly_summary.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar CSV", data=csv, file_name="vendas_mensais.csv", mime="text/csv")

elif username or password:
    st.error("❌ Usuário ou senha incorretos")
