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
        selected_matricula = st.selectbox("Matricula", ["Todas"] + matriculas, key="mobile_matricula")

        anos = sorted(df['Ano'].unique())
        selected_ano = st.selectbox("Ano", ["Todos"] + anos, key="mobile_ano")

        selected_months = st.multiselect("Month", sorted(df['Month'].unique()), default=df['Month'].unique(), key="mobile_month")
        dias = sorted(df['Dia'].unique())
        selected_dias = st.multiselect("Dia", ["Todos"] + dias, default=["Todos"], key="mobile_dia")

    # Aplicar filtros para mobile
    filtered_df_mobile = df.copy()
    if selected_matricula != "Todas":
        filtered_df_mobile = filtered_df_mobile[filtered_df_mobile['Matricula'] == selected_matricula]
    if selected_ano != "Todos":
        filtered_df_mobile = filtered_df_mobile[filtered_df_mobile['Ano'] == int(selected_ano)]
    if selected_months:
        filtered_df_mobile = filtered_df_mobile[filtered_df_mobile['Month'].isin(selected_months)]
    if "Todos" not in selected_dias:
        filtered_df_mobile = filtered_df_mobile[filtered_df_mobile['Dia'].isin(selected_dias)]

    st.subheader("📊 Dados Filtrados")
    st.dataframe(filtered_df_mobile.style.set_properties(**{'font-size': '10pt'}), use_container_width=True)

    # Gráfico de barras para mobile - CORRIGIDO
    if not filtered_df_mobile.empty:
        st.subheader("📈 Valor Total por Mês")
        
        # Agrupar por mês e somar os valores
        chart_df_mobile = filtered_df_mobile.groupby("Month")["Value"].sum().reset_index()
        
        # Ordem dos meses
        month_order = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        
        # Criar gráfico Altair para mobile também
        bar_chart_mobile = alt.Chart(chart_df_mobile).mark_bar(color='steelblue').encode(
            x=alt.X('Month:O', title='Mês', sort=month_order),
            y=alt.Y('Value:Q', title='Valor Total'),
            tooltip=['Month', 'Value']
        )
        
        # Adicionar labels nos valores
        bar_labels_mobile = alt.Chart(chart_df_mobile).mark_text(
            align='center', baseline='bottom', fontWeight='bold', color='red', dy=-5
        ).encode(
            x=alt.X('Month:O', sort=month_order),
            y='Value:Q',
            text='Value:Q'
        )
        
        st.altair_chart((bar_chart_mobile + bar_labels_mobile).properties(
            title='Valor Total por Mês (Mobile)',
            width=600,
            height=400
        ), use_container_width=True)
        
        # Métricas resumidas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Geral", f"€{filtered_df_mobile['Value'].sum():.2f}")
        with col2:
            st.metric("Número de Registos", len(filtered_df_mobile))
        with col3:
            st.metric("Média por Registo", f"€{filtered_df_mobile['Value'].mean():.2f}")
            
    else:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")

# 🖥️ Versão Desktop
with tab_desktop:
    st.header("🖥️ Dashboard Desktop")

    st.sidebar.header("Filtros Desktop")
    matriculas = sorted(df['Matricula'].unique())
    selected_matricula_desktop = st.sidebar.selectbox("Matricula", ["Todas"] + matriculas, key="desktop_matricula")

    anos = sorted(df['Ano'].unique())
    selected_ano_desktop = st.sidebar.selectbox("Ano", ["Todos"] + anos, key="desktop_ano")

    selected_months_desktop = st.sidebar.multiselect("Month", sorted(df['Month'].unique()), default=df['Month'].unique(), key="desktop_month")
    dias = sorted(df['Dia'].unique())
    selected_dias_desktop = st.sidebar.multiselect("Dia", ["Todos"] + dias, default=["Todos"], key="desktop_dia")

    # Aplicar filtros para desktop
    filtered_df_desktop = df.copy()
    if selected_matricula_desktop != "Todas":
        filtered_df_desktop = filtered_df_desktop[filtered_df_desktop['Matricula'] == selected_matricula_desktop]
    if selected_ano_desktop != "Todos":
        filtered_df_desktop = filtered_df_desktop[filtered_df_desktop['Ano'] == int(selected_ano_desktop)]
    if selected_months_desktop:
        filtered_df_desktop = filtered_df_desktop[filtered_df_desktop['Month'].isin(selected_months_desktop)]
    if "Todos" not in selected_dias_desktop:
        filtered_df_desktop = filtered_df_desktop[filtered_df_desktop['Dia'].isin(selected_dias_desktop)]

    st.subheader("📊 Dados Filtrados")
    st.dataframe(filtered_df_desktop, use_container_width=True)

    month_order = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    if not filtered_df_desktop.empty:
        st.subheader("📈 Valor Total por Mês")
        
        chart_df_desktop = filtered_df_desktop.groupby("Month")["Value"].sum().reset_index()

        # Gráfico de linha para desktop
        line_chart = alt.Chart(chart_df_desktop).mark_line(point=True, color='green').encode(
            x=alt.X('Month:O', title='Mês', sort=month_order),
            y=alt.Y('Value:Q', title='Valor Total'),
            tooltip=['Month', 'Value']
        )

        line_labels = alt.Chart(chart_df_desktop).mark_text(
            align='center', baseline='bottom', fontWeight='bold', color='red', dy=-5
        ).encode(
            x=alt.X('Month:O', sort=month_order),
            y='Value:Q',
            text='Value:Q'
        )

        st.altair_chart((line_chart + line_labels).properties(
            title='Valor Total por Mês (Desktop)',
            width=800,
            height=400
        ), use_container_width=True)
        
        # Métricas resumidas para desktop
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Geral", f"€{filtered_df_desktop['Value'].sum():.2f}")
        with col2:
            st.metric("Número de Registos", len(filtered_df_desktop))
        with col3:
            st.metric("Média por Registo", f"€{filtered_df_desktop['Value'].mean():.2f}")
        with col4:
            st.metric("Mês com Maior Valor", f"€{filtered_df_desktop.groupby('Month')['Value'].sum().max():.2f}")
            
    else:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
