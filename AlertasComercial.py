import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import BytesIO
import xlsxwriter
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import difflib

# Configuração da página com layout wide
st.set_page_config(
    page_title="📊 Dashboard de Pendências",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    .metric-card-warning {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-danger {
        background: linear-gradient(135deg, #ff5858 0%, #f09819 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-success {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
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
    
    /* Email button específico */
    .email-btn {
        background: linear-gradient(135deg, #ff5858 0%, #f09819 100%) !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Input fields styling */
    .stTextInput input, .stTextInput textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.5rem;
    }
    
    .stTextInput input:focus, .stTextInput textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Selectbox styling */
    .stSelectbox div div {
        border-radius: 10px;
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
    
    /* Container principal */
    .main-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal com gradiente
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.5rem;">📊 DASHBOARD DE VALORES PENDENTES</h1>
    <p style="margin:0; opacity: 0.9; font-size: 1.1rem;">Gestão Completa de Valores Futuros e em Atraso</p>
</div>
""", unsafe_allow_html=True)

# URL do arquivo Excel
url = "https://github.com/paulom40/PFonseca.py/raw/main/V0808.xlsx"

@st.cache_data
def load_data():
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), sheet_name="Sheet1", header=0)
        df.columns = [col.strip() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar ficheiro: {e}")
        st.info("💡 Dica: Verifique se o link do GitHub está correto e se o ficheiro está público.")
        return None

# Container principal para controles
with st.container():
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown("### 🔄 Gestão de Dados")
        if st.button("🔄 Atualizar Dados do Excel", use_container_width=True):
            st.cache_data.clear()
            st.session_state.df = load_data()
            st.session_state.last_updated = datetime.now()
            if st.session_state.df is not None:
                st.success("✅ Dados atualizados com sucesso!")
    
    with col2:
        if "last_updated" in st.session_state:
            st.markdown(f"""
            <div class="metric-card-success">
                <h3 style="margin:0; font-size: 0.9rem;">Última Atualização</h3>
                <p style="margin:0; font-size: 1rem; font-weight: bold;">
                    {st.session_state.last_updated.strftime('%d/%m/%Y')}
                </p>
                <p style="margin:0; font-size: 0.8rem;">
                    {st.session_state.last_updated.strftime('%H:%M:%S')}
                </p>
            </div>
            """, unsafe_allow_html=True)

# Carregar dados
df = st.session_state.get("df", load_data())

if df is not None:
    # Sidebar moderna
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🔎 FILTROS E CONTROLES</div>', unsafe_allow_html=True)
        
        st.markdown("### 📊 Filtro por Comercial")
        
        # Processar comerciais para a sidebar
        if 'Comercial' in df.columns:
            comerciais = sorted(df['Comercial'].dropna().astype(str).unique())
            opcoes_comerciais = ["Todos"] + comerciais
            
            selected_comercial = st.selectbox(
                "Selecione o Comercial:",
                opcoes_comerciais,
                index=0
            )
        else:
            st.warning("Coluna 'Comercial' não encontrada")
            selected_comercial = "Todos"
        
        st.markdown("---")
        st.markdown("### 🔍 Busca Avançada")
        search_term = st.text_input("Digite o nome do Comercial:")
        
        st.markdown("---")
        st.markdown("### 📈 Tipo de Análise")
        tipo_analise = st.radio(
            "Selecione o tipo de análise:",
            ["💰 Valores Futuros (Dias ≥ 0)", "⚠️ Valores em Atraso (Dias < 0)"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### 📊 Estatísticas Rápidas")
        
        if len(df) > 0:
            total_registros = len(df)
            colunas_disponiveis = df.columns.tolist()
            
            st.metric("📋 Total de Registros", f"{total_registros:,}")
            st.metric("📊 Colunas", f"{len(colunas_disponiveis)}")

    # Layout principal com tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard Principal", "📁 Exportação", "📧 Envio por Email"])

    with tab1:
        # Verificar colunas necessárias
        colunas_necessarias = ['Dias', 'Valor Pendente', 'Comercial', 'Entidade']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
        
        if colunas_faltantes:
            st.error(f"❌ Colunas em falta: {', '.join(colunas_faltantes)}")
            st.info("ℹ️ Verifique se o ficheiro Excel tem as colunas necessárias:")
            for col in colunas_necessarias:
                status = "✅" if col in df.columns else "❌"
                st.write(f"{status} {col}")
        else:
            st.success("✅ Todas as colunas necessárias estão presentes!")
            
            # Processamento dos dados
            st.markdown("### 🔧 Processamento de Dados")
            
            # Limpeza e preparação
            df_clean = df.copy()
            df_clean['Dias'] = pd.to_numeric(df_clean['Dias'], errors='coerce')
            df_clean['Valor Pendente'] = pd.to_numeric(df_clean['Valor Pendente'], errors='coerce')
            df_clean['Comercial'] = df_clean['Comercial'].astype(str).str.replace(r'[\t\n\r ]+', ' ', regex=True).str.strip()
            df_clean['Entidade'] = df_clean['Entidade'].astype(str).str.strip()

            # CORREÇÃO: INCLUIR TODOS OS VALORES PENDENTES (positivos, negativos e zero)
            if "Valores Futuros" in tipo_analise:
                # VALORES FUTUROS: Dias ≥ 0 (inclui TODOS os valores pendentes)
                df_base = df_clean[df_clean['Dias'] >= 0].copy()
                tipo_filtro = "Valores Futuros (Dias ≥ 0)"
                st.info("💰 Analisando: **Valores Futuros/Em Dia** - Faturas com vencimento hoje ou no futuro")
            else:
                # VALORES EM ATRASO: Dias < 0 (inclui TODOS os valores pendentes)
                df_base = df_clean[df_clean['Dias'] < 0].copy()
                tipo_filtro = "Valores em Atraso (Dias < 0)"
                st.warning("⚠️ Analisando: **Valores em Atraso** - Faturas vencidas")

            # Aplicar filtros de Comercial
            if selected_comercial == "Todos" and not search_term:
                df_filtrado = df_base.copy()
                filtro_aplicado = f"Todos os comerciais - {tipo_filtro}"
            elif selected_comercial != "Todos":
                df_filtrado = df_base[df_base['Comercial'] == selected_comercial].copy()
                filtro_aplicado = f"Comercial: {selected_comercial} - {tipo_filtro}"
            elif search_term:
                search_upper = search_term.upper().strip()
                mask_partial = df_base['Comercial'].str.upper().str.contains(search_upper, na=False)
                df_filtrado = df_base[mask_partial].copy()
                filtro_aplicado = f"Busca: '{search_term}' - {tipo_filtro}"
            else:
                df_filtrado = df_base.copy()
                filtro_aplicado = f"Todos os comerciais - {tipo_filtro"

            # Resumo analítico - SOMA POR COMERCIAL E ENTIDADE (INCLUI TODOS OS VALORES)
            st.markdown("### 📋 Resumo por Comercial e Entidade")
            
            if len(df_filtrado) > 0:
                # Agrupamento e cálculo - INCLUI TODOS OS VALORES (positivos e negativos)
                summary = df_filtrado.groupby(['Comercial', 'Entidade'], as_index=False).agg({
                    'Valor Pendente': 'sum',
                    'Dias': 'mean'
                })
                summary['Valor Pendente'] = summary['Valor Pendente'].round(2)
                summary['Dias'] = summary['Dias'].round(1)
                summary = summary.rename(columns={
                    'Dias': 'Dias Médios',
                    'Valor Pendente': 'Total Pendente'
                })
                summary = summary.sort_values('Total Pendente', ascending=False)

                # Métricas em cards
                col1, col2, col3, col4 = st.columns(4)
                
                sub_total = summary['Total Pendente'].sum()
                num_entidades = summary['Entidade'].nunique()
                num_comerciais = summary['Comercial'].nunique()
                dias_medios = summary['Dias Médios'].mean()

                with col1:
                    if "Futuros" in tipo_filtro:
                        card_class = "metric-card-success" if sub_total >= 0 else "metric-card-warning"
                    else:
                        card_class = "metric-card-danger" if sub_total < 0 else "metric-card-warning" if abs(sub_total) > 5000 else "metric-card"
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <h3 style="margin:0; font-size: 0.9rem;">Total Pendente</h3>
                        <p style="margin:0; font-size: 1.5rem; font-weight: bold;">€{sub_total:,.2f}</p>
                        <p style="margin:0; font-size: 0.8rem;">{tipo_filtro.split(' - ')[0]}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="margin:0; font-size: 0.9rem;">Entidades</h3>
                        <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{num_entidades}</p>
                        <p style="margin:0; font-size: 0.8rem;">Clientes únicos</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="margin:0; font-size: 0.9rem;">Comerciais</h3>
                        <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{num_comerciais}</p>
                        <p style="margin:0; font-size: 0.8rem;">Em análise</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    dias_texto = "Futuros" if dias_medios >= 0 else "Atraso"
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="margin:0; font-size: 0.9rem;">Dias Médios</h3>
                        <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{abs(dias_medios):.1f}</p>
                        <p style="margin:0; font-size: 0.8rem;">{dias_texto}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # ANÁLISE ESPECÍFICA PARA VALORES NEGATivos COM DIAS ≥ 0
                st.markdown("### 📊 Análise de Valores Negativos Futuros")
                
                # CORREÇÃO: Valores Negativos apenas onde Dias ≥ 0
                if "Futuros" in tipo_filtro:
                    # Para análise de valores futuros: mostrar negativos futuros
                    valores_negativos_futuros = df_filtrado[
                        (df_filtrado['Valor Pendente'] < 0) & 
                        (df_filtrado['Dias'] >= 0)
                    ]['Valor Pendente'].sum()
                    
                    num_negativos_futuros = len(df_filtrado[
                        (df_filtrado['Valor Pendente'] < 0) & 
                        (df_filtrado['Dias'] >= 0)
                    ])
                else:
                    # Para análise de valores em atraso: mostrar negativos em atraso
                    valores_negativos_futuros = df_filtrado[
                        (df_filtrado['Valor Pendente'] < 0) & 
                        (df_filtrado['Dias'] < 0)
                    ]['Valor Pendente'].sum()
                    
                    num_negativos_futuros = len(df_filtrado[
                        (df_filtrado['Valor Pendente'] < 0) & 
                        (df_filtrado['Dias'] < 0)
                    ])

                # Estatísticas gerais dos valores
                valores_positivos = df_filtrado[df_filtrado['Valor Pendente'] > 0]['Valor Pendente'].sum()
                valores_negativos = df_filtrado[df_filtrado['Valor Pendente'] < 0]['Valor Pendente'].sum()
                valores_zero = len(df_filtrado[df_filtrado['Valor Pendente'] == 0])
                
                col_anal1, col_anal2, col_anal3, col_anal4 = st.columns(4)
                
                with col_anal1:
                    st.metric("💰 Valores Positivos", f"€{valores_positivos:,.2f}")
                
                with col_anal2:
                    st.metric("📉 Valores Negativos", f"€{valores_negativos:,.2f}")
                
                with col_anal3:
                    st.metric("🔴 Negativos Futuros", f"€{valores_negativos_futuros:,.2f}", 
                             delta=f"{num_negativos_futuros} registos")
                
                with col_anal4:
                    st.metric("⚖️ Saldo Líquido", f"€{sub_total:,.2f}")

                # Alertas específicos para cada tipo
                st.markdown("### ⚠️ Status da Análise")
                if "Futuros" in tipo_filtro:
                    if valores_negativos_futuros < 0:
                        st.warning(f"🚨 **VALORES NEGATIVOS FUTUROS**: €{abs(valores_negativos_futuros):,.2f} em valores futuros negativos")
                    if sub_total < 0:
                        st.error(f"⚠️ **SALDO NEGATIVO**: Saldo total negativo de €{abs(sub_total):,.2f} em valores futuros")
                    else:
                        st.success(f"✅ **VALORES FUTUROS**: Saldo positivo de €{sub_total:,.2f}")
                else:
                    if sub_total < 0:
                        st.error(f"🚨 **CRÍTICO**: Saldo negativo de €{abs(sub_total):,.2f} em valores em atraso!")
                    elif sub_total > 10000:
                        st.error(f"🚨 ALERTA: €{sub_total:,.2f} em valores em atraso!")
                    elif sub_total > 5000:
                        st.warning(f"⚠️ AVISO: €{sub_total:,.2f} em valores em atraso.")
                    else:
                        st.success(f"✅ SITUAÇÃO CONTROLADA: €{sub_total:,.2f} em valores em atraso")

                # Tabela de dados
                st.markdown("### 📋 Detalhamento por Comercial e Entidade")
                st.dataframe(
                    summary,
                    use_container_width=True,
                    height=400
                )
                
                # Gráfico de barras para visualização
                st.markdown("### 📊 Visualização por Comercial")
                if num_comerciais > 1:
                    comercial_summary = summary.groupby('Comercial')['Total Pendente'].sum().sort_values(ascending=False)
                    st.bar_chart(comercial_summary)
                else:
                    st.info("ℹ️ Adicione mais comerciais ao filtro para ver o gráfico comparativo")

            else:
                st.warning(f"📭 Nenhum dado encontrado para: {filtro_aplicado}")
                
            # Visualização dos dados brutos filtrados
            with st.expander("🔍 Visualizar Dados Brutos Filtrados"):
                st.dataframe(df_filtrado.head(10))
                st.write(f"**Total de registros:** {len(df_filtrado)}")
                st.write(f"**Valor Pendente mínimo:** €{df_filtrado['Valor Pendente'].min():,.2f}")
                st.write(f"**Valor Pendente máximo:** €{df_filtrado['Valor Pendente'].max():,.2f}")
                
                # Mostrar específicamente os valores negativos futuros
                if "Futuros" in tipo_filtro:
                    negativos_futuros_df = df_filtrado[
                        (df_filtrado['Valor Pendente'] < 0) & 
                        (df_filtrado['Dias'] >= 0)
                    ]
                    if len(negativos_futuros_df) > 0:
                        st.markdown("#### 🔴 Valores Negativos Futuros (Dias ≥ 0)")
                        st.dataframe(negativos_futuros_df)

    # ... (as tabs 2 e 3 permanecem iguais, apenas atualizando as variáveis)

else:
    st.error("❌ Não foi possível carregar os dados do Excel.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "📊 Dashboard desenvolvido para gestão eficiente de valores • "
    f"Última execução: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    "</div>", 
    unsafe_allow_html=True
)
