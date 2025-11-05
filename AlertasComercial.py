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
    page_title="Business Intelligence Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded",
    page_icon="🚀"
)

# --- MODERN COLOR SCHEME ---
primary_color = "#6366f1"  # Modern purple
secondary_color = "#10b981"  # Emerald green
accent_color = "#f59e0b"   # Amber
warning_color = "#ef4444"  # Red
success_color = "#22c55e"  # Green
info_color = "#3b82f6"     # Blue

# --- CLEAN WHITE STYLING ---
st.markdown(f"""
    <style>
    /* Clean White Design */
    .main {{
        background: #ffffff;
        color: #1e293b;
    }}
    
    .stApp {{
        background: #ffffff;
    }}
    
    /* Modern Headers */
    h1 {{
        color: {primary_color};
        font-weight: 800;
        font-size: 2.8em;
        margin-bottom: 20px;
        font-family: 'Inter', sans-serif;
        border-bottom: 3px solid {primary_color};
        padding-bottom: 10px;
    }}
    
    h2 {{
        color: #1e293b;
        font-weight: 700;
        font-size: 2em;
        margin-top: 30px;
        margin-bottom: 20px;
        font-family: 'Inter', sans-serif;
    }}
    
    h3 {{
        color: #475569;
        font-weight: 600;
        font-size: 1.4em;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Modern Cards */
    [data-testid="metric-container"] {{
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }}
    
    [data-testid="metric-container"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        border-color: {primary_color};
    }}
    
    /* Modern Sidebar */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {primary_color} 0%, #4f46e5 100%);
        border-right: none;
    }}
    
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    /* Enhanced Form Elements */
    .stRadio, .stSelectbox, .stMultiSelect {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }}
    
    .stRadio label, .stSelectbox label, .stMultiSelect label {{
        font-weight: 600;
        color: white !important;
        font-size: 1.1em;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Modern Buttons */
    .stDownloadButton button {{
        background: linear-gradient(135deg, {primary_color}, {secondary_color});
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 12px 25px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }}
    
    .stDownloadButton button:hover {{
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }}
    
    /* Metric Value Styling */
    [data-testid="metric-value"] {{
        font-size: 2em !important;
        font-weight: 800 !important;
        color: #1e293b !important;
        font-family: 'Inter', sans-serif;
    }}
    
    [data-testid="metric-label"] {{
        font-size: 1.1em !important;
        font-weight: 600 !important;
        color: {primary_color} !important;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Elegant Dividers */
    hr {{
        border: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 30px 0;
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: #f1f5f9;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {primary_color};
        border-radius: 3px;
    }}
    
    /* Streamlit element overrides */
    .st-bb {{
        background-color: transparent;
    }}
    
    .st-at {{
        background-color: white;
    }}
    
    /* Expander styling */
    .streamlit-expanderHeader {{
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        font-weight: 600;
    }}
    
    /* Dataframe styling */
    .dataframe {{
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }}
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING FUNCTION ---
month_names_to_number = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
    'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
    'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
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
            st.error(f"❌ Erro ao carregar dados: Status {response.status_code}")
            return pd.DataFrame()
        
        df = pd.read_excel(BytesIO(response.content))
        
        # Column mapping
        col_mappings = {
            'Mês': 'mes', 'mes': 'mes', 'MÊS': 'mes',
            'Qtd.': 'qtd', 'Qtd': 'qtd', 'qtd': 'qtd', 'QTD': 'qtd', 'Quantidade': 'qtd',
            'Ano': 'ano', 'ano': 'ano', 'ANO': 'ano',
            'Cliente': 'cliente', 'cliente': 'cliente', 'CLIENTE': 'cliente',
            'Comercial': 'comercial', 'comercial': 'comercial', 'COMERCIAL': 'comercial',
            'V. Líquido': 'v_liquido', 'V_Liquido': 'v_liquido', 'V Liquido': 'v_liquido',
            'PM': 'pm', 'pm': 'pm', 'Preço Médio': 'pm',
            'Categoria': 'categoria', 'categoria': 'categoria', 'CATEGORIA': 'categoria'
        }
        
        df = df.rename(columns=col_mappings)
        
        # Check critical columns
        critical_cols = ['mes', 'qtd', 'ano', 'cliente', 'comercial']
        missing_cols = [col for col in critical_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ Colunas em falta: {missing_cols}")
            return pd.DataFrame()
        
        # Convert month names to numbers
        if df['mes'].dtype == 'object':
            df['mes'] = df['mes'].apply(lambda x: month_names_to_number.get(str(x).strip(), np.nan))
        else:
            df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
        
        # Convert numeric columns
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')
        if 'v_liquido' in df.columns:
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')
        
        # Clean data
        df = df.dropna(subset=['mes', 'qtd', 'ano', 'cliente', 'comercial'])
        df = df[(df['mes'] >= 1) & (df['mes'] <= 12)]
        
        return df
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# Load data
df = carregar_dados()

if df.empty:
    st.error("❌ Não foi possível carregar os dados. Verifique a conexão e o URL.")
    st.stop()

# --- MODERN SIDEBAR ---
st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 30px 0;">
        <div style="font-size: 2.5em; margin-bottom: 10px;">📊</div>
        <h1 style="color: white; margin: 0; font-size: 1.8em; font-weight: 700;">Business Intelligence</h1>
        <p style="color: rgba(255, 255, 255, 0.8); margin: 5px 0 0 0; font-size: 0.9em;">Dashboard Analítico</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div style='height: 2px; background: rgba(255,255,255,0.3); margin: 20px 0;'></div>", unsafe_allow_html=True)

# Navigation
pagina = st.sidebar.radio("**🌐 NAVEGAÇÃO**", [
    "📊 VISÃO GERAL", 
    "🎯 KPIS PERSONALIZADOS", 
    "📈 TENDÊNCIAS", 
    "⚠️ ALERTAS",
    "👥 ANÁLISE DE CLIENTES",
    "🔍 VISTA COMPARATIVA"
], key="navigation")

st.sidebar.markdown("<div style='height: 2px; background: rgba(255,255,255,0.3); margin: 20px 0;'></div>", unsafe_allow_html=True)

# Filters
st.sidebar.markdown("### 🔍 FILTROS")
st.sidebar.markdown("<p style='color: rgba(255,255,255,0.7); font-size: 0.9em;'>Filtre os dados conforme necessário</p>", unsafe_allow_html=True)

# Filter functions
def get_filtro_opcoes(dados, ano, comercial, cliente):
    temp = dados.copy()
    if ano != "Todos":
        temp = temp[temp['ano'] == int(ano)]
    if comercial != "Todos":
        temp = temp[temp['comercial'].astype(str) == str(comercial)]
    if cliente != "Todos":
        temp = temp[temp['cliente'].astype(str) == str(cliente)]
    
    anos = sorted([int(x) for x in temp['ano'].dropna().unique()])
    comerciais = sorted(list(temp['comercial'].dropna().unique()))
    clientes = sorted(list(temp['cliente'].dropna().unique()))
    categorias = sorted(list(temp['categoria'].dropna().unique())) if 'categoria' in temp.columns else []
    
    return anos, comerciais, clientes, categorias

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

# Get initial options
anos_disponiveis, comerciais_disponiveis, clientes_disponiveis, categorias_disponiveis = get_filtro_opcoes(df, "Todos", "Todos", "Todos")

# Filters
ano = st.sidebar.selectbox("**📅 ANO**", ["Todos"] + anos_disponiveis)
_, comerciais_for_year, _, _ = get_filtro_opcoes(df, ano, "Todos", "Todos")
comercial = st.sidebar.selectbox("**👨‍💼 COMERCIAL**", ["Todos"] + comerciais_for_year)
_, _, clientes_for_filters, _ = get_filtro_opcoes(df, ano, comercial, "Todos")
cliente = st.sidebar.selectbox("**🏢 CLIENTE**", ["Todos"] + clientes_for_filters)
_, _, _, categorias_for_filters = get_filtro_opcoes(df, ano, comercial, cliente)
categoria = st.sidebar.selectbox("**📦 CATEGORIA**", ["Todas"] + categorias_for_filters)

# Apply filters
dados_filtrados = aplicar_filtros(df, ano, comercial, cliente, categoria)

# Export function
def gerar_excel(dados):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dados.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

# Chart settings
color_scale_modern = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
month_names_pt = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}

# --- PAGE 1: MODERN OVERVIEW ---
if pagina == "📊 VISÃO GERAL":
    st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <h1>📊 DASHBOARD ANALÍTICO</h1>
            <p style="font-size: 1.2em; color: #64748b; font-weight: 500;">Visão Geral de Performance Comercial</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_qty = dados_filtrados['qtd'].sum()
    total_value = dados_filtrados['v_liquido'].sum() if 'v_liquido' in dados_filtrados.columns else 0
    num_customers = dados_filtrados['cliente'].nunique()
    num_commercials = dados_filtrados['comercial'].nunique()
    
    with col1:
        st.metric(
            label="📦 QUANTIDADE TOTAL", 
            value=f"{total_qty:,.0f}",
            delta=None
        )
    with col2:
        st.metric(
            label="💰 VALOR TOTAL", 
            value=f"€ {total_value:,.0f}" if total_value > 0 else "N/A",
            delta=None
        )
    with col3:
        st.metric(
            label="👥 CLIENTES ÚNICOS", 
            value=f"{num_customers}",
            delta=None
        )
    with col4:
        st.metric(
            label="👨‍💼 COMERCIAIS", 
            value=f"{num_commercials}",
            delta=None
        )
    
    st.markdown("---")
    
    # Top Customers
    st.markdown("### 🏆 TOP 10 CLIENTES")
    top_clientes = dados_filtrados.groupby('cliente')[['qtd', 'v_liquido']].sum().sort_values('qtd', ascending=False).head(10)
    
    fig_top = px.bar(
        top_clientes.reset_index(),
        x='cliente',
        y='qtd',
        color='v_liquido',
        title='',
        labels={'qtd': 'Quantidade', 'cliente': 'Cliente', 'v_liquido': 'Valor (€)'},
        color_continuous_scale='Viridis',
        text='qtd'
    )
    fig_top.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside',
        marker_line_color='white',
        marker_line_width=2
    )
    fig_top.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color="#1e293b", size=12),
        xaxis_tickangle=-45,
        showlegend=False,
        height=500
    )
    st.plotly_chart(fig_top, use_container_width=True)
    
    # Commercial and Category Performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👨‍💼 PERFORMANCE COMERCIAL")
        kpi_comercial = dados_filtrados.groupby('comercial')[['qtd', 'v_liquido']].sum().sort_values('qtd', ascending=False).head(8)
        
        fig_comercial = px.pie(
            kpi_comercial.reset_index(),
            values='qtd',
            names='comercial',
            title='',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_comercial.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color="#1e293b", size=12),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="auto",
                y=1,
                xanchor="left",
                x=1.1
            )
        )
        st.plotly_chart(fig_comercial, use_container_width=True)
    
    with col2:
        if 'categoria' in dados_filtrados.columns and not dados_filtrados['categoria'].isna().all():
            st.markdown("### 📊 PERFORMANCE POR CATEGORIA")
            kpi_categoria = dados_filtrados.groupby('categoria')[['qtd', 'v_liquido']].sum().sort_values('qtd', ascending=False).head(6)
            
            fig_categoria = px.bar(
                kpi_categoria.reset_index(),
                x='categoria',
                y='qtd',
                color='qtd',
                title='',
                labels={'qtd': 'Quantidade', 'categoria': 'Categoria'},
                color_continuous_scale='Plasma'
            )
            fig_categoria.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color="#1e293b", size=12),
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_categoria, use_container_width=True)

# --- PAGE 2: MODERN CUSTOM KPIs ---
elif pagina == "🎯 KPIS PERSONALIZADOS":
    st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <h1>🎯 KPIS PERSONALIZADOS</h1>
            <p style="font-size: 1.2em; color: #64748b; font-weight: 500;">Crie e analise métricas personalizadas</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        kpi_name = st.text_input("**📝 NOME DO KPI**", value="Performance de Vendas")
    
    with col2:
        kpi_period = st.selectbox("**📅 PERÍODO**", ["Mensal", "Trimestral", "Anual"])
        show_trend = st.checkbox("📈 Mostrar Tendência", value=True)
    
    if dados_filtrados.empty:
        st.warning("⚠️ Sem dados disponíveis para os filtros selecionados.")
    else:
        # KPI Data
        kpi_data = dados_filtrados.groupby('mes')['qtd'].sum().reset_index()
        kpi_data.columns = ['mes', 'value']
        kpi_data = kpi_data.sort_values('mes')
        kpi_data['month_name'] = kpi_data['mes'].map(month_names_pt)
        
        # Modern KPI Chart
        fig_kpi = px.line(
            kpi_data,
            x='month_name',
            y='value',
            title=f"📊 {kpi_name} - Evolução Mensal",
            labels={'value': 'Quantidade', 'month_name': 'Mês'},
            color_discrete_sequence=[primary_color]
        )
        
        fig_kpi.update_traces(
            line=dict(width=4),
            marker=dict(size=8, line=dict(width=2, color='white'))
        )
        
        fig_kpi.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color="#1e293b", size=12),
            xaxis=dict(showgrid=True, gridcolor='#e2e8f0'),
            yaxis=dict(showgrid=True, gridcolor='#e2e8f0'),
            height=500
        )
        
        st.plotly_chart(fig_kpi, use_container_width=True)
        
        # KPI Statistics
        st.markdown("### 📊 ESTATÍSTICAS DO KPI")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("🎯 Máximo", f"{kpi_data['value'].max():,.0f}")
        col2.metric("📉 Mínimo", f"{kpi_data['value'].min():,.0f}")
        col3.metric("📊 Média", f"{kpi_data['value'].mean():,.0f}")
        col4.metric("📈 Mediana", f"{kpi_data['value'].median():,.0f}")

# --- PAGE 3: MODERN TRENDS ---
elif pagina == "📈 TENDÊNCIAS":
    st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <h1>📈 ANÁLISE DE TENDÊNCIAS</h1>
            <p style="font-size: 1.2em; color: #64748b; font-weight: 500;">Identifique padrões e tendências nos dados</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        trend_window = st.slider("**📊 PERÍODO MÉDIA MÓVEL**", 1, 6, 2)
    
    with col2:
        show_forecast = st.checkbox("🔮 Mostrar Previsão", value=False)
    
    if dados_filtrados.empty:
        st.warning("⚠️ Sem dados disponíveis para os filtros selecionados.")
    else:
        # Trend Analysis
        trend_data = dados_filtrados.groupby('mes')['qtd'].sum().reset_index()
        trend_data.columns = ['mes', 'value']
        trend_data = trend_data.sort_values('mes')
        trend_data['month_name'] = trend_data['mes'].map(month_names_pt)
        
        if len(trend_data) > 1:
            trend_data['MA'] = trend_data['value'].rolling(window=trend_window, center=True).mean()
            
            # Modern Trend Chart - CORRIGIDO
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=trend_data['month_name'],
                y=trend_data['value'],
                mode='lines+markers',
                name='Valor Real',
                line=dict(color=primary_color, width=4),
                marker=dict(size=10, color=primary_color, line=dict(width=2, color='white'))
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=trend_data['month_name'],
                y=trend_data['MA'],
                mode='lines',
                name=f'Média Móvel ({trend_window} meses)',
                line=dict(color=accent_color, width=3, dash='dash')
            ))
            
            fig_trend.update_layout(
                title="📈 Evolução Temporal - Quantidade de Vendas",
                xaxis_title="Mês",
                yaxis_title="Quantidade",
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color="#1e293b", size=12),
                hovermode='x unified',
                height=500,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)

# --- PAGE 4: MODERN ALERTS ---
elif pagina == "⚠️ ALERTAS":
    st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <h1>⚠️ SISTEMA DE ALERTAS</h1>
            <p style="font-size: 1.2em; color: #64748b; font-weight: 500;">Monitorize desempenhos críticos</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Alert Analysis
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
    
    # Status Overview
    st.markdown("### 📊 VISÃO GERAL DE STATUS")
    col1, col2, col3 = st.columns(3)
    
    excellent = len(analise_clientes[analise_clientes['Status'] == '🟢 Excelente'])
    warning = len(analise_clientes[analise_clientes['Status'] == '🟡 Atenção'])
    critical = len(analise_clientes[analise_clientes['Status'] == '🔴 Crítico'])
    
    col1.metric("🟢 EXCELENTE", excellent, delta_color="off")
    col2.metric("🟡 ATENÇÃO", warning, delta_color="off")
    col3.metric("🔴 CRÍTICO", critical, delta_color="off")
    
    # Critical Alerts
    st.markdown("### 🔴 ALERTAS CRÍTICOS")
    criticos = analise_clientes[analise_clientes['Status'] == '🔴 Crítico']
    
    if not criticos.empty:
        st.error(f"🚨 {len(criticos)} clientes necessitam de atenção imediata!")
        
        # Display critical clients
        for _, cliente in criticos.head(5).iterrows():
            with st.container():
                st.markdown(f"""
                    <div style="background: #fef2f2; 
                                padding: 15px; border-radius: 10px; margin: 10px 0; 
                                border-left: 4px solid #ef4444;">
                        <h4 style="margin: 0; color: #dc2626;">🔴 {cliente['Cliente']}</h4>
                        <p style="margin: 5px 0; color: #991b1b;">
                            Média: {cliente['Avg_Qtd']:,.0f} | Transações: {cliente['Transactions']}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.success("🎉 Todos os clientes estão com desempenho satisfatório!")

# --- PAGE 5: CUSTOMER ANALYSIS ---
elif pagina == "👥 ANÁLISE DE CLIENTES":
    st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <h1>👥 ANÁLISE DE CLIENTES</h1>
            <p style="font-size: 1.2em; color: #64748b; font-weight: 500;">Análise detalhada por cliente</p>
        </div>
    """, unsafe_allow_html=True)
    
    if cliente == "Todos":
        st.info("👈 Selecione um cliente específico no painel lateral para análise detalhada")
    else:
        cliente_data = dados_filtrados[dados_filtrados['cliente'] == cliente]
        
        if cliente_data.empty:
            st.warning("❌ Dados não disponíveis para o cliente selecionado")
        else:
            # Customer Profile
            st.markdown(f"### 📊 PERFIL DO CLIENTE: **{cliente}**")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📦 Quantidade Total", f"{cliente_data['qtd'].sum():,.0f}")
            col2.metric("💰 Valor Total", f"€ {cliente_data['v_liquido'].sum():,.0f}")
            col3.metric("📊 Média por Transação", f"{cliente_data['qtd'].mean():,.0f}")
            col4.metric("🔄 Transações", len(cliente_data))
            
            # Customer Trend
            st.markdown("### 📈 EVOLUÇÃO DO CLIENTE")
            historico = cliente_data.groupby(['ano', 'mes']).agg({'qtd': 'sum'}).reset_index()
            historico['month_name'] = historico['mes'].map(month_names_pt)
            historico = historico.sort_values(['ano', 'mes'])
            
            fig_historico = px.line(
                historico,
                x='month_name',
                y='qtd',
                markers=True,
                title=f"Desempenho Mensal - {cliente}",
                labels={'qtd': 'Quantidade', 'month_name': 'Mês'},
                color_discrete_sequence=[primary_color]
            )
            fig_historico.update_traces(
                line=dict(width=3),
                marker=dict(size=8)
            )
            fig_historico.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color="#1e293b", size=12),
                hovermode='x unified',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_historico, use_container_width=True)

# --- PAGE 6: COMPARATIVE VIEW ---
else:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <h1>🔍 VISTA COMPARATIVA</h1>
            <p style="font-size: 1.2em; color: #64748b; font-weight: 500;">Compare métricas entre diferentes categorias</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        comp_metric1 = st.selectbox("**📊 MÉTRICA**", ["qtd", "v_liquido", "pm"])
        comp_groupby1 = st.selectbox("**🗂️ AGRUPAR POR**", ["cliente", "comercial", "categoria"])
    
    with col2:
        comp_top = st.slider("**🔝 TOP N ITENS**", 5, 20, 10)
        show_pie = st.checkbox("🍕 Mostrar Gráfico de Pizza", value=True)
    
    # Get top items
    top_items = dados_filtrados.groupby(comp_groupby1)[comp_metric1].sum().nlargest(comp_top)
    
    if show_pie:
        # Comparative visualization
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
                marker=dict(color=color_scale_modern),
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
                marker=dict(colors=color_scale_modern)
            ),
            row=1, col=2
        )
        
        fig_comp.update_layout(
            height=500, 
            showlegend=False, 
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color="#1e293b", size=12)
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
            color_continuous_scale='Viridis',
            text=comp_metric1
        )
        fig_single.update_traces(
            texttemplate='%{text:,.0f}',
            textposition='outside'
        )
        fig_single.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color="#1e293b", size=12),
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_single, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.9em; padding: 20px;">
        <p>📊 Business Intelligence Dashboard • Desenvolvido com Streamlit</p>
    </div>
""", unsafe_allow_html=True)
