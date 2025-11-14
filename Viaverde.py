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

# 🔍 Filtros
st.header("🔍 Filtros")

col1, col2, col3, col4 = st.columns(4)

with col1:
    matriculas = sorted(df['Matricula'].unique())
    selected_matricula = st.selectbox("Matricula", ["Todas"] + matriculas)

with col2:
    anos = sorted(df['Ano'].unique())
    selected_ano = st.selectbox("Ano", ["Todos"] + anos)

with col3:
    months_available = sorted(df['Month'].unique())
    selected_months = st.multiselect("Mês", months_available, default=months_available)
    
with col4:
    dias = sorted(df['Dia'].unique())
    selected_dias = st.multiselect("Dia", ["Todos"] + dias, default=["Todos"])

# Aplicar filtros
filtered_df = df.copy()

# Filtro Matricula
if selected_matricula != "Todas":
    filtered_df = filtered_df[filtered_df['Matricula'] == selected_matricula]

# Filtro Ano
if selected_ano != "Todos":
    filtered_df = filtered_df[filtered_df['Ano'].astype(str) == str(selected_ano)]

# Filtro Mês
if selected_months:
    filtered_df = filtered_df[filtered_df['Month'].isin(selected_months)]

# Filtro Dia
if "Todos" not in selected_dias:
    filtered_df = filtered_df[filtered_df['Dia'].isin(selected_dias)]

# 📊 Dados Filtrados
st.header("📊 Dados Filtrados")
st.dataframe(filtered_df, use_container_width=True)

# 📈 Gráficos
if not filtered_df.empty:
    st.header("📈 Análise de Valores")
    
    # Ordem dos meses
    month_order = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    
    # Gráfico 1: Valor Total por Mês
    st.subheader("Valor Total por Mês")
    
    # Agrupar por mês
    chart_df_month = filtered_df.groupby("Month")["Value"].sum().reset_index()
    
    # Garantir que todos os meses estejam presentes
    all_months_df = pd.DataFrame({'Month': month_order})
    chart_df_month = all_months_df.merge(chart_df_month, on='Month', how='left').fillna(0)
    
    # Criar gráfico de barras
    bar_chart = alt.Chart(chart_df_month).mark_bar(color='steelblue').encode(
        x=alt.X('Month:O', title='Mês', sort=month_order),
        y=alt.Y('Value:Q', title='Valor Total (€)'),
        tooltip=['Month', alt.Tooltip('Value:Q', title='Valor (€)', format='.2f')]
    ).properties(
        height=400
    )
    
    # Adicionar labels
    bar_labels = alt.Chart(chart_df_month[chart_df_month['Value'] > 0]).mark_text(
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
    
    st.altair_chart(bar_chart + bar_labels, use_container_width=True)
    
    # Gráfico 2: Valor Total por Dia (opcional)
    st.subheader("Valor Total por Dia")
    
    # Agrupar por dia
    chart_df_day = filtered_df.groupby("Dia")["Value"].sum().reset_index().sort_values("Dia")
    
    line_chart = alt.Chart(chart_df_day).mark_line(point=True, color='green').encode(
        x=alt.X('Dia:O', title='Dia do Mês'),
        y=alt.Y('Value:Q', title='Valor Total (€)'),
        tooltip=['Dia', alt.Tooltip('Value:Q', title='Valor (€)', format='.2f')]
    ).properties(
        height=300
    )
    
    st.altair_chart(line_chart, use_container_width=True)
    
    # 📊 Métricas Resumidas
    st.header("📊 Métricas Resumidas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_value = filtered_df['Value'].sum()
        st.metric("Total Geral", f"€{total_value:.2f}")
    
    with col2:
        st.metric("Número de Registos", len(filtered_df))
    
    with col3:
        avg_value = filtered_df['Value'].mean()
        st.metric("Média por Registo", f"€{avg_value:.2f}")
    
    with col4:
        max_value = filtered_df['Value'].max()
        st.metric("Valor Máximo", f"€{max_value:.2f}")
    
    # Detalhes por Matrícula (se houver múltiplas)
    if selected_matricula == "Todas" and len(matriculas) > 1:
        st.subheader("📋 Detalhes por Matrícula")
        
        matricula_summary = filtered_df.groupby('Matricula').agg({
            'Value': ['sum', 'count', 'mean']
        }).round(2)
        
        matricula_summary.columns = ['Total', 'Nº Registos', 'Média']
        st.dataframe(matricula_summary)
        
else:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")

# ℹ️ Informações sobre os dados
with st.expander("ℹ️ Informações sobre os dados"):
    st.write(f"**Período total dos dados:** {df['Ano'].min()} - {df['Ano'].max()}")
    st.write(f"**Matrículas disponíveis:** {', '.join(map(str, matriculas))}")
    st.write(f"**Total de registos no dataset:** {len(df)}")
    st.write(f"**Período coberto:** {df['Month'].nunique()} meses")
