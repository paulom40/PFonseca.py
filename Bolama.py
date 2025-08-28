import streamlit as st
import pandas as pd
import numpy as np

# Load your Excel data
@st.cache_data
def load_data():
    df = pd.read_excel("Bolama_Vendas.xlsx")
    df["Data"] = pd.to_datetime(df["Data"])
    return df

df = load_data()

# --- Login Sidebar ---
st.sidebar.title("🔐 Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")

if login_button and username == "pedro" and password == "pedro":
    st.success("✅ Login successful")

    # --- Filters Sidebar ---
    st.sidebar.title("📦 Filtros")
    selected_artigo = st.sidebar.multiselect("Artigo", options=df["Artigo"].unique())
    selected_mes = st.sidebar.multiselect("Mês", options=df["Mês"].unique())

    # --- Filtered Data ---
    filtered_df = df.copy()
    if selected_artigo:
        filtered_df = filtered_df[filtered_df["Artigo"].isin(selected_artigo)]
    if selected_mes:
        filtered_df = filtered_df[filtered_df["Mês"].isin(selected_mes)]

    # --- KPIs ---
    st.title("📊 Bolama Vendas Dashboard")
    st.markdown("### Indicadores por Mês")

    kpi_df = filtered_df.groupby("Mês").agg({
        "Quantidade": "sum",
        "V Líquido": "sum"
    }).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Quantidade", f"{kpi_df['Quantidade'].sum():,.2f} KG")
    with col2:
        st.metric("Total Vendas Líquidas", f"€ {kpi_df['V Líquido'].sum():,.2f}")

    # --- Top 10 Artigos ---
    st.markdown("### 🏆 Top 10 Artigos por Mês")
    top_artigos = (
        filtered_df.groupby(["Mês", "Artigo"])
        .agg({"Quantidade": "sum", "V Líquido": "sum"})
        .sort_values(by="V Líquido", ascending=False)
        .groupby("Mês")
        .head(10)
        .reset_index()
    )

    # --- Styled Table ---
    st.markdown("### 📋 Resultados Filtrados")
    st.dataframe(
        filtered_df.style.background_gradient(cmap="YlGnBu").format({
            "Quantidade": "{:.2f}",
            "V Líquido": "€ {:.2f}"
        }),
        use_container_width=True
    )

    st.markdown("### 📌 Top Artigos")
    st.dataframe(
        top_artigos.style.background_gradient(cmap="OrRd").format({
            "Quantidade": "{:.2f}",
            "V Líquido": "€ {:.2f}"
        }),
        use_container_width=True
    )

else:
    st.warning("🔒 Please log in to access the dashboard.")
