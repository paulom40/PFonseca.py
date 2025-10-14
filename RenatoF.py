import streamlit as st
import pandas as pd
from io import BytesIO

# CSS personalizado com gradientes e estilo moderno
st.markdown("""
<style>
    /* Gradiente principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
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
    }
    
    .logo-container {
        display: flex;
        align-items: center;
    }
    
    .logo-img {
        height: 60px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    .title-container {
        text-align: center;
    }
    
    /* Cards com gradiente */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-orange {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-red {
        background: linear-gradient(135deg, #ff5858 0%, #f09819 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-green {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
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
        gap: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: white;
        border-radius: 10px;
        padding: 0 2rem;
        font-weight: 600;
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
    
    /* Sidebar sempre visível */
    section[data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
    }
</style>
""", unsafe_allow_html=True)

# 🚀 Page configuration - FORÇAR sidebar visível
st.set_page_config(
    page_title="Bruno Brito - Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
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
            <h1 style="margin:0; font-size: 2.5rem;">BRUNO BRITO</h1>
            <p style="margin:0; opacity: 0.9; font-size: 1.1rem;">Dashboard de Gestão de Alertas</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 📱 Mobile tip
st.markdown("""
<div class="mobile-tip">
    📱 <strong>Filtros disponíveis no menu lateral</strong> → Use o ícone ≡ no canto superior esquerdo para ajustar a visibilidade
</div>
""", unsafe_allow_html=True)

# 📥 Load data
url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/BBrito.xlsx"
try:
    df = pd.read_excel(url)
except Exception as e:
    st.error(f"❌ Erro ao carregar o ficheiro: {e}")
    st.stop()

# 🧼 CLEAN DATA - CORREÇÃO DOS PROBLEMAS DE SERIALIZAÇÃO
df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
df.dropna(subset=['Dias'], inplace=True)

# Converter colunas problemáticas para string para evitar erros de serialização
problem_columns = ['Série', 'N.º Doc.', 'N.º Cliente', 'N.º Fornecedor']
for col in problem_columns:
    if col in df.columns:
        df[col] = df[col].astype(str)

# Garantir que colunas numéricas são numéricas
numeric_columns = ['Valor Pendente', 'Valor Liquidado', 'Valor Pago']
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 📅 Define ranges with colors
ranges = [
    (0, 15, "0 a 15 dias 🟦", "metric-card-blue"),
    (16, 30, "16 a 30 dias 🟫", "metric-card"),
    (31, 60, "31 a 60 dias 🟧", "metric-card-orange"),
    (61, 90, "61 a 90 dias 🟨", "metric-card-orange"),
    (91, 365, "91 a 365 dias 🟥", "metric-card-red")
]

# 🎛️ Sidebar filters - AGORA DEVE ESTAR VISÍVEL
with st.sidebar:
    st.markdown('<div class="sidebar-header">🎛️ FILTROS</div>', unsafe_allow_html=True)
    
    st.markdown("**Filtros de Dados**")
    
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
        "📅 Intervalos de Dias",
        options=[r[2] for r in ranges],
        default=[r[2] for r in ranges]
    )
    
    # Estatísticas rápidas na sidebar
    st.markdown("---")
    st.markdown("### 📊 Estatísticas Globais")
    total_registros = len(df)
    total_filtrado = len(filtered_df) if 'filtered_df' in locals() else total_registros
    
    st.metric("Total de Registros", f"{total_registros:,}")
    
    if total_registros > 0:
        percentagem = (total_filtrado / total_registros) * 100
        st.metric("Registros Filtrados", f"{total_filtrado:,} ({percentagem:.1f}%)")
    
    # Informação adicional
    st.markdown("---")
    st.markdown("### 💡 Informação")
    st.info("Os filtros aplicam-se automaticamente a todo o dashboard")

# 🔍 Filter data (após definir os filtros)
filtered_df = df[
    df['Comercial'].isin(selected_comercial) &
    df['Entidade'].isin(selected_entidade)
]

# Container principal com botões
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("🔄 Atualizar Tudo", use_container_width=True):
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div class="metric-card-green" style="text-align: center;">
            <h3 style="margin:0; font-size: 0.9rem;">Dados Filtrados</h3>
            <p style="margin:0; font-size: 1rem; font-weight: bold;">{len(filtered_df):,} registros</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card-blue" style="text-align: center;">
            <h3 style="margin:0; font-size: 0.9rem;">Última Atualização</h3>
            <p style="margin:0; font-size: 1rem; font-weight: bold;">{pd.Timestamp.now().strftime('%d/%m/%Y')}</p>
        </div>
        """, unsafe_allow_html=True)

# 📋 Summary com cards coloridos
st.subheader("📊 Resumo por Intervalos de Dias")

# Criar lista de dados para o resumo
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

# Verificar se há dados para mostrar
if summary_data:
    # Mostrar cards métricos
    cols = st.columns(len(summary_data))
    for idx, (col, data) in enumerate(zip(cols, summary_data)):
        with col:
            # Remover emojis para o título do card
            clean_label = data['Intervalo'].split(' 🟦')[0].split(' 🟫')[0].split(' 🟧')[0].split(' 🟨')[0].split(' 🟥')[0]
            st.markdown(f"""
            <div class="{data['card_class']}">
                <h3 style="margin:0; font-size: 0.9rem;">{clean_label}</h3>
                <p style="margin:0; font-size: 1.2rem; font-weight: bold;">{data['Quantidade']}</p>
                <p style="margin:0; font-size: 0.8rem;">€{data['Valor Pendente']:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Tabela de resumo
    st.markdown("### 📈 Tabela de Resumo Consolidado")
    summary_df = pd.DataFrame([{
        "Intervalo": data["Intervalo"],
        "Quantidade": data["Quantidade"],
        "Valor Pendente (€)": f"€{data['Valor Pendente']:,.2f}"
    } for data in summary_data])
    
    st.dataframe(summary_df, use_container_width=True)
else:
    st.warning("⚠️ Nenhum dado encontrado nos intervalos selecionados")

# 📂 Detalhes por intervalo com expansores
st.subheader("🔍 Detalhes por Intervalo")

for low, high, label, card_class in ranges:
    if label in selected_ranges:
        with st.expander(f"{label} - Ver Detalhes Completos", expanded=False):
            range_df = filtered_df[(filtered_df['Dias'] >= low) & (filtered_df['Dias'] <= high)]
            
            if not range_df.empty:
                # Métricas do intervalo
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total de Registros", len(range_df))
                with col2:
                    valor_total = range_df['Valor Pendente'].sum() if 'Valor Pendente' in range_df.columns else 0
                    st.metric("Valor Total", f"€{valor_total:,.2f}")
                with col3:
                    dias_medios = range_df['Dias'].mean()
                    st.metric("Dias Médios", f"{dias_medios:.1f}")
                with col4:
                    dias_max = range_df['Dias'].max()
                    st.metric("Dias Máximos", dias_max)
                
                # Tabela de dados - JÁ CORRIGIDA para evitar problemas de serialização
                display_df = range_df.copy()
                
                # Formatar colunas para melhor visualização
                if 'Valor Pendente' in display_df.columns:
                    display_df['Valor Pendente'] = display_df['Valor Pendente'].apply(lambda x: f"€{x:,.2f}" if pd.notnull(x) else "€0.00")
                
                st.dataframe(display_df, use_container_width=True)
                
                # Mostrar algumas estatísticas adicionais
                with st.expander("📊 Estatísticas Detalhadas deste Intervalo"):
                    st.write(f"**Distribuição por Comercial:**")
                    comercial_counts = range_df['Comercial'].value_counts()
                    st.dataframe(comercial_counts)
                    
            else:
                st.info(f"ℹ️ Nenhum alerta encontrado no intervalo {label}")

# 📥 Download Excel com botão estilizado
st.subheader("💾 Exportação de Dados")

if not filtered_df.empty:
    # Preparar dados para exportação
    export_df = filtered_df.copy()
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Dados_Filtrados')
        
        # Adicionar um sheet com resumo
        summary_export = pd.DataFrame([{
            'Intervalo': data['Intervalo'],
            'Quantidade': data['Quantidade'],
            'Valor_Pendente': data['Valor Pendente']
        } for data in summary_data])
        summary_export.to_excel(writer, index=False, sheet_name='Resumo')
    
    # Botão de download
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.download_button(
            label="📥 BAIXAR DADOS FILTRADOS EM EXCEL",
            data=output.getvalue(),
            file_name=f"dados_filtrados_bruno_brito_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        st.metric("Registros para Exportar", len(filtered_df))
    
    st.success(f"✅ Pronto para exportar {len(filtered_df)} registros filtrados")
else:
    st.warning("⚠️ Nenhum dado disponível para exportação com os filtros atuais")

# ❤️ Footer estilizado
st.markdown("""
<div class="custom-footer">
    <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 0.5rem;">
        <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" 
             style="height: 30px; border-radius: 5px;" 
             alt="Bracar Logo">
        <p style="margin:0;">Desenvolvido com ❤️ usando Streamlit</p>
    </div>
    <p style="margin:0; font-size: 0.8rem; opacity: 0.7;">
        Dashboard Bruno Brito - Sistema de Gestão de Alertas | Atualizado em {pd.Timestamp.now().strftime('%d/%m/%Y')}
    </p>
</div>
""", unsafe_allow_html=True)
