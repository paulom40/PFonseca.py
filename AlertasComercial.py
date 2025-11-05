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
# CARREGAMENTO CORRIGIDO - DADOS COM VÍRGULA DECIMAL
# =============================================
month_map = {'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,
             'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}

@st.cache_data(ttl=3600)
def load_data():
    try:
        # Carregar o Excel mantendo o formato original
        df = pd.read_excel(BytesIO(requests.get(
            "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx", 
            timeout=15).content))
        
        # === 1. PADRONIZAR COLUNAS ===
        df.columns = [col.strip() for col in df.columns]
        col_map = {}
        raw_lower = [col.lower() for col in df.columns]
        mapping = {
            'mes': ['mês', 'mes'],
            'qtd': ['qtd.', 'qtd', 'quantidade'],
            'ano': ['ano'],
            'cliente': ['cliente'],
            'comercial': ['comercial'],
            'v_liquido': ['v. líquido', 'v_liquido']
        }
        for std, variants in mapping.items():
            for var in variants:
                if var in raw_lower:
                    idx = raw_lower.index(var)
                    col_map[df.columns[idx]] = std
                    break
        df.rename(columns=col_map, inplace=True)

        # === 2. CONVERSÃO CORRETA PARA DADOS COM VÍRGULA DECIMAL ===
        
        # Mês - converter para número
        df['mes'] = df['mes'].astype(str).str.strip().str.lower().map(month_map)
        df['mes'] = pd.to_numeric(df['mes'], errors='coerce')

        # Ano - converter para número
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')

        # Quantidade - tratar como texto com vírgula decimal
        if 'qtd' in df.columns:
            # Converter para string e tratar vírgula decimal
            df['qtd'] = df['qtd'].astype(str)
            
            # Remover possíveis pontos de milhares e converter vírgula para ponto decimal
            df['qtd'] = (df['qtd']
                        .str.replace(r'\.', '', regex=True)  # Remove pontos de milhares
                        .str.replace(',', '.', regex=False)  # Converte vírgula para ponto
                        .str.replace(r'[^\d\.]', '', regex=True)  # Remove caracteres não numéricos
            )
            
            # Converter para numérico
            df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce').fillna(0)
            
            # Arredondar para 2 casas decimais
            df['qtd'] = df['qtd'].round(2)

        # Valor Líquido - tratar como texto com vírgula decimal
        if 'v_liquido' in df.columns:
            # Converter para string e tratar vírgula decimal
            df['v_liquido'] = df['v_liquido'].astype(str)
            
            # Remover possíveis pontos de milhares e converter vírgula para ponto decimal
            df['v_liquido'] = (df['v_liquido']
                              .str.replace(r'\.', '', regex=True)  # Remove pontos de milhares
                              .str.replace(',', '.', regex=False)  # Converte vírgula para ponto
                              .str.replace(r'[^\d\.]', '', regex=True)  # Remove caracteres não numéricos
            )
            
            # Converter para numérico
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce').fillna(0)
            
            # Arredondar para 2 casas decimais
            df['v_liquido'] = df['v_liquido'].round(2)

        # === 3. VALIDAÇÃO E LIMPEZA ===
        st.info(f"🔍 Antes da limpeza: {len(df)} registros")
        
        # Remover registros com valores inválidos
        df = df.dropna(subset=['mes', 'qtd', 'ano', 'cliente', 'comercial', 'v_liquido'])
        df = df[(df['mes'].between(1, 12)) & 
                (df['qtd'] > 0) & 
                (df['v_liquido'] > 0)]
        
        # Remover duplicatas
        df = df.drop_duplicates(subset=['cliente','comercial','ano','mes','qtd','v_liquido'])
        
        st.info(f"✅ Depois da limpeza: {len(df)} registros")
        
        # Mostrar estatísticas dos dados carregados
        with st.expander("📊 Estatísticas dos dados carregados"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Quantidade (Qtd):**")
                st.write(f"- Mínimo: {df['qtd'].min():,.2f}")
                st.write(f"- Máximo: {df['qtd'].max():,.2f}")
                st.write(f"- Média: {df['qtd'].mean():,.2f}")
                st.write(f"- Total: {df['qtd'].sum():,.2f}")
                
            with col2:
                st.write("**Valor Líquido:**")
                st.write(f"- Mínimo: {df['v_liquido'].min():,.2f}")
                st.write(f"- Máximo: {df['v_liquido'].max():,.2f}")
                st.write(f"- Média: {df['v_liquido'].mean():,.2f}")
                st.write(f"- Total: {df['v_liquido'].sum():,.2f}")

        st.success("✅ Dados carregados e convertidos corretamente!")
        return df

    except Exception as e:
        st.error(f"❌ Erro no carregamento: {e}")
        return pd.DataFrame()

# Carregar dados
df = load_data()
if df.empty: 
    st.error("Não foi possível carregar os dados. Verifique a conexão e o formato do arquivo.")
    st.stop()

# =============================================
# SIDEBAR
# =============================================
with st.sidebar:
    st.markdown("<h2 style='color:white'>BI Pro</h2>", unsafe_allow_html=True)
    page = st.radio("Navegação", [
        "Visão Geral", "KPIs", "Tendências", "Alertas", "Clientes", "Comparação", "Comparação Clientes"
    ])
    
    def opts(d, a, c, cl):
        t = d.copy()
        if a != "Todos": t = t[t['ano'] == int(a)]
        if c != "Todos": t = t[t['comercial'].astype(str) == str(c)]
        if cl != "Todos": t = t[t['cliente'].astype(str) == str(cl)]
        return (sorted(t['ano'].unique().astype(int)),
                sorted(t['comercial'].unique()),
                sorted(t['cliente'].unique()),
                sorted(t.get('categoria', pd.Series()).dropna().unique()))
    
    anos = sorted(df['ano'].unique().astype(int))
    ano = st.selectbox("Ano", ["Todos"] + anos)
    coms = opts(df, ano, "Todos", "Todos")[1]
    comercial = st.selectbox("Comercial", ["Todos"] + coms)
    cls = opts(df, ano, comercial, "Todos")[2]
    cliente = st.selectbox("Cliente", ["Todos"] + cls)
    cats = opts(df, ano, comercial, cliente)[3]
    categoria = st.selectbox("Categoria", ["Todas"] + cats)

    data = df.copy()
    if ano != "Todos": data = data[data['ano'] == int(ano)]
    if comercial != "Todos": data = data[data['comercial'].astype(str) == str(comercial)]
    if cliente != "Todos": data = data[data['cliente'].astype(str) == str(cliente)]
    if categoria != "Todas" and 'categoria' in data.columns:
        data = data[data['categoria'].astype(str) == str(categoria)]

# =============================================
# FUNÇÕES DE FORMATAÇÃO PARA VÍRGULA DECIMAL
# =============================================
def formatar_numero_europeu(numero, casas_decimais=2):
    """
    Formata número no formato europeu: 1.234.567,89
    """
    if pd.isna(numero) or numero == 0:
        return "0" if casas_decimais == 0 else "0,00"
    
    try:
        # Formatar com separador de milhares e vírgula decimal
        if casas_decimais == 0:
            formatted = f"{numero:,.0f}"
        else:
            formatted = f"{numero:,.{casas_decimais}f}"
        
        # Converter formato americano para europeu
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0" if casas_decimais == 0 else "0,00"

def fmt_valor(x, u=""):
    """Formata valores monetários"""
    return f"{formatar_numero_europeu(x, 2)} {u}".strip()

def fmt_quantidade(x, u=""):
    """Formata quantidades"""
    # Verificar se é número inteiro
    if pd.notna(x) and x == int(x):
        return f"{formatar_numero_europeu(x, 0)} {u}".strip()
    else:
        return f"{formatar_numero_europeu(x, 2)} {u}".strip()

def fmt_percentual(x):
    """Formata percentuais"""
    if pd.isna(x) or np.isinf(x):
        return "0,00%"
    
    try:
        formatted = f"{x:+.2f}%"
        return formatted.replace(".", ",")
    except:
        return "0,00%"

# =============================================
# PÁGINAS
# =============================================
if page == "Visão Geral":
    st.markdown("<h1>Visão Geral</h1>", unsafe_allow_html=True)
    
    # Calcular totais
    qtd_total = data['qtd'].sum()
    valor_total = data['v_liquido'].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        st.metric("Quantidade", fmt_quantidade(qtd_total, "kg"))
    with c2: 
        st.metric("Valor Total", fmt_valor(valor_total, "EUR"))
    with c3: 
        st.metric("Clientes", f"{data['cliente'].nunique():,}")
    with c4: 
        st.metric("Comerciais", f"{data['comercial'].nunique():,}")
    
    # Amostra dos dados
    with st.expander("🔍 Amostra dos dados processados"):
        st.write("**Primeiras 10 linhas:**")
        display_data = data[['cliente', 'qtd', 'v_liquido', 'ano', 'mes']].head(10).copy()
        display_data['qtd'] = display_data['qtd'].apply(lambda x: fmt_quantidade(x, ''))
        display_data['v_liquido'] = display_data['v_liquido'].apply(lambda x: fmt_valor(x, ''))
        st.dataframe(display_data, use_container_width=True)

elif page == "Comparação":
    st.markdown("<h1>Comparação</h1>", unsafe_allow_html=True)
    anos_disponiveis = sorted(data['ano'].unique())
    
    if len(anos_disponiveis) >= 2:
        a1, a2 = st.columns(2)
        with a1: 
            y1 = st.selectbox("Ano 1", anos_disponiveis)
        with a2: 
            default_idx = 1 if len(anos_disponiveis) > 1 else 0
            y2 = st.selectbox("Ano 2", anos_disponiveis, index=default_idx)
        
        d1 = data[data['ano'] == y1]
        d2 = data[data['ano'] == y2]
        
        # Calcular totais
        qtd_y1 = d1['qtd'].sum()
        qtd_y2 = d2['qtd'].sum()
        valor_y1 = d1['v_liquido'].sum()
        valor_y2 = d2['v_liquido'].sum()
        
        # Métricas principais
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            st.metric(f"Quantidade {y1}", fmt_quantidade(qtd_y1, "kg"))
        with c2: 
            st.metric(f"Quantidade {y2}", fmt_quantidade(qtd_y2, "kg"))
        with c3: 
            st.metric(f"Valor {y1}", fmt_valor(valor_y1, "EUR"))
        with c4: 
            st.metric(f"Valor {y2}", fmt_valor(valor_y2, "EUR"))
        
        # Variação
        col1, col2 = st.columns(2)
        with col1:
            if qtd_y1 > 0:
                variacao_qtd = ((qtd_y2 - qtd_y1) / qtd_y1) * 100
                st.metric("Variação Quantidade", fmt_percentual(variacao_qtd))
            else:
                st.metric("Variação Quantidade", "N/A")
        
        with col2:
            if valor_y1 > 0:
                variacao_valor = ((valor_y2 - valor_y1) / valor_y1) * 100
                st.metric("Variação Valor", fmt_percentual(variacao_valor))
            else:
                st.metric("Variação Valor", "N/A")

# ... (outras páginas mantêm a mesma lógica)

# Informações do dataset no sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("**Dataset Info:**")
    
    qtd_resumo = df['qtd'].sum()
    valor_resumo = df['v_liquido'].sum()
    
    st.markdown(f"- Período: {int(df['ano'].min())}-{int(df['ano'].max())}")
    st.markdown(f"- Total: {fmt_valor(valor_resumo, 'EUR')}")
    st.markdown(f"- Clientes: {df['cliente'].nunique():,}")
    st.markdown(f"- Registros: {len(df):,}")
