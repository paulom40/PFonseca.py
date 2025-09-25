import streamlit as st
import pandas as pd
import altair as alt

# Ocultar menu, header e footer
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Configuração da página
st.set_page_config(layout="wide")

# 📂 Carregar Excel do GitHub
file_url = "https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx"

# 🔷 Cabeçalho
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://github.com/paulom40/PFonseca.py/raw/main/Bracar.png", width=100)
with col2:
    st.title("Via Verde Dashboard")

# 📊 Carregar e validar dados
try:
    df = pd.read_excel(file_url)
    df = df.drop(columns=['Mês'], errors='ignore')
    st.success("✅ Dados carregados com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {e}")
    st.stop()

required_cols = ['Matricula', 'Date', 'Ano', 'Month', 'Dia', 'Value']
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"⚠️ Faltam colunas: {', '.join(missing_cols)}")
    st.stop()

# 🗓️ Normalizar nomes dos meses
month_mapping = {
    'janeiro': 'Janeiro', 'fevereiro': 'Fevereiro', 'março': 'Março', 'abril': 'Abril',
    'maio': 'Maio', 'junho': 'Junho', 'julho': 'Julho', 'agosto': 'Agosto',
    'setembro': 'Setembro', 'outubro': 'Outubro', 'novembro': 'Novembro', 'dezembro': 'Dezembro'
}
df['Month'] = df['Month'].str.lower().map(month_mapping).fillna(df['Month'])

# 📱🖥️ Separadores para versão mobile e desktop
tab_mobile, tab_desktop = st.tabs(["📱 Versão Mobile", "🖥️ Versão Desktop"])

# 📱 Versão Mobile
with tab_mobile:
    st.header("📱 Dashboard Mobile")

    with st.expander("🔍 Filtros", expanded=False):
        matriculas = sorted(df['Matricula'].unique())
        selected_matricula = st.selectbox("Matricula", ["Todas"] + matriculas)

        anos = sorted(df['Ano'].unique())
        selected_ano = st.selectbox("Ano", ["Todos"] + anos)

        selected_months = st.multiselect("Month", sorted(df['Month'].unique()), default=df['Month'].unique())
        dias = sorted(df['Dia'].unique())
        selected_dias = st.multiselect("Dia", ["Todos"] + dias, default=["Todos"])

    filtered_df = df.copy()
    if selected_matricula != "Todas":
        filtered_df = filtered_df[filtered_df['Matricula'] == selected_matricula]
    if selected_ano != "Todos":
        filtered_df = filtered_df[filtered_df['Ano'] == selected_ano]
    if selected_months:
        filtered_df = filtered_df[filtered_df['Month'].isin(selected_months)]
    if "Todos" not in selected_dias:
        filtered_df = filtered_df[filtered_df['Dia'].isin(selected_dias)]

    st.dataframe(filtered_df.style.set_properties(**{'font-size': '10pt'}), use_container_width=True)

    chart_df = filtered_df.groupby("Month")["Value"].sum().reset_index()
    st.bar_chart(chart_df.set_index("Month"))

# 🖥️ Versão Desktop
with tab_desktop:
    st.header("🖥️ Dashboard Desktop")

    st.sidebar.header("Filtros")
    matriculas = sorted(df['Matricula'].unique())
    selected_matricula = st.sidebar.selectbox("Matricula", ["Todas"] + matriculas)

    anos = sorted(df['Ano'].unique())
    selected_ano = st.sidebar.selectbox("Ano", ["Todos"] + anos)

    selected_months = st.sidebar.multiselect("Month", sorted(df['Month'].unique()), default=df['Month'].unique())
    dias = sorted(df['Dia'].unique())
    selected_dias = st.sidebar.multiselect("Dia", ["Todos"] + dias, default=["Todos"])

    filtered_df = df.copy()
    if selected_matricula != "Todas":
        filtered_df = filtered_df[filtered_df['Matricula'] == selected_matricula]
    if selected_ano != "Todos":
        filtered_df = filtered_df[filtered_df['Ano'] == selected_ano]
    if selected_months:
        filtered_df = filtered_df[filtered_df['Month'].isin(selected_months)]
    if "Todos" not in selected_dias:
        filtered_df = filtered_df[filtered_df['Dia'].isin(selected_dias)]

    st.write("✅ Dados filtrados:")
    st.dataframe(filtered_df, use_container_width=True)

    month_order = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    chart_df = filtered_df.groupby("Month")["Value"].sum().reset_index()

    line_chart = alt.Chart(chart_df).mark_line(point=True).encode(
        x=alt.X('Month:O', title='Mês', sort=month_order),
        y=alt.Y('Value:Q', title='Valor Total'),
        tooltip=['Month', 'Value']
    )

    line_labels = alt.Chart(chart_df).mark_text(
        align='center', baseline='bottom', fontWeight='bold', color='red', dy=-5
    ).encode(
        x=alt.X('Month:O', sort=month_order),
        y='Value:Q',
        text='Value:Q'
    )

    st.altair_chart((line_chart + line_labels).properties(title='Valor Total por Mês'), use_container_width=True)
