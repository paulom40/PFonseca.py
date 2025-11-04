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
@st.cache_data
def carregar_dados():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    df = pd.read_excel(url)
    
    # Normalize column names
    df.columns = (
        df.columns.str.strip().str.lower().str.replace(" ", "_")
        .str.replace(".", "", regex=False)
        .map(lambda x: unicodedata.normalize('NFKD', x).encode('ascii', errors='ignore').decode('utf-8'))
    )
    
    # Mapping
    esperadas = {
        'cliente': ['cliente'],
        'comercial': ['comercial'],
        'ano': ['ano'],
        'mes': ['mes'],
        'qtd': ['qtd', 'quantidade'],
        'v_liquido': ['v_liquido', 'vl_liquido', 'valor_liquido'],
        'pm': ['pm', 'preco_medio'],
        'categoria': ['categoria', 'segmento']
    }
    
    detectadas = list(df.columns)
    col_map = {}
    
    for chave, variantes in esperadas.items():
        for variante in variantes:
            for col in detectadas:
                if variante == col or variante.replace("_", "") in col.replace("_", ""):
                    col_map[chave] = col
                    break
            if chave in col_map:
                break
    
    df = df.rename(columns=col_map)
    df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
    df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
    df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')
    df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')
    df['pm'] = pd.to_numeric(df['pm'], errors='coerce')
    
    return df

df = carregar_dados()

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("# 📊 KPI Dashboard")
st.sidebar.markdown("---")

pagina = st.sidebar.radio("Navigate", [
    "📈 Overview", 
    "🎯 Custom KPIs", 
    "📉 Trends", 
    "⚠️ Alerts",
    "👥 Customer Analysis",
    "📊 Comparative View"
])

# --- FILTERS WITH CASCADING LOGIC - Fixed to work properly with dynamic options ---
st.sidebar.markdown("### 🔍 Filters")
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
    if ano != "All":
        temp = temp[temp['ano'] == ano]
    
    # Filter by commercial
    if comercial != "All":
        temp = temp[temp['comercial'] == comercial]
    
    anos = sorted([int(x) for x in temp['ano'].dropna().unique()])
    comerciais = sorted(temp['comercial'].dropna().unique())
    clientes = sorted(temp['cliente'].dropna().unique())
    
    return anos, comerciais, clientes

# Year filter
anos_disponiveis, _, _ = get_filtro_opcoes(dados_base, "All", "All")
ano = st.sidebar.selectbox("Year", ["All"] + anos_disponiveis, key="year_select")
st.session_state.ano_filter = ano

# Commercial filter (updates based on year)
_, comerciais_disponiveis, _ = get_filtro_opcoes(dados_base, ano, "All")
comercial = st.sidebar.selectbox("Commercial", ["All"] + comerciais_disponiveis, key="commercial_select")
st.session_state.comercial_filter = comercial

# Customer filter (updates based on year and commercial)
_, _, clientes_disponiveis = get_filtro_opcoes(dados_base, ano, comercial)
cliente = st.sidebar.selectbox("Customer", ["All"] + clientes_disponiveis, key="customer_select")
st.session_state.cliente_filter = cliente

# Apply filters to data
def aplicar_filtros(dados, ano, comercial, cliente):
    resultado = dados.copy()
    if ano != "All":
        resultado = resultado[resultado['ano'] == ano]
    if comercial != "All":
        resultado = resultado[resultado['comercial'] == comercial]
    if cliente != "All":
        resultado = resultado[resultado['cliente'] == cliente]
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

# --- PAGE 1: OVERVIEW ---
if pagina == "📈 Overview":
    st.title("📊 KPI Dashboard Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_qty = dados_filtrados['qtd'].sum()
    total_value = dados_filtrados['v_liquido'].sum()
    num_customers = dados_filtrados['cliente'].nunique()
    num_commercials = dados_filtrados['comercial'].nunique()
    
    col1.metric("📦 Total Quantity", f"{total_qty:,.0f}")
    col2.metric("💰 Total Value", f"R$ {total_value:,.0f}")
    col3.metric("👥 Unique Customers", f"{num_customers}")
    col4.metric("🧑‍💼 Active Commercials", f"{num_commercials}")
    
    st.markdown("---")
    
    # KPI by Customer
    st.subheader("🏆 Top 10 Customers by Quantity")
    top_clientes = dados_filtrados.groupby('cliente')[['qtd', 'v_liquido']].sum().sort_values('qtd', ascending=False).head(10)
    top_clientes['Share %'] = (top_clientes['qtd'] / top_clientes['qtd'].sum() * 100).round(2)
    
    fig_top = px.bar(
        top_clientes.reset_index(),
        x='cliente',
        y='qtd',
        color='v_liquido',
        title='Top 10 Customers by Quantity',
        labels={'qtd': 'Quantity', 'cliente': 'Customer', 'v_liquido': 'Value (R$)'},
        color_continuous_scale='Turbo'
    )
    fig_top.update_layout(template=template_chart, showlegend=True, hovermode='x unified')
    st.plotly_chart(fig_top, use_container_width=True)
    
    # KPI by Commercial
    st.subheader("🧑‍💼 Performance by Commercial")
    kpi_comercial = dados_filtrados.groupby('comercial')[['qtd', 'v_liquido']].sum().sort_values('qtd', ascending=False)
    
    fig_comercial = px.bar(
        kpi_comercial.reset_index(),
        x='comercial',
        y='qtd',
        color='v_liquido',
        title='Quantity by Commercial',
        color_continuous_scale='Plasma'
    )
    fig_comercial.update_layout(template=template_chart, showlegend=True)
    st.plotly_chart(fig_comercial, use_container_width=True)
    
    # Data Table
    st.subheader("📋 Detailed Data")
    st.dataframe(dados_filtrados, use_container_width=True)
    st.download_button("📥 Export Data", data=gerar_excel(dados_filtrados), file_name="kpi_data.xlsx")

# --- PAGE 2: CUSTOM KPIs ---
elif pagina == "🎯 Custom KPIs":
    st.title("🎯 Custom KPI Creator")
    
    st.markdown("### Create Your Custom KPIs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        kpi_name = st.text_input("KPI Name", value="Revenue Growth")
        kpi_metric = st.selectbox("Select Metric", ["Sum", "Average", "Max", "Min", "Count", "Median"])
        kpi_field = st.selectbox("Field", ["qtd", "v_liquido", "pm"])
        kpi_groupby = st.selectbox("Group By", ["cliente", "comercial", "categoria", "mes", "ano"])
    
    with col2:
        kpi_period = st.selectbox("Period", ["Monthly", "Quarterly", "Yearly"])
        show_trend = st.checkbox("Show Trend Line", value=True)
        show_forecast = st.checkbox("Show Forecast", value=False)
    
    # Calculate KPI
    if kpi_metric == "Sum":
        kpi_data = dados_filtrados.groupby(kpi_groupby)[kpi_field].sum()
    elif kpi_metric == "Average":
        kpi_data = dados_filtrados.groupby(kpi_groupby)[kpi_field].mean()
    elif kpi_metric == "Max":
        kpi_data = dados_filtrados.groupby(kpi_groupby)[kpi_field].max()
    elif kpi_metric == "Min":
        kpi_data = dados_filtrados.groupby(kpi_groupby)[kpi_field].min()
    elif kpi_metric == "Count":
        kpi_data = dados_filtrados.groupby(kpi_groupby)[kpi_field].count()
    else:
        kpi_data = dados_filtrados.groupby(kpi_groupby)[kpi_field].median()
    
    kpi_data = kpi_data.sort_values(ascending=False)
    
    # Display KPI with vibrant colors
    fig_kpi = px.bar(
        x=kpi_data.index,
        y=kpi_data.values,
        title=f"{kpi_name} - {kpi_metric}({kpi_field})",
        labels={'x': kpi_groupby.title(), 'y': 'Value'},
        color=kpi_data.values,
        color_continuous_scale='Rainbow'
    )
    fig_kpi.update_layout(template=template_chart, showlegend=False)
    st.plotly_chart(fig_kpi, use_container_width=True)
    
    # Summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔝 Maximum", f"{kpi_data.max():,.2f}")
    col2.metric("📉 Minimum", f"{kpi_data.min():,.2f}")
    col3.metric("📊 Average", f"{kpi_data.mean():,.2f}")
    col4.metric("📈 Median", f"{kpi_data.median():,.2f}")
    
    # Data Table
    st.dataframe(kpi_data.reset_index().rename(columns={0: kpi_name}), use_container_width=True)

# --- PAGE 3: TRENDS ---
elif pagina == "📉 Trends":
    st.title("📉 Trend Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        trend_metric = st.selectbox("Select Metric", ["Quantity", "Value"])
        trend_groupby = st.selectbox("Group By", ["mes", "ano", "cliente", "comercial"])
    
    with col2:
        trend_window = st.slider("Moving Average (months)", 1, 12, 3)
    
    # Prepare trend data
    if trend_metric == "Quantity":
        trend_data = dados_filtrados.groupby(trend_groupby)['qtd'].sum().reset_index()
        trend_data.columns = [trend_groupby, 'value']
    else:
        trend_data = dados_filtrados.groupby(trend_groupby)['v_liquido'].sum().reset_index()
        trend_data.columns = [trend_groupby, 'value']
    
    trend_data = trend_data.sort_values(trend_groupby)
    
    # Add moving average
    trend_data['MA'] = trend_data['value'].rolling(window=trend_window, center=True).mean()
    
    # Plot trend with vibrant colors
    fig_trend = go.Figure()
    
    fig_trend.add_trace(go.Scatter(
        x=trend_data[trend_groupby],
        y=trend_data['value'],
        mode='lines+markers',
        name='Actual',
        line=dict(color='#ff006e', width=3),
        marker=dict(size=8, color='#ff006e'),
        fill='tozeroy',
        fillcolor='rgba(255, 0, 110, 0.1)'
    ))
    
    fig_trend.add_trace(go.Scatter(
        x=trend_data[trend_groupby],
        y=trend_data['MA'],
        mode='lines',
        name=f'MA({trend_window})',
        line=dict(color='#00f5ff', width=2, dash='dash')
    ))
    
    fig_trend.update_layout(
        title=f"Trend: {trend_metric} by {trend_groupby.title()}",
        xaxis_title=trend_groupby.title(),
        yaxis_title="Value",
        hovermode='x unified',
        template=template_chart
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Trend Statistics
    st.subheader("📊 Trend Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    trend_pct_change = ((trend_data['value'].iloc[-1] - trend_data['value'].iloc[0]) / trend_data['value'].iloc[0] * 100) if trend_data['value'].iloc[0] != 0 else 0
    
    col1.metric("Current Value", f"{trend_data['value'].iloc[-1]:,.0f}")
    col2.metric("Previous Value", f"{trend_data['value'].iloc[-2]:,.0f}" if len(trend_data) > 1 else "N/A")
    col3.metric("% Change", f"{trend_pct_change:+.1f}%")
    col4.metric("Trend", "📈 Up" if trend_pct_change > 0 else "📉 Down")

# --- PAGE 4: ALERTS ---
elif pagina == "⚠️ Alerts":
    st.title("⚠️ Alert System")
    
    st.markdown("### Performance Alerts")
    
    # Customer Performance Analysis
    analise_clientes = dados_filtrados.groupby('cliente').agg({
        'qtd': ['sum', 'mean', 'count'],
        'v_liquido': 'sum'
    }).reset_index()
    
    analise_clientes.columns = ['Cliente', 'Total_Qtd', 'Avg_Qtd', 'Transactions', 'Total_Value']
    analise_clientes = analise_clientes.sort_values('Total_Qtd', ascending=False)
    
    media_geral = dados_filtrados['qtd'].mean()
    
    analise_clientes['Status'] = analise_clientes['Avg_Qtd'].apply(
        lambda x: '🟢 Excellent' if x >= media_geral else '🟡 Warning' if x >= media_geral * 0.7 else '🔴 Critical'
    )
    
    col1, col2, col3 = st.columns(3)
    
    excellent = len(analise_clientes[analise_clientes['Status'] == '🟢 Excellent'])
    warning = len(analise_clientes[analise_clientes['Status'] == '🟡 Warning'])
    critical = len(analise_clientes[analise_clientes['Status'] == '🔴 Critical'])
    
    col1.metric("🟢 Excellent", excellent)
    col2.metric("🟡 Warning", warning)
    col3.metric("🔴 Critical", critical)
    
    st.markdown("---")
    
    st.subheader("📋 Customer Status Report")
    st.dataframe(analise_clientes, use_container_width=True)
    
    # Critical Customers
    st.subheader("🔴 Critical Alert Customers")
    criticos = analise_clientes[analise_clientes['Status'] == '🔴 Critical']
    if not criticos.empty:
        st.error(f"⚠️ {len(criticos)} customers need immediate attention!")
        st.dataframe(criticos, use_container_width=True)
    else:
        st.success("✅ No critical alerts!")

# --- PAGE 5: CUSTOMER ANALYSIS ---
elif pagina == "👥 Customer Analysis":
    st.title("👥 Customer Analysis")
    
    if cliente == "All":
        st.info("👈 Select a specific customer in the sidebar")
    else:
        cliente_data = dados_filtrados[dados_filtrados['cliente'] == cliente]
        
        if cliente_data.empty:
            st.warning("No data available")
        else:
            # Customer Summary
            st.subheader(f"📊 Customer Profile: {cliente}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Quantity", f"{cliente_data['qtd'].sum():,.0f}")
            col2.metric("Total Value", f"R$ {cliente_data['v_liquido'].sum():,.0f}")
            col3.metric("Avg per Transaction", f"{cliente_data['qtd'].mean():,.2f}")
            col4.metric("Transactions", len(cliente_data))
            
            # Trend
            st.subheader("📈 Customer Trend")
            historico = cliente_data.groupby(['ano', 'mes'])['qtd'].sum().reset_index()
            historico = historico.sort_values(['ano', 'mes'])
            
            fig_historico = px.line(
                historico,
                x='mes',
                y='qtd',
                markers=True,
                title=f"Monthly Performance - {cliente}",
                color_discrete_sequence=['#00f5ff']
            )
            fig_historico.update_layout(template=template_chart)
            st.plotly_chart(fig_historico, use_container_width=True)
            
            # Comparison with others
            st.subheader("🔄 vs. Market Average")
            media_mercado = dados_filtrados.groupby(['ano', 'mes'])['qtd'].mean().reset_index()
            
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Scatter(
                x=historico['mes'], 
                y=historico['qtd'], 
                mode='lines+markers', 
                name=cliente, 
                line=dict(color='#ff006e', width=3),
                marker=dict(size=8)
            ))
            fig_comp.add_trace(go.Scatter(
                x=media_mercado['mes'], 
                y=media_mercado['qtd'], 
                mode='lines', 
                name='Market Avg', 
                line=dict(color='#00f5ff', width=2, dash='dash')
            ))
            
            fig_comp.update_layout(
                title="Customer vs Market Trend", 
                xaxis_title="Month", 
                yaxis_title="Quantity", 
                hovermode='x unified', 
                template=template_chart
            )
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Data
            st.dataframe(cliente_data, use_container_width=True)

# --- PAGE 6: COMPARATIVE VIEW ---
else:
    st.title("📊 Comparative Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        comp_metric1 = st.selectbox("Metric 1", ["qtd", "v_liquido", "pm"])
        comp_groupby1 = st.selectbox("Group By 1", ["cliente", "comercial", "categoria"])
    
    with col2:
        comp_top = st.slider("Top N Items", 5, 20, 10)
    
    # Get top items
    top_items = dados_filtrados.groupby(comp_groupby1)[comp_metric1].sum().nlargest(comp_top)
    
    # Create comparative visualizations with vibrant colors
    fig_comp = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "bar"}, {"type": "pie"}]],
        subplot_titles=("Bar Chart", "Pie Chart")
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
    st.subheader("📈 Comparative Statistics")
    comp_stats = pd.DataFrame({
        comp_groupby1: top_items.index,
        comp_metric1: top_items.values,
        'Share %': (top_items.values / top_items.sum() * 100).round(2)
    })
    
    st.dataframe(comp_stats, use_container_width=True)
    st.download_button("📥 Export Analysis", data=gerar_excel(comp_stats), file_name="comparative_analysis.xlsx")
