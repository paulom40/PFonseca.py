import streamlit as st
import pandas as pd
import io

# 🚀 Configuração da página
st.set_page_config(page_title="Bolama Dashboard", layout="wide", page_icon="📊")

# 🔒 Ocultar elementos padrão
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 📥 Carregar dados
@st.cache_data
def load_data():
    df = pd.read_excel("Bolama_Vendas.xlsx")
    df["Data"] = pd.to_datetime(df["Data"])
    df["Mês"] = df["Data"].dt.strftime("%Y-%m")
    return df

df = load_data()

# 🔐 Controle de sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 🔐 Login
st.sidebar.title("🔐 Login")
if not st.session_state.logged_in:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        if username == "pedro" and password == "pedro":
            st.session_state.logged_in = True
            st.success("✅ Login bem-sucedido")
        else:
            st.error("❌ Credenciais inválidas")
else:
    # 📦 Filtros
    st.sidebar.title("📦 Filtros")
    selected_artigo = st.sidebar.multiselect("Artigo", options=sorted(df["Artigo"].unique()))
    selected_mes = st.sidebar.multiselect("Mês", options=sorted(df["Mês"].unique()))

    filtered_df = df.copy()
    if selected_artigo:
        filtered_df = filtered_df[filtered_df["Artigo"].isin(selected_artigo)]
    if selected_mes:
        filtered_df = filtered_df[filtered_df["Mês"].isin(selected_mes)]

    # 🧮 KPIs
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

    # 🏆 Top Artigos
    st.markdown("### 🏆 Top 10 Artigos por Mês")
    top_artigos = (
        filtered_df.groupby(["Mês", "Artigo"])
        .agg({"Quantidade": "sum", "V Líquido": "sum"})
        .sort_values(by="V Líquido", ascending=False)
        .groupby("Mês")
        .head(10)
        .reset_index()
    )

    # 📋 Tabelas
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

    # 📈 Aba de Crescimento
    tab1, tab2 = st.tabs(["📊 Dashboard Principal", "📈 Crescimento por Artigo (2024 vs 2025)"])

    with tab2:
        st.markdown("### 📈 Percentagem de Crescimento por Artigo entre 2024 e 2025")

        df_growth = df[df["Data"].dt.year.isin([2024, 2025])].copy()
        df_growth["Ano"] = df_growth["Data"].dt.year
        df_growth["Mês"] = df_growth["Data"].dt.strftime("%m")

        grouped = df_growth.groupby(["Artigo", "Mês", "Ano"]).agg({
            "Quantidade": "sum",
            "V Líquido": "sum"
        }).reset_index()

        pivot_qtd = grouped.pivot(index=["Artigo", "Mês"], columns="Ano", values="Quantidade").reset_index()
        pivot_vl = grouped.pivot(index=["Artigo", "Mês"], columns="Ano", values="V Líquido").reset_index()

        pivot_qtd = pivot_qtd.rename(columns={2024: "Qtd 2024", 2025: "Qtd 2025"})
        pivot_vl = pivot_vl.rename(columns={2024: "Vendas 2024", 2025: "Vendas 2025"})

        crescimento_df = pd.merge(pivot_qtd, pivot_vl, on=["Artigo", "Mês"])
        crescimento_df["Crescimento Qtd (%)"] = ((crescimento_df["Qtd 2025"] - crescimento_df["Qtd 2024"]) / crescimento_df["Qtd 2024"]) * 100
        crescimento_df["Crescimento Vendas (%)"] = ((crescimento_df["Vendas 2025"] - crescimento_df["Vendas 2024"]) / crescimento_df["Vendas 2024"]) * 100
        crescimento_df = crescimento_df.round(2)

        st.dataframe(
            crescimento_df.style.format({
                "Qtd 2024": "{:.2f} KG",
                "Qtd 2025": "{:.2f} KG",
                "Vendas 2024": "€ {:.2f}",
                "Vendas 2025": "€ {:.2f}",
                "Crescimento Qtd (%)": "{:+.2f}%",
                "Crescimento Vendas (%)": "{:+.2f}%"
            }).background_gradient(cmap="RdYlGn", subset=["Crescimento Qtd (%)", "Crescimento Vendas (%)"]),
            use_container_width=True
        )

        # 📤 Exportar para Excel com estilo e gráficos
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Dados Filtrados')
            top_artigos.to_excel(writer, index=False, sheet_name='Top Artigos')
            crescimento_df.to_excel(writer, index=False, sheet_name='Crescimento')

            ws3 = writer.sheets['Crescimento']
            ws3.set_column('A:Z', 18)

            format_up = writer.book.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
            format_down = writer.book.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
            ws3.conditional_format(f'G2:G{len(crescimento_df)+1}', {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': format_up})
            ws3.conditional_format(f'G2:G{len(crescimento_df)+1}', {'type': 'cell', 'criteria': '<', 'value': 0, 'format': format_down})
            ws3.conditional_format(f'H2:H{len(crescimento_df)+1}', {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': format_up})
            ws3.conditional_format(f'H2:H{len(crescimento_df)+1}', {'type': 'cell', 'criteria': '<', 'value': 0, 'format': format_down})

            chart_vendas = writer.book.add_chart({'type': 'column'})
            chart_vendas.add_series({
                'name': 'Crescimento Vendas (%)',
                'categories': ['Crescimento', 1, 0, len(crescimento_df), 0],
                'values': ['Crescimento', 1, 7, len(crescimento_df), 7],
            })
            chart_vendas.set_title({'name': 'Crescimento de Vendas (%) por Artigo'})
            chart_vendas.set_x_axis({'name': 'Artigo'})
            chart_vendas.set_y_axis({'name': 'Variação (%)'})
            ws3.insert_chart('J2', chart_vendas)

            chart_qtd = writer.book.add_chart({'type': 'column'})
            chart_qtd.add_series({
                'name': 'Crescimento Quantidade (%)',
                'categories': ['Crescimento', 1, 0, len(crescimento_df), 0],
                'values': ['Crescimento', 1, 6, len(crescimento_df), 6],
            })
            chart_qtd.set_title({'name': 'Crescimento de Quantidade (%) por Artigo'})
            chart_qtd.set_x_axis({'name': 'Artigo'})
            chart_qtd.set_y_axis({'name': 'Variação
