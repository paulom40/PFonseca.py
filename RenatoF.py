import streamlit as st
import pandas as pd
from io import BytesIO

# CSS personalizado otimizado para mobile
st.markdown("""
<style>
    /* Reset e configurações mobile */
    * {
        box-sizing: border-box;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .header-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }
    
    .logo-img {
        height: 50px;
        border-radius: 8px;
    }
    
    .title-container h1 {
        margin: 0;
        font-size: 1.5rem !important;
    }
    
    .title-container p {
        margin: 0;
        font-size: 0.9rem !important;
        opacity: 0.9;
    }
    
    /* Cards responsivos */
    .metric-card {
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.25rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
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
        font-size: 0.8rem !important;
        line-height: 1.2;
    }
    
    .metric-card p {
        margin: 0.2rem 0 0 0;
        font-size: 1rem !important;
        font-weight: bold;
    }
    
    .metric-card .value-small {
        font-size: 0.7rem !important;
        margin-top: 0.2rem;
    }
    
    /* Sidebar mobile */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.8rem;
        border-radius: 8px;
        color: white;
        margin-bottom: 1rem;
        text-align: center;
        font-size: 0.9rem;
    }
    
    /* Botões mobile */
    .stButton button {
        border: none;
        padding: 0.8rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        width: 100%;
        margin: 0.2rem 0;
    }
    
    /* Inputs mobile */
    .stMultiSelect, .stSelectbox {
        font-size: 0.9rem;
    }
    
    /* Dataframes mobile */
    .dataframe {
        font-size: 0.8rem;
        border-radius: 8px;
    }
    
    /* Expanders mobile */
    .streamlit-expanderHeader {
        font-size: 0.9rem !important;
        padding: 0.8rem 1rem;
    }
    
    /* Alertas mobile */
    .stAlert {
        border-radius: 10px;
        padding: 0.8rem;
        font-size: 0.9rem;
    }
    
    /* Mobile tip */
    .mobile-tip {
        text-align: center;
        font-size: 0.8rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    /* Footer mobile */
    .custom-footer {
        text-align: center;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 8px;
    }
    
    /* Ocultar elementos desktop */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Media queries para diferentes tamanhos de tela */
    @media (max-width: 768px) {
        .main-header {
            padding: 0.8rem;
            margin-bottom: 0.8rem;
        }
        
        .logo-img {
            height: 40px;
        }
        
        .title-container h1 {
            font-size: 1.3rem !important;
        }
        
        .metric-card {
            padding: 0.8rem;
            min-height: 70px;
        }
        
        .metric-card h3 {
            font-size: 0.75rem !important;
        }
        
        .metric-card p {
            font-size: 0.9rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            padding: 0.6rem;
        }
        
        .title-container h1 {
            font-size: 1.1rem !important;
        }
        
        .title-container p {
            font-size: 0.8rem !important;
        }
        
        .metric-card {
            padding: 0.6rem;
            min-height: 65px;
        }
    }
    
    /* Melhorias para touch */
    .stButton button, .stDownloadButton button {
        min-height: 44px; /* Tamanho mínimo para touch */
    }
    
    .stMultiSelect div div, .stSelectbox div div {
        min-height: 44px;
        display: flex;
        align-items: center;
    }
    
    /* Sidebar mobile friendly */
    section[data-testid="stSidebar"] {
        min-width: 280px !important;
        max-width: 280px !important;
    }
    
    /* Scroll suave */
    html {
        scroll-behavior: smooth;
    }
</style>
""", unsafe_allow_html=True)

# 🚀 Page configuration otimizada para mobile
st.set_page_config(
    page_title="Bruno Brito - Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Dashboard Bruno Brito - Versão Mobile"
    }
)

# Header principal otimizado para mobile
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
            <p>Dashboard de Gestão de Alertas</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 📱 Mobile tip atualizado
st.markdown("""
<div class="mobile-tip">
    📱 <strong>Versão Mobile</strong> - Toque no menu ≡ para filtrar • Use dois dedos para zoom nas tabelas
</div>
""", unsafe_allow_html=True)

# 📥 Load data
url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/BBrito.xlsx"
try:
    df = pd.read_excel(url)
except Exception as e:
    st.error(f"❌ Erro ao carregar o ficheiro: {e}")
    st.stop()

# 🧼 CLEAN DATA
df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
df.dropna(subset=['Dias'], inplace=True)

# Converter colunas problemáticas para string
problem_columns = ['Série', 'N.º Doc.', 'N.º Cliente', 'N.º Fornecedor']
for col in problem_columns:
    if col in df.columns:
        df[col] = df[col].astype(str)

# Garantir que colunas numéricas são numéricas
numeric_columns = ['Valor Pendente', 'Valor Liquidado', 'Valor Pago']
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 📅 Define ranges com cores para mobile
ranges = [
    (0, 15, "0-15 dias", "metric-card-blue"),
    (16, 30, "16-30 dias", "metric-card"),
    (31, 60, "31-60 dias", "metric-card-orange"),
    (61, 90, "61-90 dias", "metric-card-orange"),
    (91, 365, "91+ dias", "metric-card-red")
]

# 🎛️ Sidebar otimizado para mobile
with st.sidebar:
    st.markdown('<div class="sidebar-header">🎛️ FILTROS</div>', unsafe_allow_html=True)
    
    # Botão para recolher sidebar em mobile
    if st.button("📋 Mostrar/Ocultar Filtros", width='stretch'):
        st.session_state.show_filters = not st.session_state.get('show_filters', True)
    
    if st.session_state.get('show_filters', True):
        selected_comercial = st.multiselect(
            "👨‍💼 Comercial",
            options=sorted(df['Comercial'].unique()),
            default=sorted(df['Comercial'].unique()),
            help="Selecione os comerciais"
        )
        
        selected_entidade = st.multiselect(
            "🏢 Entidade",
            options=sorted(df['Entidade'].unique()),
            default=sorted(df['Entidade'].unique()),
            help="Selecione as entidades"
        )
        
        selected_ranges = st.multiselect(
            "📅 Intervalos",
            options=[r[2] for r in ranges],
            default=[r[2] for r in ranges],
            help="Selecione os intervalos de dias"
        )
    
    # Estatísticas rápidas
    st.markdown("---")
    st.markdown("**📊 Estatísticas**")
    
    total_registros = len(df)
    st.metric("Total Registros", f"{total_registros:,}")
    
    # Botão de ação rápida
    if st.button("🔄 Atualizar Dados", width='stretch'):
        st.rerun()

# 🔍 Filter data
if 'selected_comercial' in locals() and 'selected_entidade' in locals():
    filtered_df = df[
        df['Comercial'].isin(selected_comercial) &
        df['Entidade'].isin(selected_entidade)
    ]
else:
    filtered_df = df

# 📊 Container principal otimizado para mobile
st.subheader("📈 Visão Geral")

# Cards métricos em grid responsivo
summary_data = []
for low, high, label, card_class in ranges:
    if 'selected_ranges' not in locals() or label in selected_ranges:
        range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
        count = len(range_df)
        total_value = range_df['Valor Pendente'].sum() if 'Valor Pendente' in filtered_df.columns else 0
        summary_data.append({
            "Intervalo": label,
            "Quantidade": count,
            "Valor Pendente": total_value,
            "card_class": card_class
        })

# Grid responsivo - 2 colunas em mobile
if summary_data:
    cols = st.columns(2)  # Sempre 2 colunas para mobile
    
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
    
    # Estatísticas resumidas
    col1, col2 = st.columns(2)
    with col1:
        total_filtrado = len(filtered_df)
        st.metric("📋 Total Filtrado", f"{total_filtrado:,}")
    
    with col2:
        valor_total = filtered_df['Valor Pendente'].sum() if 'Valor Pendente' in filtered_df.columns else 0
        st.metric("💰 Valor Total", f"€{valor_total:,.0f}")

# 📋 Detalhes por intervalo com accordion mobile-friendly
st.subheader("🔍 Detalhes por Intervalo")

# Usar tabs para melhor organização em mobile
tabs = st.tabs([data["Intervalo"] for data in summary_data])

for tab, data in zip(tabs, summary_data):
    with tab:
        low, high = next((r[0], r[1]) for r in ranges if r[2] == data["Intervalo"])
        range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
        
        if not range_df.empty:
            # Métricas compactas
            mcol1, mcol2 = st.columns(2)
            with mcol1:
                st.metric("Registros", len(range_df))
                st.metric("Dias Médios", f"{range_df['Dias'].mean():.0f}")
            
            with mcol2:
                valor_tab = range_df['Valor Pendente'].sum() if 'Valor Pendente' in range_df.columns else 0
                st.metric("Valor Total", f"€{valor_tab:,.0f}")
                st.metric("Dias Máx", range_df['Dias'].max())
            
            # Tabela compacta
            display_df = range_df.copy()
            # Selecionar apenas colunas essenciais para mobile
            essential_cols = ['Comercial', 'Entidade', 'Dias']
            if 'Valor Pendente' in display_df.columns:
                essential_cols.append('Valor Pendente')
            
            display_df = display_df[essential_cols].head(10)  # Limitar a 10 registros em mobile
            
            st.dataframe(display_df, width='stretch')
            
            if len(range_df) > 10:
                st.info(f"📄 Mostrando 10 de {len(range_df)} registros. Use a exportação para ver todos.")
            
        else:
            st.info("ℹ️ Nenhum dado neste intervalo")

# 📥 Exportação otimizada para mobile
st.subheader("💾 Exportar Dados")

if not filtered_df.empty:
    # Preparar dados para exportação
    export_df = filtered_df.copy()
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Dados_Filtrados')
    
    # Botão de download grande para mobile
    st.download_button(
        label="📥 BAIXAR EXCEL (" + str(len(filtered_df)) + " registros)",
        data=output.getvalue(),
        file_name=f"bruno_brito_{pd.Timestamp.now().strftime('%d%m%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width='stretch',
        help="Toque para baixar o ficheiro Excel com os dados filtrados"
    )
    
    # Estatísticas de exportação
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Ficheiro Pronto", "✅")
    with col2:
        st.metric("Tamanho", f"{(len(output.getvalue()) / 1024 / 1024):.1f}MB")
        
else:
    st.warning("⚠️ Nenhum dado para exportar")

# 🔄 Botão de refresh flutuante
st.markdown("---")
refresh_col1, refresh_col2, refresh_col3 = st.columns([1, 2, 1])
with refresh_col2:
    if st.button("🔄 Atualizar Dashboard", width='stretch', type="primary"):
        st.rerun()

# ❤️ Footer otimizado para mobile
st.markdown("""
<div class="custom-footer">
    <div style="display: flex; flex-direction: column; align-items: center; gap: 0.5rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" 
                 style="height: 25px; border-radius: 4px;" 
                 alt="Bracar Logo">
            <span>Desenvolvido com ❤️</span>
        </div>
        <div style="font-size: 0.7rem; opacity: 0.7;">
            Bruno Brito - Gestão de Alertas | Mobile v1.0
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 📱 Script JavaScript para melhorias mobile
st.markdown("""
<script>
// Melhorias para experiência mobile
document.addEventListener('DOMContentLoaded', function() {
    // Prevenir zoom duplo em inputs
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('touchstart', function(e) {
            e.preventDefault();
        }, { passive: false });
    });
    
    // Melhorar scroll em tables
    const tables = document.querySelectorAll('.dataframe');
    tables.forEach(table => {
        table.style.overflowX = 'auto';
        table.style.webkitOverflowScrolling = 'touch';
    });
});
</script>
""", unsafe_allow_html=True)
