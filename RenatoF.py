import streamlit as st
import pandas as pd
from io import BytesIO

# CSS ultra-otimizado para mobile
st.markdown("""
<style>
    /* Reset e configurações base para mobile */
    * {
        box-sizing: border-box;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .header-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.8rem;
        flex-wrap: wrap;
    }
    
    .logo-img {
        height: 45px;
        border-radius: 8px;
    }
    
    .title-container h1 {
        margin: 0;
        font-size: 1.6rem !important;
        line-height: 1.2;
    }
    
    /* Cards compactos para mobile */
    .metric-card {
        padding: 0.8rem;
        border-radius: 12px;
        color: white;
        margin: 0.3rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card-blue { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .metric-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .metric-card-orange { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); }
    .metric-card-red { background: linear-gradient(135deg, #ff5858 0%, #f09819 100%); }
    .metric-card-green { background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%); }
    
    /* Sidebar mobile-first */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.8rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 0.8rem;
        text-align: center;
        font-size: 0.9rem;
    }
    
    /* Botões otimizados para touch */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        min-height: 48px;
        font-size: 0.9rem;
    }
    
    /* Inputs mobile-friendly */
    .stMultiSelect, .stSelectbox {
        font-size: 0.9rem;
    }
    
    .stMultiSelect div div, .stSelectbox div div {
        min-height: 48px;
        border-radius: 10px;
    }
    
    /* Tabs responsivas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        padding: 0 0.8rem;
        font-size: 0.8rem;
    }
    
    /* Mobile-specific styles */
    @media (max-width: 768px) {
        /* Ajustes gerais */
        .main-header {
            padding: 0.8rem;
            margin-bottom: 0.8rem;
        }
        
        .logo-img {
            height: 40px;
        }
        
        .title-container h1 {
            font-size: 1.4rem !important;
        }
        
        /* Sidebar full-screen no mobile */
        section[data-testid="stSidebar"] {
            width: 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
        }
        
        /* Cards em coluna única no mobile */
        .metric-card {
            margin: 0.2rem 0;
            padding: 0.7rem;
            min-height: 70px;
        }
        
        /* Melhorar espaçamento entre elementos */
        .element-container {
            margin-bottom: 0.8rem !important;
        }
        
        /* Textos menores mas legíveis */
        .stMarkdown h1 {
            font-size: 1.5rem !important;
        }
        
        .stMarkdown h2 {
            font-size: 1.3rem !important;
        }
        
        .stMarkdown h3 {
            font-size: 1.1rem !important;
        }
        
        /* Dataframes scrolláveis */
        .dataframe {
            font-size: 0.8rem;
        }
        
        /* Expanders mais fáceis de tocar */
        .streamlit-expanderHeader {
            font-size: 0.9rem;
            padding: 0.8rem;
            min-height: 48px;
        }
    }
    
    /* Melhorias para telas muito pequenas */
    @media (max-width: 480px) {
        .header-content {
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .title-container h1 {
            font-size: 1.3rem !important;
        }
        
        .logo-img {
            height: 35px;
        }
        
        .metric-card {
            min-height: 65px;
            padding: 0.6rem;
        }
    }
    
    /* Scroll suave para mobile */
    html {
        scroll-behavior: smooth;
    }
    
    /* Esconder elementos desnecessários no mobile */
    @media (max-width: 768px) {
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Remover sombras complexas no mobile para performance */
        .metric-card, .main-header, .sidebar-header {
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
    }
    
    /* Banner de ajuda para mobile */
    .mobile-help {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .mobile-help-icon {
        font-size: 1.2rem;
    }
    
    /* Loading otimizado */
    .stSpinner > div {
        border-color: #667eea transparent transparent transparent !important;
    }
    
    /* Melhorias de performance */
    .metric-card h3, .metric-card p {
        margin: 0;
        line-height: 1.3;
    }
    
    .metric-card h3 {
        font-size: 0.75rem;
        opacity: 0.9;
    }
    
    .metric-card p {
        font-size: 0.9rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 🚀 Configuração da página mobile-first
st.set_page_config(
    page_title="Renato Ferreira",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={}
)

# Header compacto para mobile
st.markdown("""
<div class="main-header">
    <div class="header-content">
        <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" 
             class="logo-img" 
             alt="Bracar Logo">
        <div class="title-container">
            <h1>RENATO FERREIRA</h1>
            <p style="margin:0; opacity: 0.9; font-size: 0.9rem;">Dashboard de Alertas</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Banner de ajuda super visível
st.markdown("""
<div class="mobile-help">
    <span class="mobile-help-icon">👆</span>
    <span><strong>Toque no menu ☰ para filtrar dados</strong></span>
</div>
""", unsafe_allow_html=True)

# 📥 Carregar dados com loading otimizado
with st.spinner('📊 A carregar dados...'):
    url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/RFerreira.xlsx"
    try:
        df = pd.read_excel(url)
    except Exception as e:
        st.error(f"❌ Erro ao carregar: {e}")
        st.stop()

# 🧼 Limpar dados
df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
df.dropna(subset=['Dias'], inplace=True)

# 📅 Intervalos
ranges = [
    (0, 15, "0-15 dias", "metric-card-blue"),
    (16, 30, "16-30 dias", "metric-card"),
    (31, 60, "31-60 dias", "metric-card-orange"),
    (61, 90, "61-90 dias", "metric-card-orange"),
    (91, 365, "91-365 dias", "metric-card-red")
]

# 🎛️ Sidebar mobile-optimized
with st.sidebar:
    st.markdown('<div class="sidebar-header">🎯 FILTROS</div>', unsafe_allow_html=True)
    
    # Filtros com labels compactos
    selected_comercial = st.multiselect(
        "👤 Comercial",
        options=sorted(df['Comercial'].unique()),
        default=sorted(df['Comercial'].unique()),
        key="comercial_mobile"
    )
    
    selected_entidade = st.multiselect(
        "🏛️ Entidade",
        options=sorted(df['Entidade'].unique()),
        default=sorted(df['Entidade'].unique()),
        key="entidade_mobile"
    )
    
    selected_ranges = st.multiselect(
        "📅 Dias",
        options=[r[2] for r in ranges],
        default=[r[2] for r in ranges],
        key="ranges_mobile"
    )
    
    # Botões de ação
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.rereun()
    with col2:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.rerun()
    
    # Stats rápidas
    st.markdown("---")
    st.markdown("**📊 Estatísticas**")
    total_registros = len(df)
    st.metric("Total", f"{total_registros:,}")

# Container principal otimizado
with st.container():
    # Status de atualização compacto
    st.markdown(f"""
    <div class="metric-card-green" style="text-align: center; padding: 0.6rem;">
        <p style="margin:0; font-size: 0.8rem;">🔄 Atualizado</p>
        <p style="margin:0; font-size: 0.9rem; font-weight: bold;">{pd.Timestamp.now().strftime('%d/%m/%Y')}</p>
    </div>
    """, unsafe_allow_html=True)

# 🔍 Filtrar dados
filtered_df = df[
    df['Comercial'].isin(selected_comercial) &
    df['Entidade'].isin(selected_entidade)
]

# 📋 Resumo com cards responsivos
st.subheader("📈 Resumo por Intervalo")

if not filtered_df.empty:
    # Cards em grid responsivo
    summary_data = []
    for low, high, label, card_class in ranges:
        if label in selected_ranges:
            range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
            count = len(range_df)
            total_value = range_df['Valor Pendente'].sum() if 'Valor Pendente' in range_df.columns else 0
            summary_data.append({
                "label": label,
                "count": count,
                "value": total_value,
                "card_class": card_class
            })
    
    # Layout responsivo - 2 colunas no mobile
    cols = st.columns(2)
    for idx, data in enumerate(summary_data):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="{data['card_class']}">
                <h3>{data['label']}</h3>
                <p>{data['count']} registos</p>
                <p style="font-size: 0.7rem;">€{data['value']:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 📊 Detalhes com accordion mobile-friendly
    st.subheader("📋 Detalhes por Intervalo")
    
    for low, high, label, card_class in ranges:
        if label in selected_ranges:
            with st.expander(f"{label} ({len(filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)])} registos)", expanded=False):
                range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
                if not range_df.empty:
                    # Métricas compactas
                    mcol1, mcol2, mcol3 = st.columns(3)
                    with mcol1:
                        st.metric("Qtd", len(range_df))
                    with mcol2:
                        valor_total = range_df['Valor Pendente'].sum() if 'Valor Pendente' in range_df.columns else 0
                        st.metric("Valor", f"€{valor_total:,.0f}")
                    with mcol3:
                        st.metric("Média", f"{range_df['Dias'].mean():.0f}d")
                    
                    # Tabela scrollável
                    st.dataframe(
                        range_df, 
                        use_container_width=True,
                        height=300
                    )
                else:
                    st.info("📭 Sem dados neste intervalo")

    # 📥 Download otimizado
    st.subheader("📤 Exportar Dados")
    
    if not filtered_df.empty:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Dados_Filtrados')
        
        st.download_button(
            label="💾 BAIXAR EXCEL",
            data=output.getvalue(),
            file_name=f"alertas_renato_ferreira_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        st.success(f"✅ {len(filtered_df)} registos prontos para exportar")
    else:
        st.warning("📭 Nenhum dado para exportar")

else:
    st.warning("🔍 Nenhum resultado com os filtros atuais")

# Footer mobile-optimized
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem; margin-top: 2rem; padding: 1rem;">
    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.5rem; flex-wrap: wrap;">
        <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" 
             style="height: 25px; border-radius: 4px;" 
             alt="Bracar">
        <span>Feito com ❤️ em Streamlit</span>
    </div>
    <div>Dashboard Renato Ferreira - Otimizado para mobile</div>
</div>
""", unsafe_allow_html=True)

# Script JavaScript para melhorias mobile
st.markdown("""
<script>
// Melhorias para mobile
if (window.innerWidth <= 768) {
    // Fechar sidebar após seleção (opcional)
    setTimeout(() => {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.width = '0';
        }
    }, 3000);
    
    // Melhorar scroll em tables
    const tables = document.querySelectorAll('.dataframe');
    tables.forEach(table => {
        table.style.fontSize = '12px';
    });
}
</script>
""", unsafe_allow_html=True)
