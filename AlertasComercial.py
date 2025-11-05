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
# CARREGAMENTO + VALIDAÇÃO 100% SEGURA
# =============================================
month_map = {'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,
             'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}

@st.cache_data(ttl=3600)
def load_data():
    try:
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

        # === 2. FORÇAR CONVERSÃO NUMÉRICA (100% SEGURA) ===
        df['mes'] = df['mes'].astype(str).str.strip().str.lower().map(month_map)
        df['mes'] = pd.to_numeric(df['mes'], errors='coerce')

        df['qtd'] = df['qtd'].astype(str).str.replace(r'\D', '', regex=True)
        df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce').fillna(0).astype(int)

        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')

        if 'v_liquido' in df.columns:
            df['v_liquido'] = (df['v_liquido'].astype(str)
                               .str.replace(r'[^\d,.]', '', regex=True)
                               .str.replace(r'\.', '', regex=True)
                               .str.replace(',', '.', regex=False))
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce').fillna(0)
            
            # FORMATAR PARA 2 CASAS DECIMAIS
            df['v_liquido'] = df['v_liquido'].round(2)

        # === 3. LIMPEZA FINAL ===
        df = df.dropna(subset=['mes', 'qtd', 'ano', 'cliente', 'comercial', 'v_liquido'])
        df = df[(df['mes'].between(1, 12)) & 
                (df['qtd'] > 0) & 
                (df['v_liquido'] > 0)]
        df = df.drop_duplicates(subset=['cliente','comercial','ano','mes','qtd','v_liquido'])

        st.success("Dados carregados com sucesso!")
        return df

    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty: st.stop()

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
# FUNÇÕES DE FORMATAÇÃO CORRIGIDAS - SIMPLES E DIRETAS
# =============================================
def fmt_valor_simples(x, u=""):
    """Formata valores com 2 casas decimais no formato europeu"""
    if pd.isna(x) or x == 0:
        return f"0,00 {u}".strip()
    
    try:
        # Formato europeu: ponto para milhares, vírgula para decimais
        return f"{x:,.2f} {u}".replace(",", "X").replace(".", ",").replace("X", ".").strip()
    except:
        return f"0,00 {u}".strip()

def fmt_quantidade_simples(x, u=""):
    """Formata quantidades no formato europeu"""
    if pd.isna(x) or x == 0:
        return f"0 {u}".strip()
    
    try:
        if x == int(x):  # Se for número inteiro
            return f"{x:,} {u}".replace(",", ".").strip()
        else:
            return f"{x:,.2f} {u}".replace(",", "X").replace(".", ",").replace("X", ".").strip()
    except:
        return f"0 {u}".strip()

def fmt_percentual_simples(x):
    """Formata percentuais de forma segura"""
    if pd.isna(x) or np.isinf(x):
        return "0,00%"
    
    try:
        return f"{x:+.2f}%".replace(".", ",")
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
        st.metric("Quantidade", fmt_quantidade_simples(qtd_total, "kg"))
    with c2: 
        st.metric("Valor Total", fmt_valor_simples(valor_total, "EUR"))
    with c3: 
        st.metric("Clientes", f"{data['cliente'].nunique():,}")
    with c4: 
        st.metric("Comerciais", f"{data['comercial'].nunique():,}")
    
    # Debug: mostrar valores reais
    with st.expander("🔍 Ver valores detalhados"):
        st.write(f"Quantidade total real: {qtd_total:,.2f} kg")
        st.write(f"Valor total real: {valor_total:,.2f} EUR")
        st.write(f"Primeiras linhas dos dados:")
        st.dataframe(data[['cliente', 'qtd', 'v_liquido']].head())

elif page == "KPIs":
    st.markdown("<h1>KPIs</h1>", unsafe_allow_html=True)
    metrica = st.selectbox("Métrica", ["Quantidade", "Valor"])
    grupo = st.selectbox("Agrupar", ["Mês", "Comercial", "Cliente"])
    col = 'qtd' if metrica == "Quantidade" else 'v_liquido'
    gcol = {'Mês':'mes', 'Comercial':'comercial', 'Cliente':'cliente'}[grupo]
    
    agg = data.groupby(gcol)[col].sum().reset_index().sort_values(col, ascending=False).head(10)
    
    if grupo == "Mês": 
        agg['mes'] = agg['mes'].map({1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',
                                     7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'})
    
    fig = px.bar(agg, x=gcol, y=col, title=f"Top 10 {metrica} por {grupo}")
    
    if metrica == "Quantidade":
        fig.update_yaxes(tickformat=",", title="Quantidade (kg)")
    else:
        fig.update_yaxes(tickformat=",.2f", title="Valor (EUR)")
        
    st.plotly_chart(fig, use_container_width=True)

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
            st.metric(f"Quantidade {y1}", fmt_quantidade_simples(qtd_y1, "kg"))
        with c2: 
            st.metric(f"Quantidade {y2}", fmt_quantidade_simples(qtd_y2, "kg"))
        with c3: 
            st.metric(f"Valor {y1}", fmt_valor_simples(valor_y1, "EUR"))
        with c4: 
            st.metric(f"Valor {y2}", fmt_valor_simples(valor_y2, "EUR"))
        
        # Variação
        col1, col2 = st.columns(2)
        with col1:
            if qtd_y1 > 0:
                variacao_qtd = ((qtd_y2 - qtd_y1) / qtd_y1) * 100
                st.metric("Variação Quantidade", fmt_percentual_simples(variacao_qtd))
            else:
                st.metric("Variação Quantidade", "N/A")
        
        with col2:
            if valor_y1 > 0:
                variacao_valor = ((valor_y2 - valor_y1) / valor_y1) * 100
                st.metric("Variação Valor", fmt_percentual_simples(variacao_valor))
            else:
                st.metric("Variação Valor", "N/A")
        
        # Debug section
        with st.expander("🔍 Ver detalhes dos cálculos"):
            st.write(f"**Ano {y1}:**")
            st.write(f"- Quantidade: {qtd_y1:,.2f} kg")
            st.write(f"- Valor: {valor_y1:,.2f} EUR")
            st.write(f"- Registros: {len(d1)}")
            
            st.write(f"**Ano {y2}:**")
            st.write(f"- Quantidade: {qtd_y2:,.2f} kg")
            st.write(f"- Valor: {valor_y2:,.2f} EUR")
            st.write(f"- Registros: {len(d2)}")
            
            if qtd_y1 > 0:
                st.write(f"Variação Qtd: {((qtd_y2 - qtd_y1) / qtd_y1) * 100:.2f}%")
            if valor_y1 > 0:
                st.write(f"Variação Valor: {((valor_y2 - valor_y1) / valor_y1) * 100:.2f}%")
            
    else:
        st.warning("São necessários pelo menos 2 anos de dados para comparação.")

# ... (mantenha as outras páginas similares)

elif page == "Comparação Clientes":
    st.markdown("<h1>Comparação Clientes</h1>", unsafe_allow_html=True)
    
    # Tabela pivot com quantidades mensais
    temp = data.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    pivot = temp.groupby(['cliente','data'])['qtd'].sum().unstack(fill_value=0)
    pivot.columns = pivot.columns.strftime('%b/%y')
    
    # Tabela principal formatada
    st.markdown("### Quantidade Mensal por Cliente (kg)")
    
    # Formatar a tabela para exibição
    def formatar_numero_simples(x):
        return f"{x:,.0f}".replace(",", ".")
    
    pivot_formatado = pivot.applymap(formatar_numero_simples)
    st.dataframe(pivot_formatado, use_container_width=True)

# Exportar dados
if st.sidebar.button("Exportar Dados"):
    data_export = data.copy()
    csv = data_export.to_csv(index=False, sep=';', decimal=',')
    st.download_button(
        label="📥 Baixar CSV",
        data=csv,
        file_name="vendas_formatadas.csv",
        mime="text/csv"
    )

# Informações do dataset no sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("**Dataset Info:**")
    
    qtd_resumo = data['qtd'].sum()
    valor_resumo = data['v_liquido'].sum()
    
    st.markdown(f"- Período: {int(data['ano'].min())}-{int(data['ano'].max())}")
    st.markdown(f"- Total: {fmt_valor_simples(valor_resumo, 'EUR')}")
    st.markdown(f"- Clientes: {data['cliente'].nunique():,}")
    st.markdown(f"- Registros: {len(data):,}")
