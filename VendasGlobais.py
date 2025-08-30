import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# -------------------- CUSTOM CSS --------------------
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .main {background-color: #f0f4f8;}
    .sidebar .sidebar-content {
        background-color: #1E3A8A;
        color: white;
    }
    h1, h2, h3 {
        color: #1E40AF;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #10B981;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #047857;
    }
    .stMultiSelect [data-testid="stMarkdownContainer"] {
        color: #3B82F6;
    }
    .stDataFrame {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        overflow: hidden;
    }
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 10px;
    }
    .kpi-title {
        font-size: 18px;
        color: #6B7280;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 32px;
        font-weight: bold;
        color: #1F2937;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- LOGO + HEADER --------------------
st.markdown("""
    <div style="display: flex; align-items: center; background-color: #4CAF50; padding: 10px; border-radius: 10px;">
        <img src="https://github.com/paulom40/PFonseca.py/raw/main/Bracar.png" width="120" style="margin-right: 20px;" />
        <h1 style="margin: 0; font-family: 'Segoe UI', sans-serif; color: white;">Vendas Globais Dashboard</h1>
    </div>
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
        st.error(f"❌ Erro ao carregar o ficheiro Excel: {str(e)}")
        st.stop()

    # Ensure Qtd. is numeric
    df["Qtd."] = pd.to_numeric(df["Qtd."], errors="coerce")

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
        # -------------------- MONTHLY SUMMARY FOR QTD --------------------
        monthly_summary = (
            filtered_df.groupby(["Ano", "Mês"])["Qtd."]
            .sum()
            .reset_index()
            .sort_values(["Ano", "Mês"])
        )

        # Ensure numeric values
        monthly_summary["Qtd."] = pd.to_numeric(monthly_summary["Qtd."], errors="coerce")

        # Calculate percentage variation
        monthly_summary["Variação (%)"] = monthly_summary["Qtd."].pct_change().round(2) * 100

        # -------------------- DISPLAY MONTHLY TABLE --------------------
        st.subheader("📈 Evolução Mensal do Artigo")
        st.dataframe(monthly_summary)

        # -------------------- PIVOT TABLE FOR ARTIGO, CLIENTE, QTD BY MÊS AND ANO --------------------
        st.subheader("📊 Tabela de Qtd. por Artigo, Cliente, Mês e Ano")
        try:
            pivot_table = pd.pivot_table(
                filtered_df,
                values="Qtd.",
                index=["Artigo", "Cliente"],
                columns=["Ano", "Mês"],
                aggfunc="sum",
                fill_value=0
            )
            # Flatten the MultiIndex for display
            pivot_table = pivot_table.reset_index()
            # Ensure all Qtd. columns are numeric
            for col in pivot_table.columns:
                if col not in ["Artigo", "Cliente"]:
                    pivot_table[col] = pd.to_numeric(pivot_table[col], errors="coerce").fillna(0)
            st.dataframe(pivot_table)
        except Exception as e:
            st.error(f"❌ Erro ao exibir a tabela pivô: {str(e)}")

        # -------------------- KPIs --------------------
        st.subheader("📊 KPIs por Artigo e Cliente")

        # KPI: Total Qtd por Artigo
        kpi_artigo = filtered_df.groupby("Artigo")["Qtd."].sum().reset_index()
        kpi_artigo.columns = ["Artigo", "Total Qtd."]

        # KPI: Total Qtd por Cliente
        kpi_cliente = filtered_df.groupby("Cliente")["Qtd."].sum().reset_index()
        kpi_cliente.columns = ["Cliente", "Total Qtd."]

        # Display KPIs in cards
        cols = st.columns(2)
        with cols[0]:
            st.markdown('<div class="kpi-card"><div class="kpi-title">KPIs por Artigo</div></div>', unsafe_allow_html=True)
            for _, row in kpi_artigo.iterrows():
                st.markdown(f'<div class="kpi-card"><div class="kpi-title">{row["Artigo"]}</div><div class="kpi-value">{int(row["Total Qtd."])}</div></div>', unsafe_allow_html=True)

        with cols[1]:
            st.markdown('<div class="kpi-card"><div class="kpi-title">KPIs por Cliente</div></div>', unsafe_allow_html=True)
            for _, row in kpi_cliente.iterrows():
                st.markdown(f'<div class="kpi-card"><div class="kpi-title">{row["Cliente"]}</div><div class="kpi-value">{int(row["Total Qtd."])}</div></div>', unsafe_allow_html=True)

        # -------------------- INTERACTIVE CHART --------------------
        st.subheader("📊 Gráfico de Qtd. Mensais")
        fig = px.line(monthly_summary, x="Mês", y="Qtd.", markers=True,
                      title="Qtd. Mensais",
                      labels={"Qtd.": "Quantidade", "Mês": "Mês"},
                      color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig, use_container_width=True)

        # -------------------- EXPORT BUTTON --------------------
        st.subheader("📤 Exportar Dados")
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            monthly_summary.to_excel(writer, sheet_name="Evolucao Mensal", index=False)
            pivot_table.to_excel(writer, sheet_name="Pivot Tabela", index=True)
            kpi_artigo.to_excel(writer, sheet_name="KPI Artigo", index=False)
            kpi_cliente.to_excel(writer, sheet_name="KPI Cliente", index=False)
        output.seek(0)
        st.download_button("📥 Baixar Excel", data=output, file_name="vendas_mensais.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif username or password:
    st.error("❌ Usuário ou senha incorretos")
