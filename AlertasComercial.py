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
                               .str.replace(',', '.', regex=False)
                               .str.replace(r'(\.\d{2})\d+', r'\1', regex=True))
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
# FUNÇÕES DE FORMATAÇÃO COM 2 CASAS DECIMAIS
# =============================================
def fmt(x, u):
    """Formata números com 2 casas decimais e separador de milhares"""
    if pd.notna(x):
        # Formata com 2 casas decimais e separadores
        formatted = f"{x:,.2f} {u}"
        # Converte para formato brasileiro (ponto para milhar, vírgula para decimal)
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        return f"0,00 {u}"

def fmt_simple(x, u):
    """Formatação simples com 2 casas decimais (formato internacional)"""
    if pd.notna(x):
        return f"{x:,.2f} {u}"
    else:
        return f"0.00 {u}"

# =============================================
# PÁGINAS
# =============================================
if page == "Visão Geral":
    st.markdown("<h1>Visão Geral</h1>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        qtd_total = data['qtd'].sum()
        st.metric("Quantidade", fmt(qtd_total, "kg"))
    with c2: 
        valor_total = data['v_liquido'].sum()
        st.metric("Valor Total", fmt(valor_total, "EUR"))
    with c3: 
        st.metric("Clientes", f"{data['cliente'].nunique():,}")
    with c4: 
        st.metric("Comerciais", f"{data['comercial'].nunique():,}")

elif page == "KPIs":
    st.markdown("<h1>KPIs</h1>", unsafe_allow_html=True)
    metrica = st.selectbox("Métrica", ["Quantidade", "Valor"])
    grupo = st.selectbox("Agrupar", ["Mês", "Comercial", "Cliente"])
    col = 'qtd' if metrica == "Quantidade" else 'v_liquido'
    gcol = {'Mês':'mes', 'Comercial':'comercial', 'Cliente':'cliente'}[grupo]
    
    agg = data.groupby(gcol)[col].sum().reset_index().sort_values(col, ascending=False).head(10)
    
    # Formatar valores para exibição
    if grupo == "Mês": 
        agg['mes'] = agg['mes'].map({v:k for k,v in {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',
                                                    7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}.items()})
    
    # Adicionar coluna formatada para hover
    if metrica == "Quantidade":
        agg[f'{col}_formatado'] = agg[col].apply(lambda x: fmt(x, "kg"))
    else:
        agg[f'{col}_formatado'] = agg[col].apply(lambda x: fmt(x, "EUR"))
    
    fig = px.bar(agg, x=gcol, y=col, title=f"Top 10 {metrica} por {grupo}",
                 hover_data={f'{col}_formatado': True})
    fig.update_traces(hovertemplate=f'<b>{grupo}</b>: %{{x}}<br><b>{metrica}</b>: %{{customdata[0]}}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True)

elif page == "Tendências":
    st.markdown("<h1>Tendências</h1>", unsafe_allow_html=True)
    temp = data.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    serie = temp.groupby('data')['v_liquido'].sum().reset_index()
    
    # Formatar valores para hover
    serie['v_liquido_formatado'] = serie['v_liquido'].apply(lambda x: fmt(x, "EUR"))
    
    fig = px.line(serie, x='data', y='v_liquido', title="Evolução de Vendas",
                  hover_data={'v_liquido_formatado': True})
    fig.update_traces(hovertemplate='<b>Data</b>: %{x}<br><b>Valor</b>: %{customdata[0]}<extra></extra>')
    fig.update_yaxes(tickformat=",.2f")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Alertas":
    st.markdown("<h1>Alertas</h1>", unsafe_allow_html=True)
    temp = data.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    mensal = temp.groupby(pd.Grouper(key='data', freq='M'))[['qtd','v_liquido']].sum().reset_index()
    
    alertas_encontrados = False
    for i in range(1, len(mensal)):
        qtd_atual = mensal['qtd'].iloc[i]
        qtd_anterior = mensal['qtd'].iloc[i-1]
        if qtd_anterior > 0 and qtd_atual / qtd_anterior < 0.8:
            data_alerta = mensal['data'].iloc[i]
            st.error(f"🚨 Queda >20% em Qtd: {data_alerta.strftime('%b/%Y')} "
                    f"({fmt(qtd_anterior, 'kg')} → {fmt(qtd_atual, 'kg')})")
            alertas_encontrados = True
    
    if not alertas_encontrados:
        st.success("✅ Sem quedas críticas detectadas.")

elif page == "Clientes":
    st.markdown("<h1>Clientes</h1>", unsafe_allow_html=True)
    cli = st.selectbox("Cliente", ["Todos"] + sorted(data['cliente'].unique()))
    dfc = data if cli == "Todos" else data[data['cliente'] == cli]
    
    c1, c2 = st.columns(2)
    with c1: 
        qtd_cliente = dfc['qtd'].sum()
        st.metric("Quantidade Total", fmt(qtd_cliente, "kg"))
    with c2: 
        valor_cliente = dfc['v_liquido'].sum()
        st.metric("Valor Total", fmt(valor_cliente, "EUR"))
    
    # Formatar valores para o scatter plot
    dfc_plot = dfc.copy()
    dfc_plot['qtd_formatado'] = dfc_plot['qtd'].apply(lambda x: fmt(x, "kg"))
    dfc_plot['v_liquido_formatado'] = dfc_plot['v_liquido'].apply(lambda x: fmt(x, "EUR"))
    
    fig = px.scatter(dfc_plot, x='qtd', y='v_liquido', color='comercial',
                     hover_data={'qtd_formatado': True, 'v_liquido_formatado': True},
                     title=f"Relação Quantidade vs Valor - {cli if cli != 'Todos' else 'Todos Clientes'}")
    fig.update_traces(hovertemplate='<b>Qtd</b>: %{customdata[0]}<br><b>Valor</b>: %{customdata[1]}<br><b>Comercial</b>: %{marker.color}<extra></extra>')
    fig.update_xaxes(tickformat=",.2f", title="Quantidade (kg)")
    fig.update_yaxes(tickformat=",.2f", title="Valor Líquido (EUR)")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Comparação":
    st.markdown("<h1>Comparação</h1>", unsafe_allow_html=True)
    anos_disponiveis = sorted(data['ano'].unique())
    
    if len(anos_disponiveis) >= 2:
        a1, a2 = st.columns(2)
        with a1: 
            y1 = st.selectbox("Ano 1", anos_disponiveis)
        with a2: 
            # Seleciona o segundo ano mais recente por padrão
            default_idx = 1 if len(anos_disponiveis) > 1 else 0
            y2 = st.selectbox("Ano 2", anos_disponiveis, index=default_idx)
        
        d1 = data[data['ano'] == y1]
        d2 = data[data['ano'] == y2]
        
        # Métricas principais
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            qtd_y1 = d1['qtd'].sum()
            st.metric(f"Quantidade {y1}", fmt(qtd_y1, "kg"))
        with c2: 
            qtd_y2 = d2['qtd'].sum()
            st.metric(f"Quantidade {y2}", fmt(qtd_y2, "kg"))
        with c3: 
            valor_y1 = d1['v_liquido'].sum()
            st.metric(f"Valor {y1}", fmt(valor_y1, "EUR"))
        with c4: 
            valor_y2 = d2['v_liquido'].sum()
            st.metric(f"Valor {y2}", fmt(valor_y2, "EUR"))
        
        # Variação
        if qtd_y1 > 0:
            variacao_qtd = ((qtd_y2 - qtd_y1) / qtd_y1) * 100
            st.metric("Variação Quantidade", f"{variacao_qtd:+.2f}%")
        
        if valor_y1 > 0:
            variacao_valor = ((valor_y2 - valor_y1) / valor_y1) * 100
            st.metric("Variação Valor", f"{variacao_valor:+.2f}%")
            
    else:
        st.warning("São necessários pelo menos 2 anos de dados para comparação.")

elif page == "Comparação Clientes":
    st.markdown("<h1>Comparação Clientes</h1>", unsafe_allow_html=True)
    
    # Tabela pivot com quantidades mensais
    pivot = data.assign(data=pd.to_datetime(data['ano'].astype(str)+'-'+data['mes'].astype(str).str.zfill(2)+'-01'))\
                .groupby(['cliente','data'])['qtd'].sum().unstack(fill_value=0)
    pivot.columns = pivot.columns.strftime('%b/%y')
    
    # Formatar a tabela para exibição
    st.markdown("### Quantidade Mensal por Cliente (kg)")
    pivot_display = pivot.copy()
    pivot_display = pivot_display.map(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.dataframe(pivot_display, use_container_width=True)
    
    # Crescimento percentual
    st.markdown("### Crescimento Mensal (%)")
    cresc = pivot.pct_change(axis=1).mul(100).round(2)
    cresc_display = cresc.copy()
    cresc_display = cresc_display.map(lambda x: f"{x:+.2f}%")
    st.dataframe(cresc_display.style.applymap(
        lambda v: 'color: #16a34a' if float(v.strip('%')) > 0 else 'color: #dc2626' if float(v.strip('%')) < 0 else 'color: #666'
    ), use_container_width=True)
    
    # Alertas de clientes sem compra
    st.markdown("### Alertas - Clientes sem Compra")
    sem_compra = (pivot == 0).sum(axis=1)
    clientes_com_alerta = sem_compra[sem_compra > 0]
    
    if len(clientes_com_alerta) > 0:
        for cli, meses_sem_compra in clientes_com_alerta.items():
            st.error(f"**{cli}** sem compra em **{meses_sem_compra} mês(es)**")
    else:
        st.success("✅ Todos os clientes compraram em todos os meses!")
    
    # Gráfico de tendência dos top clientes
    st.markdown("### Top 10 Clientes - Evolução")
    if not pivot.empty:
        top_clientes = pivot.sum(axis=1).nlargest(10).index
        pivot_top = pivot.loc[top_clientes]
        
        # Preparar dados para o gráfico
        plot_data = pivot_top.T.reset_index()
        plot_data = plot_data.melt(id_vars=['index'], value_vars=top_clientes, 
                                  var_name='Cliente', value_name='Quantidade')
        
        fig = px.line(plot_data, x='index', y='Quantidade', color='Cliente',
                     title="Evolução dos Top 10 Clientes")
        fig.update_yaxes(tickformat=",.2f", title="Quantidade (kg)")
        fig.update_xaxes(title="Mês")
        st.plotly_chart(fig, use_container_width=True)

# Exportar dados
if st.sidebar.button("Exportar Dados"):
    # Garantir que os dados exportados tenham 2 casas decimais
    data_export = data.copy()
    if 'v_liquido' in data_export.columns:
        data_export['v_liquido'] = data_export['v_liquido'].round(2)
    
    csv = data_export.to_csv(index=False, decimal=',', sep=';')
    st.download_button(
        label="📥 Baixar CSV Formatado",
        data=csv,
        file_name="vendas_formatadas.csv",
        mime="text/csv"
    )

# Informações do dataset no sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown(f"**Dataset Info:**")
    st.markdown(f"- Período: {int(data['ano'].min())}-{int(data['ano'].max())}")
    st.markdown(f"- Total: {fmt(data['v_liquido'].sum(), 'EUR')}")
    st.markdown(f"- Clientes: {data['cliente'].nunique():,}")
