import streamlit as st
import pandas as pd
from io import BytesIO

# CSS personalizado com melhorias para mobile
st.markdown("""
<style>
    /* Gradiente principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .header-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
    }
    
    .logo-img {
        height: 50px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    .title-container {
        text-align: center;
    }
    
    /* Cards com gradiente */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-orange {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-red {
        background: linear-gradient(135deg, #ff5858 0%, #f09819 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-green {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling melhorado para mobile */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Botões modernos */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Download button específico */
    .download-btn {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%) !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Input fields styling */
    .stTextInput input, .stSelectbox div div, .stMultiSelect div div {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    
    .stTextInput input:focus, .stSelectbox div div:focus, .stMultiSelect div div:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 0.5rem;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background: white;
        border-radius: 10px;
        padding: 0 1rem;
        font-weight: 600;
        font-size: 0.8rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Alert boxes customizados */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Mobile tip styling */
    .mobile-tip {
        text-align: center;
        font-size: 14px;
        color: #666;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Footer styling */
    .custom-footer {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-top: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
    }
    
    /* Mobile-specific improvements */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .header-content {
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .logo-img {
            height: 40px;
        }
        
        .title-container h1 {
            font-size: 1.8rem !important;
        }
        
        .metric-card, .metric-card-blue, .metric-card-orange, 
        .metric-card-red, .metric-card-green {
            padding: 0.8rem;
            margin: 0.3rem 0;
        }
        
        /* Sidebar mobile improvements */
        section[data-testid="stSidebar"] {
            width: 85% !important;
            min-width: 85% !important;
            max-width: 85% !important;
        }
        
        /* Make multiselect more touch-friendly */
        .stMultiSelect div div {
            min-height: 44px;
        }
        
        /* Improve button touch targets */
        .stButton button {
            min-height: 44px;
            padding: 0.8rem 1rem;
        }
    }
    
    /* Sidebar visibility helper */
    .sidebar-helper {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 🚀 Page configuration com layout wide para mobile
st.set_page_config(
    page_title="Renato Ferreira", 
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar fechada por padrão em mobile
)

# Header principal com gradiente E LOGO DA BRACAR
st.markdown("""
<div class="main-header">
    <div class="header-content">
        <div class="logo-container">
            <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" 
                 class="logo-img" 
                 alt="Bracar Logo">
        </div>
        <div class="title-container">
            <h1 style="margin:0; font-size: 2.2rem;">RENATO FERREIRA</h1>
            <p style="margin:0; opacity: 0.9; font-size: 1rem;">Dashboard de Gestão de Alertas</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 📱 Mobile tip melhorado
st.markdown("""
<div class="mobile-tip">
    📱 <strong>PARA ACESSAR OS FILTROS:</strong> Toque no ícone <strong>☰</strong> no canto superior esquerdo
</div>
""", unsafe_allow_html=True)

# 📥 Load data
url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/RFerreira.xlsx"
try:
    df = pd.read_excel(url)
except Exception as e:
    st.error(f"❌ Erro ao carregar o ficheiro: {e}")
    st.stop()

# 🧼 Clean data
df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
df.dropna(subset=['Dias'], inplace=True)

# 📅 Define ranges with colors
ranges = [
    (0, 15, "0 a 15 dias 🟦", "metric-card-blue"),
    (16, 30, "16 a 30 dias 🟫", "metric-card"),
    (31, 60, "31 a 60 dias 🟧", "metric-card-orange"),
    (61, 90, "61 a 90 dias 🟨", "metric-card-orange"),
    (91, 365, "91 a 365 dias 🟥", "metric-card-red")
]

# 🎛️ Sidebar filters com design mobile-friendly
with st.sidebar:
    st.markdown('<div class="sidebar-header">🎨 FILTROS</div>', unsafe_allow_html=True)
    
    # Helper para mobile
    st.markdown("""
    <div class="sidebar-helper">
        👆 Toque nos campos abaixo para filtrar
    </div>
    """, unsafe_allow_html=True)
    
    selected_comercial = st.multiselect(
        "👨‍💼 Comercial",
        options=sorted(df['Comercial'].unique()),
        default=sorted(df['Comercial'].unique()),
        key="comercial_mobile"
    )
    
    selected_entidade = st.multiselect(
        "🏢 Entidade",
        options=sorted(df['Entidade'].unique()),
        default=sorted(df['Entidade'].unique()),
        key="entidade_mobile"
    )
    
    selected_ranges = st.multiselect(
        "📅 Intervalos de Dias",
        options=[r[2] for r in ranges],
        default=[r[2] for r in ranges],
        key="ranges_mobile"
    )
    
    # Botão para limpar filtros
    if st.button("🗑️ Limpar Filtros", use_container_width=True):
        st.rerun()
    
    # Estatísticas rápidas na sidebar
    st.markdown("---")
    st.markdown("### 📊 Estatísticas")
    total_registros = len(df)
    st.metric("Total de Registros", f"{total_registros:,}")

# Container principal
with st.container():
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div class="metric-card-green" style="text-align: center;">
            <h3 style="margin:0; font-size: 0.9rem;">Última Atualização</h3>
            <p style="margin:0; font-size: 1rem; font-weight: bold;">{pd.Timestamp.now().strftime('%d/%m/%Y')}</p>
        </div>
        """, unsafe_allow_html=True)

# 🔍 Filter data
filtered_df = df[
    df['Comercial'].isin(selected_comercial) &
    df['Entidade'].isin(selected_entidade)
]

# 📋 Summary com cards coloridos
st.subheader("📋 Resumo por Intervalos")

# Criar lista de dados para o resumo
summary_data = []
for low, high, label, card_class in ranges:
    if label in selected_ranges:
        range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
        count = len(range_df)
        total_value = range_df['Valor Pendente'].sum() if 'Valor Pendente' in range_df.columns else 0
        summary_data.append({
            "Intervalo": label,
            "Quantidade": count,
            "Valor Pendente": total_value,
            "card_class": card_class
        })

# Verificar se há dados para mostrar
if summary_data:
    # Mostrar cards métricos - layout responsivo
    cols = st.columns(len(summary_data))
    for idx, (col, data) in enumerate(zip(cols, summary_data)):
        with col:
            st.markdown(f"""
            <div class="{data['card_class']}">
                <h3 style="margin:0; font-size: 0.8rem;">{data['Intervalo'].split(' 🟦')[0].split(' 🟫')[0].split(' 🟧')[0].split(' 🟨')[0].split(' 🟥')[0]}</h3>
                <p style="margin:0; font-size: 1.1rem; font-weight: bold;">{data['Quantidade']}</p>
                <p style="margin:0; font-size: 0.7rem;">€{data['Valor Pendente']:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Tabela de resumo
    st.markdown("### 📊 Tabela de Resumo")
    summary_df = pd.DataFrame([{
        "Intervalo": data["Intervalo"],
        "Quantidade": data["Quantidade"],
        "Valor Pendente": f"€{data['Valor Pendente']:,.2f}"
    } for data in summary_data])
    
    st.dataframe(summary_df, use_container_width=True, height=200)
else:
    st.warning("⚠️ Nenhum dado nos intervalos selecionados")

# 📂 Detalhes por intervalo com expansores
st.subheader("📊 Detalhes por Intervalo")

for low, high, label, card_class in ranges:
    if label in selected_ranges:
        with st.expander(f"{label} - Ver Detalhes", expanded=False):
            range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
            if not range_df.empty:
                # Métricas do intervalo
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de Registros", len(range_df))
                with col2:
                    valor_total = range_df['Valor Pendente'].sum() if 'Valor Pendente' in range_df.columns else 0
                    st.metric("Valor Total", f"€{valor_total:,.2f}")
                with col3:
                    st.metric("Dias Médios", f"{range_df['Dias'].mean():.1f}")
                
                # Tabela de dados
                st.dataframe(range_df, use_container_width=True)
            else:
                st.info("ℹ️ Nenhum alerta neste intervalo")

# 📥 Download Excel com botão estilizado
st.subheader("📁 Exportação de Dados")

if not filtered_df.empty:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Dados Filtrados')
    
    st.download_button(
        label="📥 BAIXAR DADOS FILTRADOS EM EXCEL",
        data=output.getvalue(),
        file_name="dados_filtrados_renato_ferreira.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.success(f"✅ Pronto para exportar {len(filtered_df)} registros")
else:
    st.warning("⚠️ Nenhum dado disponível para download")

# ❤️ Footer estilizado
st.markdown("""
<div class="custom-footer">
    <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 0.5rem; flex-wrap: wrap;">
        <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" 
             style="height: 30px; border-radius: 5px;" 
             alt="Bracar Logo">
        <p style="margin:0;">Feito com ❤️ em Streamlit</p>
    </div>
    <p style="margin:0; font-size: 0.8rem; opacity: 0.7;">Dashboard Renato Ferreira - Gestão de Alertas</p>
</div>
""", unsafe_allow_html=True)
