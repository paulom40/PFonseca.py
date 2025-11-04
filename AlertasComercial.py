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
    try:
        url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx"
        df = pd.read_excel(url)
        
        original_columns = df.columns.tolist()
        
        # Define expected columns with their variants (keep accent variants!)
        col_map = {}
        
        expected_cols = {
            'cliente': ['cliente', 'Cliente', 'CLIENTE'],
            'comercial': ['comercial', 'Comercial', 'COMERCIAL'],
            'ano': ['ano', 'Ano', 'ANO'],
            'mes': ['mes', 'Mês', 'mês', 'MÊS'],
            'qtd': ['qtd', 'Qtd', 'QTD', 'Qtd.', 'quantidade', 'Quantidade', 'QUANTIDADE'],
            'v_liquido': ['v_liquido', 'V_Liquido', 'V. Líquido', 'vl_liquido', 'valor_liquido', 'V_LIQUIDO', 'V. LÍQUIDO'],
            'pm': ['pm', 'PM', 'preco_medio', 'Preco_Medio', 'preço_médio', 'Preço Médio'],
            'categoria': ['categoria', 'Categoria', 'CATEGORIA', 'segmento', 'Segmento'],
            'artigo': ['artigo', 'Artigo', 'ARTIGO'],
            'codigo': ['código', 'Código', 'CÓDIGO', 'Cod.', 'cod', 'codigo', 'Codigo'],
            'un': ['un', 'UN', 'unidade', 'Unidade', 'UNIDADE']
        }
        
        # Map each original column to standardized name
        for original_col in original_columns:
            col_matched = False
            for standard_name, variants in expected_cols.items():
                # Direct match first (preserves exact names like 'Qtd.')
                if original_col in variants:
                    col_map[original_col] = standard_name
                    col_matched = True
                    break
                # Then try case-insensitive match
                if not col_matched:
                    for variant in variants:
                        if original_col.lower() == variant.lower():
                            col_map[original_col] = standard_name
                            col_matched = True
                            break
                if col_matched:
                    break
        
        # Rename columns
        df = df.rename(columns=col_map)
        
        critical_cols = ['mes', 'qtd', 'ano', 'cliente', 'comercial']
        missing_cols = [col for col in critical_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ Missing critical columns: {missing_cols}")
            st.info(f"✓ Available columns: {list(df.columns)}")
            return pd.DataFrame()
        
        df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')
        if 'v_liquido' in df.columns:
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')
        if 'pm' in df.columns:
            df['pm'] = pd.to_numeric(df['pm'], errors='coerce')
        
        # Remove rows with NaN values in critical columns
        df = df.dropna(subset=['mes', 'qtd', 'ano', 'cliente', 'comercial'])
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return pd.DataFrame()

df = carregar_dados()

if df.empty:
    st.error("❌ Failed to load data. Please check the GitHub URL and ensure the file is accessible.")
    st.stop()

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

# --- FILTERS WITH CASCADING LOGIC ---
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
        temp = temp[temp['ano'] == int(ano)]
    
    # Filter by commercial
    if comercial != "All":
        temp = temp[temp['comercial'].astype(str) == str(comercial)]
    
    anos = sorted([int(x) for x in temp['ano'].dropna().unique()])
    comerciais = sorted(list(temp['comercial'].dropna().unique()))
    clientes = sorted(list(temp['cliente'].dropna().unique()))
    
    return anos, comerciais, clientes

anos_disponiveis, comerciais_disponiveis, clientes_disponiveis = get_filtro_opcoes(dados_base, "All", "All")

# Year filter
ano = st.sidebar.selectbox(
    "Year", 
    ["All"] + anos_disponiveis, 
    key="year_select"
)

# Commercial filter (updates based on year)
_, comerciais_for_year, _ = get_filtro_opcoes(dados_base, ano, "All")
comercial = st.sidebar.selectbox(
    "Commercial", 
    ["All"] + comerciais_for_year, 
    key="commercial_select"
)

# Customer filter (updates based on year and commercial)
_, _, clientes_for_filters = get_filtro_opcoes(dados_base, ano, comercial)
cliente = st.sidebar.selectbox(
    "Customer", 
    ["All"] + clientes_for_filters, 
    key="customer_select"
)

# Apply filters to data
def aplicar_filtros(dados, ano, comercial, cliente):
    resultado = dados.copy()
    if ano != "All":
        resultado = resultado[resultado['ano'] == int(ano)]
    if comercial != "All":
        resultado = resultado[resultado['comercial'].astype(str) == str(comercial)]
    if cliente != "All":
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
        st.info("📊 KPI displays monthly performance (Sum of Quantity)")
    
    with col2:
        kpi_period = st.selectbox("Period", ["Monthly", "Quarterly", "Yearly"])
        show_trend = st.checkbox("Show Trend Line", value=True)
    
    if dados_filtrados.empty:
        st.warning("⚠️ No data available for selected filters. Please adjust your filters.")
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
            title=f"Monthly Performance - {kpi_name}",
            labels={'value': 'Quantity (Sum)', 'month_name': 'Month'},
            color='value',
            text='value',
            color_continuous_scale='Rainbow'
        )
        fig_kpi.update_traces(textposition='outside', textfont=dict(color='#00f5ff'))
        fig_kpi.update_layout(template=template_chart, showlegend=False, xaxis_title="Month", yaxis_title="Quantity (Sum)")
        st.plotly_chart(fig_kpi, use_container_width=True)
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🔝 Maximum", f"{kpi_data['value'].max():,.0f}")
        col2.metric("📉 Minimum", f"{kpi_data['value'].min():,.0f}")
        col3.metric("📊 Average", f"{kpi_data['value'].mean():,.2f}")
        col4.metric("📈 Median", f"{kpi_data['value'].median():,.2f}")
        
        # Data Table
        st.subheader("📋 Monthly KPI Data")
        st.dataframe(kpi_data[['month_name', 'value']], use_container_width=True)

# --- PAGE 3: TRENDS ---
elif pagina == "📉 Trends":
    st.title("📉 Trend Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        trend_metric = "Quantity"
        st.selectbox("Select Metric", ["Quantity"], disabled=True)
        trend_groupby = st.selectbox("Group By", ["mes"], disabled=True)
    
    with col2:
        trend_window = st.slider("Moving Average (months)", 1, 12, 3)
    
    # Check if filtered data is empty
    if dados_filtrados.empty:
        st.warning("⚠️ No data available for selected filters. Please adjust your filters.")
    else:
        # Prepare trend data - always sum qtd by month
        trend_data = dados_filtrados.groupby('mes')['qtd'].sum().reset_index()
        trend_data.columns = ['mes', 'value']
        trend_data = trend_data.sort_values('mes')
        trend_data['month_name'] = trend_data['mes'].map(month_names_pt)
        
        # Check if trend_data has at least 2 rows
        if len(trend_data) < 2:
            st.warning("⚠️ Insufficient data points for trend analysis. At least 2 data points are required.")
        else:
            # Add moving average
            trend_data['MA'] = trend_data['value'].rolling(window=trend_window, center=True).mean()
            
            # Plot trend with vibrant colors
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=trend_data['month_name'],
                y=trend_data['value'],
                mode='lines+markers',
                name='Actual',
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
                name=f'MA({trend_window})',
                line=dict(color='#00f5ff', width=2, dash='dash')
            ))
            
            fig_trend.update_layout(
                title=f"Monthly Trend - Quantity Sum",
                xaxis_title="Month",
                yaxis_title="Quantity (Sum)",
                hovermode='x unified',
                template=template_chart
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Trend Statistics
            st.subheader("📊 Trend Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            current_value = trend_data['value'].iloc[-1]
            previous_value = trend_data['value'].iloc[-2] if len(trend_data) > 1 else trend_data['value'].iloc[0]
            
            if trend_data['value'].iloc[0] != 0:
                trend_pct_change = ((current_value - trend_data['value'].iloc[0]) / trend_data['value'].iloc[0] * 100)
            else:
                trend_pct_change = 0
            
            trend_direction = "📈 Up" if trend_pct_change > 0 else "📉 Down" if trend_pct_change < 0 else "➡️ Stable"
            
            col1.metric("Current Month", f"{current_value:,.0f}")
            col2.metric("Previous Month", f"{previous_value:,.0f}")
            col3.metric("% Change", f"{trend_pct_change:+.1f}%")
            col4.metric("Trend", trend_direction)
            
            # Display trend data table with month names
            st.subheader("📋 Monthly Trend Data")
            display_trend = trend_data[['month_name', 'value', 'MA']].rename(columns={'month_name': 'Month', 'value': 'Quantity', 'MA': 'Moving Avg'})
            st.dataframe(display_trend, use_container_width=True)

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
    
    st.markdown("---")
    
    # Customers with Purchase Gaps (Don't Buy Every Month)
    st.subheader("📅 Customers with Purchase Gaps (Don't Buy Every Month)")
    
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
            display_gaps.columns = ['Customer', 'Months Purchased', 'Months with Gap', 'Expected Months', 'Missing Months']
            
            # Calculate gap percentage
            display_gaps['Gap %'] = (display_gaps['Months with Gap'] / display_gaps['Expected Months'] * 100).round(1)
            
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
            
            display_gaps['Missing Month Names'] = display_gaps['Missing Months'].apply(safe_convert_month_pt)
            
            # Format final display table with percentage as primary column
            final_display = display_gaps[['Customer', 'Months Purchased', 'Expected Months', 'Gap %', 'Missing Month Names']].copy()
            final_display = final_display.sort_values('Gap %', ascending=False)
            
            # Show summary metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Customers with Gaps", len(customers_with_gaps))
            col2.metric("Avg Gap Percentage", f"{(customers_with_gaps['gap_count'].mean() / len(expected_months) * 100):.1f}%")
            col3.metric("Max Gap Percentage", f"{(customers_with_gaps['gap_count'].max() / len(expected_months) * 100):.1f}%")
            
            # Display alert table
            st.warning(f"⚠️ {len(customers_with_gaps)} customers have not purchased in every month!")
            st.dataframe(final_display, use_container_width=True)
            
            # Export gaps report
            st.download_button(
                "📥 Export Gap Report", 
                data=gerar_excel(final_display), 
                file_name="customers_with_gaps.xlsx"
            )
        else:
            st.success("✅ All customers are buying every month!")
    
    st.markdown("---")

# --- PAGE 5: CUSTOMER ANALYSIS ---
elif pagina == "👥 Customer Analysis":
    st.title("👥 Customer Analysis")
    
    if cliente == "All":
        st.info("👈 Selecione um cliente específico no painel lateral")
    else:
        cliente_data = dados_filtrados[dados_filtrados['cliente'] == cliente]
        
        if cliente_data.empty:
            st.warning("Não disponível")
        else:
            # Customer Summary
            st.subheader(f"📊 Perfil do Cliente: {cliente}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Quantity", f"{cliente_data['qtd'].sum():,.0f}")
            col2.metric("Total Value", f"R$ {cliente_data['v_liquido'].sum():,.0f}")
            col3.metric("Avg per Transaction", f"{cliente_data['qtd'].mean():,.2f}")
            col4.metric("Transactions", len(cliente_data))
            
            st.subheader("📈 Customer Trend - Monthly Performance")
            
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
                title=f"Monthly Performance (Quantity Sum) - {cliente}",
                labels={'qtd': 'Quantity (Sum)', 'month_name': 'Month'},
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
            
            st.subheader("🔄 vs. Market Average - Monthly Comparison")
            
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
                title="Monthly Performance: Customer vs Market Average (Quantity Sum)", 
                xaxis_title="Month", 
                yaxis_title="Quantity (Sum)", 
                hovermode='x unified', 
                template=template_chart,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Display comparison metrics
            st.subheader("📊 Performance Comparison")
            comp_metrics = pd.DataFrame({
                'Metrica': ['Total Quantity', 'Average Monthly', 'Best Month', 'Worst Month'],
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
    st.title("📊 Comparative Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        comp_metric1 = st.selectbox("Metrica 1", ["qtd", "v_liquido", "pm"])
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
    st.subheader("📈 Comparative Statistics")
    comp_stats = pd.DataFrame({
        comp_groupby1: top_items.index,
        comp_metric1: top_items.values,
        'Share %': (top_items.values / top_items.sum() * 100).round(2)
    })
    
    st.dataframe(comp_stats, use_container_width=True)
    st.download_button("📥 Exportar Análise", data=gerar_excel(comp_stats), file_name="comparative_analysis.xlsx")
