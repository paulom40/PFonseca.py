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
        st.info(f"📊 Colunas encontradas: {list(df.columns)}")
        
        # === VERIFICAR ESTRUTURA DOS DADOS ===
        with st.expander("🔍 Estrutura inicial dos dados"):
            st.write("**Primeiras 5 linhas:**")
            st.dataframe(df.head(), use_container_width=True)
            st.write("**Tipos de dados:**")
            st.write(df.dtypes)
            st.write("**Estatísticas básicas:**")
            st.write(df.describe())
        
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
        
        st.info(f"📋 Colunas após padronização: {list(df.columns)}")
        
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
        
        # 3. Converter Quantidade - tratamento robusto
        if 'qtd' in df.columns:
            # Primeiro verificar o tipo atual
            st.write(f"Tipo da coluna Qtd antes: {df['qtd'].dtype}")
            st.write(f"Amostra Qtd: {df['qtd'].head(10).tolist()}")
            
            # Converter para string e limpar
            df['qtd'] = df['qtd'].astype(str)
            
            # Remover caracteres não numéricos exceto ponto e vírgula
            df['qtd'] = df['qtd'].str.replace(r'[^\d,\.\-]', '', regex=True)
            
            # Substituir vírgula por ponto para decimal
            df['qtd'] = df['qtd'].str.replace(',', '.', regex=False)
            
            # Converter para numérico
            df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')
            
            # Preencher NA com 0
            df['qtd'] = df['qtd'].fillna(0)
            
            st.write(f"Tipo da coluna Qtd depois: {df['qtd'].dtype}")
            st.write(f"Amostra Qtd convertida: {df['qtd'].head(10).tolist()}")
        
        # 4. Converter Valor Líquido - mesmo tratamento
        if 'v_liquido' in df.columns:
            st.write(f"Tipo da coluna V_Liquido antes: {df['v_liquido'].dtype}")
            st.write(f"Amostra V_Liquido: {df['v_liquido'].head(10).tolist()}")
            
            df['v_liquido'] = df['v_liquido'].astype(str)
            df['v_liquido'] = df['v_liquido'].str.replace(r'[^\d,\.\-]', '', regex=True)
            df['v_liquido'] = df['v_liquido'].str.replace(',', '.', regex=False)
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')
            df['v_liquido'] = df['v_liquido'].fillna(0)
            
            st.write(f"Tipo da coluna V_Liquido depois: {df['v_liquido'].dtype}")
            st.write(f"Amostra V_Liquido convertida: {df['v_liquido'].head(10).tolist()}")
        
        # === LIMPEZA FINAL ===
        st.info(f"🔍 Antes da limpeza final: {len(df)} registros")
        
        # Remover registros completamente inválidos
        initial_count = len(df)
        df = df[
            (df['qtd'].notna()) & 
            (df['v_liquido'].notna()) &
            (df['qtd'] != 0) &
            (df['cliente'].notna())
        ].copy()
        
        final_count = len(df)
        st.info(f"✅ Depois da limpeza final: {final_count} registros")
        st.info(f"🗑️ Registros removidos: {initial_count - final_count}")
        
        # Mostrar estatísticas finais
        with st.expander("📊 Estatísticas finais dos dados"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Quantidade (Qtd):**")
                st.write(f"- Total: {df['qtd'].sum():,.2f}")
                st.write(f"- Média: {df['qtd'].mean():,.2f}")
                st.write(f"- Registros: {len(df[df['qtd'] > 0])}")
                
            with col2:
                st.write("**Valor Líquido:**")
                st.write(f"- Total: {df['v_liquido'].sum():,.2f}")
                st.write(f"- Média: {df['v_liquido'].mean():,.2f}")
                st.write(f"- Registros: {len(df[df['v_liquido'] > 0])}")
                
            with col3:
                st.write("**Outras informações:**")
                st.write(f"- Clientes: {df['cliente'].nunique()}")
                st.write(f"- Comerciais: {df['comercial'].nunique()}")
                st.write(f"- Período: {df['ano'].min()}-{df['ano'].max()}")
        
        st.success("🎉 Dados carregados e processados com sucesso!")
        return df

    except Exception as e:
        st.error(f"❌ Erro crítico no carregamento: {str(e)}")
        import traceback
        st.error(f"Detalhes do erro: {traceback.format_exc()}")
        return pd.DataFrame()

# Carregar dados
with st.spinner('📥 Carregando dados...'):
    df = load_data()

if df.empty: 
    st.error("Não foi possível carregar os dados. Verifique a conexão e o formato do arquivo.")
    st.stop()

# =============================================
# SIDEBAR SIMPLIFICADO
# =============================================
with st.sidebar:
    st.markdown("<h2 style='color:white'>BI Pro</h2>", unsafe_allow_html=True)
    
    # Navegação
    page = st.radio("Navegação", [
        "Visão Geral", "KPIs", "Comparação", "Clientes", "Análise Detalhada"
    ])
    
    # Filtros básicos
    st.markdown("---")
    st.markdown("**Filtros:**")
    
    # Ano
    anos_disponiveis = sorted(df['ano'].unique())
    ano_selecionado = st.selectbox("Ano", ["Todos"] + anos_disponiveis)
    
    # Comercial
    comerciais_disponiveis = sorted(df['comercial'].unique())
    comercial_selecionado = st.selectbox("Comercial", ["Todos"] + comerciais_disponiveis)
    
    # Cliente
    clientes_disponiveis = sorted(df['cliente'].unique())
    cliente_selecionado = st.selectbox("Cliente", ["Todos"] + clientes_disponiveis)

# Aplicar filtros
data = df.copy()
if ano_selecionado != "Todos":
    data = data[data['ano'] == ano_selecionado]
if comercial_selecionado != "Todos":
    data = data[data['comercial'] == comercial_selecionado]
if cliente_selecionado != "Todos":
    data = data[data['cliente'] == cliente_selecionado]

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

# =============================================
# PÁGINAS PRINCIPAIS
# =============================================
if page == "Visão Geral":
    st.markdown("<h1>📊 Visão Geral</h1>", unsafe_allow_html=True)
    
    # Métricas principais
    total_qtd = data['qtd'].sum()
    total_valor = data['v_liquido'].sum()
    total_clientes = data['cliente'].nunique()
    total_comerciais = data['comercial'].nunique()
    
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
    
    # Gráficos básicos
    col1, col2 = st.columns(2)
    
    with col1:
        # Vendas por comercial
        vendas_por_comercial = data.groupby('comercial')['v_liquido'].sum().sort_values(ascending=False)
        
        if not vendas_por_comercial.empty:
            fig1 = px.bar(
                vendas_por_comercial.head(10),
                title="Top 10 Comerciais por Valor de Vendas",
                labels={'value': 'Valor (€)', 'comercial': 'Comercial'}
            )
            fig1.update_layout(showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Vendas por cliente
        vendas_por_cliente = data.groupby('cliente')['v_liquido'].sum().sort_values(ascending=False)
        
        if not vendas_por_cliente.empty:
            fig2 = px.bar(
                vendas_por_cliente.head(10),
                title="Top 10 Clientes por Valor de Vendas",
                labels={'value': 'Valor (€)', 'cliente': 'Cliente'}
            )
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
    
    # Tabela de dados
    with st.expander("📋 Visualizar Dados Filtrados"):
        st.write(f"Mostrando {len(data)} registros")
        
        # Preparar dados para exibição
        display_data = data[['cliente', 'comercial', 'qtd', 'v_liquido', 'ano', 'mes_nome']].copy()
        display_data['qtd_formatada'] = display_data['qtd'].apply(fmt_quantidade)
        display_data['v_liquido_formatado'] = display_data['v_liquido'].apply(fmt_valor)
        
        st.dataframe(
            display_data[['cliente', 'comercial', 'qtd_formatada', 'v_liquido_formatado', 'ano', 'mes_nome']],
            use_container_width=True
        )

elif page == "Comparação":
    st.markdown("<h1>📈 Comparação</h1>", unsafe_allow_html=True)
    
    anos_disponiveis = sorted(data['ano'].unique())
    
    if len(anos_disponiveis) >= 2:
        col1, col2 = st.columns(2)
        
        with col1:
            ano1 = st.selectbox("Selecione o Ano 1", anos_disponiveis)
        
        with col2:
            # Selecionar ano2 diferente do ano1
            outros_anos = [a for a in anos_disponiveis if a != ano1]
            ano2 = st.selectbox("Selecione o Ano 2", outros_anos if outros_anos else anos_disponiveis)
        
        # Filtrar dados para cada ano
        dados_ano1 = data[data['ano'] == ano1]
        dados_ano2 = data[data['ano'] == ano2]
        
        # Calcular métricas
        qtd_ano1 = dados_ano1['qtd'].sum()
        qtd_ano2 = dados_ano2['qtd'].sum()
        valor_ano1 = dados_ano1['v_liquido'].sum()
        valor_ano2 = dados_ano2['v_liquido'].sum()
        
        # Exibir métricas
        st.subheader("Comparação de Métricas")
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric(f"Quantidade {ano1}", fmt_quantidade(qtd_ano1))
        
        with metric_col2:
            st.metric(f"Quantidade {ano2}", fmt_quantidade(qtd_ano2))
        
        with metric_col3:
            st.metric(f"Valor {ano1}", fmt_valor(valor_ano1))
        
        with metric_col4:
            st.metric(f"Valor {ano2}", fmt_valor(valor_ano2))
        
        # Calcular variações
        if qtd_ano1 > 0:
            variacao_qtd = ((qtd_ano2 - qtd_ano1) / qtd_ano1) * 100
        else:
            variacao_qtd = 0
            
        if valor_ano1 > 0:
            variacao_valor = ((valor_ano2 - valor_ano1) / valor_ano1) * 100
        else:
            variacao_valor = 0
        
        # Exibir variações
        st.subheader("Variações")
        
        var_col1, var_col2 = st.columns(2)
        
        with var_col1:
            st.metric(
                "Variação na Quantidade",
                f"{variacao_qtd:+.1f}%"
            )
        
        with var_col2:
            st.metric(
                "Variação no Valor",
                f"{variacao_valor:+.1f}%"
            )
        
    else:
        st.warning("⚠️ São necessários pelo menos 2 anos de dados para comparação")

elif page == "Clientes":
    st.markdown("<h1>👥 Análise de Clientes</h1>", unsafe_allow_html=True)
    
    # Top clientes
    clientes_analysis = data.groupby('cliente').agg({
        'v_liquido': 'sum',
        'qtd': 'sum',
        'comercial': 'nunique'
    }).sort_values('v_liquido', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Clientes por Valor")
        top_clientes_valor = clientes_analysis.head(10)
        
        fig = px.bar(
            top_clientes_valor,
            x=top_clientes_valor.index,
            y='v_liquido',
            title="Top 10 Clientes por Valor de Vendas"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Top 10 Clientes por Quantidade")
        top_clientes_qtd = clientes_analysis.sort_values('qtd', ascending=False).head(10)
        
        fig = px.bar(
            top_clientes_qtd,
            x=top_clientes_qtd.index,
            y='qtd',
            title="Top 10 Clientes por Quantidade"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    with st.expander("📊 Tabela Detalhada de Clientes"):
        clientes_detalhados = clientes_analysis.copy()
        clientes_detalhados['v_liquido_formatado'] = clientes_detalhados['v_liquido'].apply(fmt_valor)
        clientes_detalhados['qtd_formatada'] = clientes_detalhados['qtd'].apply(fmt_quantidade)
        
        st.dataframe(
            clientes_detalhados[['v_liquido_formatado', 'qtd_formatada', 'comercial']],
            use_container_width=True
        )

# Informações do dataset no sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("**Resumo do Dataset:**")
    
    qtd_total = df['qtd'].sum()
    valor_total = df['v_liquido'].sum()
    
    st.markdown(f"• Período: {df['ano'].min()}-{df['ano'].max()}")
    st.markdown(f"• Valor Total: {fmt_valor(valor_total)}")
    st.markdown(f"• Clientes: {df['cliente'].nunique():,}")
    st.markdown(f"• Registros: {len(df):,}")

st.sidebar.markdown("---")
st.sidebar.markdown("🔄 *Atualizado automaticamente*")
