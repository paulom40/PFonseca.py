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
        
        # Converter colunas numéricas
        if 'V_Liquido' in df.columns:
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

# 🔍 Aplicar filtros
df_filtrado = df.copy()
filtros_aplicados = []

if clientes or artigos or comerciais or categorias or meses or anos:
    mascara = pd.Series([True] * len(df_filtrado), index=df_filtrado.index)
    
    if clientes:
        mascara_cliente = df_filtrado["Cliente"].astype(str).isin(clientes)
        mascara = mascara & mascara_cliente
        filtros_aplicados.append(f"👥 Clientes: {len(clientes)}")
    
    if artigos:
        mascara_artigo = df_filtrado["Artigo"].astype(str).isin(artigos)
        mascara = mascara & mascara_artigo
        filtros_aplicados.append(f"📦 Artigos: {len(artigos)}")
    
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

# 🎯 Header principal
st.markdown("<h1 class='main-header'>📊 Business Intelligence - Dashboard de Vendas</h1>", unsafe_allow_html=True)

if df_filtrado.empty:
    st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
    st.markdown("### ⚠️ Nenhum dado encontrado com os filtros selecionados")
    st.markdown("**Sugestões:**")
    st.markdown("- Verifique se os filtros não estão conflitando")
    st.markdown("- Tente aplicar menos filtros de cada vez")
    st.markdown("- Verifique se os valores existem nos dados")
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # ✅ Indicadores de sucesso
    st.markdown("<div class='success-box'>", unsafe_allow_html=True)
    st.markdown(f"### ✅ **{len(df_filtrado):,}** registros encontrados após filtro")
    if filtros_aplicados:
        st.markdown("**Filtros aplicados:** " + " | ".join(filtros_aplicados))
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
            total_vendas = df_filtrado['V_Liquido'].sum()
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("💰 Total de Vendas", f"€ {total_vendas:,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            total_qtd = df_filtrado['Qtd'].sum()
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("📦 Quantidade Total", f"{total_qtd:,.0f}")
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
            # Top 10 comerciais
            top_comerciais = df_filtrado.groupby('Comercial')['V_Liquido'].sum().nlargest(10)
            if not top_comerciais.empty:
                fig = px.pie(
                    top_comerciais,
                    values=top_comerciais.values,
                    names=top_comerciais.index,
                    title='👨‍💼 Distribuição por Comercial',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 📋 Dados detalhados
        st.markdown("<div class='section-header'>📋 Dados Filtrados</div>", unsafe_allow_html=True)
        st.dataframe(df_filtrado, width='stretch')
    
    with tab2:
        st.markdown("<div class='section-header'>👥 Análise Detalhada por Cliente</div>", unsafe_allow_html=True)
        
        clientes_disponiveis = sorted(df_filtrado['Cliente'].dropna().astype(str).unique())
        if clientes_disponiveis:
            cliente_selecionado = st.selectbox("🔍 Selecionar Cliente", clientes_disponiveis)
            
            if cliente_selecionado:
                dados_cliente = df_filtrado[df_filtrado['Cliente'].astype(str) == cliente_selecionado]
                
                if not dados_cliente.empty:
                    # Métricas do cliente
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        vendas_cliente = dados_cliente['V_Liquido'].sum()
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.metric(f"💰 Vendas Totais", f"€ {vendas_cliente:,.2f}")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        qtd_cliente = dados_cliente['Qtd'].sum()
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.metric(f"📦 Quantidade", f"{qtd_cliente:,.0f}")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col3:
                        artigos_cliente = dados_cliente['Artigo'].nunique()
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.metric(f"🏷️ Artigos", f"{artigos_cliente:,}")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col4:
                        ticket_medio = vendas_cliente / qtd_cliente if qtd_cliente > 0 else 0
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.metric(f"🎫 Ticket Médio", f"€ {ticket_medio:,.2f}")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Análise temporal
                    st.markdown("#### 📈 Evolução Temporal")
                    vendas_mensais = dados_cliente.groupby(['Ano', 'Mes'])['V_Liquido'].sum().reset_index()
                    if not vendas_mensais.empty:
                        vendas_mensais['Mes_Ano'] = vendas_mensais['Mes'].astype(str) + '-' + vendas_mensais['Ano'].astype(str)
                        fig = px.line(
                            vendas_mensais, 
                            x='Mes_Ano', 
                            y='V_Liquido',
                            title=f'Evolução de Vendas - {cliente_selecionado}',
                            markers=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Top produtos
                    st.markdown("#### 🏆 Top Produtos")
                    top_produtos = dados_cliente.groupby('Artigo').agg({
                        'V_Liquido': 'sum',
                        'Qtd': 'sum'
                    }).sort_values('V_Liquido', ascending=False).head(10)
                    
                    if not top_produtos.empty:
                        st.dataframe(
                            top_produtos.style.format({
                                'V_Liquido': '€ {:,.2f}',
                                'Qtd': '{:,.0f}'
                            }), 
                            width='stretch'
                        )
    
    with tab3:
        st.markdown("<div class='section-header'>👨‍💼 Análise por Comercial</div>", unsafe_allow_html=True)
        
        comerciais_disponiveis = sorted(df_filtrado['Comercial'].dropna().astype(str).unique())
        if comerciais_disponiveis:
            comercial_selecionado = st.selectbox("🔍 Selecionar Comercial", comerciais_disponiveis)
            
            if comercial_selecionado:
                dados_comercial = df_filtrado[df_filtrado['Comercial'].astype(str) == comercial_selecionado]
                
                if not dados_comercial.empty:
                    # Métricas do comercial
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        vendas_comercial = dados_comercial['V_Liquido'].sum()
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.metric(f"💰 Vendas Totais", f"€ {vendas_comercial:,.2f}")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        qtd_comercial = dados_comercial['Qtd'].sum()
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.metric(f"📦 Quantidade", f"{qtd_comercial:,.0f}")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col3:
                        clientes_comercial = dados_comercial['Cliente'].nunique()
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.metric(f"👥 Clientes", f"{clientes_comercial:,}")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col4:
                        ticket_medio_comercial = vendas_comercial / qtd_comercial if qtd_comercial > 0 else 0
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.metric(f"🎫 Ticket Médio", f"€ {ticket_medio_comercial:,.2f}")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Top clientes do comercial
                    st.markdown("#### 🏆 Top Clientes")
                    top_clientes_comercial = dados_comercial.groupby('Cliente').agg({
                        'V_Liquido': 'sum',
                        'Qtd': 'sum',
                        'Artigo': 'nunique'
                    }).rename(columns={'Artigo': 'Artigos Únicos'}).sort_values('V_Liquido', ascending=False).head(10)
                    
                    if not top_clientes_comercial.empty:
                        st.dataframe(
                            top_clientes_comercial.style.format({
                                'V_Liquido': '€ {:,.2f}',
                                'Qtd': '{:,.0f}'
                            }), 
                            width='stretch'
                        )
    
    with tab4:
        st.markdown("<div class='section-header'>🚨 Alertas & Insights</div>", unsafe_allow_html=True)
        
        # Análise de performance mensal
        if not df_filtrado.empty and 'Mes' in df_filtrado.columns and 'Ano' in df_filtrado.columns:
            df_filtrado['Mes_Ano'] = df_filtrado['Mes'].astype(str) + '-' + df_filtrado['Ano'].astype(str)
            
            # Mapeamento de meses para ordenação
            meses_map = {
                'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
                'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
                'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
                'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
            }
            
            def ordenar_mes_ano(mes_ano):
                try:
                    mes_str, ano = mes_ano.split('-')
                    try:
                        mes_num = int(mes_str)
                    except ValueError:
                        mes_num = meses_map.get(mes_str.lower(), 13)
                    return (int(ano), mes_num)
                except:
                    return (9999, 13)
            
            meses_ordenados = sorted(df_filtrado['Mes_Ano'].unique(), key=ordenar_mes_ano)
            
            if len(meses_ordenados) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    opcoes_mes_anterior = meses_ordenados[:-1]
                    mes_anterior = st.selectbox("📅 Mês Anterior", opcoes_mes_anterior, 
                                              index=len(opcoes_mes_anterior)-1 if opcoes_mes_anterior else 0)
                with col2:
                    opcoes_mes_atual = meses_ordenados[1:]
                    mes_atual = st.selectbox("📊 Mês Atual", opcoes_mes_atual,
                                           index=len(opcoes_mes_atual)-1 if opcoes_mes_atual else 0)
                
                # Cálculo de comparação
                dados_mes_anterior = df_filtrado[df_filtrado['Mes_Ano'] == mes_anterior].groupby('Cliente')['Qtd'].sum().reset_index()
                dados_mes_atual = df_filtrado[df_filtrado['Mes_Ano'] == mes_atual].groupby('Cliente')['Qtd'].sum().reset_index()
                
                comparacao = pd.merge(dados_mes_anterior, dados_mes_atual, on='Cliente', 
                                    how='outer', suffixes=('_anterior', '_atual'))
                comparacao = comparacao.fillna(0)
                
                comparacao['Variacao'] = comparacao['Qtd_atual'] - comparacao['Qtd_anterior']
                comparacao['Variacao_Percentual'] = np.where(
                    comparacao['Qtd_anterior'] > 0,
                    (comparacao['Variacao'] / comparacao['Qtd_anterior']) * 100,
                    np.where(comparacao['Qtd_atual'] > 0, 100, 0)
                )
                
                def classificar_variacao(row):
                    if row['Qtd_anterior'] == 0 and row['Qtd_atual'] == 0:
                        return "Sem Compras"
                    elif row['Qtd_anterior'] == 0 and row['Qtd_atual'] > 0:
                        return "Novo Cliente"
                    elif row['Qtd_anterior'] > 0 and row['Qtd_atual'] == 0:
                        return "Parou de Comprar"
                    elif row['Variacao'] > 0:
                        return "Subiu"
                    elif row['Variacao'] < 0:
                        return "Desceu"
                    else:
                        return "Estável"
                
                comparacao['Status'] = comparacao.apply(classificar_variacao, axis=1)
                
                # Alertas visuais
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    subiram = len(comparacao[comparacao['Status'] == 'Subiram'])
                    st.markdown(f"<div class='success-box' style='text-align: center; padding: 1rem;'>", unsafe_allow_html=True)
                    st.markdown(f"### 📈 {subiram}")
                    st.markdown("Clientes em Crescimento")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    desceram = len(comparacao[comparacao['Status'] == 'Desceu'])
                    st.markdown(f"<div class='warning-box' style='text-align: center; padding: 1rem;'>", unsafe_allow_html=True)
                    st.markdown(f"### 📉 {desceram}")
                    st.markdown("Clientes em Queda")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col3:
                    novos = len(comparacao[comparacao['Status'] == 'Novo Cliente'])
                    st.markdown(f"<div class='info-box' style='text-align: center; padding: 1rem;'>", unsafe_allow_html=True)
                    st.markdown(f"### 🆕 {novos}")
                    st.markdown("Novos Clientes")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col4:
                    pararam = len(comparacao[comparacao['Status'] == 'Parou de Comprar'])
                    st.markdown(f"<div class='warning-box' style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #636e72 0%, #2d3436 100%);'>", unsafe_allow_html=True)
                    st.markdown(f"### ⚫ {pararam}")
                    st.markdown("Clientes Inativos")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Tabela detalhada
                st.markdown("#### 📋 Detalhamento por Cliente")
                comparacao_display = comparacao[['Cliente', 'Qtd_anterior', 'Qtd_atual', 'Variacao', 'Variacao_Percentual', 'Status']]
                comparacao_display = comparacao_display.rename(columns={
                    'Qtd_anterior': f'Qtd {mes_anterior}',
                    'Qtd_atual': f'Qtd {mes_atual}',
                    'Variacao': 'Variação',
                    'Variacao_Percentual': 'Variação %'
                })
                
                st.dataframe(comparacao_display.style.format({
                    f'Qtd {mes_anterior}': '{:,.0f}',
                    f'Qtd {mes_atual}': '{:,.0f}',
                    'Variação': '{:,.0f}',
                    'Variação %': '{:.1f}%'
                }), width='stretch')

# 🎯 Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #7f8c8d;'>", unsafe_allow_html=True)
st.markdown("📊 **Business Intelligence Dashboard** • Desenvolvido com Streamlit • ")
st.markdown(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown("</div>", unsafe_allow_html=True)
