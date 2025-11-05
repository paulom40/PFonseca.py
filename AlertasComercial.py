# dashboard_pro.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import requests
import warnings
warnings.filterwarnings("ignore")

# =============================================
# CONFIG & ESTILO
# =============================================
st.set_page_config(page_title="BI Pro", layout="wide", page_icon="📊")
st.markdown("""
<style>
    .main {background:#f8fafc; padding:2rem}
    h1 {color:#1e293b; font-size:2.6rem; font-weight:800; text-align:center}
    [data-testid="stSidebar"] {background:linear-gradient(#4f46e5,#7c3aed); border-radius:0 20px 20px 0; padding:2rem}
    .stSelectbox > div > div {background:white !important; border:2px solid #e2e8f0 !important; border-radius:12px !important}
    .stSelectbox span, .stSelectbox input {color:#1e293b !important}
    [data-testid="metric-container"] {background:white; border-radius:16px; padding:1.5rem; box-shadow:0 6px 25px rgba(0,0,0,0.1)}
    .plotly-graph-div {border-radius:18px; overflow:hidden; box-shadow:0 8px 30px rgba(0,0,0,0.12)}
    .filter-section {background:white; padding:1rem; border-radius:12px; margin-bottom:1rem; border:1px solid #e2e8f0}
</style>
""", unsafe_allow_html=True)

# =============================================
# CARREGAMENTO SIMPLIFICADO E CORRIGIDO
# =============================================
month_map = {'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,
             'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}

@st.cache_data(ttl=3600)
def load_data():
    try:
        # URL direta do arquivo Excel
        url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx"
        
        # Fazer download do arquivo
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Carregar o Excel
        df = pd.read_excel(BytesIO(response.content))
        
        st.info(f"📥 Dados carregados: {len(df)} registros")
        
        # === PADRONIZAR NOMES DAS COLUNAS ===
        df.columns = [col.strip().lower() for col in df.columns]
        
        # Mapear nomes de colunas para padrão
        column_mapping = {
            'mês': 'mes',
            'qtd.': 'qtd', 
            'v. líquido': 'v_liquido',
            'v.líquido': 'v_liquido',
            'v_líquido': 'v_liquido'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # === CONVERSÃO DE TIPOS DE DADOS ===
        
        # 1. Converter Mês - tratar como texto primeiro
        if 'mes' in df.columns:
            df['mes'] = df['mes'].astype(str).str.strip().str.lower()
            df['mes_num'] = df['mes'].map(month_map)
            # Manter o mês original também
            df['mes_nome'] = df['mes']
        
        # 2. Converter Ano
        if 'ano' in df.columns:
            df['ano'] = pd.to_numeric(df['ano'], errors='coerce').fillna(2024).astype(int)
        
        # 3. Converter Quantidade
        if 'qtd' in df.columns:
            df['qtd'] = df['qtd'].astype(str)
            df['qtd'] = df['qtd'].str.replace(r'[^\d,\.\-]', '', regex=True)
            df['qtd'] = df['qtd'].str.replace(',', '.', regex=False)
            df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')
            df['qtd'] = df['qtd'].fillna(0)
        
        # 4. Converter Valor Líquido
        if 'v_liquido' in df.columns:
            df['v_liquido'] = df['v_liquido'].astype(str)
            df['v_liquido'] = df['v_liquido'].str.replace(r'[^\d,\.\-]', '', regex=True)
            df['v_liquido'] = df['v_liquido'].str.replace(',', '.', regex=False)
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')
            df['v_liquido'] = df['v_liquido'].fillna(0)
        
        # === LIMPEZA FINAL ===
        df = df[
            (df['qtd'].notna()) & 
            (df['v_liquido'].notna()) &
            (df['cliente'].notna())
        ].copy()
        
        st.success("🎉 Dados carregados e processados com sucesso!")
        return df

    except Exception as e:
        st.error(f"❌ Erro crítico no carregamento: {str(e)}")
        return pd.DataFrame()

# Carregar dados
with st.spinner('📥 Carregando dados...'):
    df = load_data()

if df.empty: 
    st.error("Não foi possível carregar os dados. Verifique a conexão e o formato do arquivo.")
    st.stop()

# =============================================
# FUNÇÕES AUXILIARES PARA FILTROS DINÂMICOS
# =============================================
def get_filtered_options(base_data, selected_filters):
    """Retorna opções disponíveis com base nos filtros selecionados"""
    temp_data = base_data.copy()
    
    # Aplicar filtros existentes
    if selected_filters['ano'] != "Todos":
        temp_data = temp_data[temp_data['ano'] == selected_filters['ano']]
    
    if selected_filters['comercial'] != "Todos":
        temp_data = temp_data[temp_data['comercial'] == selected_filters['comercial']]
    
    if selected_filters['cliente'] != "Todos":
        temp_data = temp_data[temp_data['cliente'] == selected_filters['cliente']]
    
    if selected_filters['categoria'] != "Todas" and 'categoria' in temp_data.columns:
        temp_data = temp_data[temp_data['categoria'] == selected_filters['categoria']]
    
    # Retornar opções disponíveis
    options = {
        'anos': ["Todos"] + sorted(temp_data['ano'].unique().tolist()),
        'comerciais': ["Todos"] + sorted(temp_data['comercial'].unique().tolist()),
        'clientes': ["Todos"] + sorted(temp_data['cliente'].unique().tolist()),
        'categorias': ["Todas"] + sorted(temp_data.get('categoria', pd.Series()).dropna().unique().tolist())
    }
    
    return options

def update_filters():
    """Atualiza os filtros com base nas seleções atuais"""
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            'ano': "Todos",
            'comercial': "Todos", 
            'cliente': "Todos",
            'categoria': "Todas"
        }
    
    # Obter opções disponíveis com base nos filtros atuais
    available_options = get_filtered_options(df, st.session_state.filters)
    
    return available_options

# =============================================
# SIDEBAR COM FILTROS DINÂMICOS
# =============================================
with st.sidebar:
    st.markdown("<h2 style='color:white'>BI Pro</h2>", unsafe_allow_html=True)
    
    # Inicializar filtros na session_state
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            'ano': "Todos",
            'comercial': "Todos", 
            'cliente': "Todos",
            'categoria': "Todas"
        }
    
    # Navegação
    page = st.radio("Navegação", [
        "Visão Geral", "KPIs", "Comparação", "Clientes", "Análise Detalhada"
    ])
    
    # Seção de Filtros
    st.markdown("---")
    st.markdown("### 🔧 Filtros Dinâmicos")
    
    # Obter opções disponíveis
    available_options = update_filters()
    
    # Filtro de Ano
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    ano_selecionado = st.selectbox(
        "📅 Ano",
        options=available_options['anos'],
        key='ano_filter'
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Atualizar filtro de ano
    st.session_state.filters['ano'] = ano_selecionado
    
    # Recalcular opções após seleção do ano
    available_options = get_filtered_options(df, st.session_state.filters)
    
    # Filtro de Comercial
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    comercial_selecionado = st.selectbox(
        "👨‍💼 Comercial", 
        options=available_options['comerciais'],
        key='comercial_filter'
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Atualizar filtro de comercial
    st.session_state.filters['comercial'] = comercial_selecionado
    
    # Recalcular opções após seleção do comercial
    available_options = get_filtered_options(df, st.session_state.filters)
    
    # Filtro de Cliente
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    cliente_selecionado = st.selectbox(
        "🏢 Cliente",
        options=available_options['clientes'],
        key='cliente_filter'
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Atualizar filtro de cliente
    st.session_state.filters['cliente'] = cliente_selecionado
    
    # Recalcular opções após seleção do cliente
    available_options = get_filtered_options(df, st.session_state.filters)
    
    # Filtro de Categoria (se existir na base de dados)
    if 'categoria' in df.columns:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        categoria_selecionada = st.selectbox(
            "📦 Categoria",
            options=available_options['categorias'],
            key='categoria_filter'
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Atualizar filtro de categoria
        st.session_state.filters['categoria'] = categoria_selecionada
    
    # Botão para limpar filtros
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    if st.button("🔄 Limpar Todos os Filtros", use_container_width=True):
        st.session_state.filters = {
            'ano': "Todos",
            'comercial': "Todos", 
            'cliente': "Todos",
            'categoria': "Todas"
        }
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# APLICAR FILTROS AOS DADOS
# =============================================
def apply_filters(data, filters):
    """Aplica os filtros selecionados aos dados"""
    filtered_data = data.copy()
    
    if filters['ano'] != "Todos":
        filtered_data = filtered_data[filtered_data['ano'] == filters['ano']]
    
    if filters['comercial'] != "Todos":
        filtered_data = filtered_data[filtered_data['comercial'] == filters['comercial']]
    
    if filters['cliente'] != "Todos":
        filtered_data = filtered_data[filtered_data['cliente'] == filters['cliente']]
    
    if filters['categoria'] != "Todas" and 'categoria' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['categoria'] == filters['categoria']]
    
    return filtered_data

# Aplicar filtros
data_filtrada = apply_filters(df, st.session_state.filters)

# =============================================
# FUNÇÕES DE FORMATAÇÃO
# =============================================
def formatar_numero_europeu(numero, casas_decimais=2):
    """Formata número no formato europeu: 1.234.567,89"""
    if pd.isna(numero) or numero == 0:
        return "0" if casas_decimais == 0 else "0,00"
    
    try:
        if casas_decimais == 0:
            formatted = f"{numero:,.0f}"
        else:
            formatted = f"{numero:,.{casas_decimais}f}"
        
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0" if casas_decimais == 0 else "0,00"

def fmt_valor(x):
    """Formata valores monetários"""
    return f"€ {formatar_numero_europeu(x, 2)}"

def fmt_quantidade(x):
    """Formata quantidades"""
    if pd.notna(x) and x == int(x):
        return f"{formatar_numero_europeu(x, 0)}"
    else:
        return f"{formatar_numero_europeu(x, 2)}"

def fmt_percentual(x):
    """Formata percentuais"""
    if pd.isna(x) or np.isinf(x):
        return "0,00%"
    return f"{x:.2f}%".replace(".", ",")

# =============================================
# PÁGINAS PRINCIPAIS
# =============================================
if page == "Visão Geral":
    st.markdown("<h1>📊 Visão Geral</h1>", unsafe_allow_html=True)
    
    # Mostrar filtros ativos
    filtros_ativos = []
    if st.session_state.filters['ano'] != "Todos":
        filtros_ativos.append(f"Ano: {st.session_state.filters['ano']}")
    if st.session_state.filters['comercial'] != "Todos":
        filtros_ativos.append(f"Comercial: {st.session_state.filters['comercial']}")
    if st.session_state.filters['cliente'] != "Todos":
        filtros_ativos.append(f"Cliente: {st.session_state.filters['cliente']}")
    if st.session_state.filters['categoria'] != "Todas":
        filtros_ativos.append(f"Categoria: {st.session_state.filters['categoria']}")
    
    if filtros_ativos:
        st.info(f"🔍 **Filtros ativos:** {', '.join(filtros_ativos)} | **Registros:** {len(data_filtrada):,}")
    
    # Métricas principais
    total_qtd = data_filtrada['qtd'].sum()
    total_valor = data_filtrada['v_liquido'].sum()
    total_clientes = data_filtrada['cliente'].nunique()
    total_comerciais = data_filtrada['comercial'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Quantidade Total", 
            fmt_quantidade(total_qtd),
            "kg"
        )
    
    with col2:
        st.metric(
            "Valor Total", 
            fmt_valor(total_valor)
        )
    
    with col3:
        st.metric(
            "Total de Clientes",
            f"{total_clientes:,}"
        )
    
    with col4:
        st.metric(
            "Comerciais Ativos", 
            f"{total_comerciais:,}"
        )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        if not data_filtrada.empty:
            # Vendas por comercial
            vendas_comercial = data_filtrada.groupby('comercial')['v_liquido'].sum().sort_values(ascending=False).head(10)
            if not vendas_comercial.empty:
                fig = px.bar(
                    vendas_comercial,
                    title="Top Comerciais por Valor",
                    labels={'value': 'Valor (€)', 'comercial': 'Comercial'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not data_filtrada.empty:
            # Vendas por cliente
            vendas_cliente = data_filtrada.groupby('cliente')['v_liquido'].sum().sort_values(ascending=False).head(10)
            if not vendas_cliente.empty:
                fig = px.bar(
                    vendas_cliente,
                    title="Top Clientes por Valor",
                    labels={'value': 'Valor (€)', 'cliente': 'Cliente'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Evolução mensal
    if not data_filtrada.empty and 'mes_num' in data_filtrada.columns:
        st.subheader("📈 Evolução Mensal")
        evolucao_mensal = data_filtrada.groupby(['ano', 'mes_num'])['v_liquido'].sum().reset_index()
        if not evolucao_mensal.empty:
            fig = px.line(
                evolucao_mensal,
                x='mes_num',
                y='v_liquido',
                color='ano',
                title="Evolução das Vendas por Mês",
                labels={'mes_num': 'Mês', 'v_liquido': 'Valor (€)', 'ano': 'Ano'}
            )
            st.plotly_chart(fig, use_container_width=True)

elif page == "KPIs":
    st.markdown("<h1>📈 KPIs e Métricas</h1>", unsafe_allow_html=True)
    
    # Mostrar filtros ativos
    filtros_ativos = []
    if st.session_state.filters['ano'] != "Todos":
        filtros_ativos.append(f"Ano: {st.session_state.filters['ano']}")
    if st.session_state.filters['comercial'] != "Todos":
        filtros_ativos.append(f"Comercial: {st.session_state.filters['comercial']}")
    
    if filtros_ativos:
        st.info(f"🔍 **Filtros ativos:** {', '.join(filtros_ativos)}")
    
    if not data_filtrada.empty:
        # KPIs principais
        total_vendas = data_filtrada['v_liquido'].sum()
        media_venda = data_filtrada['v_liquido'].mean()
        ticket_medio = total_vendas / len(data_filtrada) if len(data_filtrada) > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Vendas", fmt_valor(total_vendas))
        
        with col2:
            st.metric("Média por Venda", fmt_valor(media_venda))
        
        with col3:
            st.metric("Ticket Médio", fmt_valor(ticket_medio))
        
        # KPIs adicionais
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.metric("Total de Transações", f"{len(data_filtrada):,}")
        
        with col5:
            clientes_ativos = data_filtrada['cliente'].nunique()
            st.metric("Clientes Ativos", f"{clientes_ativos:,}")
        
        with col6:
            comercial_ativos = data_filtrada['comercial'].nunique()
            st.metric("Comerciais Ativos", f"{comercial_ativos:,}")
        
        # Análise de performance
        st.subheader("📊 Análise de Performance")
        
        col7, col8 = st.columns(2)
        
        with col7:
            # Vendas por comercial
            performance_comercial = data_filtrada.groupby('comercial').agg({
                'v_liquido': ['sum', 'count', 'mean']
            }).round(2)
            performance_comercial.columns = ['Total Vendas', 'Nº Transações', 'Média por Venda']
            performance_comercial = performance_comercial.sort_values('Total Vendas', ascending=False)
            
            st.write("**Performance por Comercial:**")
            st.dataframe(performance_comercial, use_container_width=True)
        
        with col8:
            # Vendas por cliente
            performance_cliente = data_filtrada.groupby('cliente').agg({
                'v_liquido': ['sum', 'count', 'mean']
            }).round(2)
            performance_cliente.columns = ['Total Vendas', 'Nº Transações', 'Média por Venda']
            performance_cliente = performance_cliente.sort_values('Total Vendas', ascending=False).head(10)
            
            st.write("**Top 10 Clientes:**")
            st.dataframe(performance_cliente, use_container_width=True)

elif page == "Comparação":
    st.markdown("<h1>📊 Comparação</h1>", unsafe_allow_html=True)
    
    # Mostrar filtros ativos (exceto ano)
    filtros_ativos = []
    if st.session_state.filters['comercial'] != "Todos":
        filtros_ativos.append(f"Comercial: {st.session_state.filters['comercial']}")
    if st.session_state.filters['cliente'] != "Todos":
        filtros_ativos.append(f"Cliente: {st.session_state.filters['cliente']}")
    
    if filtros_ativos:
        st.info(f"🔍 **Filtros ativos:** {', '.join(filtros_ativos)}")
    
    anos_disponiveis = sorted(data_filtrada['ano'].unique())
    
    if len(anos_disponiveis) >= 2:
        col1, col2 = st.columns(2)
        
        with col1:
            ano1 = st.selectbox("Selecione o Ano 1", anos_disponiveis, key="ano1")
        
        with col2:
            outros_anos = [a for a in anos_disponiveis if a != ano1]
            ano2 = st.selectbox("Selecione o Ano 2", outros_anos if outros_anos else anos_disponiveis, key="ano2")
        
        # Aplicar mesmos filtros para ambos os anos
        filtros_comparacao = st.session_state.filters.copy()
        
        dados_ano1 = apply_filters(df, {**filtros_comparacao, 'ano': ano1})
        dados_ano2 = apply_filters(df, {**filtros_comparacao, 'ano': ano2})
        
        # Calcular métricas
        qtd_ano1 = dados_ano1['qtd'].sum()
        qtd_ano2 = dados_ano2['qtd'].sum()
        valor_ano1 = dados_ano1['v_liquido'].sum()
        valor_ano2 = dados_ano2['v_liquido'].sum()
        
        # Exibir comparação
        st.subheader("📈 Comparação Entre Anos")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(f"Quantidade {ano1}", fmt_quantidade(qtd_ano1))
        
        with col2:
            st.metric(f"Quantidade {ano2}", fmt_quantidade(qtd_ano2))
        
        with col3:
            st.metric(f"Valor {ano1}", fmt_valor(valor_ano1))
        
        with col4:
            st.metric(f"Valor {ano2}", fmt_valor(valor_ano2))
        
        # Variações
        st.subheader("🔄 Variações")
        
        col5, col6 = st.columns(2)
        
        with col5:
            if qtd_ano1 > 0:
                variacao_qtd = ((qtd_ano2 - qtd_ano1) / qtd_ano1) * 100
                st.metric("Variação na Quantidade", fmt_percentual(variacao_qtd))
        
        with col6:
            if valor_ano1 > 0:
                variacao_valor = ((valor_ano2 - valor_ano1) / valor_ano1) * 100
                st.metric("Variação no Valor", fmt_percentual(variacao_valor))
        
        # Gráfico comparativo
        if not dados_ano1.empty and not dados_ano2.empty:
            comparativo_data = pd.DataFrame({
                'Ano': [ano1, ano2],
                'Quantidade': [qtd_ano1, qtd_ano2],
                'Valor': [valor_ano1, valor_ano2]
            })
            
            col7, col8 = st.columns(2)
            
            with col7:
                fig = px.bar(
                    comparativo_data,
                    x='Ano',
                    y='Quantidade',
                    title=f"Comparação de Quantidade: {ano1} vs {ano2}",
                    color='Ano'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col8:
                fig = px.bar(
                    comparativo_data,
                    x='Ano',
                    y='Valor',
                    title=f"Comparação de Valor: {ano1} vs {ano2}",
                    color='Ano'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("⚠️ São necessários pelo menos 2 anos de dados para comparação")

elif page == "Clientes":
    st.markdown("<h1>👥 Análise de Clientes</h1>", unsafe_allow_html=True)
    
    # Mostrar filtros ativos
    filtros_ativos = []
    if st.session_state.filters['ano'] != "Todos":
        filtros_ativos.append(f"Ano: {st.session_state.filters['ano']}")
    if st.session_state.filters['comercial'] != "Todos":
        filtros_ativos.append(f"Comercial: {st.session_state.filters['comercial']}")
    
    if filtros_ativos:
        st.info(f"🔍 **Filtros ativos:** {', '.join(filtros_ativos)}")
    
    if not data_filtrada.empty:
        # Análise de clientes
        analise_clientes = data_filtrada.groupby('cliente').agg({
            'v_liquido': ['sum', 'count', 'mean'],
            'qtd': 'sum',
            'comercial': 'nunique'
        }).round(2)
        
        analise_clientes.columns = ['Total Vendas', 'Nº Transações', 'Ticket Médio', 'Quantidade Total', 'Comerciais']
        analise_clientes = analise_clientes.sort_values('Total Vendas', ascending=False)
        
        # Métricas de clientes
        total_clientes = len(analise_clientes)
        clientes_ativos = len(analise_clientes[analise_clientes['Nº Transações'] > 1])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Clientes", f"{total_clientes:,}")
        
        with col2:
            st.metric("Clientes com Múltiplas Transações", f"{clientes_ativos:,}")
        
        with col3:
            if total_clientes > 0:
                percentual_ativos = (clientes_ativos / total_clientes) * 100
                st.metric("Taxa de Retenção", fmt_percentual(percentual_ativos))
        
        # Gráficos
        col4, col5 = st.columns(2)
        
        with col4:
            top_clientes_valor = analise_clientes.head(10)
            fig = px.bar(
                top_clientes_valor,
                y=top_clientes_valor.index,
                x='Total Vendas',
                title="Top 10 Clientes por Valor",
                orientation='h'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col5:
            top_clientes_qtd = analise_clientes.nlargest(10, 'Quantidade Total')
            fig = px.bar(
                top_clientes_qtd,
                y=top_clientes_qtd.index,
                x='Quantidade Total',
                title="Top 10 Clientes por Quantidade",
                orientation='h'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        st.subheader("📋 Detalhes dos Clientes")
        
        # Formatar a tabela para exibição
        analise_display = analise_clientes.copy()
        analise_display['Total Vendas'] = analise_display['Total Vendas'].apply(fmt_valor)
        analise_display['Ticket Médio'] = analise_display['Ticket Médio'].apply(fmt_valor)
        analise_display['Quantidade Total'] = analise_display['Quantidade Total'].apply(fmt_quantidade)
        
        st.dataframe(analise_display, use_container_width=True)

elif page == "Análise Detalhada":
    st.markdown("<h1>🔍 Análise Detalhada</h1>", unsafe_allow_html=True)
    
    # Mostrar todos os filtros ativos
    filtros_ativos = []
    for key, value in st.session_state.filters.items():
        if value != "Todos" and value != "Todas":
            filtros_ativos.append(f"{key.capitalize()}: {value}")
    
    if filtros_ativos:
        st.info(f"🔍 **Filtros ativos:** {', '.join(filtros_ativos)} | **Registros:** {len(data_filtrada):,}")
    
    if not data_filtrada.empty:
        # Estatísticas detalhadas
        st.subheader("📈 Estatísticas Detalhadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Estatísticas de Valor:**")
            st.write(f"- Média: {fmt_valor(data_filtrada['v_liquido'].mean())}")
            st.write(f"- Mediana: {fmt_valor(data_filtrada['v_liquido'].median())}")
            st.write(f"- Desvio Padrão: {fmt_valor(data_filtrada['v_liquido'].std())}")
            st.write(f"- Mínimo: {fmt_valor(data_filtrada['v_liquido'].min())}")
            st.write(f"- Máximo: {fmt_valor(data_filtrada['v_liquido'].max())}")
        
        with col2:
            st.write("**Estatísticas de Quantidade:**")
            st.write(f"- Média: {fmt_quantidade(data_filtrada['qtd'].mean())}")
            st.write(f"- Mediana: {fmt_quantidade(data_filtrada['qtd'].median())}")
            st.write(f"- Desvio Padrão: {fmt_quantidade(data_filtrada['qtd'].std())}")
            st.write(f"- Mínimo: {fmt_quantidade(data_filtrada['qtd'].min())}")
            st.write(f"- Máximo: {fmt_quantidade(data_filtrada['qtd'].max())}")
        
        # Distribuição
        st.subheader("📊 Distribuições")
        
        col3, col4 = st.columns(2)
        
        with col3:
            fig = px.histogram(
                data_filtrada,
                x='v_liquido',
                title="Distribuição de Valores",
                nbins=20
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            fig = px.histogram(
                data_filtrada,
                x='qtd',
                title="Distribuição de Quantidades",
                nbins=20
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Dados brutos
        st.subheader("📋 Dados Detalhados")
        
        with st.expander("Visualizar todos os dados filtrados"):
            display_data = data_filtrada.copy()
            display_data['v_liquido_formatado'] = display_data['v_liquido'].apply(fmt_valor)
            display_data['qtd_formatada'] = display_data['qtd'].apply(fmt_quantidade)
            
            colunas_display = ['cliente', 'comercial', 'qtd_formatada', 'v_liquido_formatado', 'ano', 'mes_nome']
            if 'categoria' in display_data.columns:
                colunas_display.append('categoria')
            
            st.dataframe(display_data[colunas_display], use_container_width=True)

# =============================================
# RESUMO NO SIDEBAR
# =============================================
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📈 Resumo")
    
    qtd_total = data_filtrada['qtd'].sum()
    valor_total = data_filtrada['v_liquido'].sum()
    
    st.markdown(f"**Período:** {data_filtrada['ano'].min()}-{data_filtrada['ano'].max()}")
    st.markdown(f"**Valor Total:** {fmt_valor(valor_total)}")
    st.markdown(f"**Quantidade Total:** {fmt_quantidade(qtd_total)}")
    st.markdown(f"**Clientes:** {data_filtrada['cliente'].nunique():,}")
    st.markdown(f"**Registros:** {len(data_filtrada):,}")

st.sidebar.markdown("---")
st.sidebar.markdown("🔄 *Filtros atualizados dinamicamente*")
