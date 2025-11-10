import streamlit as st
import pandas as pd
import json
from pathlib import Path
import numpy as np
import plotly.express as px
from datetime import datetime
from io import BytesIO
import re

# -------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Vendas - BI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# CSS + LOGO
# -------------------------------------------------
st.markdown("""
<style>
    .main-header {font-size:2.5rem;color:#1f77b4;text-align:center;margin-bottom:2rem;font-weight:700;}
    .metric-card {background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:1.5rem;border-radius:15px;color:white;box-shadow:0 4px 6px rgba(0,0,0,0.1);}
    .section-header {font-size:1.5rem;color:#2c3e50;margin:2rem 0 1rem 0;padding-bottom:0.5rem;border-bottom:3px solid #3498db;font-weight:600;}
    .alerta-critico {color: #8B0000; font-weight: bold; background-color: #ffe6e6; padding: 2px 6px; border-radius: 4px;}
    .alerta-alto {color: #d32f2f; font-weight: bold;}
    .alerta-moderado {color: #f57c00; font-weight: bold;}
    .alerta-positivo {color: #2e7d32; font-weight: bold; background-color: #e8f5e8; padding: 2px 6px; border-radius: 4px;}
    .alerta-negativo {color: #8B0000; font-weight: bold; background-color: #ffe6e6; padding: 2px 6px; border-radius: 4px;}
    .logo-container {
        position: fixed;
        top: 10px;
        left: 10px;
        z-index: 1000;
        background: white;
        padding: 5px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .logo-container img {
        height: 70px;
        width: auto;
    }
    .nav-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .nav-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# LOGO
st.markdown(f"""
<div class="logo-container">
    <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" alt="Bracar Logo">
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# FUNÇÕES GLOBAIS
# -------------------------------------------------
def formatar_numero_pt(valor, simbolo="", sinal_forcado=False):
    if pd.isna(valor):
        return "N/D"
    try:
        valor = float(valor)
        sinal = "+" if sinal_forcado and valor >= 0 else ("-" if valor < 0 else "")
        valor_abs = abs(valor)
        if valor_abs == int(valor_abs):
            return f"{sinal}{simbolo}{valor_abs:,.0f}".replace(",", " ")
        else:
            return f"{sinal}{simbolo}{valor_abs:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "N/D"

def to_excel(df, sheet_name="Dados"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

@st.cache_data
def load_all_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/VendasGeraisTranf.xlsx"
        df = pd.read_excel(url, thousands=None, decimal=',')
        
        # Mapeamento de colunas
        mapeamento_possivel = {
            'Código': 'Codigo', 
            'Cliente': 'Cliente', 
            'Qtd.': 'Qtd', 
            'Qtd': 'Qtd',
            'UN': 'UN',
            'PM': 'PM', 
            'V. Líquido': 'V_Liquido', 
            'V Líquido': 'V_Liquido',
            'Artigo': 'Artigo',
            'Comercial': 'Comercial', 
            'Categoria': 'Categoria',
            'Mês': 'Mes', 
            'Mes': 'Mes',
            'Ano': 'Ano'
        }
        
        mapeamento = {}
        for col_orig, col_novo in mapeamento_possivel.items():
            if col_orig in df.columns:
                mapeamento[col_orig] = col_novo
        
        df = df.rename(columns=mapeamento)
        
        # Processar colunas
        colunas_string = ['UN', 'Artigo', 'Cliente', 'Comercial', 'Categoria', 'Mes', 'Ano']
        for col in colunas_string:
            if col in df.columns:
                df[col] = df[col].astype(str).replace({'nan': 'N/D', 'None': 'N/D'})
        
        for col in ['V_Liquido', 'Qtd', 'PM']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# -------------------------------------------------
# SIDEBAR (COMUM PARA TODAS AS PÁGINAS)
# -------------------------------------------------
with st.sidebar:
    st.markdown("<div class='metric-card'>Painel de Controle</div>", unsafe_allow_html=True)
    
    # Presets
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
    
    presets = carregar_presets()
    preset_selecionado = st.selectbox("Configuração", [""] + list(presets.keys()))
    filtros = presets.get(preset_selecionado, {}) if preset_selecionado else {}

    st.markdown("---")
    st.markdown("### Filtros")
    
    df = load_all_data()
    
    def criar_filtro(label, coluna, default=None):
        if coluna not in df.columns or df.empty: 
            return []
        opcoes = sorted(df[coluna].dropna().astype(str).unique())
        return st.multiselect(label, opcoes, default=default or [])
    
    # Criar filtros apenas para colunas que existem
    clientes = criar_filtro("Clientes", "Cliente", filtros.get("Cliente"))
    
    if 'Artigo' in df.columns:
        artigos = criar_filtro("Artigos", "Artigo", filtros.get("Artigo"))
    else:
        artigos = []
    
    if 'Comercial' in df.columns:
        comerciais = criar_filtro("Comerciais", "Comercial", filtros.get("Comercial"))
    else:
        comerciais = []
    
    if 'Categoria' in df.columns:
        categorias = criar_filtro("Categorias", "Categoria", filtros.get("Categoria"))
    else:
        categorias = []
    
    if 'Mes' in df.columns:
        meses = criar_filtro("Meses", "Mes", filtros.get("Mes"))
    else:
        meses = []
    
    if 'Ano' in df.columns:
        anos = criar_filtro("Anos", "Ano", filtros.get("Ano"))
    else:
        anos = []

    st.markdown("---")
    nome_preset = st.text_input("Nome da configuração")
    if st.button("Salvar Configuração") and nome_preset:
        salvar_preset(nome_preset, {"Cliente": clientes, "Artigo": artigos, "Comercial": comerciais,
                                   "Categoria": categorias, "Mes": meses, "Ano": anos})
        st.success(f"Salvo: {nome_preset}")

# Aplicar filtros
df_filtrado = df.copy()
if clientes: df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes)]
if artigos: df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(artigos)]
if comerciais: df_filtrado = df_filtrado[df_filtrado['Comercial'].isin(comerciais)]
if categorias: df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias)]
if meses: df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses)]
if anos: df_filtrado = df_filtrado[df_filtrado['Ano'].isin(anos)]

# Salvar dados filtrados na sessão para outras páginas
st.session_state.df_filtrado = df_filtrado
st.session_state.df_original = df

# -------------------------------------------------
# PÁGINA PRINCIPAL
# -------------------------------------------------
st.markdown("<h1 class='main-header'>Dashboard de Vendas - BI Completo</h1>", unsafe_allow_html=True)

if df.empty:
    st.error("Erro ao carregar dados.")
elif df_filtrado.empty:
    st.warning("Nenhum dado com os filtros aplicados.")
else:
    st.success(f"**{len(df_filtrado):,}** registos carregados com sucesso")

    # -------------------------------------------------
    # MÉTRICAS RÁPIDAS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>📈 Métricas Principais</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if 'V_Liquido' in df_filtrado.columns:
            st.metric("Vendas Totais", formatar_numero_pt(df_filtrado['V_Liquido'].sum(), "EUR "))
        else:
            st.metric("Vendas Totais", "N/D")
    
    with col2:
        st.metric("Quantidade Total", formatar_numero_pt(df_filtrado['Qtd'].sum()))
    
    with col3:
        st.metric("Total Clientes", f"{df_filtrado['Cliente'].nunique():,}")
    
    with col4:
        if 'Artigo' in df_filtrado.columns:
            st.metric("Total Artigos", f"{df_filtrado['Artigo'].nunique():,}")
        else:
            st.metric("Total Artigos", "N/D")
    
    with col5:
        if 'Comercial' in df_filtrado.columns:
            st.metric("Comerciais", f"{df_filtrado['Comercial'].nunique():,}")
        else:
            st.metric("Comerciais", "N/D")

    # -------------------------------------------------
    # NAVEGAÇÃO ENTRE PÁGINAS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>🚀 Navegação Rápida</div>", unsafe_allow_html=True)
    
    col_nav1, col_nav2 = st.columns(2)
    
    with col_nav1:
        st.markdown("""
        <div class='nav-card'>
            <h3>🚨 Alertas de Compras</h3>
            <p>• Subidas e descidas significativas<br>
            • Clientes que pararam de comprar<br>
            • Análise de tendências por cliente</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Alertas", key="alertas", use_container_width=True):
            st.switch_page("pages/1_🚨_Alertas_Compras.py")
        
        st.markdown("""
        <div class='nav-card'>
            <h3>📊 Tabela Geral</h3>
            <p>• Visão mensal completa<br>
            • Alertas integrados na tabela<br>
            • Filtros avançados</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Tabela", key="tabela", use_container_width=True):
            st.switch_page("pages/2_📊_Tabela_Geral_Clientes.py")
    
    with col_nav2:
        st.markdown("""
        <div class='nav-card'>
            <h3>📈 Comparações Mensais</h3>
            <p>• Mês a mês<br>
            • Entre anos diferentes<br>
            • Análise temporal detalhada</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Comparações", key="comparacoes", use_container_width=True):
            st.switch_page("pages/3_📈_Comparacoes_Mensais.py")
        
        st.markdown("""
        <div class='nav-card'>
            <h3>🔍 Análise Detalhada</h3>
            <p>• Dados completos filtrados<br>
            • Exportação para Excel<br>
            • Análise granular</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Análise", key="analise", use_container_width=True):
            st.switch_page("pages/4_🔍_Analise_Detalhada.py")

    # -------------------------------------------------
    # VISUALIZAÇÕES RÁPIDAS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>📊 Visualizações Rápidas</div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Top Clientes", "Top Artigos"])
    
    with tab1:
        if 'V_Liquido' in df_filtrado.columns:
            top_clientes = df_filtrado.groupby('Cliente')['V_Liquido'].sum().nlargest(10)
            if not top_clientes.empty:
                fig_clientes = px.bar(
                    top_clientes.reset_index(), 
                    x='V_Liquido', 
                    y='Cliente', 
                    orientation='h',
                    title="Top 10 Clientes por Vendas",
                    labels={'V_Liquido': 'Vendas (EUR)', 'Cliente': ''}
                )
                st.plotly_chart(fig_clientes, use_container_width=True)
    
    with tab2:
        if 'V_Liquido' in df_filtrado.columns and 'Artigo' in df_filtrado.columns:
            top_artigos = df_filtrado.groupby('Artigo')['V_Liquido'].sum().nlargest(10)
            if not top_artigos.empty:
                fig_artigos = px.bar(
                    top_artigos.reset_index(), 
                    x='V_Liquido', 
                    y='Artigo', 
                    orientation='h',
                    title="Top 10 Artigos por Vendas",
                    labels={'V_Liquido': 'Vendas (EUR)', 'Artigo': ''}
                )
                st.plotly_chart(fig_artigos, use_container_width=True)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#7f8c8d;'>Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)
