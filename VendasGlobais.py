# app.py

import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd

# -------------------- LOGIN SETUP --------------------
credentials = {
    "usernames": {
        "paulojt": {
            "name": "paulo",
            "password": stauth.Hasher(["teste"]).generate()[0]  # Replace with your actual password
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "vendas_app",
    "auth_token",
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", "main")

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

# -------------------- APP LOGIC --------------------
if authentication_status:
    st.title("📊 Vendas Globais Dashboard")
    st.write(f"Bem-vindo, {name} 👋")

    # Load Excel data from GitHub
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    df = pd.read_excel(url)

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

else:
    if authentication_status is False:
        st.error("Usuário ou senha incorretos")
    elif authentication_status is None:
        st.warning("Por favor, insira suas credenciais")
