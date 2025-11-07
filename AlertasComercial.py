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

# 🔄 CORREÇÃO COMPLETA do carregamento de dados
@st.cache_data
def load_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
        
        # Carregar o arquivo SEM renomear as colunas inicialmente
        df = pd.read_excel(url)
        
        st.sidebar.info(f"📋 Colunas originais: {list(df.columns)}")
        
        # CORREÇÃO: Identificar a coluna G (índice 6) como Artigo
        # Vamos usar a coluna na posição 6 (coluna G) como Artigo
        mapeamento_colunas = {}
        
        # Mapear as colunas pelas suas posições
        if len(df.columns) > 0:
            mapeamento_colunas[df.columns[0]] = "Cliente"  # Coluna A
        if len(df.columns) > 1:
            mapeamento_colunas[df.columns[1]] = "Qtd"      # Coluna B
        if len(df.columns) > 6:
            # CORREÇÃO: Coluna G (índice 6) é o Artigo
            mapeamento_colunas[df.columns[6]] = "Artigo"
            st.sidebar.success(f"✅ Coluna G identificada como Artigo: '{df.columns[6]}'")
        
        # Procurar outras colunas importantes pelo nome
        for coluna in df.columns:
            coluna_upper = coluna.strip().upper()
            
            if "LÍQUIDO" in coluna_upper or "LIQUIDO" in coluna_upper or "VALOR" in coluna_upper:
                mapeamento_colunas[coluna] = "V_Liquido"
            elif "COMERCIAL" in coluna_upper or "VENDEDOR" in coluna_upper:
                mapeamento_colunas[coluna] = "Comercial"
            elif "CATEGORIA" in coluna_upper:
                mapeamento_colunas[coluna] = "Categoria"
            elif "MÊS" in coluna_upper or "MES" in coluna_upper:
                mapeamento_colunas[coluna] = "Mes"
            elif "ANO" in coluna_upper:
                mapeamento_colunas[coluna] = "Ano"
        
        # Aplicar o mapeamento
        df = df.rename(columns=mapeamento_colunas)
        
        # Manter apenas as colunas mapeadas
        colunas_para_manter = ['Cliente', 'Qtd', 'Artigo', 'V_Liquido', 'Comercial', 'Categoria', 'Mes', 'Ano']
        colunas_existentes = [col for col in colunas_para_manter if col in df.columns]
        df = df[colunas_existentes]
        
        st.sidebar.info(f"📊 Colunas mapeadas: {', '.join(colunas_existentes)}")
        
        # CORREÇÃO: Garantir que a coluna Artigo existe
        if 'Artigo' not in df.columns:
            st.error("❌ COLUNA ARTIGO NÃO ENCONTRADA!")
            st.error("Por favor, verifique se o arquivo Excel tem dados na coluna G")
            return pd.DataFrame()
        
        # Converter todas as colunas de texto para string
        text_columns = ['Cliente', 'Artigo', 'Comercial', 'Categoria', 'Mes', 'Ano']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        # Converter colunas numéricas
        if 'V_Liquido' in df.columns:
            df['V_Liquido'] = pd.to_numeric(df['V_Liquido'], errors='coerce')
        
        if 'Qtd' in df.columns:
            df['Qtd'] = pd.to_numeric(df['Qtd'], errors='coerce')
        
        # Mostrar estatísticas da coluna Artigo
        if 'Artigo' in df.columns:
            st.sidebar.success(f"📦 Artigos únicos carregados: {df['Artigo'].nunique():,}")
            st.sidebar.success(f"📊 Registros com Artigo: {df['Artigo'].notna().sum():,}")
        
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

# 🎛️ Sidebar com filtros - CORREÇÃO COMPLETA do filtro Artigo
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
            st.warning(f"⚠️ Coluna '{coluna}' não encontrada")
            return []
        valores_default = valores if valores else []
        opcoes = sorted(df[coluna].dropna().astype(str).unique())
        return st.multiselect(label, opcoes, default=valores_default)

    clientes = filtro_multiselect("👥 Clientes", "Cliente", filtros.get("Cliente"))
    
    # CORREÇÃO: Filtro de Artigos - verificação robusta
    if 'Artigo' in df.columns:
        artigos_disponiveis = sorted(df['Artigo'].dropna().astype(str).unique())
        st.sidebar.info(f"📦 Artigos disponíveis: {len(artigos_disponiveis):,}")
        
        # Mostrar amostra de artigos na sidebar
        with st.sidebar.expander("🔍 Ver amostra de Artigos"):
            for i, artigo in enumerate(artigos_disponiveis[:10]):
                st.write(f"{i+1}. {artigo}")
            if len(artigos_disponiveis) > 10:
                st.write(f"... e mais {len(artigos_disponiveis) - 10} artigos")
        
        artigos = st.multiselect(
            "📦 Artigos (Coluna G)", 
            artigos_disponiveis,
            default=filtros.get("Artigo", [])
        )
    else:
        st.error("❌ COLUNA ARTIGO NÃO DISPONÍVEL")
        artigos = []
    
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
        st.success(f"✅ Configuração '{nome_preset}' salva!")
    
    # Estatísticas
    st.markdown("---")
    st.markdown("### 📈 Estatísticas")
    st.write(f"**Total de Registros:** {len(df):,}")
    st.write(f"**Clientes Únicos:** {df['Cliente'].nunique():,}")
    if 'Artigo' in df.columns:
        st.write(f"**Artigos Únicos:** {df['Artigo'].nunique():,}")
    else:
        st.write("**Artigos Únicos:** ❌ Coluna não encontrada")

# 🔍 CORREÇÃO: Aplicar filtros de forma mais clara
df_filtrado = df.copy()
filtros_aplicados = []

if clientes or artigos or comerciais or categorias or meses or anos:
    mascara = pd.Series([True] * len(df_filtrado), index=df_filtrado.index)
    registros_iniciais = len(df_filtrado)
    
    # Aplicar cada filtro individualmente
    if clientes:
        mascara_cliente = df_filtrado["Cliente"].astype(str).isin(clientes)
        mascara = mascara & mascara_cliente
        filtros_aplicados.append(f"👥 Clientes: {len(clientes)}")
    
    # CORREÇÃO: Aplicar filtro de Artigos com verificação
    if artigos:
        if 'Artigo' in df_filtrado.columns:
            mascara_artigo = df_filtrado["Artigo"].astype(str).isin(artigos)
            registros_apos_artigo = mascara_artigo.sum()
            mascara = mascara & mascara_artigo
            filtros_aplicados.append(f"📦 Artigos: {len(artigos)}")
            st.sidebar.info(f"📊 Registros após filtro Artigo: {registros_apos_artigo}")
        else:
            st.error("❌ Não foi possível aplicar filtro de Artigos - coluna não encontrada")
    
    if comerciais:
        mascara_comercial = df_filtrado["Comercial"].astype(str).isin(comerciais)
        mascara = mascara & mascara_comercial
        filtros_aplicados.append(f"👨‍💼 Comerciais: {len(comerciais)}")
    
    if categorias:
        mascara_categoria = df_filtrado["Categoria"].astype(str).isin(categorias)
        mascara = mascara & mascara_categoria
        filtros_aplicados.append(f"🏷️ Categorias: {len(categorias)}")
    
    if meses:
        mascara_mes = df_filtrado["Mes"].astype(str).isin(meses)
        mascara = mascara & mascara_mes
        filtros_aplicados.append(f"📅 Meses: {len(meses)}")
    
    if anos:
        mascara_ano = df_filtrado["Ano"].astype(str).isin(anos)
        mascara = mascara & mascara_ano
        filtros_aplicados.append(f"📊 Anos: {len(anos)}")
    
    df_filtrado = df_filtrado[mascara]
    
    # Mostrar estatísticas de filtragem
    st.sidebar.info(f"📈 Filtros aplicados: {len(filtros_aplicados)}")
    st.sidebar.info(f"🔍 Resultado: {len(df_filtrado)}/{registros_iniciais} registros")

# 🎯 Header principal
st.markdown("<h1 class='main-header'>📊 Business Intelligence - Dashboard de Vendas</h1>", unsafe_allow_html=True)

# Informações de debug
with st.expander("🔧 Informações Técnicas", expanded=False):
    if not df.empty:
        st.write("**📋 Estrutura dos dados:**")
        st.write(f"- Colunas carregadas: {list(df.columns)}")
        st.write(f"- Total de registros: {len(df):,}")
        
        if 'Artigo' in df.columns:
            st.write("**📦 Informações da coluna Artigo:**")
            st.write(f"- Artigos únicos: {df['Artigo'].nunique():,}")
            st.write(f"- Registros com Artigo preenchido: {df['Artigo'].notna().sum():,}")
            st.write(f"- Registros sem Artigo: {df['Artigo'].isna().sum():,}")
            
            st.write("**🔍 Amostra de Artigos:**")
            artigos_amostra = df['Artigo'].dropna().astype(str).unique()[:10]
            for i, artigo in enumerate(artigos_amostra):
                st.write(f"  {i+1}. {artigo}")

if df_filtrado.empty:
    st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
    st.markdown("### ⚠️ Nenhum dado encontrado com os filtros selecionados")
    
    if artigos and 'Artigo' not in df.columns:
        st.markdown("**❌ Problema crítico:** Coluna Artigo não foi encontrada no arquivo!")
        st.markdown("**💡 Solução:** Verifique se o arquivo Excel tem dados na coluna G")
    
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # ✅ Indicadores de sucesso
    st.markdown("<div class='success-box'>", unsafe_allow_html=True)
    st.markdown(f"### ✅ **{len(df_filtrado):,}** registros encontrados após filtro")
    
    if filtros_aplicados:
        st.markdown("**Filtros aplicados:** " + " | ".join(filtros_aplicados))
    
    # Informações específicas sobre Artigos
    if 'Artigo' in df_filtrado.columns and artigos:
        artigos_filtrados = df_filtrado['Artigo'].nunique()
        st.markdown(f"**📦 Artigos no resultado:** {artigos_filtrados} de {len(artigos)} selecionados")
    
    if 'V_Liquido' in df_filtrado.columns:
        total_vendas = df_filtrado['V_Liquido'].sum()
        st.markdown(f"**💰 Total de Vendas:** € {total_vendas:,.2f}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 📊 Abas principais (o restante do código permanece similar)
    # ... [restante do código das abas]

# 🎯 Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #7f8c8d;'>", unsafe_allow_html=True)
st.markdown("📊 **Business Intelligence Dashboard** • Desenvolvido com Streamlit • ")
st.markdown(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown("</div>", unsafe_allow_html=True)
