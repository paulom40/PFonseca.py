import streamlit as st
import pandas as pd
import json
from pathlib import Path
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas - Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para melhorar o visual
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3498db;
        font-weight: 600;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    .stSelectbox, .stMultiselect {
        background-color: white;
        border-radius: 8px;
    }
    .success-box {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 🔄 Carregamento e renomeação
@st.cache_data
def load_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
        df = pd.read_excel(url)

        df.columns = df.columns.str.strip().str.upper()
        renomear = {}
        for col in df.columns:
            if "CLIENTE" in col: renomear[col] = "Cliente"
            elif "QTD" in col: renomear[col] = "Qtd"
            elif "ARTIGO" in col: renomear[col] = "Artigo"
            elif "LÍQUIDO" in col: renomear[col] = "V_Liquido"
            elif "COMERCIAL" in col: renomear[col] = "Comercial"
            elif "CATEGORIA" in col: renomear[col] = "Categoria"
            elif "MÊS" in col or "MES" in col: renomear[col] = "Mes"
            elif "ANO" in col: renomear[col] = "Ano"
        df = df.rename(columns=renomear)
        
        # Remover colunas problemáticas
        colunas_para_manter = ['Cliente', 'Qtd', 'Artigo', 'V_Liquido', 'Comercial', 'Categoria', 'Mes', 'Ano']
        colunas_existentes = [col for col in colunas_para_manter if col in df.columns]
        df = df[colunas_existentes]
        
        # CORREÇÃO: Converter todas as colunas de texto para string
        text_columns = ['Cliente', 'Artigo', 'Comercial', 'Categoria', 'Mes', 'Ano']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        # CORREÇÃO: Converter colunas numéricas com tratamento robusto
        if 'V_Liquido' in df.columns:
            # Primeiro converter para string para limpar, depois para numérico
            df['V_Liquido'] = df['V_Liquido'].astype(str)
            # Remover caracteres não numéricos exceto ponto e vírgula
            df['V_Liquido'] = df['V_Liquido'].str.replace('[^\d.,]', '', regex=True)
            # Substituir vírgula por ponto para decimal
            df['V_Liquido'] = df['V_Liquido'].str.replace(',', '.')
            # Converter para numérico
            df['V_Liquido'] = pd.to_numeric(df['V_Liquido'], errors='coerce')
        
        if 'Qtd' in df.columns:
            df['Qtd'] = pd.to_numeric(df['Qtd'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

df = load_data()

# 📁 Presets
preset_path = Path("diagnosticos/presets_filtros.json")
preset_path.parent.mkdir(exist_ok=True)

def carregar_presets():
    if preset_path.exists():
        with open(preset_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_preset(nome, filtros):
    presets = carregar_presets()
    presets[nome] = filtros
    with open(preset_path, "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=2)

# 🎛️ Sidebar com filtros
with st.sidebar:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("### 🎛️ Painel de Controle")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Presets
    presets = carregar_presets()
    preset_selecionado = st.selectbox("📂 Carregar Configuração", [""] + list(presets.keys()))
    filtros = presets.get(preset_selecionado, {}) if preset_selecionado else {}
    
    # Filtros
    st.markdown("---")
    st.markdown("### 🔍 Filtros")
    
    def filtro_multiselect(label, coluna, valores=None):
        if coluna not in df.columns:
            return []
        valores_default = valores if valores else []
        opcoes = sorted(df[coluna].dropna().astype(str).unique())
        return st.multiselect(label, opcoes, default=valores_default)

    clientes = filtro_multiselect("👥 Clientes", "Cliente", filtros.get("Cliente"))
    artigos = filtro_multiselect("📦 Artigos", "Artigo", filtros.get("Artigo"))
    comerciais = filtro_multiselect("👨‍💼 Comerciais", "Comercial", filtros.get("Comercial"))
    categorias = filtro_multiselect("🏷️ Categorias", "Categoria", filtros.get("Categoria"))
    meses = filtro_multiselect("📅 Meses", "Mes", filtros.get("Mes"))
    anos = filtro_multiselect("📊 Anos", "Ano", filtros.get("Ano"))
    
    # Salvar preset
    st.markdown("---")
    st.markdown("### 💾 Configurações")
    nome_preset = st.text_input("Nome da configuração")
    if st.button("💾 Salvar Configuração") and nome_preset:
        filtros_atuais = {
            "Cliente": clientes, "Artigo": artigos, "Comercial": comerciais,
            "Categoria": categorias, "Mes": meses, "Ano": anos
        }
        salvar_preset(nome_preset, filtros_atuais)
        st.success(f"Configuração '{nome_preset}' salva!")
    
    # Estatísticas
    st.markdown("---")
    st.markdown("### 📈 Estatísticas")
    st.write(f"**Total de Registros:** {len(df):,}")
    st.write(f"**Clientes Únicos:** {df['Cliente'].nunique():,}")
    st.write(f"**Artigos Únicos:** {df['Artigo'].nunique():,}")

# 🔍 CORREÇÃO: Aplicar filtros de forma mais robusta
df_filtrado = df.copy()
filtros_aplicados = []

# CORREÇÃO: Aplicar cada filtro individualmente e mostrar debug
if clientes or artigos or comerciais or categorias or meses or anos:
    mascara = pd.Series([True] * len(df_filtrado), index=df_filtrado.index)
    
    # Debug: mostrar contagem antes dos filtros
    registros_iniciais = len(df_filtrado)
    
    if clientes:
        # CORREÇÃO: Garantir que estamos comparando strings
        clientes_str = [str(cliente) for cliente in clientes]
        mascara_cliente = df_filtrado["Cliente"].astype(str).isin(clientes_str)
        mascara = mascara & mascara_cliente
        filtros_aplicados.append(f"👥 Clientes: {len(clientes)}")
        st.sidebar.info(f"Filtro Clientes: {len(df_filtrado[mascara_cliente])} registros")
    
    if artigos:
        # CORREÇÃO: Garantir que estamos comparando strings para artigos
        artigos_str = [str(artigo) for artigo in artigos]
        mascara_artigo = df_filtrado["Artigo"].astype(str).isin(artigos_str)
        mascara = mascara & mascara_artigo
        filtros_aplicados.append(f"📦 Artigos: {len(artigos)}")
        st.sidebar.info(f"Filtro Artigos: {len(df_filtrado[mascara_artigo])} registros")
    
    if comerciais:
        comerciais_str = [str(comercial) for comercial in comerciais]
        mascara_comercial = df_filtrado["Comercial"].astype(str).isin(comerciais_str)
        mascara = mascara & mascara_comercial
        filtros_aplicados.append(f"👨‍💼 Comerciais: {len(comerciais)}")
    
    if categorias:
        categorias_str = [str(categoria) for categoria in categorias]
        mascara_categoria = df_filtrado["Categoria"].astype(str).isin(categorias_str)
        mascara = mascara & mascara_categoria
        filtros_aplicados.append(f"🏷️ Categorias: {len(categorias)}")
    
    if meses:
        meses_str = [str(mes) for mes in meses]
        mascara_mes = df_filtrado["Mes"].astype(str).isin(meses_str)
        mascara = mascara & mascara_mes
        filtros_aplicados.append(f"📅 Meses: {len(meses)}")
    
    if anos:
        anos_str = [str(ano) for ano in anos]
        mascara_ano = df_filtrado["Ano"].astype(str).isin(anos_str)
        mascara = mascara & mascara_ano
        filtros_aplicados.append(f"📊 Anos: {len(anos)}")
    
    df_filtrado = df_filtrado[mascara]
    
    # Debug info
    st.sidebar.info(f"Registros após filtros: {len(df_filtrado)}/{registros_iniciais}")

# 🎯 Header principal
st.markdown("<h1 class='main-header'>📊 Business Intelligence - Dashboard de Vendas</h1>", unsafe_allow_html=True)

# CORREÇÃO: Mostrar informações de debug sobre os dados
with st.expander("🔍 Informações dos Dados", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Colunas disponíveis:**", list(df.columns))
    with col2:
        if not df.empty:
            st.write("**Tipos de dados:**")
            for col in df.columns:
                st.write(f"- {col}: {df[col].dtype}")
    with col3:
        if not df.empty and 'V_Liquido' in df.columns:
            st.write("**Estatísticas V_Liquido:**")
            st.write(f"- Não nulos: {df['V_Liquido'].notna().sum()}")
            st.write(f"- Nulos: {df['V_Liquido'].isna().sum()}")
            st.write(f"- Soma: € {df['V_Liquido'].sum():,.2f}")

if df_filtrado.empty:
    st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
    st.markdown("### ⚠️ Nenhum dado encontrado com os filtros selecionados")
    st.markdown("**Sugestões:**")
    st.markdown("- Verifique se os filtros não estão conflitando")
    st.markdown("- Tente aplicar menos filtros de cada vez")
    st.markdown("- Verifique se os valores existem nos dados")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Mostrar amostra de dados disponíveis
    with st.expander("🔍 Ver amostra de dados disponíveis"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**📦 Artigos disponíveis (primeiros 10):**")
            artigos_disponiveis = sorted(df['Artigo'].dropna().astype(str).unique())[:10]
            for artigo in artigos_disponiveis:
                st.write(f"- {artigo}")
        
        with col2:
            st.write("**👥 Clientes disponíveis (primeiros 10):**")
            clientes_disponiveis = sorted(df['Cliente'].dropna().astype(str).unique())[:10]
            for cliente in clientes_disponiveis:
                st.write(f"- {cliente}")
        
        with col3:
            st.write("**👨‍💼 Comerciais disponíveis:**")
            comerciais_disponiveis = sorted(df['Comercial'].dropna().astype(str).unique())
            for comercial in comerciais_disponiveis:
                st.write(f"- {comercial}")
else:
    # ✅ Indicadores de sucesso
    st.markdown("<div class='success-box'>", unsafe_allow_html=True)
    st.markdown(f"### ✅ **{len(df_filtrado):,}** registros encontrados após filtro")
    if filtros_aplicados:
        st.markdown("**Filtros aplicados:** " + " | ".join(filtros_aplicados))
    
    # CORREÇÃO: Mostrar informações sobre o cálculo do Total de Vendas
    if 'V_Liquido' in df_filtrado.columns:
        total_vendas_calculado = df_filtrado['V_Liquido'].sum()
        registros_validos = df_filtrado['V_Liquido'].notna().sum()
        registros_invalidos = df_filtrado['V_Liquido'].isna().sum()
        
        st.markdown(f"**💰 Total de Vendas calculado:** € {total_vendas_calculado:,.2f}")
        st.markdown(f"**📊 Baseado em:** {registros_validos} registros válidos")
        if registros_invalidos > 0:
            st.markdown(f"**⚠️ Ignorados:** {registros_invalidos} registros inválidos")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 📊 Abas principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Dashboard Principal", 
        "👥 Análise por Cliente", 
        "👨‍💼 Análise por Comercial", 
        "🚨 Alertas & Insights"
    ])
    
    with tab1:
        # 🎯 Métricas principais
        st.markdown("<div class='section-header'>🎯 Métricas Principais</div>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # CORREÇÃO: Cálculo robusto do Total de Vendas
            if 'V_Liquido' in df_filtrado.columns:
                total_vendas = df_filtrado['V_Liquido'].sum()
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric("💰 Total de Vendas", f"€ {total_vendas:,.2f}")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric("💰 Total de Vendas", "N/D")
                st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            if 'Qtd' in df_filtrado.columns:
                total_qtd = df_filtrado['Qtd'].sum()
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric("📦 Quantidade Total", f"{total_qtd:,.0f}")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric("📦 Quantidade Total", "N/D")
                st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            clientes_unicos = df_filtrado['Cliente'].nunique()
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("👥 Clientes Únicos", f"{clientes_unicos:,}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            artigos_unicos = df_filtrado['Artigo'].nunique()
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("🏷️ Artigos Únicos", f"{artigos_unicos:,}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # 📈 Visualizações
        st.markdown("<div class='section-header'>📈 Visualizações</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 clientes
            if 'V_Liquido' in df_filtrado.columns:
                top_clientes = df_filtrado.groupby('Cliente')['V_Liquido'].sum().nlargest(10)
                if not top_clientes.empty:
                    fig = px.bar(
                        top_clientes, 
                        x=top_clientes.values, 
                        y=top_clientes.index,
                        orientation='h',
                        title='🏆 Top 10 Clientes por Vendas',
                        labels={'x': 'Vendas (€)', 'y': 'Cliente'},
                        color=top_clientes.values,
                        color_continuous_scale='viridis'
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top 10 artigos
            if 'V_Liquido' in df_filtrado.columns:
                top_artigos = df_filtrado.groupby('Artigo')['V_Liquido'].sum().nlargest(10)
                if not top_artigos.empty:
                    fig = px.pie(
                        top_artigos,
                        values=top_artigos.values,
                        names=top_artigos.index,
                        title='📦 Top 10 Artigos por Vendas',
                        hole=0.4
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # 📋 Dados detalhados
        st.markdown("<div class='section-header'>📋 Dados Filtrados</div>", unsafe_allow_html=True)
        
        # Mostrar estatísticas dos dados filtrados
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'V_Liquido' in df_filtrado.columns:
                st.info(f"**📊 Total de Vendas:** € {df_filtrado['V_Liquido'].sum():,.2f}")
        with col2:
            if 'Qtd' in df_filtrado.columns:
                st.info(f"**📦 Quantidade Total:** {df_filtrado['Qtd'].sum():,.0f}")
        with col3:
            st.info(f"**👥 Clientes no Filtro:** {df_filtrado['Cliente'].nunique():,}")
        
        # CORREÇÃO: Garantir que todas as colunas sejam strings antes de exibir
        df_display = df_filtrado.copy()
        for col in df_display.columns:
            if df_display[col].dtype == 'object':
                df_display[col] = df_display[col].astype(str)
        
        st.dataframe(df_display, width='stretch')
    
    # ... (resto do código das outras abas permanece igual)

# 🎯 Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #7f8c8d;'>", unsafe_allow_html=True)
st.markdown("📊 **Business Intelligence Dashboard** • Desenvolvido com Streamlit • ")
st.markdown(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown("</div>", unsafe_allow_html=True)
