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

        months_available = sorted(df['Month'].unique())
        selected_months = st.multiselect("Month", months_available, default=months_available, key="mobile_month")
        
        dias = sorted(df['Dia'].unique())
        selected_dias = st.multiselect("Dia", ["Todos"] + dias, default=["Todos"], key="mobile_dia")

    # Aplicar filtros para mobile - CORREÇÃO: garantir que todos os filtros são aplicados
    filtered_df_mobile = df.copy()
    
    # Debug: mostrar contagem inicial
    st.write(f"📊 Dados iniciais: {len(filtered_df_mobile)} registos")
    
    # Aplicar filtro de Matricula
    if selected_matricula != "Todas":
        filtered_df_mobile = filtered_df_mobile[filtered_df_mobile['Matricula'] == selected_matricula]
        st.write(f"📊 Após filtro Matricula ({selected_matricula}): {len(filtered_df_mobile)} registos")
    
    # Aplicar filtro de Ano
    if selected_ano != "Todos":
        # Converter para o mesmo tipo de dados (ambos int ou ambos str)
        filtered_df_mobile = filtered_df_mobile[filtered_df_mobile['Ano'].astype(str) == str(selected_ano)]
        st.write(f"📊 Após filtro Ano ({selected_ano}): {len(filtered_df_mobile)} registos")
    
    # Aplicar filtro de Month
    if selected_months:
        filtered_df_mobile = filtered_df_mobile[filtered_df_mobile['Month'].isin(selected_months)]
        st.write(f"📊 Após filtro Month ({len(selected_months)} meses): {len(filtered_df_mobile)} registos")
    
    # Aplicar filtro de Dia
    if "Todos" not in selected_dias:
        filtered_df_mobile = filtered_df_mobile[filtered_df_mobile['Dia'].isin(selected_dias)]
        st.write(f"📊 Após filtro Dia ({len(selected_dias)} dias): {len(filtered_df_mobile)} registos")

    st.subheader("📊 Dados Filtrados")
    st.dataframe(filtered_df_mobile, use_container_width=True)

    # Gráfico de barras para mobile - CORREÇÃO: usar o dataframe filtrado corretamente
    if not filtered_df_mobile.empty:
        st.subheader("📈 Valor Total por Mês")
        
        # Agrupar por mês e somar os valores - CORREÇÃO: usar filtered_df_mobile
        chart_df_mobile = filtered_df_mobile.groupby("Month")["Value"].sum().reset_index()
        st.write(f"📈 Dados para gráfico: {len(chart_df_mobile)} meses")
        
        # Ordem dos meses
        month_order = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        
        # Garantir que todos os meses estejam presentes (mesmo com valor 0)
        all_months_df = pd.DataFrame({'Month': month_order})
        chart_df_mobile = all_months_df.merge(chart_df_mobile, on='Month', how='left').fillna(0)
        
        # Criar gráfico Altair para mobile
        bar_chart_mobile = alt.Chart(chart_df_mobile).mark_bar(color='steelblue').encode(
            x=alt.X('Month:O', title='Mês', sort=month_order),
            y=alt.Y('Value:Q', title='Valor Total (€)'),
            tooltip=['Month', alt.Tooltip('Value:Q', title='Valor (€)', format='.2f')]
        ).properties(
            title='Valor Total por Mês (Mobile)',
            width=600,
            height=400
        )
        
        # Adicionar labels nos valores (apenas se valor > 0)
        bar_labels_mobile = alt.Chart(chart_df_mobile[chart_df_mobile['Value'] > 0]).mark_text(
            align='center', 
            baseline='bottom', 
            fontWeight='bold', 
            color='red', 
            dy=-5
        ).encode(
            x=alt.X('Month:O', sort=month_order),
            y='Value:Q',
            text=alt.Text('Value:Q', format='.2f')
        )
        
        st.altair_chart(bar_chart_mobile + bar_labels_mobile, use_container_width=True)
        
        # Métricas resumidas
        col1, col2, col3 = st.columns(3)
        with col1:
            total_value = filtered_df_mobile['Value'].sum()
            st.metric("Total Geral", f"€{total_value:.2f}")
        with col2:
            st.metric("Número de Registos", len(filtered_df_mobile))
        with col3:
            avg_value = filtered_df_mobile['Value'].mean() if len(filtered_df_mobile) > 0 else 0
            st.metric("Média por Registo", f"€{avg_value:.2f}")
            
    else:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")

# 🖥️ Versão Desktop
with tab_desktop:
    st.header("🖥️ Dashboard Desktop")

    st.sidebar.header("Filtros Desktop")
    matriculas = sorted(df['Matricula'].unique())
    selected_matricula_desktop = st.sidebar.selectbox("Matricula", ["Todas"] + matriculas, key="desktop_matricula")

    anos = sorted(df['Ano'].unique())
    selected_ano_desktop = st.sidebar.selectbox("Ano", ["Todos"] + anos, key="desktop_ano")

    months_available_desktop = sorted(df['Month'].unique())
    selected_months_desktop = st.sidebar.multiselect("Month", months_available_desktop, default=months_available_desktop, key="desktop_month")
    
    dias = sorted(df['Dia'].unique())
    selected_dias_desktop = st.sidebar.multiselect("Dia", ["Todos"] + dias, default=["Todos"], key="desktop_dia")

    # Aplicar filtros para desktop
    filtered_df_desktop = df.copy()
    
    # Aplicar filtro de Matricula
    if selected_matricula_desktop != "Todas":
        filtered_df_desktop = filtered_df_desktop[filtered_df_desktop['Matricula'] == selected_matricula_desktop]
    
    # Aplicar filtro de Ano
    if selected_ano_desktop != "Todos":
        filtered_df_desktop = filtered_df_desktop[filtered_df_desktop['Ano'].astype(str) == str(selected_ano_desktop)]
    
    # Aplicar filtro de Month
    if selected_months_desktop:
        filtered_df_desktop = filtered_df_desktop[filtered_df_desktop['Month'].isin(selected_months_desktop)]
    
    # Aplicar filtro de Dia
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
        
        # Garantir que todos os meses estejam presentes (mesmo com valor 0)
        all_months_df = pd.DataFrame({'Month': month_order})
        chart_df_desktop = all_months_df.merge(chart_df_desktop, on='Month', how='left').fillna(0)

        # Gráfico de linha para desktop
        line_chart = alt.Chart(chart_df_desktop).mark_line(point=True, color='green').encode(
            x=alt.X('Month:O', title='Mês', sort=month_order),
            y=alt.Y('Value:Q', title='Valor Total (€)'),
            tooltip=['Month', alt.Tooltip('Value:Q', title='Valor (€)', format='.2f')]
        ).properties(
            title='Valor Total por Mês (Desktop)',
            width=800,
            height=400
        )

        line_labels = alt.Chart(chart_df_desktop[chart_df_desktop['Value'] > 0]).mark_text(
            align='center', 
            baseline='bottom', 
            fontWeight='bold', 
            color='red', 
            dy=-5
        ).encode(
            x=alt.X('Month:O', sort=month_order),
            y='Value:Q',
            text=alt.Text('Value:Q', format='.2f')
        )

        st.altair_chart(line_chart + line_labels, use_container_width=True)
        
        # Métricas resumidas para desktop
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_value_desktop = filtered_df_desktop['Value'].sum()
            st.metric("Total Geral", f"€{total_value_desktop:.2f}")
        with col2:
            st.metric("Número de Registos", len(filtered_df_desktop))
        with col3:
            avg_value_desktop = filtered_df_desktop['Value'].mean() if len(filtered_df_desktop) > 0 else 0
            st.metric("Média por Registo", f"€{avg_value_desktop:.2f}")
        with col4:
            max_month_value = chart_df_desktop['Value'].max()
            st.metric("Valor Máximo Mensal", f"€{max_month_value:.2f}")
            
    else:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
