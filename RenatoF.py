import streamlit as st
import pandas as pd
from io import BytesIO

# CSS personalizado otimizado para mobile com colunas compactas
st.markdown("""
<style>
    /* Reset e configurações mobile */
    * {
        box-sizing: border-box;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        color: white;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .header-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.3rem;
    }
    
    .logo-img {
        height: 35px;
        border-radius: 6px;
    }
    
    .title-container h1 {
        margin: 0;
        font-size: 1.2rem !important;
        line-height: 1.2;
    }
    
    .title-container p {
        margin: 0;
        font-size: 0.75rem !important;
        opacity: 0.9;
    }
    
    /* Cards compactos */
    .metric-card {
        padding: 0.6rem;
        border-radius: 8px;
        color: white;
        margin: 0.2rem 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        text-align: center;
        min-height: 60px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .metric-card-orange {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
    }
    
    .metric-card-red {
        background: linear-gradient(135deg, #ff5858 0%, #f09819 100%);
    }
    
    .metric-card-green {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
    }
    
    .metric-card h3 {
        margin: 0;
        font-size: 0.65rem !important;
        line-height: 1.1;
        font-weight: 600;
    }
    
    .metric-card p {
        margin: 0.1rem 0 0 0;
        font-size: 0.85rem !important;
        font-weight: bold;
        line-height: 1.1;
    }
    
    .metric-card .value-small {
        font-size: 0.6rem !important;
        margin-top: 0.1rem;
        opacity: 0.9;
    }
    
    /* Sidebar compacto */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.6rem;
        border-radius: 6px;
        color: white;
        margin-bottom: 0.8rem;
        text-align: center;
        font-size: 0.75rem;
    }
    
    /* Botões compactos */
    .stButton button {
        border: none;
        padding: 0.5rem 0.8rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.75rem;
        width: 100%;
        margin: 0.1rem 0;
        min-height: 36px;
    }
    
    /* Inputs compactos */
    .stMultiSelect, .stSelectbox {
        font-size: 0.75rem;
    }
    
    .stMultiSelect div div, .stSelectbox div div {
        min-height: 36px;
        padding: 0.3rem 0.5rem;
    }
    
    /* Dataframes compactos */
    .dataframe {
        font-size: 0.7rem !important;
        border-radius: 6px;
    }
    
    /* Ajustar headers de dataframe */
    .dataframe thead th {
        font-size: 0.65rem !important;
        padding: 0.2rem 0.3rem !important;
    }
    
    .dataframe tbody td {
        font-size: 0.65rem !important;
        padding: 0.2rem 0.3rem !important;
        line-height: 1.1;
    }
    
    /* Expanders compactos */
    .streamlit-expanderHeader {
        font-size: 0.75rem !important;
        padding: 0.5rem 0.8rem;
    }
    
    /* Alertas compactos */
    .stAlert {
        border-radius: 6px;
        padding: 0.5rem 0.8rem;
        font-size: 0.75rem;
    }
    
    /* Métricas compactas */
    [data-testid="metric-container"] {
        padding: 0.5rem 0.6rem !important;
    }
    
    [data-testid="metric-label"] {
        font-size: 0.7rem !important;
    }
    
    [data-testid="metric-value"] {
        font-size: 0.9rem !important;
    }
    
    [data-testid="metric-delta"] {
        font-size: 0.65rem !important;
    }
    
    /* Mobile tip compacto */
    .mobile-tip {
        text-align: center;
        font-size: 0.7rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 0.5rem 0.6rem;
        border-radius: 6px;
        margin-bottom: 0.8rem;
        border-left: 3px solid #667eea;
        line-height: 1.2;
    }
    
    /* Footer compacto */
    .custom-footer {
        text-align: center;
        font-size: 0.65rem;
        margin-top: 1rem;
        padding: 0.6rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 6px;
        line-height: 1.2;
    }
    
    /* Tabs compactos */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 35px;
        padding: 0 0.8rem;
        font-size: 0.7rem;
    }
    
    /* Subheaders compactos */
    .stSubheader {
        font-size: 0.9rem !important;
        padding: 0.3rem 0 !important;
    }
    
    /* Ocultar elementos desktop */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Media queries para telas muito pequenas */
    @media (max-width: 480px) {
        .main-header {
            padding: 0.5rem;
        }
        
        .logo-img {
            height: 30px;
        }
        
        .title-container h1 {
            font-size: 1rem !important;
        }
        
        .title-container p {
            font-size: 0.65rem !important;
        }
        
        .metric-card {
            padding: 0.4rem;
            min-height: 50px;
        }
        
        .metric-card h3 {
            font-size: 0.6rem !important;
        }
        
        .metric-card p {
            font-size: 0.75rem !important;
        }
        
        .metric-card .value-small {
            font-size: 0.55rem !important;
        }
    }
    
    /* Melhorias para touch em elementos pequenos */
    .stButton button, .stDownloadButton button {
        min-height: 36px;
    }
    
    /* Sidebar mobile friendly compacto */
    section[data-testid="stSidebar"] {
        min-width: 250px !important;
        max-width: 250px !important;
    }
    
    /* Espaçamento entre seções */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Linhas divisórias mais finas */
    hr {
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 🚀 Page configuration super compacta para mobile
st.set_page_config(
    page_title="Bruno Brito",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Dashboard Mobile Compacto"
    }
)

# Header principal super compacto
st.markdown("""
<div class="main-header">
    <div class="header-content">
        <div class="logo-container">
            <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" 
                 class="logo-img" 
                 alt="Bracar Logo">
        </div>
        <div class="title-container">
            <h1>BRUNO BRITO</h1>
            <p>Gestão de Alertas</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 📱 Mobile tip compacto
st.markdown("""
<div class="mobile-tip">
    📱 <strong>Versão Mobile Compacta</strong><br>Toque no menu ≡ para filtrar
</div>
""", unsafe_allow_html=True)

# 📥 Load data
url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/BBrito.xlsx"
try:
    df = pd.read_excel(url)
except Exception as e:
    st.error(f"❌ Erro: {e}")
    st.stop()

# 🧼 CLEAN DATA
df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
df.dropna(subset=['Dias'], inplace=True)

# Converter colunas problemáticas
problem_columns = ['Série', 'N.º Doc.', 'N.º Cliente', 'N.º Fornecedor']
for col in problem_columns:
    if col in df.columns:
        df[col] = df[col].astype(str)

# Colunas numéricas
numeric_columns = ['Valor Pendente', 'Valor Liquidado', 'Valor Pago']
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 📅 Ranges compactos
ranges = [
    (0, 15, "0-15d", "metric-card-blue"),
    (16, 30, "16-30d", "metric-card"),
    (31, 60, "31-60d", "metric-card-orange"),
    (61, 90, "61-90d", "metric-card-orange"),
    (91, 365, "91+d", "metric-card-red")
]

# 🎛️ Sidebar super compacto
with st.sidebar:
    st.markdown('<div class="sidebar-header">🎛️ FILTROS</div>', unsafe_allow_html=True)
    
    selected_comercial = st.multiselect(
        "👨‍💼 Comercial",
        options=sorted(df['Comercial'].unique()),
        default=sorted(df['Comercial'].unique())
    )
    
    selected_entidade = st.multiselect(
        "🏢 Entidade",
        options=sorted(df['Entidade'].unique()),
        default=sorted(df['Entidade'].unique())
    )
    
    selected_ranges = st.multiselect(
        "📅 Dias",
        options=[r[2] for r in ranges],
        default=[r[2] for r in ranges]
    )
    
    # Estatísticas rápidas
    st.markdown("---")
    st.markdown("**📊 Stats**")
    total_registros = len(df)
    st.metric("Total", f"{total_registros:,}")

# 🔍 Filter data
filtered_df = df[
    df['Comercial'].isin(selected_comercial) &
    df['Entidade'].isin(selected_entidade)
]

# 📊 Container principal super compacto
st.subheader("📈 Visão Geral")

# Cards métricos em grid 2 colunas
summary_data = []
for low, high, label, card_class in ranges:
    if label in selected_ranges:
        range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
        count = len(range_df)
        total_value = range_df['Valor Pendente'].sum() if 'Valor Pendente' in filtered_df.columns else 0
        summary_data.append({
            "Intervalo": label,
            "Quantidade": count,
            "Valor Pendente": total_value,
            "card_class": card_class
        })

# Grid 2 colunas sempre
if summary_data:
    cols = st.columns(2)
    
    for i, data in enumerate(summary_data):
        col_idx = i % 2
        with cols[col_idx]:
            st.markdown(f"""
            <div class="{data['card_class']}">
                <h3>{data['Intervalo']}</h3>
                <p>{data['Quantidade']}</p>
                <p class="value-small">€{data['Valor Pendente']:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)

# 📋 Estatísticas rápidas
col1, col2 = st.columns(2)
with col1:
    total_filtrado = len(filtered_df)
    st.metric("📋 Filtrados", f"{total_filtrado:,}")

with col2:
    valor_total = filtered_df['Valor Pendente'].sum() if 'Valor Pendente' in filtered_df.columns else 0
    st.metric("💰 Valor", f"€{valor_total:,.0f}")

# 🔍 Detalhes com tabs compactos
st.subheader("🔍 Detalhes")

# Usar tabs para melhor organização
tab_labels = [data["Intervalo"] for data in summary_data]
if tab_labels:
    tabs = st.tabs(tab_labels)

    for tab, data in zip(tabs, summary_data):
        with tab:
            low, high = next((r[0], r[1]) for r in ranges if r[2] == data["Intervalo"])
            range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
            
            if not range_df.empty:
                # Métricas ultra compactas
                mcol1, mcol2 = st.columns(2)
                with mcol1:
                    st.metric("Reg", len(range_df))
                    st.metric("Méd", f"{range_df['Dias'].mean():.0f}")
                
                with mcol2:
                    valor_tab = range_df['Valor Pendente'].sum() if 'Valor Pendente' in range_df.columns else 0
                    st.metric("Valor", f"€{valor_tab:,.0f}")
                
                # Tabela super compacta - apenas colunas essenciais
                display_df = range_df[['Comercial', 'Dias', 'Valor Pendente']].head(8)
                display_df['Valor Pendente'] = display_df['Valor Pendente'].apply(lambda x: f"€{x:,.0f}" if pd.notnull(x) else "€0")
                
                st.dataframe(display_df, width='stretch')
                
                if len(range_df) > 8:
                    st.caption(f"Mostrando 8 de {len(range_df)}")
                
            else:
                st.info("ℹ️ Sem dados")

# 📥 Exportação compacta
st.subheader("💾 Exportar")

if not filtered_df.empty:
    export_df = filtered_df.copy()
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Dados')
    
    st.download_button(
        label=f"📥 EXCEL ({len(filtered_df)})",
        data=output.getvalue(),
        file_name=f"bbrito_{pd.Timestamp.now().strftime('%d%m%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width='stretch'
    )
    
else:
    st.warning("⚠️ Sem dados")

# 🔄 Refresh compacto
refresh_col1, refresh_col2, refresh_col3 = st.columns([1, 2, 1])
with refresh_col2:
    if st.button("🔄 Atualizar", width='stretch'):
        st.rerun()

# ❤️ Footer super compacto
st.markdown("""
<div class="custom-footer">
    <div style="display: flex; flex-direction: column; align-items: center; gap: 0.3rem;">
        <div style="display: flex; align-items: center; gap: 0.3rem;">
            <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" 
                 style="height: 20px; border-radius: 3px;" 
                 alt="Bracar">
            <span>Bracar • Bruno Brito</span>
        </div>
        <div>Mobile v1.0</div>
    </div>
</div>
""", unsafe_allow_html=True)
