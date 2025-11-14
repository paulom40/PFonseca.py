import streamlit as st
import pandas as pd
import altair as alt

# Configuração da página
st.set_page_config(
    page_title="Via Verde Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para aparência moderna
st.markdown("""
<style>
    /* Ocultar menu, header e footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Estilos modernos */
    .main {
        background-color: #f8f9fa;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-left: 5px solid #667eea;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .filter-section {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
    }
    
    .stSelectbox, .stMultiselect {
        border-radius: 10px;
    }
    
    .stDataFrame {
        border-radius: 10px;
    }
    
    h1, h2, h3 {
        color: white !important;
        font-weight: 600 !important;
    }
    
    .stExpander {
        border-radius: 10px !important;
    }
    
    .stExpander > div {
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# 📂 Carregar Excel do GitHub
file_url = "https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx"

# 🔷 Header moderno
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='color: white; font-size: 2.5em; margin-bottom: 10px;'>🚗 Via Verde Dashboard</h1>
        <p style='color: white; font-size: 1.2em;'>Análise Inteligente de Portagens</p>
    </div>
    """, unsafe_allow_html=True)

# 📊 Carregar e validar dados
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(file_url)
        df = df.drop(columns=['Mês'], errors='ignore')
        return df, True
    except Exception as e:
        st.error(f"❌ Erro ao carregar o arquivo: {e}")
        return None, False

df, success = load_data()

if not success:
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

# 🔍 Seção de Filtros
st.markdown('<div class="filter-section">', unsafe_allow_html=True)

st.markdown("### 🔍 Filtros Avançados")
st.markdown("Selecione os critérios para análise dos dados:")

col1, col2, col3, col4 = st.columns([2, 2, 3, 2])

with col1:
    matriculas = sorted(df['Matricula'].unique())
    selected_matricula = st.selectbox(
        "**Matrícula**", 
        ["Todas"] + matriculas,
        help="Selecione uma matrícula específica ou 'Todas'"
    )

with col2:
    anos = sorted(df['Ano'].unique())
    selected_ano = st.selectbox(
        "**Ano**", 
        ["Todos"] + anos,
        help="Filtrar por ano específico"
    )

with col3:
    months_available = sorted(df['Month'].unique(), key=lambda x: [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ].index(x))
    selected_months = st.multiselect(
        "**Mês**", 
        months_available, 
        default=months_available,
        help="Selecione um ou mais meses"
    )
    
with col4:
    dias = sorted(df['Dia'].unique())
    selected_dias = st.multiselect(
        "**Dia**", 
        ["Todos"] + dias, 
        default=["Todos"],
        help="Filtrar por dias específicos do mês"
    )

st.markdown('</div>', unsafe_allow_html=True)

# Aplicar filtros
filtered_df = df.copy()

if selected_matricula != "Todas":
    filtered_df = filtered_df[filtered_df['Matricula'] == selected_matricula]

if selected_ano != "Todos":
    filtered_df = filtered_df[filtered_df['Ano'].astype(str) == str(selected_ano)]

if selected_months:
    filtered_df = filtered_df[filtered_df['Month'].isin(selected_months)]

if "Todos" not in selected_dias:
    filtered_df = filtered_df[filtered_df['Dia'].isin(selected_dias)]

# 📊 Métricas em tempo real
if not filtered_df.empty:
    total_value = filtered_df['Value'].sum()
    total_records = len(filtered_df)
    avg_value = filtered_df['Value'].mean()
    max_value = filtered_df['Value'].max()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>💰 Total Gasto</h3>
            <h2>€{total_value:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);'>
            <h3>📊 Total de Registos</h3>
            <h2>{total_records:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);'>
            <h3>📈 Média por Registo</h3>
            <h2>€{avg_value:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #fdbb2d 0%, #22c1c3 100%);'>
            <h3>🎯 Valor Máximo</h3>
            <h2>€{max_value:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

# 📈 Visualizações
if not filtered_df.empty:
    st.markdown("---")
    
    # Gráfico 1: Valor Total por Mês
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📅 Valor Total por Mês")
    
    month_order = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    
    chart_df_month = filtered_df.groupby("Month")["Value"].sum().reset_index()
    all_months_df = pd.DataFrame({'Month': month_order})
    chart_df_month = all_months_df.merge(chart_df_month, on='Month', how='left').fillna(0)
    
    bar_chart = alt.Chart(chart_df_month).mark_bar(
        color='linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        cornerRadiusTop=5,
        cornerRadiusBottom=5
    ).encode(
        x=alt.X('Month:O', title='Mês', sort=month_order, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Value:Q', title='Valor Total (€)'),
        tooltip=['Month', alt.Tooltip('Value:Q', title='Valor (€)', format='.2f')]
    ).properties(height=400)
    
    bar_labels = alt.Chart(chart_df_month[chart_df_month['Value'] > 0]).mark_text(
        align='center', 
        baseline='bottom', 
        fontWeight='bold', 
        color='#2c3e50',
        dy=-8,
        fontSize=12
    ).encode(
        x=alt.X('Month:O', sort=month_order),
        y='Value:Q',
        text=alt.Text('Value:Q', format='.2f')
    )
    
    st.altair_chart(bar_chart + bar_labels, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráfico 2 e Tabela
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📈 Tendência por Dia")
        
        chart_df_day = filtered_df.groupby("Dia")["Value"].sum().reset_index().sort_values("Dia")
        
        area_chart = alt.Chart(chart_df_day).mark_area(
            color='linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
            opacity=0.7
        ).encode(
            x=alt.X('Dia:O', title='Dia do Mês'),
            y=alt.Y('Value:Q', title='Valor Total (€)'),
            tooltip=['Dia', alt.Tooltip('Value:Q', title='Valor (€)', format='.2f')]
        ).properties(height=300)
        
        st.altair_chart(area_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📋 Dados Filtrados")
        
        # Mostrar apenas as colunas principais
        display_df = filtered_df[['Matricula', 'Date', 'Month', 'Dia', 'Value']].copy()
        display_df['Value'] = display_df['Value'].map('€{:.2f}'.format)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=350
        )
        
        st.markdown(f"**Total de registos:** {len(filtered_df)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detalhes por Matrícula
    if selected_matricula == "Todas" and len(matriculas) > 1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🚗 Análise por Matrícula")
        
        matricula_summary = filtered_df.groupby('Matricula').agg({
            'Value': ['sum', 'count', 'mean', 'max']
        }).round(2)
        
        matricula_summary.columns = ['Total (€)', 'Nº Registos', 'Média (€)', 'Máximo (€)']
        matricula_summary['Total (€)'] = matricula_summary['Total (€)'].map('€{:.2f}'.format)
        matricula_summary['Média (€)'] = matricula_summary['Média (€)'].map('€{:.2f}'.format)
        matricula_summary['Máximo (€)'] = matricula_summary['Máximo (€)'].map('€{:.2f}'.format)
        
        st.dataframe(matricula_summary, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning("""
    <div style='background: #fff3cd; color: #856404; padding: 20px; border-radius: 10px; border-left: 5px solid #ffc107;'>
        <h4 style='margin: 0;'>⚠️ Nenhum dado encontrado</h4>
        <p style='margin: 10px 0 0 0;'>Tente ajustar os filtros para visualizar os dados.</p>
    </div>
    """, unsafe_allow_html=True)

# 📊 Informações do Dataset
with st.expander("📊 Informações do Dataset", expanded=False):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Período Total", f"{df['Ano'].min()} - {df['Ano'].max()}")
    
    with col2:
        st.metric("Matrículas Únicas", len(matriculas))
    
    with col3:
        st.metric("Total de Registos", f"{len(df):,}")
    
    st.write(f"**Meses cobertos:** {', '.join(sorted(df['Month'].unique()))}")
    st.write(f"**Faixa de dias:** {df['Dia'].min()} a {df['Dia'].max()}")
    st.write(f"**Valor total no dataset:** €{df['Value'].sum():,.2f}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 20px;'>
    <p>🚗 <strong>Via Verde Dashboard</strong> - Desenvolvido para análise inteligente de portagens</p>
</div>
""", unsafe_allow_html=True)
