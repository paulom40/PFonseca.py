import streamlit as st
import pandas as pd
import json
from pathlib import Path
import numpy as np
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas - Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
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
</style>
""", unsafe_allow_html=True)

# 🔄 CARREGAMENTO SIMPLIFICADO - CORREÇÃO DEFINITIVA
@st.cache_data
def load_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
        
        # Carregar o arquivo mantendo os nomes originais
        df = pd.read_excel(url)
        
        st.sidebar.info(f"📋 Colunas originais carregadas: {list(df.columns)}")
        
        # VERIFICAÇÃO MANUAL DAS COLUNAS
        st.sidebar.markdown("### 🔍 Verificação das Colunas")
        
        # Mostrar amostra de cada coluna para identificação
        for i, coluna in enumerate(df.columns):
            amostra = df[coluna].dropna().head(3).tolist()
            st.sidebar.write(f"**Coluna {i} ({coluna}):** {amostra}")
        
        # CORREÇÃO DEFINITIVA: MAPEAMENTO MANUAL BASEADO NA POSIÇÃO
        # Vamos assumir que:
        # Coluna 0: Cliente
        # Coluna 1: Qtd  
        # Coluna 6: Artigo (Coluna G)
        # E procurar as outras pelo nome
        
        mapeamento = {}
        
        # Mapeamento por posição (garantido)
        if len(df.columns) > 0:
            mapeamento[df.columns[0]] = "Cliente"
        if len(df.columns) > 1:
            mapeamento[df.columns[1]] = "Qtd"
        if len(df.columns) > 6:
            mapeamento[df.columns[6]] = "Artigo"
            st.sidebar.success(f"✅ **Coluna G definida como Artigo:** '{df.columns[6]}'")
        
        # Procurar outras colunas pelo nome
        for coluna in df.columns:
            col_upper = str(coluna).upper()
            if "LÍQUIDO" in col_upper or "LIQUIDO" in col_upper:
                mapeamento[coluna] = "V_Liquido"
            elif "COMERCIAL" in col_upper:
                mapeamento[coluna] = "Comercial"
            elif "CATEGORIA" in col_upper:
                mapeamento[coluna] = "Categoria"
            elif "MÊS" in col_upper or "MES" in col_upper:
                mapeamento[coluna] = "Mes"
            elif "ANO" in col_upper:
                mapeamento[coluna] = "Ano"
        
        # Aplicar renomeação
        df = df.rename(columns=mapeamento)
        
        # Manter apenas colunas mapeadas
        colunas_desejadas = ['Cliente', 'Qtd', 'Artigo', 'V_Liquido', 'Comercial', 'Categoria', 'Mes', 'Ano']
        colunas_existentes = [col for col in colunas_desejadas if col in df.columns]
        df = df[colunas_existentes]
        
        st.sidebar.success(f"🎯 Colunas finais: {colunas_existentes}")
        
        # VERIFICAÇÃO CRÍTICA DA COLUNA ARTIGO
        if 'Artigo' in df.columns:
            st.sidebar.success(f"📦 Coluna Artigo carregada com {df['Artigo'].nunique():,} valores únicos")
            st.sidebar.write(f"📊 Amostra de Artigos: {df['Artigo'].dropna().head(5).tolist()}")
        else:
            st.sidebar.error("❌ COLUNA ARTIGO NÃO ENCONTRADA!")
            return pd.DataFrame()
        
        # Converter tipos de dados
        if 'Artigo' in df.columns:
            df['Artigo'] = df['Artigo'].astype(str)
        if 'Cliente' in df.columns:
            df['Cliente'] = df['Cliente'].astype(str)
        if 'V_Liquido' in df.columns:
            df['V_Liquido'] = pd.to_numeric(df['V_Liquido'], errors='coerce')
        if 'Qtd' in df.columns:
            df['Qtd'] = pd.to_numeric(df['Qtd'], errors='coerce')
            
        return df
        
    except Exception as e:
        st.error(f"Erro no carregamento: {str(e)}")
        return pd.DataFrame()

# Carregar dados
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

# 🎛️ SIDEBAR SIMPLIFICADA
with st.sidebar:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("### 🎛️ Painel de Controle")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Presets
    presets = carregar_presets()
    preset_selecionado = st.selectbox("📂 Carregar Configuração", [""] + list(presets.keys()))
    filtros = presets.get(preset_selecionado, {}) if preset_selecionado else {}
    
    st.markdown("---")
    st.markdown("### 🔍 Filtros")
    
    # FUNÇÃO DE FILTRO SIMPLIFICADA
    def criar_filtro(label, coluna, valores_default=None):
        if coluna not in df.columns:
            st.warning(f"Coluna '{coluna}' não disponível")
            return []
        
        valores_default = valores_default or []
        opcoes = sorted(df[coluna].dropna().astype(str).unique())
        return st.multiselect(label, opcoes, default=valores_default)
    
    # FILTROS
    clientes = criar_filtro("👥 Clientes", "Cliente", filtros.get("Cliente"))
    
    # FILTRO DE ARTIGOS - CORREÇÃO DEFINITIVA
    if 'Artigo' in df.columns:
        artigos_opcoes = sorted(df['Artigo'].dropna().astype(str).unique())
        artigos = st.multiselect(
            "📦 Artigos (Coluna G)", 
            artigos_opcoes,
            default=filtros.get("Artigo", [])
        )
        st.sidebar.info(f"Artigos disponíveis: {len(artigos_opcoes):,}")
    else:
        st.error("❌ Coluna Artigo não carregada")
        artigos = []
    
    comerciais = criar_filtro("👨‍💼 Comerciais", "Comercial", filtros.get("Comercial"))
    categorias = criar_filtro("🏷️ Categorias", "Categoria", filtros.get("Categoria"))
    meses = criar_filtro("📅 Meses", "Mes", filtros.get("Mes"))
    anos = criar_filtro("📊 Anos", "Ano", filtros.get("Ano"))
    
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
        st.success(f"✅ Configuração salva!")
    
    # Estatísticas
    st.markdown("---")
    st.markdown("### 📈 Estatísticas")
    if not df.empty:
        st.write(f"**Registros:** {len(df):,}")
        if 'Artigo' in df.columns:
            st.write(f"**Artigos únicos:** {df['Artigo'].nunique():,}")
        if 'Cliente' in df.columns:
            st.write(f"**Clientes únicos:** {df['Cliente'].nunique():,}")

# 🎯 APLICAÇÃO DOS FILTROS
df_filtrado = df.copy()
filtros_aplicados = []

if clientes or artigos or comerciais or categorias or meses or anos:
    # Aplicar filtros sequencialmente
    if clientes:
        df_filtrado = df_filtrado[df_filtrado['Cliente'].astype(str).isin(clientes)]
        filtros_aplicados.append(f"👥 Clientes: {len(clientes)}")
    
    # FILTRO DE ARTIGOS - APLICAÇÃO DIRETA
    if artigos and 'Artigo' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Artigo'].astype(str).isin(artigos)]
        filtros_aplicados.append(f"📦 Artigos: {len(artigos)}")
        st.sidebar.success(f"✅ Filtro Artigo aplicado: {len(df_filtrado)} registros")
    
    if comerciais and 'Comercial' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Comercial'].astype(str).isin(comerciais)]
        filtros_aplicados.append(f"👨‍💼 Comerciais: {len(comerciais)}")
    
    if categorias and 'Categoria' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Categoria'].astype(str).isin(categorias)]
        filtros_aplicados.append(f"🏷️ Categorias: {len(categorias)}")
    
    if meses and 'Mes' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Mes'].astype(str).isin(meses)]
        filtros_aplicados.append(f"📅 Meses: {len(meses)}")
    
    if anos and 'Ano' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Ano'].astype(str).isin(anos)]
        filtros_aplicados.append(f"📊 Anos: {len(anos)}")

# 🎯 INTERFACE PRINCIPAL
st.markdown("<h1 class='main-header'>📊 Dashboard de Vendas</h1>", unsafe_allow_html=True)

# DEBUG EXPANDER
with st.expander("🔧 Debug - Informações Técnicas", expanded=False):
    if not df.empty:
        st.write("**Estrutura dos dados:**")
        for col in df.columns:
            st.write(f"- **{col}**: {df[col].dtype} | Únicos: {df[col].nunique():,}")
        
        if 'Artigo' in df.columns:
            st.write("**Valores de Artigo (primeiros 20):**")
            artigos_unicos = sorted(df['Artigo'].dropna().astype(str).unique())[:20]
            for i, artigo in enumerate(artigos_unicos, 1):
                st.write(f"  {i:2d}. {artigo}")

if df.empty:
    st.error("❌ Não foi possível carregar os dados. Verifique o arquivo Excel.")
elif df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros aplicados.")
    
    if artigos and 'Artigo' not in df.columns:
        st.error("""
        **Problema crítico com a coluna Artigo:**
        - A coluna G não foi identificada como Artigo
        - Verifique se o arquivo Excel tem dados na coluna G
        - As colunas carregadas são mostradas na sidebar
        """)
else:
    # ✅ DADOS ENCONTRADOS
    st.success(f"✅ **{len(df_filtrado):,}** registros encontrados")
    
    if filtros_aplicados:
        st.info(f"**Filtros aplicados:** {' | '.join(filtros_aplicados)}")
    
    # MÉTRICAS PRINCIPAIS
    st.markdown("<div class='section-header'>🎯 Métricas Principais</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'V_Liquido' in df_filtrado.columns:
            total_vendas = df_filtrado['V_Liquido'].sum()
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("💰 Total Vendas", f"€ {total_vendas:,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        if 'Qtd' in df_filtrado.columns:
            total_qtd = df_filtrado['Qtd'].sum()
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("📦 Quantidade", f"{total_qtd:,.0f}")
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        if 'Cliente' in df_filtrado.columns:
            clientes_unicos = df_filtrado['Cliente'].nunique()
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("👥 Clientes", f"{clientes_unicos:,}")
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        if 'Artigo' in df_filtrado.columns:
            artigos_unicos = df_filtrado['Artigo'].nunique()
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("🏷️ Artigos", f"{artigos_unicos:,}")
            st.markdown("</div>", unsafe_allow_html=True)
    
    # GRÁFICOS
    st.markdown("<div class='section-header'>📈 Visualizações</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'V_Liquido' in df_filtrado.columns and 'Cliente' in df_filtrado.columns:
            top_clientes = df_filtrado.groupby('Cliente')['V_Liquido'].sum().nlargest(10)
            if not top_clientes.empty:
                fig = px.bar(
                    top_clientes, 
                    x=top_clientes.values, 
                    y=top_clientes.index,
                    orientation='h',
                    title='🏆 Top 10 Clientes',
                    labels={'x': 'Vendas (€)', 'y': ''}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'V_Liquido' in df_filtrado.columns and 'Artigo' in df_filtrado.columns:
            top_artigos = df_filtrado.groupby('Artigo')['V_Liquido'].sum().nlargest(10)
            if not top_artigos.empty:
                fig = px.bar(
                    top_artigos,
                    x=top_artigos.values,
                    y=top_artigos.index,
                    orientation='h',
                    title='📦 Top 10 Artigos',
                    labels={'x': 'Vendas (€)', 'y': ''}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # DADOS FILTRADOS
    st.markdown("<div class='section-header'>📋 Dados Filtrados</div>", unsafe_allow_html=True)
    st.dataframe(df_filtrado, width='stretch')

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #7f8c8d;'>", unsafe_allow_html=True)
st.markdown(f"📊 Dashboard • {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown("</div>", unsafe_allow_html=True)
