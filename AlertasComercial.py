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
st.set_page_config(
    page_title="Customer KPI Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# --- PROFESSIONAL COLOR SCHEME ---
primary_color = "#1f77b4"  # Professional blue
secondary_color = "#2ca02c"  # Professional green
accent_color = "#ff7f0e"  # Professional orange
warning_color = "#d62728"  # Professional red
neutral_dark = "#2c3e50"
neutral_light = "#ecf0f1"
background_dark = "#0f1c2e"
sidebar_dark = "#1a2b3c"

# --- ENHANCED PROFESSIONAL STYLING ---
st.markdown(f"""
    <style>
    /* Professional Dark Theme with Refined Colors */
    .main {{ 
        background: linear-gradient(135deg, {background_dark} 0%, #1a2b3c 100%); 
        color: {neutral_light}; 
    }}
    .stApp {{ 
        background: linear-gradient(135deg, {background_dark} 0%, #1a2b3c 100%); 
    }}
    
    /* Professional Headers */
    h1 {{ 
        color: {primary_color}; 
        font-weight: 700; 
        font-size: 2.8em;
        border-bottom: 2px solid {primary_color};
        padding-bottom: 10px;
        margin-bottom: 25px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    h2 {{ 
        color: {secondary_color}; 
        font-weight: 600;
        font-size: 1.8em;
        margin-top: 30px;
        margin-bottom: 15px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    h3 {{ 
        color: {accent_color}; 
        font-weight: 600;
        font-size: 1.4em;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* Enhanced Metric Cards */
    [data-testid="metric-container"] {{
        background: linear-gradient(135deg, {sidebar_dark} 0%, #2c3e50 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }}
    
    [data-testid="metric-container"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
        border-color: {primary_color};
    }}
    
    /* Professional Sidebar */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {sidebar_dark} 0%, #2c3e50 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    /* Enhanced Form Elements */
    .stRadio label, .stSelectbox label, .stMultiSelect label {{ 
        font-weight: 600; 
        color: {neutral_light};
        font-size: 1.05em;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* Professional Selectbox */
    [data-testid="stSelectbox"] {{
        background: linear-gradient(135deg, {sidebar_dark} 0%, #2c3e50 100%);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    /* Enhanced Buttons */
    .stDownloadButton button {{ 
        background: linear-gradient(135deg, {primary_color} 0%, #2980b9 100%);
        color: white; 
        border: none; 
        border-radius: 8px; 
        font-weight: 600;
        padding: 12px 24px;
        box-shadow: 0 4px 15px rgba(31, 119, 180, 0.3);
        transition: all 0.3s ease;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    .stDownloadButton button:hover {{
        box-shadow: 0 6px 20px rgba(31, 119, 180, 0.5);
        transform: translateY(-2px);
        background: linear-gradient(135deg, #2980b9 0%, {primary_color} 100%);
    }}
    
    /* Professional Text Input */
    .stTextInput input {{
        background: linear-gradient(135deg, {sidebar_dark} 0%, #2c3e50 100%);
        color: {neutral_light};
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* Enhanced Dataframes */
    .dataframe {{
        border-radius: 10px;
        overflow: hidden;
    }}
    
    /* Professional Info/Warning/Error Boxes */
    .stInfo {{
        background: linear-gradient(135deg, {primary_color}15, {primary_color}25);
        border: 1px solid {primary_color}40;
        border-radius: 10px;
        padding: 15px;
        font-weight: 500;
    }}
    
    .stSuccess {{
        background: linear-gradient(135deg, {secondary_color}15, {secondary_color}25);
        border: 1px solid {secondary_color}40;
        border-radius: 10px;
        padding: 15px;
        font-weight: 500;
    }}
    
    .stWarning {{
        background: linear-gradient(135deg, {accent_color}15, {accent_color}25);
        border: 1px solid {accent_color}40;
        border-radius: 10px;
        padding: 15px;
        font-weight: 500;
    }}
    
    .stError {{
        background: linear-gradient(135deg, {warning_color}15, {warning_color}25);
        border: 1px solid {warning_color}40;
        border-radius: 10px;
        padding: 15px;
        font-weight: 500;
    }}
    
    /* Elegant Dividers */
    hr {{
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, {primary_color}40, transparent);
        margin: 30px 0;
    }}
    
    /* Metric Value Styling */
    [data-testid="metric-value"] {{
        font-size: 1.5em !important;
        font-weight: 700 !important;
        color: {neutral_light} !important;
    }}
    
    [data-testid="metric-label"] {{
        font-size: 1em !important;
        font-weight: 600 !important;
        color: {primary_color} !important;
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {sidebar_dark};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {primary_color};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: #2980b9;
    }}
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
month_names_to_number = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
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

# --- ENHANCED SIDEBAR NAVIGATION ---
st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: {primary_color}; margin: 0; font-size: 1.8em;">📊 KPI Dashboard</h1>
        <p style="color: {neutral_light}; opacity: 0.8; margin: 5px 0 0 0;">Business Intelligence</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

pagina = st.sidebar.radio("**Navegação**", [
    "📈 Visão Geral", 
    "🎯 KPIs Personalizados", 
    "📉 Tendências", 
    "⚠️ Alertas",
    "👥 Análise de Clientes",
    "📊 Vista Comparativa"
], key="navigation")

# --- ENHANCED FILTERS WITH PROFESSIONAL STYLING ---
st.sidebar.markdown(f"### 🔍 **Filtros**")
st.sidebar.markdown(f"<div style='color: {neutral_light}; opacity: 0.8; margin-bottom: 15px;'>Filtre os dados conforme necessário</div>", unsafe_allow_html=True)

dados_base = df.copy()

# Initialize session state for filters
if 'ano_filter' not in st.session_state:
    st.session_state.ano_filter = "All"
if 'comercial_filter' not in st.session_state:
    st.session_state.comercial_filter = "All"
if 'cliente_filter' not in st.session_state:
    st.session_state.cliente_filter = "All"
if 'categoria_filter' not in st.session_state:
    st.session_state.categoria_filter = "All"

# Get available options based on current filters
def get_filtro_opcoes(dados, ano, comercial, cliente):
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
    
    # Filter by customer
    if cliente != "All" and cliente != "Todos":
        temp = temp[temp['cliente'].astype(str) == str(cliente)]
    
    anos = sorted([int(x) for x in temp['ano'].dropna().unique()])
    comerciais = sorted(list(temp['comercial'].dropna().unique()))
    clientes = sorted(list(temp['cliente'].dropna().unique()))
    
    # Get categories if the column exists
    categorias = []
    if 'categoria' in temp.columns:
        categorias = sorted(list(temp['categoria'].dropna().unique()))
    
    return anos, comerciais, clientes, categorias

anos_disponiveis, comerciais_disponiveis, clientes_disponiveis, categorias_disponiveis = get_filtro_opcoes(dados_base, "All", "All", "All")

# Year filter
ano = st.sidebar.selectbox(
    "**Ano**", 
    ["Todos"] + anos_disponiveis, 
    key="year_select"
)

# Commercial filter (updates based on year)
_, comerciais_for_year, _, _ = get_filtro_opcoes(dados_base, ano, "All", "All")
comercial = st.sidebar.selectbox(
    "**Comercial**", 
    ["Todos"] + comerciais_for_year, 
    key="commercial_select"
)

# Customer filter (updates based on year and commercial)
_, _, clientes_for_filters, _ = get_filtro_opcoes(dados_base, ano, comercial, "All")
cliente = st.sidebar.selectbox(
    "**Cliente**", 
    ["Todos"] + clientes_for_filters, 
    key="customer_select"
)

# Category filter (updates based on all previous filters)
_, _, _, categorias_for_filters = get_filtro_opcoes(dados_base, ano, comercial, cliente)
categoria = st.sidebar.selectbox(
    "**Categoria**", 
    ["Todas"] + categorias_for_filters, 
    key="category_select"
)

# Apply filters to data
def aplicar_filtros(dados, ano, comercial, cliente, categoria):
    resultado = dados.copy()
    if ano != "Todos":
        resultado = resultado[resultado['ano'] == int(ano)]
    if comercial != "Todos":
        resultado = resultado[resultado['comercial'].astype(str) == str(comercial)]
    if cliente != "Todos":
        resultado = resultado[resultado['cliente'].astype(str) == str(cliente)]
    if categoria != "Todas" and 'categoria' in resultado.columns:
        resultado = resultado[resultado['categoria'].astype(str) == str(categoria)]
    return resultado

dados_filtrados = aplicar_filtros(dados_base, ano, comercial, cliente, categoria)

# --- FUNCTION: EXPORT EXCEL ---
def gerar_excel(dados):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dados.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

# --- PROFESSIONAL CHART SETTINGS ---
color_scale_primary = [primary_color, secondary_color, accent_color, "#9467bd", "#8c564b"]
color_scale_sequential = 'Blues'
template_chart = 'plotly_white'

month_names_pt = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
    5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
    9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}

# --- PAGE 1: ENHANCED OVERVIEW ---
if pagina == "📈 Visão Geral":
    st.title("📊 Painel KPI - Visão Geral")
    
    # Summary Metrics with enhanced styling
    st.markdown("### 📈 Métricas Principais")
    col1, col2, col3, col4 = st.columns(4)
    
    total_qty = dados_filtrados['qtd'].sum()
    total_value = dados_filtrados['v_liquido'].sum() if 'v_liquido' in dados_filtrados.columns else 0
    num_customers = dados_filtrados['cliente'].nunique()
    num_commercials = dados_filtrados['comercial'].nunique()
    
    with col1:
        st.metric(
            label="📦 Quantidade Total", 
            value=f"{total_qty:,.0f}",
            delta=None
        )
    with col2:
        st.metric(
            label="💰 Valor Total", 
            value=f"€ {total_value:,.0f}" if total_value > 0 else "N/A",
            delta=None
        )
    with col3:
        st.metric(
            label="👥 Clientes Únicos", 
            value=f"{num_customers}",
            delta=None
        )
    with col4:
        st.metric(
            label="🧑‍💼 Comerciais", 
            value=f"{num_commercials}",
            delta=None
        )
    
    st.markdown("---")
    
    # KPI by Customer
    st.markdown("### 🏆 Top 10 Clientes")
    top_clientes = dados_filtrados.groupby('cliente')[['qtd', 'v_liquido']].sum().sort_values('qtd', ascending=False).head(10)
    top_clientes['Quota %'] = (top_clientes['qtd'] / top_clientes['qtd'].sum() * 100).round(2)
    
    fig_top = px.bar(
        top_clientes.reset_index(),
        x='cliente',
        y='qtd',
        color='v_liquido',
        title='',
        labels={'qtd': 'Quantidade', 'cliente': 'Cliente', 'v_liquido': 'Valor (€)'},
        color_continuous_scale=color_scale_sequential,
        text='qtd'
    )
    fig_top.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside',
        marker_line_color=primary_color,
        marker_line_width=1
    )
    fig_top.update_layout(
        template=template_chart,
        showlegend=False,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=neutral_dark),
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_top, use_container_width=True)
    
    # Two columns for Commercial and Category KPIs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🧑‍💼 Desempenho por Comercial")
        kpi_comercial = dados_filtrados.groupby('comercial')[['qtd', 'v_liquido']].sum().sort_values('qtd', ascending=False).head(8)
        
        fig_comercial = px.bar(
            kpi_comercial.reset_index(),
            x='comercial',
            y='qtd',
            color='qtd',
            title='',
            labels={'qtd': 'Quantidade', 'comercial': 'Comercial'},
            color_continuous_scale=color_scale_sequential
        )
        fig_comercial.update_layout(
            template=template_chart,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=neutral_dark)
        )
        st.plotly_chart(fig_comercial, use_container_width=True)
    
    with col2:
        # Category KPI (if available)
        if 'categoria' in dados_filtrados.columns and not dados_filtrados['categoria'].isna().all():
            st.markdown("### 📊 Desempenho por Categoria")
            kpi_categoria = dados_filtrados.groupby('categoria')[['qtd', 'v_liquido']].sum().sort_values('qtd', ascending=False).head(8)
            
            fig_categoria = px.pie(
                kpi_categoria.reset_index(),
                values='qtd',
                names='categoria',
                title='',
                color_discrete_sequence=[primary_color, secondary_color, accent_color, "#9467bd", "#8c564b"]
            )
            fig_categoria.update_layout(
                template=template_chart,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color=neutral_dark)
            )
            st.plotly_chart(fig_categoria, use_container_width=True)
    
    # Data Table
    st.markdown("### 📋 Dados Detalhados")
    with st.expander("Ver dados completos"):
        st.dataframe(dados_filtrados, use_container_width=True)
        st.download_button(
            "📥 Exportar Dados", 
            data=gerar_excel(dados_filtrados), 
            file_name="kpi_data.xlsx",
            use_container_width=True
        )

# --- PAGE 2: ENHANCED CUSTOM KPIs ---
elif pagina == "🎯 KPIs Personalizados":
    st.title("🎯 KPIs Personalizados")
    
    st.markdown("### Criar KPIs Personalizados")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        kpi_name = st.text_input("**Nome do KPI**", value="Desempenho de Vendas")
        st.info("📊 KPI apresenta desempenho mensal (Soma de Quantidade)")
    
    with col2:
        kpi_period = st.selectbox("**Período**", ["Mensal", "Trimestral", "Anual"])
        show_trend = st.checkbox("Mostrar Linha de Tendência", value=True)
    
    if dados_filtrados.empty:
        st.warning("⚠️ Sem dados disponíveis para os filtros selecionados. Ajuste seus filtros.")
    else:
        # Prepare KPI data - always sum qtd by month
        kpi_data = dados_filtrados.groupby('mes')['qtd'].sum().reset_index()
        kpi_data.columns = ['mes', 'value']
        kpi_data = kpi_data.sort_values('mes')
        kpi_data['month_name'] = kpi_data['mes'].map(month_names_pt)
        
        # Display KPI with professional colors
        fig_kpi = px.bar(
            kpi_data,
            x='month_name',
            y='value',
            title=f"{kpi_name} - Desempenho Mensal",
            labels={'value': 'Quantidade (Soma)', 'month_name': 'Mês'},
            color='value',
            text='value',
            color_continuous_scale=color_scale_sequential
        )
        fig_kpi.update_traces(
            texttemplate='%{text:,.0f}',
            textposition='outside',
            marker_line_color=primary_color,
            marker_line_width=1
        )
        fig_kpi.update_layout(
            template=template_chart,
            showlegend=False,
            xaxis_title="Mês",
            yaxis_title="Quantidade (Soma)",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=neutral_dark)
        )
        st.plotly_chart(fig_kpi, use_container_width=True)
        
        # Enhanced Summary Cards
        st.markdown("### 📊 Estatísticas do KPI")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🔝 Máximo", f"{kpi_data['value'].max():,.0f}")
        col2.metric("📉 Mínimo", f"{kpi_data['value'].min():,.0f}")
        col3.metric("📊 Média", f"{kpi_data['value'].mean():,.0f}")
        col4.metric("📈 Mediana", f"{kpi_data['value'].median():,.0f}")

# --- PAGE 3: TRENDS ---
elif pagina == "📉 Tendências":
    st.title("📉 Análise de Tendências")
    
    col1, col2 = st.columns(2)
    
    with col1:
        trend_metric = "Quantidade"
        st.selectbox("**Selecionar Métrica**", ["Quantidade"], disabled=True)
        trend_groupby = st.selectbox("**Agrupar Por**", ["mês"], disabled=True)
    
    with col2:
        trend_window = st.slider("**Média Móvel (meses)**", 1, 12, 3)
    
    if dados_filtrados.empty:
        st.warning("⚠️ Sem dados disponíveis para os filtros selecionados. Ajuste seus filtros.")
    else:
        # Prepare trend data
        trend_data = dados_filtrados.groupby('mes')['qtd'].sum().reset_index()
        trend_data.columns = ['mes', 'value']
        trend_data = trend_data.sort_values('mes')
        trend_data['month_name'] = trend_data['mes'].map(month_names_pt)
        
        if len(trend_data) < 2:
            st.warning("⚠️ Dados insuficientes para análise de tendências.")
        else:
            # Add moving average
            trend_data['MA'] = trend_data['value'].rolling(window=trend_window, center=True).mean()
            
            # Professional trend chart
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=trend_data['month_name'],
                y=trend_data['value'],
                mode='lines+markers',
                name='Real',
                line=dict(color=primary_color, width=3),
                marker=dict(size=8, color=primary_color),
                fill='tozeroy',
                fillcolor=f'{primary_color}20',
                text=trend_data['value'].astype(str),
                textposition='top center'
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=trend_data['month_name'],
                y=trend_data['MA'],
                mode='lines',
                name=f'Média Móvel ({trend_window} meses)',
                line=dict(color=accent_color, width=2, dash='dash')
            ))
            
            fig_trend.update_layout(
                title="Tendência Mensal - Soma de Quantidade",
                xaxis_title="Mês",
                yaxis_title="Quantidade (Soma)",
                hovermode='x unified',
                template=template_chart,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color=neutral_dark)
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Enhanced Trend Statistics
            st.markdown("### 📊 Estatísticas de Tendência")
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

# --- PAGE 4: ALERTS ---
elif pagina == "⚠️ Alertas":
    st.title("⚠️ Sistema de Alertas")
    
    st.markdown("### Alertas de Desempenho")
    
    # Customer Performance Analysis
    analise_clientes = dados_filtrados.groupby('cliente').agg({
        'qtd': ['sum', 'mean', 'count'],
        'v_liquido': 'sum'
    }).reset_index()
    
    analise_clientes.columns = ['Cliente', 'Total_Qtd', 'Avg_Qtd', 'Transactions', 'Total_Value_EUR']
    analise_clientes = analise_clientes.sort_values('Total_Qtd', ascending=False)
    
    media_geral = dados_filtrados['qtd'].mean()
    
    analise_clientes['Status'] = analise_clientes['Avg_Qtd'].apply(
        lambda x: '🟢 Excelente' if x >= media_geral else '🟡 Atenção' if x >= media_geral * 0.7 else '🔴 Crítico'
    )
    
    # Enhanced Status Metrics
    st.markdown("### 📊 Status dos Clientes")
    col1, col2, col3 = st.columns(3)
    
    excellent = len(analise_clientes[analise_clientes['Status'] == '🟢 Excelente'])
    warning = len(analise_clientes[analise_clientes['Status'] == '🟡 Atenção'])
    critical = len(analise_clientes[analise_clientes['Status'] == '🔴 Crítico'])
    
    col1.metric("🟢 Excelente", excellent, delta_color="off")
    col2.metric("🟡 Atenção", warning, delta_color="off")
    col3.metric("🔴 Crítico", critical, delta_color="off")
    
    st.markdown("---")
    
    # Critical Customers Section
    st.markdown("### 🔴 Alertas Críticos")
    criticos = analise_clientes[analise_clientes['Status'] == '🔴 Crítico']
    if not criticos.empty:
        st.error(f"⚠️ {len(criticos)} clientes precisam de atenção imediata!")
        
        # Enhanced critical customers table
        fig_criticos = px.bar(
            criticos.head(10),
            x='Cliente',
            y='Avg_Qtd',
            title='Top 10 Clientes Críticos - Média de Quantidade',
            labels={'Avg_Qtd': 'Média de Quantidade', 'Cliente': 'Cliente'},
            color='Avg_Qtd',
            color_continuous_scale='Reds'
        )
        fig_criticos.update_layout(
            template=template_chart,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=neutral_dark)
        )
        st.plotly_chart(fig_criticos, use_container_width=True)
    else:
        st.success("✅ Sem alertas críticos!")

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
            # Enhanced Customer Profile
            st.markdown(f"### 📊 Perfil do Cliente: **{cliente}**")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Quantidade Total", f"{cliente_data['qtd'].sum():,.0f}")
            col2.metric("Valor Total", f"€ {cliente_data['v_liquido'].sum():,.0f}")
            col3.metric("Média por Transação", f"{cliente_data['qtd'].mean():,.0f}")
            col4.metric("Transações", len(cliente_data))
            
            # Customer Trend with professional styling
            st.markdown("### 📈 Tendência do Cliente")
            historico = cliente_data.groupby(['ano', 'mes']).agg({'qtd': 'sum'}).reset_index()
            historico['month_name'] = historico['mes'].map(month_names_pt)
            historico = historico.sort_values(['ano', 'mes'])
            
            fig_historico = px.line(
                historico,
                x='month_name',
                y='qtd',
                markers=True,
                title=f"Desempenho Mensal - {cliente}",
                labels={'qtd': 'Quantidade (Soma)', 'month_name': 'Mês'},
                color_discrete_sequence=[primary_color],
                text='qtd'
            )
            fig_historico.update_traces(
                textposition='top center', 
                textfont=dict(color=primary_color, size=10),
                line=dict(width=3),
                marker=dict(size=8)
            )
            fig_historico.update_layout(
                template=template_chart,
                hovermode='x unified',
                xaxis_tickangle=-45,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color=neutral_dark)
            )
            st.plotly_chart(fig_historico, use_container_width=True)

# --- PAGE 6: COMPARATIVE VIEW ---
else:
    st.title("📊 Análise Comparativa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        comp_metric1 = st.selectbox("**Métrica**", ["qtd", "v_liquido", "pm"])
        comp_groupby1 = st.selectbox("**Agrupar Por**", ["cliente", "comercial", "categoria"])
    
    with col2:
        comp_top = st.slider("**Top N Itens**", 5, 20, 10)
        show_pie = st.checkbox("Mostrar Gráfico de Pizza", value=True)
    
    # Get top items
    top_items = dados_filtrados.groupby(comp_groupby1)[comp_metric1].sum().nlargest(comp_top)
    
    if show_pie:
        # Professional comparative visualization
        fig_comp = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "bar"}, {"type": "pie"}]],
            subplot_titles=("Gráfico de Barras", "Distribuição"),
            column_widths=[0.6, 0.4]
        )
        
        fig_comp.add_trace(
            go.Bar(
                x=top_items.index, 
                y=top_items.values, 
                marker=dict(
                    color=top_items.values, 
                    colorscale=color_scale_sequential,
                    line=dict(color=primary_color, width=1)
                ),
                name=comp_metric1,
                text=top_items.values,
                texttemplate='%{text:,.0f}',
                textposition='outside'
            ),
            row=1, col=1
        )
        
        fig_comp.add_trace(
            go.Pie(
                labels=top_items.index, 
                values=top_items.values, 
                name=comp_metric1,
                marker=dict(colors=[primary_color, secondary_color, accent_color, "#9467bd", "#8c564b"])
            ),
            row=1, col=2
        )
        
        fig_comp.update_layout(
            height=500, 
            showlegend=False, 
            template=template_chart,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=neutral_dark)
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        # Single bar chart
        fig_single = px.bar(
            top_items.reset_index(),
            x=comp_groupby1,
            y=comp_metric1,
            title=f"Top {comp_top} por {comp_metric1}",
            labels={comp_metric1: 'Valor', comp_groupby1: 'Categoria'},
            color=comp_metric1,
            color_continuous_scale=color_scale_sequential,
            text=comp_metric1
        )
        fig_single.update_traces(
            texttemplate='%{text:,.0f}',
            textposition='outside',
            marker_line_color=primary_color,
            marker_line_width=1
        )
        fig_single.update_layout(
            template=template_chart,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=neutral_dark),
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_single, use_container_width=True)
    
    # Enhanced Statistics Table
    st.markdown("### 📈 Estatísticas Comparativas")
    comp_stats = pd.DataFrame({
        comp_groupby1: top_items.index,
        comp_metric1: top_items.values,
        'Quota %': (top_items.values / top_items.sum() * 100).round(2)
    })
    
    st.dataframe(comp_stats, use_container_width=True)
    
    # Enhanced download button
    st.download_button(
        "📥 Exportar Análise", 
        data=gerar_excel(comp_stats), 
        file_name="comparative_analysis.xlsx",
        use_container_width=True
    )
