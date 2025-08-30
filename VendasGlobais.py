import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------- LOGO + HEADER --------------------
st.markdown("""
    <div style="display: flex; align-items: center;">
        <img src="https://github.com/paulom40/PFonseca.py/raw/main/Bracar.png" width="120" style="margin-right: 20px;" />
        <h1 style="margin: 0; font-family: 'Segoe UI', sans-serif;">Vendas Globais Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

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
st.subheader("🔐 Login")
username = st.text_input("Usuário")
password = st.text_input("Senha", type="password")

if username == "paulo" and password == "teste":
    st.success("Login bem-sucedido! 👋")

    # -------------------- LOAD DATA --------------------
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    try:
        df = pd.read_excel(url)
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error("❌ Erro ao carregar o ficheiro Excel.")
        st.stop()

    # -------------------- SIDEBAR MULTISELECT FILTERS --------------------
    st.sidebar.header("🔎 Filtros")

    selected_clientes = st.sidebar.multiselect("🧑 Cliente", df["Cliente"].unique(), default=df["Cliente"].unique())
    selected_artigos = st.sidebar.multiselect("📦 Artigo", df["Artigo"].unique(), default=df["Artigo"].unique())
    selected_comerciais = st.sidebar.multiselect("💼 Comercial", df["Comercial"].unique(), default=df["Comercial"].unique())
    selected_meses = st.sidebar.multiselect("🗓️ Mês", df["Mês"].unique(), default=df["Mês"].unique())
    selected_anos = st.sidebar.multiselect("📅 Ano", df["Ano"].unique(), default=df["Ano"].unique())

    # -------------------- FILTERED DATA --------------------
    filtered_df = df[
        df["Cliente"].isin(selected_clientes) &
        df["Artigo"].isin(selected_artigos) &
        df["Comercial"].isin(selected_comerciais) &
        df["Mês"].isin(selected_meses) &
        df["Ano"].isin(selected_anos)
    ]

    if filtered_df.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    else:
        monthly_summary = (
            filtered_df.groupby(["Ano", "Mês"])["V. Líquido"]
            .sum()
            .reset_index()
            .sort_values(["Ano", "Mês"])
        )

        # Ensure numeric values
        monthly_summary["V. Líquido"] = pd.to_numeric(monthly_summary["V. Líquido"], errors="coerce")

        # Calculate percentage variation
        monthly_summary["Variação (%)"] = monthly_summary["V. Líquido"].pct_change().round(2) * 100

        # -------------------- DISPLAY TABLE --------------------
        st.subheader("📈 Evolução Mensal do Artigo")
        st.dataframe(monthly_summary)

        # -------------------- INTERACTIVE CHART --------------------
        st.subheader("📊 Gráfico de Vendas Mensais")
        fig = px.line(monthly_summary, x="Mês", y="V. Líquido", markers=True,
                      title="Vendas Mensais",
                      labels={"V. Líquido": "Valor (€)", "Mês": "Mês"})
        st.plotly_chart(fig, use_container_width=True)

        # -------------------- EXPORT BUTTON --------------------
        st.subheader("📤 Exportar Dados")
        csv = monthly_summary.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Baixar CSV", data=csv, file_name="vendas_mensais.csv", mime="text/csv")

elif username or password:
    st.error("❌ Usuário ou senha incorretos")
