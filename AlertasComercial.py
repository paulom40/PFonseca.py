import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
import unicodedata
from datetime import datetime, timedelta
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="Customer KPI Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM STYLING WITH VIBRANT COLORS AND GRADIENTS ---
st.markdown("""
    <style>
    /* Enhanced with vibrant colors, gradients, and better visual hierarchy */
    .main { background: linear-gradient(135deg, #0f0f1e 0%, #1a0f2e 100%); color: #e0e0e0; }
    .stApp { background: linear-gradient(135deg, #0f0f1e 0%, #1a0f2e 100%); }
    
    h1 { 
        color: #00d4ff; 
        font-weight: 800; 
        font-size: 2.5em;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        margin-bottom: 20px;
    }
    h2 { 
        background: linear-gradient(135deg, #ff006e 0%, #8338ec 50%, #3a86ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        margin-top: 30px;
    }
    h3 { 
        color: #00f5ff; 
        font-weight: 700;
    }
    
    /* Metric cards with vibrant gradients */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a0f2e 0%, #2d0f4e 100%);
        border: 2px solid rgba(0, 212, 255, 0.3);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a15 0%, #1a0f2e 100%);
        border-right: 2px solid rgba(0, 212, 255, 0.2);
    }
    
    .stRadio label, .stSelectbox label, .stMultiSelect label { 
        font-weight: 700; 
        color: #00f5ff;
        font-size: 1.05em;
    }
    
    /* Selectbox styling */
    [data-testid="stSelectbox"] {
        background: linear-gradient(135deg, #1a0f2e 0%, #2d0f4e 100%);
        border-radius: 8px;
    }
    
    /* Download button with vibrant gradient */
    .stDownloadButton button { 
        background: linear-gradient(135deg, #ff006e 0%, #8338ec 50%, #3a86ff 100%);
        color: white; 
        border: none; 
        border-radius: 8px; 
        font-weight: 700;
        padding: 12px 24px;
        box-shadow: 0 4px 15px rgba(255, 0, 110, 0.4);
        transition: all 0.3s ease;
    }
    
    .stDownloadButton button:hover {
        box-shadow: 0 8px 25px rgba(255, 0, 110, 0.6);
        transform: translateY(-2px);
    }
    
    /* Text input styling */
    .stTextInput input {
        background: linear-gradient(135deg, #1a0f2e 0%, #2d0f4e 100%);
        color: #00f5ff;
        border: 2px solid rgba(0, 212, 255, 0.3);
        border-radius: 8px;
    }
    
    /* Info/Warning/Error box styling */
    .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 10px;
        padding: 15px;
        font-weight: 600;
    }
    
    /* Divider styling */
    hr {
        border: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.3), transparent);
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
month_names_to_number = {
    'janeiro': 1, 'february': 2, 'março': 3, 'abril': 4,
    'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
    'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
    # English versions as backup
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
    # Uppercase versions
    'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
    'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
    'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
}

@st.cache_data
def carregar_dados():
    try:
        url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx"
        
        response = requests.get(url, timeout=15, allow_redirects=True)
        
        if response.status_code != 200:
            st.error(f"❌ GitHub returned status {response.status_code}. File may not exist or be inaccessible.")
            return pd.DataFrame()
        
        df = pd.read_excel(BytesIO(response.content))
        
        original_columns = df.columns.tolist()
        
        col_map = {}
        
        # Define column mappings with exact matches first (to handle accents properly)
        col_mappings = {
            'Mês': 'mes',
            'mes': 'mes',
            'MÊS': 'mes',
            'Qtd.': 'qtd',
            'Qtd': 'qtd',
            'qtd': 'qtd',
            'QTD': 'qtd',
            'Quantidade': 'qtd',
            'quantidade': 'qtd',
            'Ano': 'ano',
            'ano': 'ano',
            'ANO': 'ano',
            'Cliente': 'cliente',
            'cliente': 'cliente',
            'CLIENTE': 'cliente',
            'Comercial': 'comercial',
            'comercial': 'comercial',
            'COMERCIAL': 'comercial',
            'V. Líquido': 'v_liquido',
            'V_Liquido': 'v_liquido',
            'V Liquido': 'v_liquido',
            'V. LÍQUIDO': 'v_liquido',
            'PM': 'pm',
            'pm': 'pm',
            'Preço Médio': 'pm',
            'Preco Medio': 'pm',
            'Categoria': 'categoria',
            'categoria': 'categoria',
            'CATEGORIA': 'categoria',
            'Artigo': 'artigo',
            'artigo': 'artigo',
            'ARTIGO': 'artigo',
            'Código': 'codigo',
            'codigo': 'codigo',
            'CODIGO': 'codigo',
            'UN': 'un',
            'un': 'un',
            'Unidade': 'un',
            'unidade': 'un'
        }
        
        # First pass - exact matches
        for original_col in original_columns:
            if original_col in col_mappings:
                col_map[original_col] = col_mappings[original_col]
        
        # Rename columns with mapping
        df = df.rename(columns=col_map)
        
        # Check for critical columns
        critical_cols = ['mes', 'qtd', 'ano', 'cliente', 'comercial']
        missing_cols = [col for col in critical_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ Missing critical columns after mapping: {missing_cols}")
            st.error(f"✓ Available columns: {df.columns.tolist()}")
            st.error(f"📋 Original columns from file: {original_columns}")
            return pd.DataFrame()
        
        # Check if mes column contains strings (month names) instead of numbers
        if df['mes'].dtype == 'object':
            def convert_month_name_to_number(month_str):
                if pd.isna(month_str):
                    return np.nan
                month_str = str(month_str).strip()
                return month_names_to_number.get(month_str, np.nan)
            
            df['mes'] = df['mes'].apply(convert_month_name_to_number)
        else:
            # Already numeric, just ensure it's int
            df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
        
        # Convert other numeric columns
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')
        if 'v_liquido' in df.columns:
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')
        if 'pm' in df.columns:
            df['pm'] = pd.to_numeric(df['pm'], errors='coerce')
        
        # Remove rows where critical numeric columns are NaN
        df = df.dropna(subset=['mes', 'qtd', 'ano'])
        
        # Filter to valid months (1-12)
        df = df[(df['mes'] >= 1) & (df['mes'] <= 12)]
        
        # Remove rows where cliente or comercial are completely empty
        df = df.dropna(subset=['cliente', 'comercial'], how='any')
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return pd.DataFrame()

df = carregar_dados()

if df.empty:
    st.error("❌ Failed to load data. Please check:")
    st.info("1. GitHub URL is correct")
    st.info("2. File 'Vendas_Globais.xlsx' exists in the main branch")
    st.info("3. Your internet connection is active")
    st.stop()

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("# 📊 Painel KPI")
st.sidebar.markdown("---")

pagina = st.sidebar.radio("Navegar", [
    "📈 Visão Geral", 
    "🎯 KPIs Personalizados", 
    "📉 Tendências", 
    "⚠️ Alertas",
    "👥 Análise de Clientes",
    "📊 Vista Comparativa"
])

# --- FILTERS WITH CASCADING LOGIC ---
st.sidebar.markdown("### 🔍 Filtros")
dados_base = df.copy()

# Initialize session state for filters
if 'ano_filter' not in st.session_state:
    st.session_state.ano_filter = "All"
if 'comercial_filter' not in st.session_state:
    st.session_state.comercial_filter = "All"
if 'cliente_filter' not in st.session_state:
    st.session_state.cliente_filter = "All"

# Get available options based on current filters
def get_filtro_opcoes(dados, ano, comercial):
    temp = dados.copy()
    
    # Filter by year
    if ano != "All" and ano != "Todos":
        try:
            temp = temp[temp['ano'] == int(ano)]
        except (ValueError, TypeError):
            pass  # If conversion fails, keep all data
    
    # Filter by commercial
    if comercial != "All" and comercial != "Todos":
        temp = temp[temp['comercial'].astype(str) == str(comercial)]
    
    anos = sorted([int(x) for x in temp['ano'].dropna().unique()])
    comerciais = sorted(list(temp['comercial'].dropna().unique()))
    clientes = sorted(list(temp['cliente'].dropna().unique()))
    
    return anos, comerciais, clientes

anos_disponiveis, comerciais_disponiveis, clientes_disponiveis = get_filtro_opcoes(dados_base, "All", "All")

# Year filter
ano = st.sidebar.selectbox(
    "Ano", 
    ["Todos"] + anos_disponiveis, 
    key="year_select"
)

# Commercial filter (updates based on year)
_, comerciais_for_year, _ = get_filtro_opcoes(dados_base, ano, "All")
comercial = st.sidebar.selectbox(
    "Comercial", 
    ["Todos"] + comerciais_for_year, 
    key="commercial_select"
)

# Customer filter (updates based on year and commercial)
_, _, clientes_for_filters = get_filtro_opcoes(dados_base, ano, comercial)
cliente = st.sidebar.selectbox(
    "Cliente", 
    ["Todos"] + clientes_for_filters, 
    key="customer_select"
)

# Apply filters to data
def aplicar_filtros(dados, ano, comercial, cliente):
    resultado = dados.copy()
    if ano != "Todos":
        resultado = resultado[resultado['ano'] == int(ano)]
    if comercial != "Todos":
        resultado = resultado[resultado['comercial'].astype(str) == str(comercial)]
    if cliente != "Todos":
        resultado = resultado[resultado['cliente'].astype(str) == str(cliente)]
    return resultado

dados_filtrados = aplicar_filtros(dados_base, ano, comercial, cliente)

# --- FUNCTION: EXPORT EXCEL ---
def gerar_excel(dados):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dados.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

# --- VIBRANT COLOR SCHEMES ---
color_scale_primary = ['#ff006e', '#8338ec', '#3a86ff', '#06ffa5', '#ffbe0b']
color_scale_gradient = 'Viridis'
template_chart = 'plotly_dark'

month_names_pt = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

# --- PAGE 1: OVERVIEW ---
if pagina == "📈 Visão Geral":
    st.title("📊 Painel KPI - Visão Geral")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_qty = dados_filtrados['qtd'].sum()
    total_value = dados_filtrados['v_liquido'].sum()
    num_customers = dados_filtrados['cliente'].nunique()
    num_commercials = dados_filtrados['comercial'].nunique()
    
    col1.metric("📦 Quantidade Total", f"{total_qty:,.0f}")
    col2.metric("💰 Valor Total", f"€ {total_value:,.0f}")
    col3.metric("👥 Clientes Únicos", f"{num_customers}")
    col4.metric("🧑‍💼 Comerciais Ativos", f"{num_commercials}")
    
    st.markdown("---")
    
    # KPI by Customer
    st.subheader("🏆 Top 10 Clientes por Quantidade")
    top_clientes = dados_filtrados.groupby('cliente')[['qtd', 'v_liquido']].sum().sort_values('qtd', ascending=False).head(10)
    top_clientes['Quota %'] = (top_clientes['qtd'] / top_clientes['qtd'].sum() * 100).round(2)
    
    fig_top = px.bar(
        top_clientes.reset_index(),
        x='cliente',
        y='qtd',
        color='v_liquido',
        title='Top 10 Clientes por Quantidade',
        labels={'qtd': 'Quantidade', 'cliente': 'Cliente', 'v_liquido': 'Valor (€)'},
        color_continuous_scale='Turbo'
    )
    fig_top.update_layout(template=template_chart, showlegend=True, hovermode='x unified')
    st.plotly_chart(fig_top, use_container_width=True)
    
    # KPI by Commercial
    st.subheader("🧑‍💼 Desempenho por Comercial")
    kpi_comercial = dados_filtrados.groupby('comercial')[['qtd', 'v_liquido']].sum().sort_values('qtd', ascending=False)
    
    fig_comercial = px.bar(
        kpi_comercial.reset_index(),
        x='comercial',
        y='qtd',
        color='v_liquido',
        title='Quantidade por Comercial',
        color_continuous_scale='Plasma'
    )
    fig_comercial.update_layout(template=template_chart, showlegend=True)
    st.plotly_chart(fig_comercial, use_container_width=True)
    
    # Data Table
    st.subheader("📋 Dados Detalhados")
    st.dataframe(dados_filtrados, use_container_width=True)
    st.download_button("📥 Exportar Dados", data=gerar_excel(dados_filtrados), file_name="kpi_data.xlsx")

# --- PAGE 2: CUSTOM KPIs ---
elif pagina == "🎯 KPIs Personalizados":
    st.title("🎯 Criador de KPIs Personalizados")
    
    st.markdown("### Criar KPIs Personalizados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        kpi_name = st.text_input("Nome do KPI", value="Crescimento de Receita")
        st.info("📊 KPI apresenta desempenho mensal (Soma de Quantidade)")
    
    with col2:
        kpi_period = st.selectbox("Período", ["Mensal", "Trimestral", "Anual"])
        show_trend = st.checkbox("Mostrar Linha de Tendência", value=True)
    
    if dados_filtrados.empty:
        st.warning("⚠️ Sem dados disponíveis para os filtros selecionados. Ajuste seus filtros.")
    else:
        # Prepare KPI data - always sum qtd by month
        kpi_data = dados_filtrados.groupby('mes')['qtd'].sum().reset_index()
        kpi_data.columns = ['mes', 'value']
        kpi_data = kpi_data.sort_values('mes')
        kpi_data['month_name'] = kpi_data['mes'].map(month_names_pt)
        
        # Display KPI with vibrant colors
        fig_kpi = px.bar(
            kpi_data,
            x='month_name',
            y='value',
            title=f"Desempenho Mensal - {kpi_name}",
            labels={'value': 'Quantidade (Soma)', 'month_name': 'Mês'},
            color='value',
            text='value',
            color_continuous_scale='Rainbow'
        )
        fig_kpi.update_traces(textposition='outside', textfont=dict(color='#00f5ff'))
        fig_kpi.update_layout(template=template_chart, showlegend=False, xaxis_title="Mês", yaxis_title="Quantidade (Soma)")
        st.plotly_chart(fig_kpi, use_container_width=True)
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🔝 Máximo", f"{kpi_data['value'].max():,.0f}")
        col2.metric("📉 Mínimo", f"{kpi_data['value'].min():,.0f}")
        col3.metric("📊 Média", f"{kpi_data['value'].mean():,.2f}")
        col4.metric("📈 Mediana", f"{kpi_data['value'].median():,.2f}")
        
        # Data Table
        st.subheader("📋 Dados de KPI Mensal")
        st.dataframe(kpi_data[['month_name', 'value']], use_container_width=True)

# --- PAGE 3: TRENDS ---
elif pagina == "📉 Tendências":
    st.title("📉 Análise de Tendências")
    
    col1, col2 = st.columns(2)
    
    with col1:
        trend_metric = "Quantidade"
        st.selectbox("Selecionar Métrica", ["Quantidade"], disabled=True)
        trend_groupby = st.selectbox("Agrupar Por", ["mês"], disabled=True)
    
    with col2:
        trend_window = st.slider("Média Móvel (meses)", 1, 12, 3)
    
    # Check if filtered data is empty
    if dados_filtrados.empty:
        st.warning("⚠️ Sem dados disponíveis para os filtros selecionados. Ajuste seus filtros.")
    else:
        # Prepare trend data - always sum qtd by month
        trend_data = dados_filtrados.groupby('mes')['qtd'].sum().reset_index()
        trend_data.columns = ['mes', 'value']
        trend_data = trend_data.sort_values('mes')
        trend_data['month_name'] = trend_data['mes'].map(month_names_pt)
        
        # Check if trend_data has at least 2 rows
        if len(trend_data) < 2:
            st.warning("⚠️ Dados insuficientes para análise de tendências. São necessários pelo menos 2 pontos de dados.")
        else:
            # Add moving average
            trend_data['MA'] = trend_data['value'].rolling(window=trend_window, center=True).mean()
            
            # Plot trend with vibrant colors
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=trend_data['month_name'],
                y=trend_data['value'],
                mode='lines+markers',
                name='Real',
                line=dict(color='#ff006e', width=3),
                marker=dict(size=8, color='#ff006e'),
                fill='tozeroy',
                fillcolor='rgba(255, 0, 110, 0.1)',
                text=trend_data['value'].astype(str),
                textposition='top center',
                textfont=dict(color='#ff006e')
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=trend_data['month_name'],
                y=trend_data['MA'],
                mode='lines',
                name=f'MM({trend_window})',
                line=dict(color='#00f5ff', width=2, dash='dash')
            ))
            
            fig_trend.update_layout(
                title=f"Tendência Mensal - Soma de Quantidade",
                xaxis_title="Mês",
                yaxis_title="Quantidade (Soma)",
                hovermode='x unified',
                template=template_chart
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Trend Statistics
            st.subheader("📊 Estatísticas de Tendência")
            col1, col2, col3, col4 = st.columns(4)
            
            current_value = trend_data['value'].iloc[-1]
            previous_value = trend_data['value'].iloc[-2] if len(trend_data) > 1 else trend_data['value'].iloc[0]
            
            if trend_data['value'].iloc[0] != 0:
                trend_pct_change = ((current_value - trend_data['value'].iloc[0]) / trend_data['value'].iloc[0] * 100)
            else:
                trend_pct_change = 0
            
            trend_direction = "📈 Subida" if trend_pct_change > 0 else "📉 Descida" if trend_pct_change < 0 else "➡️ Estável"
            
            col1.metric("Mês Atual", f"{current_value:,.0f}")
            col2.metric("Mês Anterior", f"{previous_value:,.0f}")
            col3.metric("% Mudança", f"{trend_pct_change:+.1f}%")
            col4.metric("Tendência", trend_direction)
            
            # Display trend data table with month names
            st.subheader("📋 Dados de Tendência Mensal")
            display_trend = trend_data[['month_name', 'value', 'MA']].rename(columns={'month_name': 'Mês', 'value': 'Quantidade', 'MA': 'Média Móvel'})
            st.dataframe(display_trend, use_container_width=True)

# --- PAGE 4: ALERTS ---
elif pagina == "⚠️ Alertas":
    st.title("⚠️ Sistema de Alertas")
    
    st.markdown("### Alertas de Desempenho")
    
    # Customer Performance Analysis
    analise_clientes = dados_filtrados.groupby('cliente').agg({
        'qtd': ['sum', 'mean', 'count'],
        'v_liquido': 'sum'
    }).reset_index()
    
    analise_clientes.columns = ['Cliente', 'Total_Qtd', 'Avg_Qtd', 'Transactions', 'Total_Value']
    analise_clientes = analise_clientes.sort_values('Total_Qtd', ascending=False)
    
    media_geral = dados_filtrados['qtd'].mean()
    
    analise_clientes['Status'] = analise_clientes['Avg_Qtd'].apply(
        lambda x: '🟢 Excelente' if x >= media_geral else '🟡 Atenção' if x >= media_geral * 0.7 else '🔴 Crítico'
    )
    
    col1, col2, col3 = st.columns(3)
    
    excellent = len(analise_clientes[analise_clientes['Status'] == '🟢 Excelente'])
    warning = len(analise_clientes[analise_clientes['Status'] == '🟡 Atenção'])
    critical = len(analise_clientes[analise_clientes['Status'] == '🔴 Crítico'])
    
    col1.metric("🟢 Excelente", excellent)
    col2.metric("🟡 Atenção", warning)
    col3.metric("🔴 Crítico", critical)
    
    st.markdown("---")
    
    st.subheader("📋 Relatório de Estado do Cliente")
    st.dataframe(analise_clientes, use_container_width=True)
    
    # Critical Customers
    st.subheader("🔴 Alertas Críticos de Clientes")
    criticos = analise_clientes[analise_clientes['Status'] == '🔴 Crítico']
    if not criticos.empty:
        st.error(f"⚠️ {len(criticos)} clientes precisam de atenção imediata!")
        st.dataframe(criticos, use_container_width=True)
    else:
        st.success("✅ Sem alertas críticos!")
    
    st.markdown("---")
    
    # Customers with Purchase Gaps (Don't Buy Every Month)
    st.subheader("📅 Clientes com Lacunas de Compra (Não compram todo mês)")
    
    if not dados_filtrados.empty:
        # Get unique months in dataset
        unique_months = sorted(dados_filtrados['mes'].unique())
        expected_months = set(unique_months)
        
        # Check which customers bought in every month
        customer_months = dados_filtrados.groupby('cliente')['mes'].apply(lambda x: set(x.unique())).reset_index()
        customer_months.columns = ['cliente', 'months_purchased']
        
        # Find customers with gaps (not all months)
        customer_months['months_missing'] = customer_months['months_purchased'].apply(
            lambda x: expected_months - x
        )
        customer_months['gap_count'] = customer_months['months_missing'].apply(len)
        customer_months['purchase_frequency'] = customer_months['months_purchased'].apply(len)
        customer_months['total_expected_months'] = len(expected_months)
        
        # Filter only customers with gaps
        customers_with_gaps = customer_months[customer_months['gap_count'] > 0].copy()
        customers_with_gaps = customers_with_gaps.sort_values('gap_count', ascending=False)
        
        if not customers_with_gaps.empty:
            display_gaps = customers_with_gaps[['cliente', 'purchase_frequency', 'gap_count', 'total_expected_months', 'months_missing']].copy()
            display_gaps.columns = ['Cliente', 'Meses Comprados', 'Meses com Lacuna', 'Meses Esperados', 'Meses em Falta']
            
            # Calculate gap percentage
            display_gaps['% Lacuna'] = (display_gaps['Meses com Lacuna'] / display_gaps['Meses Esperados'] * 100).round(1)
            
            def safe_convert_month_pt(x):
                if not isinstance(x, set) or len(x) == 0:
                    return 'N/A'
                
                try:
                    month_list = []
                    for m in sorted(list(x)):
                        try:
                            month_num = int(float(m))
                            month_list.append(month_names_pt.get(month_num, f'Mês {month_num}'))
                        except (ValueError, TypeError):
                            month_list.append(f'Mês {m}')
                    return ', '.join(month_list)
                except Exception as e:
                    return 'Erro ao ler meses'
            
            display_gaps['Nomes dos Meses em Falta'] = display_gaps['Meses em Falta'].apply(safe_convert_month_pt)
            
            # Format final display table with percentage as primary column
            final_display = display_gaps[['Cliente', 'Meses Comprados', 'Meses Esperados', '% Lacuna', 'Nomes dos Meses em Falta']].copy()
            final_display = final_display.sort_values('% Lacuna', ascending=False)
            
            # Show summary metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Clientes com Lacunas", len(customers_with_gaps))
            col2.metric("% de Lacuna Média", f"{(customers_with_gaps['gap_count'].mean() / len(expected_months) * 100):.1f}%")
            col3.metric("% de Lacuna Máx.", f"{(customers_with_gaps['gap_count'].max() / len(expected_months) * 100):.1f}%")
            
            # Display alert table
            st.warning(f"⚠️ {len(customers_with_gaps)} clientes não compraram em todos os meses!")
            st.dataframe(final_display, use_container_width=True)
            
            # Export gaps report
            st.download_button(
                "📥 Exportar Relatório de Lacunas", 
                data=gerar_excel(final_display), 
                file_name="customers_with_gaps.xlsx"
            )
        else:
            st.success("✅ Todos os clientes estão a comprar todos os meses!")
    
    st.markdown("---")

# --- PAGE 5: CUSTOMER ANALYSIS ---
elif pagina == "👥 Análise de Clientes":
    st.title("👥 Análise de Clientes")
    
    if cliente == "Todos":
        st.info("👈 Selecione um cliente específico no painel lateral")
    else:
        cliente_data = dados_filtrados[dados_filtrados['cliente'] == cliente]
        
        if cliente_data.empty:
            st.warning("Não disponível")
        else:
            # Customer Summary
            st.subheader(f"📊 Perfil do Cliente: {cliente}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Quantidade Total", f"{cliente_data['qtd'].sum():,.0f}")
            col2.metric("Valor Total", f"€ {cliente_data['v_liquido'].sum():,.0f}")
            col3.metric("Média por Transação", f"{cliente_data['qtd'].mean():,.2f}")
            col4.metric("Transações", len(cliente_data))
            
            st.subheader("📈 Tendência do Cliente - Desempenho Mensal")
            
            # Create a date key for proper chronological sorting with month on x-axis
            historico = cliente_data.groupby(['ano', 'mes']).agg({'qtd': 'sum'}).reset_index()
            historico['period'] = historico['ano'].astype(str) + '-' + historico['mes'].astype(str).str.zfill(2)
            historico['month_name'] = historico['mes'].map(month_names_pt)
            historico = historico.sort_values(['ano', 'mes'])
            
            fig_historico = px.line(
                historico,
                x='month_name',
                y='qtd',
                markers=True,
                title=f"Desempenho Mensal (Soma de Quantidade) - {cliente}",
                labels={'qtd': 'Quantidade (Soma)', 'month_name': 'Mês'},
                color_discrete_sequence=['#00f5ff'],
                text='qtd'
            )
            fig_historico.update_traces(textposition='top center', textfont=dict(color='#00f5ff', size=10))
            fig_historico.update_layout(
                template=template_chart,
                hovermode='x unified',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_historico, use_container_width=True)
            
            st.subheader("🔄 vs. Média do Mercado - Comparação Mensal")
            
            # Get market average for all customers in the filtered dataset
            media_mercado = dados_filtrados.groupby(['ano', 'mes']).agg({'qtd': 'sum'}).reset_index()
            media_mercado['month_name'] = media_mercado['mes'].map(month_names_pt)
            media_mercado = media_mercado.sort_values(['ano', 'mes'])
            media_mercado = media_mercado.rename(columns={'qtd': 'market_qtd'})
            
            # Merge to align periods by month name
            historico_display = historico[['month_name', 'qtd']].rename(columns={'qtd': 'Cliente'})
            comparison_data = historico_display.merge(
                media_mercado[['month_name', 'market_qtd']].rename(columns={'market_qtd': 'Média do Mercado'}),
                on='month_name',
                how='outer'
            ).fillna(0)
            
            fig_comp = go.Figure()
            
            # Customer line
            fig_comp.add_trace(go.Scatter(
                x=comparison_data['month_name'], 
                y=comparison_data['Cliente'], 
                mode='lines+markers', 
                name=cliente, 
                line=dict(color='#ff006e', width=3),
                marker=dict(size=8),
                text=comparison_data['Cliente'].astype(str),
                textposition='top center'
            ))
            
            # Market average line
            fig_comp.add_trace(go.Scatter(
                x=comparison_data['month_name'], 
                y=comparison_data['Média do Mercado'], 
                mode='lines+markers', 
                name='Média do Mercado', 
                line=dict(color='#00f5ff', width=2, dash='dash'),
                marker=dict(size=6),
                text=comparison_data['Média do Mercado'].astype(str),
                textposition='bottom center'
            ))
            
            fig_comp.update_layout(
                title="Desempenho Mensal: Cliente vs Média do Mercado (Soma de Quantidade)", 
                xaxis_title="Mês", 
                yaxis_title="Quantidade (Soma)", 
                hovermode='x unified', 
                template=template_chart,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Display comparison metrics
            st.subheader("📊 Comparação de Desempenho")
            comp_metrics = pd.DataFrame({
                'Métrica': ['Quantidade Total', 'Média Mensal', 'Melhor Mês', 'Pior Mês'],
                cliente: [
                    f"{historico['qtd'].sum():,.0f}",
                    f"{historico['qtd'].mean():,.0f}",
                    f"{historico['qtd'].max():,.0f}",
                    f"{historico['qtd'].min():,.0f}"
                ],
                'Média do Mercado': [
                    f"{media_mercado['market_qtd'].sum():,.0f}",
                    f"{media_mercado['market_qtd'].mean():,.0f}",
                    f"{media_mercado['market_qtd'].max():,.0f}",
                    f"{media_mercado['market_qtd'].min():,.0f}"
                ]
            })
            st.dataframe(comp_metrics, use_container_width=True)
            
            # Data
            st.subheader("📋 Dados Detalhados do Cliente")
            st.dataframe(cliente_data, use_container_width=True)

# --- PAGE 6: COMPARATIVE VIEW ---
else:
    st.title("📊 Análise Comparativa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        comp_metric1 = st.selectbox("Métrica 1", ["qtd", "v_liquido", "pm"])
        comp_groupby1 = st.selectbox("Agrupar Por 1", ["cliente", "comercial", "categoria"])
    
    with col2:
        comp_top = st.slider("Top N Itens", 5, 20, 10)
    
    # Get top items
    top_items = dados_filtrados.groupby(comp_groupby1)[comp_metric1].sum().nlargest(comp_top)
    
    # Create comparative visualizations with vibrant colors
    fig_comp = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "bar"}, {"type": "pie"}]],
        subplot_titles=("Gráfico de Barras", "Gráfico de Pizza")
    )
    
    fig_comp.add_trace(
        go.Bar(
            x=top_items.index, 
            y=top_items.values, 
            marker=dict(color=top_items.values, colorscale='Rainbow'),
            name=comp_metric1
        ),
        row=1, col=1
    )
    
    fig_comp.add_trace(
        go.Pie(labels=top_items.index, values=top_items.values, name=comp_metric1),
        row=1, col=2
    )
    
    fig_comp.update_layout(height=500, showlegend=False, template=template_chart)
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Statistics
    st.subheader("📈 Estatísticas Comparativas")
    comp_stats = pd.DataFrame({
        comp_groupby1: top_items.index,
        comp_metric1: top_items.values,
        'Quota %': (top_items.values / top_items.sum() * 100).round(2)
    })
    
    st.dataframe(comp_stats, use_container_width=True)
    st.download_button("📥 Exportar Análise", data=gerar_excel(comp_stats), file_name="comparative_analysis.xlsx")
