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
    .metric-card-reference {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
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

# 🔄 CARREGAMENTO CORRETO - NOVO FICHEIRO
@st.cache_data
def load_all_data():
    try:
        # ✅ NOVO CAMINHO DO FICHEIRO
        url = "https://github.com/paulom40/PFonseca.py/raw/main/VendasGeraisTranf.xlsx"
        df = pd.read_excel(url)
        
        st.sidebar.success(f"✅ Ficheiro carregado: {len(df)} registos")
        
        # CORREÇÃO: USAR OS CABEÇALHOS EXATOS DO EXCEL
        mapeamento = {
            'Código': 'Codigo',
            'Cliente': 'Cliente', 
            'Qtd.': 'Qtd',
            'UN': 'UN',
            'PM': 'PM',
            'V. Líquido': 'V_Liquido',
            'Artigo': 'Artigo',
            'Comercial': 'Comercial',
            'Categoria': 'Categoria',
            'Mês': 'Mes',
            'Ano': 'Ano'
        }
        
        # Aplicar renomeação apenas para colunas que existem
        mapeamento_final = {}
        for col_original, col_novo in mapeamento.items():
            if col_original in df.columns:
                mapeamento_final[col_original] = col_novo
                st.sidebar.info(f"✅ {col_original} → {col_novo}")
        
        df = df.rename(columns=mapeamento_final)
        
        # ✅ CONVERSÃO SEGURA PARA NUMÉRICO
        if 'V_Liquido' in df.columns:
            df['V_Liquido'] = pd.to_numeric(df['V_Liquido'], errors='coerce')
            st.sidebar.info("✅ V_Liquido convertido para numérico")
        
        if 'Qtd' in df.columns:
            df['Qtd'] = pd.to_numeric(df['Qtd'], errors='coerce')
            st.sidebar.info("✅ Qtd convertido para numérico")
        
        if 'PM' in df.columns:
            df['PM'] = pd.to_numeric(df['PM'], errors='coerce')
        
        # ✅ CONVERSÃO PARA TEXTO
        for col in ['Artigo', 'Cliente', 'Comercial', 'Categoria', 'Mes', 'Ano', 'UN']:
            if col in df.columns:
                df[col] = df[col].astype(str)
                st.sidebar.info(f"✅ {col} convertido para texto")
            
        return df
        
    except Exception as e:
        st.error(f"Erro no carregamento: {str(e)}")
        return pd.DataFrame()

# Carregar dados
df = load_all_data()

# 📊 MÉTRICAS DE REFERÊNCIA (VALIDAÇÃO)
TOTAL_QTD_REFERENCIA = 4449342.03
TOTAL_V_LIQUIDO_REFERENCIA = 11032291.5

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

# 🎛️ SIDEBAR
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
    
    # FUNÇÃO DE FILTRO SEGURO
    def criar_filtro_seguro(label, coluna, valores_default=None):
        if coluna not in df.columns or df.empty:
            st.warning(f"Coluna '{coluna}' não disponível")
            return []
        
        try:
            valores_default = valores_default or []
            opcoes = sorted(df[coluna].dropna().astype(str).unique())
            return st.multiselect(label, opcoes, default=valores_default)
        except Exception as e:
            st.error(f"Erro no filtro {label}: {e}")
            return []
    
    # FILTROS
    clientes = criar_filtro_seguro("👥 Clientes", "Cliente", filtros.get("Cliente"))
    
    # ✅ FILTRO DE ARTIGOS - TODOS OS DADOS
    if not df.empty and 'Artigo' in df.columns:
        artigos_opcoes = sorted(df['Artigo'].dropna().astype(str).unique())
        artigos = st.multiselect(
            "📦 Artigos", 
            artigos_opcoes,
            default=filtros.get("Artigo", []),
            placeholder="Selecione os artigos..."
        )
        st.sidebar.info(f"Artigos disponíveis: {len(artigos_opcoes)}")
        
        if artigos:
            st.sidebar.success(f"✅ {len(artigos)} artigo(s) selecionado(s)")
    else:
        st.error("❌ Coluna Artigo não carregada")
        artigos = []
    
    comerciais = criar_filtro_seguro("👨‍💼 Comerciais", "Comercial", filtros.get("Comercial"))
    categorias = criar_filtro_seguro("🏷️ Categorias", "Categoria", filtros.get("Categoria"))
    meses = criar_filtro_seguro("📅 Meses", "Mes", filtros.get("Mes"))
    anos = criar_filtro_seguro("📊 Anos", "Ano", filtros.get("Ano"))
    
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
    if not df.empty:
        st.write(f"**Registros:** {len(df):,}")
        if 'Artigo' in df.columns:
            st.write(f"**Artigos únicos:** {df['Artigo'].nunique():,}")
        if 'Cliente' in df.columns:
            st.write(f"**Clientes únicos:** {df['Cliente'].nunique():,}")
        
        # Totais atuais
        if 'V_Liquido' in df.columns and 'Qtd' in df.columns:
            st.write("**Totais do ficheiro:**")
            st.write(f"- V. Líquido: € {df['V_Liquido'].sum():,.2f}")
            st.write(f"- Qtd: {df['Qtd'].sum():,.2f}")

# 🎯 APLICAÇÃO DOS FILTROS
df_filtrado = df.copy()
filtros_aplicados = []

if not df.empty:
    if clientes or artigos or comerciais or categorias or meses or anos:
        # Aplicar filtros sequencialmente
        if clientes:
            df_filtrado = df_filtrado[df_filtrado['Cliente'].astype(str).isin(clientes)]
            filtros_aplicados.append(f"👥 Clientes: {len(clientes)}")
        
        if artigos and 'Artigo' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Artigo'].astype(str).isin(artigos)]
            filtros_aplicados.append(f"📦 Artigos: {len(artigos)}")
        
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

# DEBUG: Informações técnicas
with st.expander("🔧 Informações Técnicas", expanded=False):
    if not df.empty:
        st.write("**Estrutura dos dados carregados:**")
        for col in df.columns:
            st.write(f"- **{col}**: {df[col].dtype} | Únicos: {df[col].nunique():,}")
        
        st.write("**Totais do ficheiro (sem filtros):**")
        if 'V_Liquido' in df.columns:
            st.write(f"- V_Liquido: € {df['V_Liquido'].sum():,.2f}")
        if 'Qtd' in df.columns:
            st.write(f"- Qtd: {df['Qtd'].sum():,.2f}")

if df.empty:
    st.error("❌ Não foi possível carregar os dados.")
elif df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros aplicados.")
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
    
    # 🎯 MÉTRICAS DE VALIDAÇÃO
    st.markdown("<div class='section-header'>📊 Validação de Dados</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Qtd' in df_filtrado.columns:
            total_qtd_atual = df_filtrado['Qtd'].sum()
            diferenca_qtd = total_qtd_atual - TOTAL_QTD_REFERENCIA
            percentual_qtd = (diferenca_qtd / TOTAL_QTD_REFERENCIA) * 100 if TOTAL_QTD_REFERENCIA != 0 else 0
            
            st.markdown("<div class='metric-card-reference'>", unsafe_allow_html=True)
            st.metric(
                "📦 Validação Qtd", 
                f"{total_qtd_atual:,.2f}",
                delta=f"{diferenca_qtd:+.2f} ({percentual_qtd:+.2f}%)",
                help=f"Referência: {TOTAL_QTD_REFERENCIA:,.2f}"
            )
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        if 'V_Liquido' in df_filtrado.columns:
            total_vendas_atual = df_filtrado['V_Liquido'].sum()
            diferenca_vendas = total_vendas_atual - TOTAL_V_LIQUIDO_REFERENCIA
            percentual_vendas = (diferenca_vendas / TOTAL_V_LIQUIDO_REFERENCIA) * 100 if TOTAL_V_LIQUIDO_REFERENCIA != 0 else 0
            
            st.markdown("<div class='metric-card-reference'>", unsafe_allow_html=True)
            st.metric(
                "💰 Validação V. Líquido", 
                f"€ {total_vendas_atual:,.2f}",
                delta=f"€ {diferenca_vendas:+.2f} ({percentual_vendas:+.2f}%)",
                help=f"Referência: € {TOTAL_V_LIQUIDO_REFERENCIA:,.2f}"
            )
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
                st.plotly_chart(fig, width='stretch')
    
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
                st.plotly_chart(fig, width='stretch')
    
    # DADOS FILTRADOS
    st.markdown("<div class='section-header'>📋 Dados Filtrados</div>", unsafe_allow_html=True)
    
    # Converter colunas para evitar erro de serialização
    df_display = df_filtrado.copy()
    for col in df_display.columns:
        if df_display[col].dtype == 'object':
            df_display[col] = df_display[col].astype(str)
    
    st.dataframe(df_display, width='stretch')

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #7f8c8d;'>", unsafe_allow_html=True)
st.markdown(f"📊 Dashboard • {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown("</div>", unsafe_allow_html=True)
