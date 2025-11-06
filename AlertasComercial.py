import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

# 🔄 Carregamento e renomeação
@st.cache_data
def load_data():
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
    
    # Converter colunas numéricas para o tipo correto
    if 'V_Liquido' in df.columns:
        df['V_Liquido'] = pd.to_numeric(df['V_Liquido'], errors='coerce')
    if 'Qtd' in df.columns:
        df['Qtd'] = pd.to_numeric(df['Qtd'], errors='coerce')
    
    return df

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

# 🎛️ Filtros interativos
st.sidebar.header("🎛️ Filtros Dinâmicos")
presets = carregar_presets()
preset_selecionado = st.sidebar.selectbox("📂 Carregar Preset", [""] + list(presets.keys()))

# Inicializa filtros vazios se nenhum preset for selecionado
filtros = presets.get(preset_selecionado, {}) if preset_selecionado else {}

def filtro_multiselect(label, coluna, valores=None):
    if coluna not in df.columns:
        st.warning(f"⚠️ Coluna '{coluna}' não encontrada.")
        return []
    
    # Verifica se valores é None ou vazio antes de usar
    valores_default = valores if valores else []
    
    # Converte todos os valores para string antes de ordenar para evitar erro de tipos mistos
    opcoes = sorted(df[coluna].dropna().astype(str).unique())
    return st.sidebar.multiselect(label, opcoes, default=valores_default)

# Aplica os filtros com verificação de segurança
clientes = filtro_multiselect("Cliente", "Cliente", filtros.get("Cliente"))
artigos = filtro_multiselect("Artigo", "Artigo", filtros.get("Artigo"))
comerciais = filtro_multiselect("Comercial", "Comercial", filtros.get("Comercial"))
categorias = filtro_multiselect("Categoria", "Categoria", filtros.get("Categoria"))
meses = filtro_multiselect("Mês", "Mes", filtros.get("Mes"))
anos = filtro_multiselect("Ano", "Ano", filtros.get("Ano"))

# 🔍 Aplica filtros ao dataframe
df_filtrado = df.copy()
filtros_aplicados = []

# Para aplicar os filtros, precisamos garantir que os tipos correspondam
if clientes: 
    # Converte clientes selecionados para o tipo original dos dados
    clientes_orig = df["Cliente"].astype(str).isin(clientes)
    df_filtrado = df_filtrado[clientes_orig]
    filtros_aplicados.append(f"Clientes: {len(clientes)}")
if artigos: 
    artigos_orig = df["Artigo"].astype(str).isin(artigos)
    df_filtrado = df_filtrado[artigos_orig]
    filtros_aplicados.append(f"Artigos: {len(artigos)}")
if comerciais: 
    comerciais_orig = df["Comercial"].astype(str).isin(comerciais)
    df_filtrado = df_filtrado[comerciais_orig]
    filtros_aplicados.append(f"Comerciais: {len(comerciais)}")
if categorias: 
    categorias_orig = df["Categoria"].astype(str).isin(categorias)
    df_filtrado = df_filtrado[categorias_orig]
    filtros_aplicados.append(f"Categorias: {len(categorias)}")
if meses: 
    meses_orig = df["Mes"].astype(str).isin(meses)
    df_filtrado = df_filtrado[meses_orig]
    filtros_aplicados.append(f"Meses: {len(meses)}")
if anos: 
    anos_orig = df["Ano"].astype(str).isin(anos)
    df_filtrado = df_filtrado[anos_orig]
    filtros_aplicados.append(f"Anos: {len(anos)}")

# 💾 Salvar novo preset
st.sidebar.markdown("---")
st.sidebar.markdown("💾 **Salvar Preset Atual**")
nome_preset = st.sidebar.text_input("Nome do preset")

if st.sidebar.button("Salvar preset") and nome_preset:
    filtros_atuais = {
        "Cliente": clientes,
        "Artigo": artigos,
        "Comercial": comerciais,
        "Categoria": categorias,
        "Mes": meses,
        "Ano": anos
    }
    salvar_preset(nome_preset, filtros_atuais)
    st.sidebar.success(f"Preset '{nome_preset}' salvo com sucesso!")

# 🧪 Diagnóstico lateral
st.sidebar.markdown("---")
st.sidebar.markdown("📊 **Diagnóstico de Filtros**")
st.sidebar.write("**Filtros Aplicados:**")
if filtros_aplicados:
    for filtro in filtros_aplicados:
        st.sidebar.write(f"- {filtro}")
else:
    st.sidebar.write("Nenhum filtro aplicado")

# ✅ Validação e exibição dos dados
st.title("📊 Dashboard de Vendas")

if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    st.info("💡 Tente ajustar os filtros para ver os dados.")
else:
    st.success(f"✅ {len(df_filtrado)} registros encontrados após filtro.")
    
    # Métricas principais com tratamento de erro
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            total_vendas = df_filtrado['V_Liquido'].sum()
            st.metric("Total de Vendas", f"€ {total_vendas:,.2f}")
        except (TypeError, ValueError):
            st.metric("Total de Vendas", "Erro no cálculo")
    
    with col2:
        try:
            total_qtd = df_filtrado['Qtd'].sum()
            st.metric("Quantidade Total", f"{total_qtd:,.2f}")
        except (TypeError, ValueError):
            st.metric("Quantidade Total", "Erro no cálculo")
    
    with col3:
        try:
            clientes_unicos = df_filtrado['Cliente'].nunique()
            st.metric("Clientes Únicos", clientes_unicos)
        except (TypeError, ValueError):
            st.metric("Clientes Únicos", "Erro no cálculo")
    
    with col4:
        try:
            artigos_unicos = df_filtrado['Artigo'].nunique()
            st.metric("Artigos Únicos", artigos_unicos)
        except (TypeError, ValueError):
            st.metric("Artigos Únicos", "Erro no cálculo")
    
    # Informações sobre dados inválidos
    if 'V_Liquido' in df_filtrado.columns:
        valores_invalidos = df_filtrado['V_Liquido'].isna().sum()
        if valores_invalidos > 0:
            st.info(f"💡 {valores_invalidos} registros com valores inválidos na coluna 'V_Liquido' foram ignorados.")
    
    if 'Qtd' in df_filtrado.columns:
        valores_invalidos_qtd = df_filtrado['Qtd'].isna().sum()
        if valores_invalidos_qtd > 0:
            st.info(f"💡 {valores_invalidos_qtd} registros com valores inválidos na coluna 'Qtd' foram ignorados.")
    
    # 📈 KPIS DINÂMICOS POR CLIENTE
    st.markdown("---")
    st.subheader("📈 KPIs por Cliente")
    
    # Selecionar cliente para análise detalhada
    clientes_disponiveis = sorted(df_filtrado['Cliente'].dropna().astype(str).unique())
    if clientes_disponiveis:
        cliente_selecionado = st.selectbox("🔍 Selecionar Cliente para Análise Detalhada", clientes_disponiveis)
        
        if cliente_selecionado:
            # Filtrar dados do cliente selecionado
            dados_cliente = df_filtrado[df_filtrado['Cliente'].astype(str) == cliente_selecionado]
            
            if not dados_cliente.empty:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    try:
                        vendas_cliente = dados_cliente['V_Liquido'].sum()
                        st.metric(f"Total Vendas - {cliente_selecionado}", f"€ {vendas_cliente:,.2f}")
                    except:
                        st.metric(f"Total Vendas - {cliente_selecionado}", "Erro")
                
                with col2:
                    try:
                        qtd_cliente = dados_cliente['Qtd'].sum()
                        st.metric(f"Quantidade Total - {cliente_selecionado}", f"{qtd_cliente:,.2f}")
                    except:
                        st.metric(f"Quantidade Total - {cliente_selecionado}", "Erro")
                
                with col3:
                    try:
                        artigos_cliente = dados_cliente['Artigo'].nunique()
                        st.metric(f"Artigos Únicos - {cliente_selecionado}", artigos_cliente)
                    except:
                        st.metric(f"Artigos Únicos - {cliente_selecionado}", "Erro")
                
                with col4:
                    try:
                        ticket_medio = vendas_cliente / qtd_cliente if qtd_cliente > 0 else 0
                        st.metric(f"Ticket Médio - {cliente_selecionado}", f"€ {ticket_medio:,.2f}")
                    except:
                        st.metric(f"Ticket Médio - {cliente_selecionado}", "Erro")
                
                # Top produtos do cliente
                st.subheader(f"🛍️ Top Produtos - {cliente_selecionado}")
                top_produtos = dados_cliente.groupby('Artigo').agg({
                    'V_Liquido': 'sum',
                    'Qtd': 'sum'
                }).sort_values('V_Liquido', ascending=False).head(10)
                
                if not top_produtos.empty:
                    st.dataframe(top_produtos.style.format({
                        'V_Liquido': '€ {:,.2f}',
                        'Qtd': '{:,.2f}'
                    }))
    
    # 📊 KPIS DINÂMICOS POR COMERCIAL
    st.markdown("---")
    st.subheader("📊 KPIs por Comercial")
    
    # Selecionar comercial para análise detalhada
    comerciais_disponiveis = sorted(df_filtrado['Comercial'].dropna().astype(str).unique())
    if comerciais_disponiveis:
        comercial_selecionado = st.selectbox("👨‍💼 Selecionar Comercial para Análise Detalhada", comerciais_disponiveis)
        
        if comercial_selecionado:
            # Filtrar dados do comercial selecionado
            dados_comercial = df_filtrado[df_filtrado['Comercial'].astype(str) == comercial_selecionado]
            
            if not dados_comercial.empty:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    try:
                        vendas_comercial = dados_comercial['V_Liquido'].sum()
                        st.metric(f"Total Vendas - {comercial_selecionado}", f"€ {vendas_comercial:,.2f}")
                    except:
                        st.metric(f"Total Vendas - {comercial_selecionado}", "Erro")
                
                with col2:
                    try:
                        qtd_comercial = dados_comercial['Qtd'].sum()
                        st.metric(f"Quantidade Total - {comercial_selecionado}", f"{qtd_comercial:,.2f}")
                    except:
                        st.metric(f"Quantidade Total - {comercial_selecionado}", "Erro")
                
                with col3:
                    try:
                        clientes_comercial = dados_comercial['Cliente'].nunique()
                        st.metric(f"Clientes Únicos - {comercial_selecionado}", clientes_comercial)
                    except:
                        st.metric(f"Clientes Únicos - {comercial_selecionado}", "Erro")
                
                with col4:
                    try:
                        ticket_medio_comercial = vendas_comercial / qtd_comercial if qtd_comercial > 0 else 0
                        st.metric(f"Ticket Médio - {comercial_selecionado}", f"€ {ticket_medio_comercial:,.2f}")
                    except:
                        st.metric(f"Ticket Médio - {comercial_selecionado}", "Erro")
                
                # Top clientes do comercial
                st.subheader(f"🏆 Top Clientes - {comercial_selecionado}")
                top_clientes = dados_comercial.groupby('Cliente').agg({
                    'V_Liquido': 'sum',
                    'Qtd': 'sum',
                    'Artigo': 'nunique'
                }).rename(columns={'Artigo': 'Artigos Únicos'}).sort_values('V_Liquido', ascending=False).head(10)
                
                if not top_clientes.empty:
                    st.dataframe(top_clientes.style.format({
                        'V_Liquido': '€ {:,.2f}',
                        'Qtd': '{:,.2f}'
                    }))
    
    # 📋 VISÃO GERAL COMPARATIVA
    st.markdown("---")
    st.subheader("📋 Visão Geral Comparativa")
    
    tab1, tab2 = st.tabs(["🏢 Ranking de Clientes", "👨‍💼 Ranking de Comerciais"])
    
    with tab1:
        # Ranking de clientes
        ranking_clientes = df_filtrado.groupby('Cliente').agg({
            'V_Liquido': 'sum',
            'Qtd': 'sum',
            'Artigo': 'nunique',
            'Comercial': 'nunique'
        }).rename(columns={
            'Artigo': 'Artigos Únicos',
            'Comercial': 'Comerciais'
        }).sort_values('V_Liquido', ascending=False).head(15)
        
        if not ranking_clientes.empty:
            st.dataframe(ranking_clientes.style.format({
                'V_Liquido': '€ {:,.2f}',
                'Qtd': '{:,.2f}'
            }))
    
    with tab2:
        # Ranking de comerciais
        ranking_comerciais = df_filtrado.groupby('Comercial').agg({
            'V_Liquido': 'sum',
            'Qtd': 'sum',
            'Cliente': 'nunique',
            'Artigo': 'nunique'
        }).rename(columns={
            'Cliente': 'Clientes Únicos',
            'Artigo': 'Artigos Únicos'
        }).sort_values('V_Liquido', ascending=False).head(15)
        
        if not ranking_comerciais.empty:
            st.dataframe(ranking_comerciais.style.format({
                'V_Liquido': '€ {:,.2f}',
                'Qtd': '{:,.2f}'
            }))
    
    st.subheader("📋 Dados Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)
