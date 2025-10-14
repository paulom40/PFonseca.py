import streamlit as st
import pandas as pd
from io import BytesIO

# CSS personalizado com gradientes, estilo moderno e otimizações para mobile/iPhone
st.markdown("""
<style>
    /* Gradiente principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 1rem; /* Reduzido para mobile */
        border-radius: 15px;
        margin-bottom: 1.5rem; /* Reduzido */
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .header-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.8rem; /* Reduzido para mobile */
        flex-wrap: wrap; /* Permite quebra em telas pequenas */
    }
    
    .logo-container {
        display: flex;
        align-items: center;
    }
    
    .logo-img {
        height: 50px; /* Reduzido para mobile */
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        max-width: 100%; /* Garante responsividade */
    }
    
    .title-container {
        text-align: center;
        flex: 1; /* Ocupa espaço disponível */
    }
    
    .title-container h1 {
        margin: 0;
        font-size: 2rem; /* Reduzido para mobile */
    }
    
    .title-container p {
        margin: 0;
        opacity: 0.9;
        font-size: 1rem; /* Reduzido */
    }
    
    /* Cards com gradiente - otimizados para mobile */
    .metric-card, .metric-card-blue, .metric-card-orange, .metric-card-red, .metric-card-green {
        padding: 1rem; /* Reduzido para mobile */
        border-radius: 12px; /* Ligeiramente menor */
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center; /* Centraliza texto em mobile */
    }
    
    .metric-card h3, .metric-card p {
        margin: 0.2rem 0; /* Espaçamento reduzido */
    }
    
    .metric-card p[style*="font-size: 1.2rem"] {
        font-size: 1.1rem; /* Ajuste para mobile */
    }
    
    /* Sidebar styling - otimizado para mobile */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.8rem; /* Reduzido */
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        text-align: center;
        font-size: 1.1rem; /* Ligeiramente maior para legibilidade */
    }
    
    /* Botões modernos - touch-friendly para iPhone */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 1rem; /* Maior padding para touch */
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        font-size: 1rem; /* Fonte maior para mobile */
        min-height: 44px; /* Altura mínima para touch targets iOS */
    }
    
    .stButton button:hover, .stButton button:active {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Download button específico */
    .download-btn {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%) !important;
        min-height: 44px;
    }
    
    /* Dataframe styling - responsivo para mobile */
    .dataframe {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        font-size: 0.9rem; /* Fonte menor para caber em mobile */
    }
    
    /* Scroll horizontal para tabelas em mobile */
    .element-container .dataframe {
        overflow-x: auto;
        white-space: nowrap;
    }
    
    /* Input fields styling - touch-friendly */
    .stTextInput input, .stSelectbox div div, .stMultiSelect div div {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.8rem; /* Maior padding para touch */
        font-size: 1rem;
        min-height: 44px; /* Altura mínima iOS */
    }
    
    .stTextInput input:focus, .stSelectbox div div:focus, .stMultiSelect div div:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Multiselect - ajustes para mobile */
    .stMultiSelect div div {
        max-height: 200px; /* Limita altura em mobile para evitar scroll excessivo */
    }
    
    /* Tabs styling - otimizado para mobile */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem; /* Reduzido para mobile */
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 0.8rem;
        border-radius: 15px;
        overflow-x: auto; /* Scroll horizontal se necessário */
        white-space: nowrap;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px; /* Altura touch-friendly */
        white-space: nowrap; /* Evita quebra */
        background: white;
        border-radius: 10px;
        padding: 0 1rem; /* Reduzido */
        font-weight: 600;
        font-size: 0.9rem; /* Fonte menor */
        min-width: 100px; /* Largura mínima */
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
        padding: 1rem; /* Padding consistente */
    }
    
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Mobile tip styling - sempre visível em mobile */
    .mobile-tip {
        text-align: center;
        font-size: 14px;
        color: #666;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Footer styling - otimizado para mobile */
    .custom-footer {
        text-align: center;
        color: #666;
        font-size: 0.8rem;
        margin-top: 1.5rem; /* Reduzido */
        padding: 0.8rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
    }
    
    .custom-footer img {
        height: 25px; /* Reduzido */
    }
    
    /* Expansores - ajustes para mobile */
    .stExpander {
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    
    .stExpander > div > label {
        font-size: 1.1rem; /* Título maior para touch */
        padding: 0.8rem;
    }
    
    /* Métricas em colunas - stack em mobile */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
        }
        
        .header-content {
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .title-container h1 {
            font-size: 1.8rem;
        }
        
        .metric-card, .metric-card-blue, .metric-card-orange, .metric-card-red, .metric-card-green {
            padding: 0.8rem;
            margin: 0.3rem 0;
        }
        
        .stButton button {
            padding: 1rem;
            font-size: 1.1rem;
        }
        
        /* Colunas de métricas stackam automaticamente no Streamlit em mobile */
        .block-container {
            padding-top: 1rem;
        }
        
        /* Dataframe em mobile: fonte menor e scroll */
        .dataframe th, .dataframe td {
            padding: 0.5rem;
            font-size: 0.85rem;
        }
        
        /* Sidebar em mobile: largura full */
        section[data-testid="stSidebar"] {
            width: 100% !important;
        }
        
        /* Esconde tip de mobile em desktop */
        .mobile-tip {
            display: none;
        }
        
        @media (min-width: 769px) {
            .mobile-tip {
                display: block;
            }
        }
    }
    
    /* Otimizações específicas para iPhone (Safari iOS) */
    @media (max-width: 414px) and (-webkit-min-device-pixel-ratio: 2) {
        .logo-img {
            height: 40px;
        }
        
        .title-container h1 {
            font-size: 1.6rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0 0.8rem;
            min-width: 80px;
        }
    }
    
    /* Previne zoom em inputs iOS */
    input[type="text"], input[type="email"], input[type="number"], select {
        font-size: 16px; /* Previne zoom automático no iOS */
    }
</style>
""", unsafe_allow_html=True)

# 🚀 Page configuration - wide para melhor uso em mobile landscape
st.set_page_config(page_title="Renato Ferreira", layout="wide", initial_sidebar_state="collapsed")  # Collapsed para mobile

# Header principal com gradiente E LOGO DA BRACAR - simplificado para mobile
st.markdown("""
<div class="main-header">
    <div class="header-content">
        <div class="logo-container">
            <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" 
                 class="logo-img" 
                 alt="Bracar Logo">
        </div>
        <div class="title-container">
            <h1>RENATO FERREIRA</h1>
            <p>Dashboard de Gestão de Alertas</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 📱 Mobile tip - agora condicional via CSS
st.markdown("""
<div class="mobile-tip">
    📱 Toque no ícone ≡ no canto superior esquerdo para abrir os filtros.
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

# 🎛️ Sidebar filters with modern design - otimizado para mobile
with st.sidebar:
    st.markdown('<div class="sidebar-header">🎨 FILTROS</div>', unsafe_allow_html=True)
    
    selected_comercial = st.multiselect(
        "👨‍💼 Comercial",
        sorted(df['Comercial'].unique()),
        default=sorted(df['Comercial'].unique()),
        help="Selecione um ou mais comerciais"
    )
    
    selected_entidade = st.multiselect(
        "🏢 Entidade",
        sorted(df['Entidade'].unique()),
        default=sorted(df['Entidade'].unique()),
        help="Selecione uma ou mais entidades"
    )
    
    selected_ranges = st.multiselect(
        "📅 Intervalos de Dias",
        [r[2] for r in ranges],
        default=[r[2] for r in ranges],
        help="Selecione intervalos para filtrar"
    )
    
    # Estatísticas rápidas na sidebar - simplificado
    st.markdown("---")
    st.markdown("### 📊 Estatísticas")
    total_registros = len(df)
    st.metric("Total de Registros", f"{total_registros:,}")

# Container principal - usa colunas full width em mobile
col1, col2 = st.columns([1, 3])  # Ajustado para melhor distribuição em mobile

with col1:
    if st.button("🔄 Atualizar Dados"):
        st.rerun()

with col2:
    st.markdown(f"""
    <div class="metric-card-green">
        <h3>Última Atualização</h3>
        <p>10/10/2025</p>
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
    # Mostrar cards métricos - em mobile, columns viram stack
    cols = st.columns(len(summary_data))
    for idx, (col, data) in enumerate(zip(cols, summary_data)):
        with col:
            interval_name = data['Intervalo'].split(' ')[0:3]  # Limpa emoji melhor
            interval_name = ' '.join(interval_name)
            st.markdown(f"""
            <div class="{data['card_class']}">
                <h3>{interval_name}</h3>
                <p>{data['Quantidade']}</p>
                <p>€{data['Valor Pendente']:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Tabela de resumo - hide_index para mobile
    st.markdown("### 📊 Tabela de Resumo")
    summary_df = pd.DataFrame([{
        "Intervalo": data["Intervalo"],
        "Quantidade": data["Quantidade"],
        "Valor Pendente": f"€{data['Valor Pendente']:,.2f}"
    } for data in summary_data])
    
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
else:
    st.warning("⚠️ Nenhum dado nos intervalos selecionados")

# 📂 Detalhes por intervalo com expansores - otimizado
st.subheader("📊 Detalhes por Intervalo")

for low, high, label, card_class in ranges:
    if label in selected_ranges:
        with st.expander(f"{label} - Ver Detalhes", expanded=False):
            range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
            if not range_df.empty:
                # Métricas do intervalo - columns stack em mobile
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de Registros", len(range_df))
                with col2:
                    valor_total = range_df['Valor Pendente'].sum() if 'Valor Pendente' in range_df.columns else 0
                    st.metric("Valor Total", f"€{valor_total:,.2f}")
                with col3:
                    st.metric("Dias Médios", f"{range_df['Dias'].mean():.1f}")
                
                # Tabela de dados - hide_index
                st.dataframe(range_df, use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ Nenhum alerta neste intervalo")

# 📥 Download Excel com botão estilizado - full width
st.subheader("📁 Exportação de Dados")

if not filtered_df.empty:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Dados Filtrados')
    
    st.download_button(
        label="📥 BAIXAR DADOS FILTRADOS EM EXCEL",
        data=output.getvalue(),
        file_name="dados_filtrados_renato_ferreira.xlsx",  # Corrigido nome
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.success(f"✅ Pronto para exportar {len(filtered_df)} registros")
else:
    st.warning("⚠️ Nenhum dado disponível para download")

# ❤️ Footer estilizado - simplificado
st.markdown("""
<div class="custom-footer">
    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.3rem; flex-wrap: wrap;">
        <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" 
             style="height: 25px; border-radius: 5px;" 
             alt="Bracar Logo">
        <p>Feito com ❤️ em Streamlit</p>
    </div>
    <p>Dashboard Renato Ferreira - Gestão de Alertas</p>
</div>
""", unsafe_allow_html=True)
