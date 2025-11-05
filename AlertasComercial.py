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
# CARREGAMENTO CORRIGIDO
# =============================================
month_map = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
    'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
}

month_names = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

def convert_to_numeric(value):
    """Converte um valor para numérico de forma robusta"""
    if pd.isna(value):
        return 0
    
    if isinstance(value, (int, float)):
        return float(value)
    
    try:
        # Converter para string e limpar
        str_value = str(value).strip()
        
        # Remover espaços em branco
        str_value = str_value.replace(' ', '')
        
        # Remover símbolos de moeda e outros caracteres especiais
        str_value = str_value.replace('€', '').replace('$', '').replace('R$', '')
        
        # Detectar formato: se tem ponto e vírgula, determinar qual é o separador decimal
        has_dot = '.' in str_value
        has_comma = ',' in str_value
        
        if has_dot and has_comma:
            # Ambos presentes: determinar qual é o separador decimal
            dot_pos = str_value.rfind('.')
            comma_pos = str_value.rfind(',')
            
            if dot_pos > comma_pos:
                # Ponto é decimal (formato americano)
                str_value = str_value.replace(',', '')
            else:
                # Vírgula é decimal (formato europeu)
                str_value = str_value.replace('.', '').replace(',', '.')
        elif has_comma:
            # Só vírgula: é separador decimal
            str_value = str_value.replace(',', '.')
        
        # Converter para float
        result = float(str_value)
        return result
    except:
        return 0

@st.cache_data(ttl=3600)
def load_data():
    try:
        url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Carregar Excel
        df = pd.read_excel(BytesIO(response.content), engine='openpyxl')
        
        st.info(f"📥 Dados carregados: {len(df)} registros")
        
        # Padronizar colunas
        df.columns = [col.strip().lower() for col in df.columns]
        column_mapping = {
            'mês': 'mes', 
            'qtd.': 'qtd', 
            'v. líquido': 'v_liquido',
            'v.líquido': 'v_liquido', 
            'v_líquido': 'v_liquido',
            'vliquido': 'v_liquido'
        }
        df.rename(columns=column_mapping, inplace=True)
        
        # Mostrar estrutura inicial
        with st.expander("🔍 Estrutura inicial dos dados"):
            st.write("**Colunas:**", list(df.columns))
            st.write("**Primeiras linhas:**")
            st.dataframe(df.head(10), use_container_width=True)
        
        # 1. Converter Mês
        if 'mes' in df.columns:
            df['mes'] = df['mes'].astype(str).str.strip().str.lower()
            df['mes_num'] = df['mes'].map(month_map)
            df['mes_nome'] = df['mes']
            df['mes_nome_pt'] = df['mes_num'].map(month_names)
        
        # 2. Converter Ano
        if 'ano' in df.columns:
            df['ano'] = pd.to_numeric(df['ano'], errors='coerce').fillna(2024).astype(int)
        
        # 3. Converter Quantidade com função robusta
        if 'qtd' in df.columns:
            st.write("🔄 Convertendo Quantidade...")
            df['qtd'] = df['qtd'].apply(convert_to_numeric)
            st.write(f"✅ Soma Qtd: {df['qtd'].sum():,.2f}")
        
        # 4. Converter Valor Líquido com função robusta
        if 'v_liquido' in df.columns:
            st.write("🔄 Convertendo Valor Líquido...")
            df['v_liquido'] = df['v_liquido'].apply(convert_to_numeric)
            st.write(f"✅ Soma V_Liquido: {df['v_liquido'].sum():,.2f}")
        
        # Substituir NaN por 0 ao invés de remover linhas
        df['qtd'] = df['qtd'].fillna(0)
        df['v_liquido'] = df['v_liquido'].fillna(0)
        
        st.info(f"✅ Total de registros mantidos: {len(df):,}")
        
        # Mostrar estatísticas finais
        with st.expander("📊 Estatísticas finais dos dados"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Quantidade (Qtd):**")
                st.write(f"- Total: {df['qtd'].sum():,.2f}")
                st.write(f"- Média: {df['qtd'].mean():,.2f}")
                st.write(f"- Mínimo: {df['qtd'].min():,.2f}")
                st.write(f"- Máximo: {df['qtd'].max():,.2f}")
                st.write(f"- Registros com valor: {len(df[df['qtd'] > 0])}")
                
            with col2:
                st.write("**Valor Líquido:**")
                st.write(f"- Total: {df['v_liquido'].sum():,.2f}")
                st.write(f"- Média: {df['v_liquido'].mean():,.2f}")
                st.write(f"- Mínimo: {df['v_liquido'].min():,.2f}")
                st.write(f"- Máximo: {df['v_liquido'].max():,.2f}")
                st.write(f"- Registros com valor: {len(df[df['v_liquido'] > 0])}")
        
        st.success("🎉 Dados carregados e convertidos com sucesso!")
        return df

    except Exception as e:
        st.error(f"❌ Erro no carregamento: {str(e)}")
        import traceback
        st.error(f"Detalhes do erro: {traceback.format_exc()}")
        return pd.DataFrame()

# Carregar dados
with st.spinner('📥 Carregando e convertendo dados...'):
    df = load_data()

if df.empty: 
    st.error("Não foi possível carregar os dados.")
    st.stop()

# =============================================
# INICIALIZAR SESSION STATE
# =============================================
def initialize_session_state():
    default_filters = {
        'ano': "Todos",
        'mes': "Todos",
        'comercial': "Todos", 
        'cliente': "Todos",
        'categoria': "Todas"
    }
    
    if 'filters' not in st.session_state:
        st.session_state.filters = default_filters.copy()
    else:
        for key in default_filters:
            if key not in st.session_state.filters:
                st.session_state.filters[key] = default_filters[key]

initialize_session_state()

# =============================================
# FUNÇÕES PARA FILTROS DINÂMICOS
# =============================================
def get_available_options(base_data, current_filters):
    """Retorna opções disponíveis baseadas nos filtros atuais"""
    temp_data = base_data.copy()
    
    if 'ano' in current_filters and current_filters['ano'] != "Todos":
        temp_data = temp_data[temp_data['ano'] == current_filters['ano']]
    
    if 'mes' in current_filters and current_filters['mes'] != "Todos":
        temp_data = temp_data[temp_data['mes_num'] == current_filters['mes']]
    
    if 'comercial' in current_filters and current_filters['comercial'] != "Todos":
        temp_data = temp_data[temp_data['comercial'] == current_filters['comercial']]
    
    if 'cliente' in current_filters and current_filters['cliente'] != "Todos":
        temp_data = temp_data[temp_data['cliente'] == current_filters['cliente']]
    
    if ('categoria' in current_filters and current_filters['categoria'] != "Todas" 
        and 'categoria' in temp_data.columns):
        temp_data = temp_data[temp_data['categoria'] == current_filters['categoria']]
    
    # Preparar opções de mês
    meses_disponiveis = sorted(temp_data['mes_num'].dropna().unique())
    meses_opcoes = ["Todos"] + [f"{month_names[m]} ({m})" for m in meses_disponiveis if m in month_names]
    
    return {
        'anos': ["Todos"] + sorted(temp_data['ano'].unique().tolist()),
        'meses': meses_opcoes,
        'comerciais': ["Todos"] + sorted(temp_data['comercial'].unique().tolist()),
        'clientes': ["Todos"] + sorted(temp_data['cliente'].unique().tolist()),
        'categorias': ["Todas"] + sorted(temp_data.get('categoria', pd.Series()).dropna().unique().tolist())
    }

def apply_filters(data, filters):
    """Aplica filtros aos dados"""
    filtered_data = data.copy()
    
    if 'ano' in filters and filters['ano'] != "Todos":
        filtered_data = filtered_data[filtered_data['ano'] == filters['ano']]
    
    if 'mes' in filters and filters['mes'] != "Todos":
        filtered_data = filtered_data[filtered_data['mes_num'] == filters['mes']]
    
    if 'comercial' in filters and filters['comercial'] != "Todos":
        filtered_data = filtered_data[filtered_data['comercial'] == filters['comercial']]
    
    if 'cliente' in filters and filters['cliente'] != "Todos":
        filtered_data = filtered_data[filtered_data['cliente'] == filters['cliente']]
    
    if ('categoria' in filters and filters['categoria'] != "Todas" 
        and 'categoria' in filtered_data.columns):
        filtered_data = filtered_data[filtered_data['categoria'] == filters['categoria']]
    
    return filtered_data

# =============================================
# SIDEBAR COM FILTROS
# =============================================
with st.sidebar:
    st.markdown("<h2 style='color:white'>BI Pro</h2>", unsafe_allow_html=True)
    
    page = st.radio("Navegação", [
        "Visão Geral", "KPIs", "Comparação", "Clientes", "Análise Detalhada"
    ])
    
    st.markdown("---")
    st.markdown("### 🔧 Filtros")
    
    available_options = get_available_options(df, st.session_state.filters)
    
    # Filtro de Ano
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    try:
        ano_index = available_options['anos'].index(st.session_state.filters['ano'])
    except ValueError:
        ano_index = 0
        st.session_state.filters['ano'] = available_options['anos'][0]
    
    novo_ano = st.selectbox(
        "📅 Ano",
        options=available_options['anos'],
        index=ano_index,
        key='ano_selectbox'
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if novo_ano != st.session_state.filters['ano']:
        st.session_state.filters['ano'] = novo_ano
        st.session_state.filters['mes'] = "Todos"
        st.session_state.filters['comercial'] = "Todos"
        st.session_state.filters['cliente'] = "Todos"
        if 'categoria' in df.columns:
            st.session_state.filters['categoria'] = "Todas"
        st.rerun()
    
    available_options = get_available_options(df, st.session_state.filters)
    
    # Filtro de Mês
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    mes_atual_display = "Todos"
    if st.session_state.filters['mes'] != "Todos":
        try:
            mes_num = st.session_state.filters['mes']
            mes_atual_display = f"{month_names[mes_num]} ({mes_num})"
        except:
            mes_atual_display = "Todos"
    
    try:
        mes_index = available_options['meses'].index(mes_atual_display)
    except ValueError:
        mes_index = 0
        st.session_state.filters['mes'] = "Todos"
    
    novo_mes_display = st.selectbox(
        "📆 Mês",
        options=available_options['meses'],
        index=mes_index,
        key='mes_selectbox'
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    novo_mes = "Todos"
    if novo_mes_display != "Todos":
        try:
            novo_mes = int(novo_mes_display.split('(')[-1].replace(')', '').strip())
        except:
            novo_mes = "Todos"
    
    if novo_mes != st.session_state.filters['mes']:
        st.session_state.filters['mes'] = novo_mes
        st.session_state.filters['comercial'] = "Todos"
        st.session_state.filters['cliente'] = "Todos"
        if 'categoria' in df.columns:
            st.session_state.filters['categoria'] = "Todas"
        st.rerun()
    
    available_options = get_available_options(df, st.session_state.filters)
    
    # Filtro de Comercial
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    try:
        comercial_index = available_options['comerciais'].index(st.session_state.filters['comercial'])
    except ValueError:
        comercial_index = 0
        st.session_state.filters['comercial'] = available_options['comerciais'][0]
    
    novo_comercial = st.selectbox(
        "👨‍💼 Comercial", 
        options=available_options['comerciais'],
        index=comercial_index,
        key='comercial_selectbox'
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if novo_comercial != st.session_state.filters['comercial']:
        st.session_state.filters['comercial'] = novo_comercial
        st.session_state.filters['cliente'] = "Todos"
        if 'categoria' in df.columns:
            st.session_state.filters['categoria'] = "Todas"
        st.rerun()
    
    available_options = get_available_options(df, st.session_state.filters)
    
    # Filtro de Cliente
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    try:
        cliente_index = available_options['clientes'].index(st.session_state.filters['cliente'])
    except ValueError:
        cliente_index = 0
        st.session_state.filters['cliente'] = available_options['clientes'][0]
    
    novo_cliente = st.selectbox(
        "🏢 Cliente",
        options=available_options['clientes'],
        index=cliente_index,
        key='cliente_selectbox'
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if novo_cliente != st.session_state.filters['cliente']:
        st.session_state.filters['cliente'] = novo_cliente
        if 'categoria' in df.columns:
            st.session_state.filters['categoria'] = "Todas"
        st.rerun()
    
    available_options = get_available_options(df, st.session_state.filters)
    
    # Filtro de Categoria
    if 'categoria' in df.columns:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        nova_categoria = st.selectbox(
            "📦 Categoria",
            options=available_options['categorias'],
            index=available_options['categorias'].index(st.session_state.filters['categoria']) 
            if st.session_state.filters['categoria'] in available_options['categorias'] else 0,
            key='categoria_selectbox'
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if nova_categoria != st.session_state.filters['categoria']:
            st.session_state.filters['categoria'] = nova_categoria
            st.rerun()
    
    # Botão limpar filtros
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    if st.button("🔄 Limpar Todos os Filtros", use_container_width=True, key='clear_filters'):
        st.session_state.filters = {
            'ano': "Todos", 'mes': "Todos", 'comercial': "Todos", 
            'cliente': "Todos", 'categoria': "Todas"
        }
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# APLICAR FILTROS AOS DADOS
# =============================================
data_filtrada = apply_filters(df, st.session_state.filters)

# =============================================
# FUNÇÕES DE FORMATAÇÃO
# =============================================
def formatar_numero_europeu(numero, casas_decimais=2):
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

def fmt_valor(x): return f"€ {formatar_numero_europeu(x, 2)}"
def fmt_quantidade(x): 
    return f"{formatar_numero_europeu(x, 0)}" if pd.notna(x) and x == int(x) else f"{formatar_numero_europeu(x, 2)}"
def fmt_percentual(x): return f"{x:.2f}%".replace(".", ",") if not pd.isna(x) and not np.isinf(x) else "0,00%"

# =============================================
# PÁGINAS PRINCIPAIS
# =============================================
if page == "Visão Geral":
    st.markdown("<h1>📊 Visão Geral</h1>", unsafe_allow_html=True)
    
    # Mostrar filtros ativos
    filtros_ativos = []
    for key, value in st.session_state.filters.items():
        if value != "Todos" and value != "Todas":
            if key == 'mes':
                try:
                    filtros_ativos.append(f"{key}: {month_names[value]}")
                except:
                    filtros_ativos.append(f"{key}: {value}")
            else:
                filtros_ativos.append(f"{key}: {value}")
    
    if filtros_ativos:
        st.info(f"🔍 **Filtros ativos:** {', '.join(filtros_ativos)}")
    
    # Métricas principais
    total_qtd = data_filtrada['qtd'].sum()
    total_valor = data_filtrada['v_liquido'].sum()
    total_clientes = data_filtrada['cliente'].nunique()
    total_comerciais = data_filtrada['comercial'].nunique()
    
    st.write(f"📊 **Registros após filtros:** {len(data_filtrada):,}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.metric("Quantidade Total", fmt_quantidade(total_qtd), "kg")
    with col2: 
        st.metric("Valor Total", fmt_valor(total_valor))
    with col3: 
        st.metric("Total de Clientes", f"{total_clientes:,}")
    with col4: 
        st.metric("Comerciais Ativos", f"{total_comerciais:,}")
    
    # Gráficos
    if not data_filtrada.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            vendas_comercial = data_filtrada.groupby('comercial')['v_liquido'].sum().nlargest(10)
            if not vendas_comercial.empty:
                fig = px.bar(vendas_comercial, title="Top Comerciais por Valor",
                            labels={'value': 'Valor (€)', 'comercial': 'Comercial'})
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            vendas_cliente = data_filtrada.groupby('cliente')['v_liquido'].sum().nlargest(10)
            if not vendas_cliente.empty:
                fig = px.bar(vendas_cliente, title="Top Clientes por Valor",
                            labels={'value': 'Valor (€)', 'cliente': 'Cliente'})
                st.plotly_chart(fig, use_container_width=True)

# =============================================
# RESUMO NO SIDEBAR
# =============================================
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📈 Resumo")
    
    qtd_total = data_filtrada['qtd'].sum()
    valor_total = data_filtrada['v_liquido'].sum()
    
    periodo_texto = f"{data_filtrada['ano'].min()}-{data_filtrada['ano'].max()}"
    if 'mes' in st.session_state.filters and st.session_state.filters['mes'] != "Todos":
        try:
            periodo_texto = f"{month_names[st.session_state.filters['mes']]} {data_filtrada['ano'].min()}"
        except:
            pass
    
    st.markdown(f"**Período:** {periodo_texto}")
    st.markdown(f"**Valor:** {fmt_valor(valor_total)}")
    st.markdown(f"**Quantidade:** {fmt_quantidade(qtd_total)}")
    st.markdown(f"**Clientes:** {data_filtrada['cliente'].nunique():,}")
    st.markdown(f"**Registros:** {len(data_filtrada):,}")

st.sidebar.markdown("---")
st.sidebar.markdown("🔄 *Filtros dinâmicos ativos*")
