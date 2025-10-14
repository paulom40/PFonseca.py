import streamlit as st
import pandas as pd
from io import BytesIO

# CSS personalizado com tema dark
st.markdown("""
<style>
    /* Tema Dark Principal */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Gradiente principal - Dark */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border: 1px solid #2a5298;
        position: relative;
    }
    
    .header-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.5rem;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
    }
    
    .logo-img {
        height: 65px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
        border: 2px solid rgba(255,255,255,0.1);
    }
    
    .title-container {
        text-align: center;
    }
    
    /* Cards com gradiente - Dark Theme */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .metric-card-blue {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .metric-card-orange {
        background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .metric-card-red {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .metric-card-green {
        background: linear-gradient(135deg, #0ba360 0%, #3cba92 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Sidebar styling - Dark */
    .sidebar-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .sidebar .sidebar-content {
        background-color: #0e1117;
    }
    
    /* Botões modernos - Dark */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Download button específico - Dark */
    .download-btn {
        background: linear-gradient(135deg, #0ba360 0%, #3cba92 100%) !important;
    }
    
    /* Dataframe styling - Dark */
    .dataframe {
        border-radius: 10px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        background-color: #1e1e1e !important;
        border: 1px solid #333;
    }
    
    .dataframe table {
        background-color: #1e1e1e !important;
        color: #fafafa !important;
    }
    
    .dataframe th {
        background-color: #2a5298 !important;
        color: white !important;
    }
    
    .dataframe td {
        background-color: #1e1e1e !important;
        color: #fafafa !important;
        border-color: #333 !important;
    }
    
    /* Input fields styling - Dark */
    .stTextInput input, .stSelectbox div div, .stMultiSelect div div {
        border-radius: 10px;
        border: 2px solid #333;
        background-color: #1e1e1e;
        color: #fafafa;
    }
    
    .stTextInput input:focus, .stSelectbox div div:focus, .stMultiSelect div div:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
    }
    
    /* Tabs styling - Dark */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 1rem;
        border-radius: 15px;
        border: 1px solid #333;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: #1e1e1e;
        border-radius: 10px;
        padding: 0 2rem;
        font-weight: 600;
        color: #fafafa;
        border: 1px solid #333;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: 1px solid #667eea;
    }
    
    /* Alert boxes customizados - Dark */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        background-color: #1e1e1e;
        border: 1px solid #333;
    }
    
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Mobile tip styling - Dark */
    .mobile-tip {
        text-align: center;
        font-size: 14px;
        color: #ccc;
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #333;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Footer styling - Dark */
    .custom-footer {
        text-align: center;
        color: #ccc;
        font-size: 0.9rem;
        margin-top: 2rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        border-radius: 10px;
        border: 1px solid #333;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Expander styling - Dark */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%) !important;
        color: #fafafa !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
        margin: 5px 0;
    }
    
    .streamlit-expanderContent {
        background-color: #1e1e1e !important;
        border: 1px solid #333 !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }
    
    /* Metric styling - Dark */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%) !important;
        border: 1px solid #333 !important;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Subheader styling */
    .stSubheader {
        color: #fafafa !important;
    }
    
    /* Markdown text color */
    .stMarkdown {
        color: #fafafa !important;
    }
    
    /* Warning and Info boxes */
    .stWarning {
        background-color: #332100 !important;
        border: 1px solid #665200 !important;
        color: #ffcc00 !important;
    }
    
    .stSuccess {
        background-color: #003320 !important;
        border: 1px solid #006644 !important;
        color: #00cc88 !important;
    }
    
    .stError {
        background-color: #330000 !important;
        border: 1px solid #660000 !important;
        color: #ff4444 !important;
    }
    
    .stInfo {
        background-color: #002233 !important;
        border: 1px solid #004466 !important;
        color: #44aaff !important;
    }
</style>
""", unsafe_allow_html=True)

# 🚀 Page configuration
st.set_page_config(page_title="Bruno Brito - Dark", layout="centered", page_icon="📊")

# Header principal com gradiente DARK E LOGO DA BRACAR
st.markdown("""
<div class="main-header">
    <div class="header-content">
        <div class="logo-container">
            <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" 
                 class="logo-img" 
                 alt="Bracar Logo">
        </div>
        <div class="title-container">
            <h1 style="margin:0; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">🌙 BRUNO BRITO</h1>
            <p style="margin:0; opacity: 0.9; font-size: 1.1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">Dashboard de Gestão de Alertas - Dark Mode</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 📱 Mobile tip
st.markdown("""
<div class="mobile-tip">
    📱 Em dispositivos móveis, toque no ícone <strong>≡</strong> no canto superior esquerdo para abrir os filtros.
</div>
""", unsafe_allow_html=True)

# 📥 Load data
url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/BBrito.xlsx"
try:
    df = pd.read_excel(url)
except Exception as e:
    st.error(f"❌ Erro ao carregar o ficheiro: {e}")
    st.stop()

# 🧼 Clean data
df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
df.dropna(subset=['Dias'], inplace=True)

# 📅 Define ranges with colors - Dark Theme
ranges = [
    (0, 15, "0 a 15 dias 🌊", "metric-card-blue"),
    (16, 30, "16 a 30 dias 🪨", "metric-card"),
    (31, 60, "31 a 60 dias 🔥", "metric-card-orange"),
    (61, 90, "61 a 90 dias ⚡", "metric-card-orange"),
    (91, 365, "91 a 365 dias 💀", "metric-card-red")
]

# 🎛️ Sidebar filters with dark design
with st.sidebar:
    st.markdown('<div class="sidebar-header">🎨 FILTROS</div>', unsafe_allow_html=True)
    
    selected_comercial = st.multiselect(
        "👨‍💼 Comercial",
        sorted(df['Comercial'].unique()),
        default=sorted(df['Comercial'].unique())
    )
    
    selected_entidade = st.multiselect(
        "🏢 Entidade",
        sorted(df['Entidade'].unique()),
        default=sorted(df['Entidade'].unique())
    )
    
    selected_ranges = st.multiselect(
        "📅 Intervalos de Dias",
        [r[2] for r in ranges],
        default=[r[2] for r in ranges]
    )
    
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
            <p style="margin:0; font-size: 1rem; font-weight: bold;">03/10/2025</p>
        </div>
        """, unsafe_allow_html=True)

# 🔍 Filter data
filtered_df = df[
    df['Comercial'].isin(selected_comercial) &
    df['Entidade'].isin(selected_entidade)
]

# 📋 Summary com cards coloridos - Dark Theme
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
    # Mostrar cards métricos
    cols = st.columns(len(summary_data))
    for idx, (col, data) in enumerate(zip(cols, summary_data)):
        with col:
            st.markdown(f"""
            <div class="{data['card_class']}">
                <h3 style="margin:0; font-size: 0.9rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{data['Intervalo'].split(' 🌊')[0].split(' 🪨')[0].split(' 🔥')[0].split(' ⚡')[0].split(' 💀')[0]}</h3>
                <p style="margin:0; font-size: 1.2rem; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{data['Quantidade']}</p>
                <p style="margin:0; font-size: 0.8rem; opacity: 0.9;">€{data['Valor Pendente']:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Tabela de resumo
    st.markdown("### 📊 Tabela de Resumo")
    summary_df = pd.DataFrame([{
        "Intervalo": data["Intervalo"],
        "Quantidade": data["Quantidade"],
        "Valor Pendente": f"€{data['Valor Pendente']:,.2f}"
    } for data in summary_data])
    
    st.dataframe(summary_df, use_container_width=True)
else:
    st.warning("⚠️ Nenhum dado nos intervalos selecionados")

# 📂 Detalhes por intervalo com expansores - Dark Theme
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

# 📥 Download Excel com botão estilizado - Dark Theme
st.subheader("📁 Exportação de Dados")

if not filtered_df.empty:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Dados Filtrados')
    
    st.download_button(
        label="📥 BAIXAR DADOS FILTRADOS EM EXCEL",
        data=output.getvalue(),
        file_name="dados_filtrados_bruno_brito_dark.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.success(f"✅ Pronto para exportar {len(filtered_df)} registros")
else:
    st.warning("⚠️ Nenhum dado disponível para download")

# ❤️ Footer estilizado - Dark Theme
st.markdown("""
<div class="custom-footer">
    <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 0.5rem;">
        <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" 
             style="height: 30px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.1);" 
             alt="Bracar Logo">
        <p style="margin:0;">Feito com ❤️ em Streamlit - Dark Mode</p>
    </div>
    <p style="margin:0; font-size: 0.8rem; opacity: 0.7;">Dashboard Bruno Brito - Gestão de Alertas</p>
</div>
""", unsafe_allow_html=True)
