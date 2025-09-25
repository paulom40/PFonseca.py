import streamlit as st
import pandas as pd
import altair as alt

# 🎨 Estilo visual
st.set_page_config(layout="wide", page_title="Dashboard da Frota", page_icon="🚘")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .metric {text-align: center !important;}
    </style>
""", unsafe_allow_html=True)

# 📂 Carregar dados da folha "Dados"
url = "https://github.com/paulom40/PFonseca.py/raw/main/frota.xlsx"
try:
    df = pd.read_excel(url, sheet_name="Dados")
    st.success("✅ Dados da frota carregados com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {e}")
    st.stop()

# 📱🖥️ Separadores para versão mobile e desktop
tab_mobile, tab_desktop = st.tabs(["📱 Versão Mobile", "🖥️ Versão Desktop"])

# 📱 Versão Mobile
with tab_mobile:
    st.header("📱 Dashboard Mobile")

    with st.expander("🔍 Filtros", expanded=False):
        tipos = sorted(df['Tipo'].dropna().unique())
        selected_tipo = st.selectbox("Tipo de Veículo", ["Todos"] + tipos)

        estados = sorted(df['Estado'].dropna().unique())
        selected_estado = st.selectbox("Estado", ["Todos"] + estados)

    df_mobile = df.copy()
    if selected_tipo != "Todos":
        df_mobile = df_mobile[df_mobile['Tipo'] == selected_tipo]
    if selected_estado != "Todos":
        df_mobile = df_mobile[df_mobile['Estado'] == selected_estado]

    st.metric("🚗 Total de Veículos", len(df_mobile))
    st.metric("🛠️ Manutenções Pendentes", df_mobile[df_mobile['Manutenção'] == 'Pendente'].shape[0])
    st.metric("⛽ Consumo Médio", f"{df_mobile['Consumo'].mean():.2f} L/100km")

    tipo_df = df_mobile.groupby("Tipo")["ID"].count().reset_index()
    chart = alt.Chart(tipo_df).mark_bar(color="#4e79a7").encode(
        x=alt.X("Tipo", title="Tipo de Veículo"),
        y=alt.Y("ID", title="Quantidade"),
        tooltip=["Tipo", "ID"]
    ).properties(title="Distribuição por Tipo de Veículo")

    st.altair_chart(chart, use_container_width=True)

    st.subheader("📋 Detalhes da Frota")
    st.dataframe(df_mobile.style.set_properties(**{'font-size': '10pt'}), use_container_width=True)

# 🖥️ Versão Desktop
with tab_desktop:
    st.header("🖥️ Dashboard Desktop")

    st.sidebar.header("🔍 Filtros")
    tipos = sorted(df['Tipo'].dropna().unique())
    selected_tipo = st.sidebar.selectbox("Tipo de Veículo", ["Todos"] + tipos)

    estados = sorted(df['Estado'].dropna().unique())
    selected_estado = st.sidebar.selectbox("Estado", ["Todos"] + estados)

    df_desktop = df.copy()
    if selected_tipo != "Todos":
        df_desktop = df_desktop[df_desktop['Tipo'] == selected_tipo]
    if selected_estado != "Todos":
        df_desktop = df_desktop[df_desktop['Estado'] == selected_estado]

    col1, col2, col3 = st.columns(3)
    col1.metric("🚗 Total de Veículos", len(df_desktop))
    col2.metric("🛠️ Manutenções Pendentes", df_desktop[df_desktop['Manutenção'] == 'Pendente'].shape[0])
    col3.metric("⛽ Consumo Médio", f"{df_desktop['Consumo'].mean():.2f} L/100km")

    tipo_df = df_desktop.groupby("Tipo")["ID"].count().reset_index()
    chart = alt.Chart(tipo_df).mark_bar().encode(
        x=alt.X("Tipo", title="Tipo de Veículo"),
        y=alt.Y("ID", title="Quantidade"),
        tooltip=["Tipo", "ID"]
    ).properties(title="Distribuição por Tipo de Veículo")

    st.altair_chart(chart, use_container_width=True)

    st.subheader("📋 Detalhes da Frota")
    st.dataframe(df_desktop, use_container_width=True)
