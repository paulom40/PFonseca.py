import pandas as pd
import streamlit as st
import plotly.express as px
import io
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ====================== CONFIGURAÇÃO DA PÁGINA ======================
st.set_page_config(
    page_title="Dashboard Compras - Análise Premium",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="chart_with_upwards_trend"
)

# ====================== CSS PREMIUM ======================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    .stMetric {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    [data-testid="stSidebar"] { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); }
    .sidebar-section {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ====================== HEADER ======================
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size:2.8rem;">DASHBOARD DE COMPRAS</h1>
    <p style="margin:5px 0 0 0; opacity:0.9; font-size:1.2rem;">Análise Avançada • KPIs em Tempo Real</p>
</div>
""", unsafe_allow_html=True)

# ====================== CARREGAR DADOS ======================
@st.cache_data(show_spinner="Carregando dados...")
def load_data():
    try:
        df = pd.read_excel("ResumoTR.xlsx")

        # Padronizar nomes de colunas
        mapa = {'entidade':'Entidade', 'nome':'Nome', 'artigo':'Artigo', 'quantidade':'Quantidade',
                'v líquido':'V Líquido', 'v liquido':'V Líquido', 'pm':'PM', 'data':'Data',
                'comercial':'Comercial', 'mês':'Mês', 'ano':'Ano'}
        df.columns = [next((v for k,v in mapa.items() if k in c.lower()), c) for c in df.columns]

        essenciais = ['Nome', 'Artigo', 'Quantidade', 'V Líquido', 'Data']
        for col in essenciais:
            if col not in df.columns:
                st.error(f"Coluna obrigatória não encontrada: {col}")
                st.stop()

        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df = df.dropna(subset=['Data']).copy()

        df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce').fillna(0)
        df['V Líquido'] = pd.to_numeric(df['V Líquido'], errors='coerce').fillna(0)

        df = df[(df['Quantidade'] > 0) & (df['V Líquido'] > 0)].copy()

        df['Ano'] = df['Data'].dt.year
        df['Mes_Numero'] = df['Data'].dt.month
        df['Mês'] = df['Data'].dt.strftime('%B')
        df['AnoMes'] = df['Data'].dt.strftime('%Y-%m')
        df['Trimestre'] = df['Data'].dt.quarter

        return df.sort_values('Data').reset_index(drop=True)

    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# ====================== SIDEBAR - FILTROS CORRIGIDOS ======================
st.sidebar.markdown("""
<div style="text-align:center;padding:1rem;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;color:white;margin-bottom:1rem;">
    <h3 style="margin:0;">FILTROS DINÂMICOS</h3>
</div>
""", unsafe_allow_html=True)

df_temp = df.copy()

def secao(titulo):
    st.sidebar.markdown(f"""
    <div class="sidebar-section">
        <h4 style="margin:0 0 10px 0;color:#2c3e50;border-bottom:2px solid #667eea;padding-bottom:5px;">{titulo}</h4>
    </div>
    """, unsafe_allow_html=True)

# 1. ANO
secao("ANO")
anos = sorted(df['Ano'].unique(), reverse=True)
todos_anos = st.sidebar.checkbox("Todos os anos", value=True, key="chk_ano")
anos_sel = anos if todos_anos else st.sidebar.multiselect("Selecione os anos", anos, default=anos[:2], key="sel_ano")
if anos_sel:
    df_temp = df_temp[df_temp['Ano'].isin(anos_sel)]

# 2. MÊS
secao("MÊS")
if df_temp.empty:
    st.sidebar.info("Selecione um ano primeiro")
else:
    meses_num = sorted(df_temp['Mes_Numero'].unique())
    meses_nomes = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    opcoes = [meses_nomes[i-1] for i in meses_num]
    todos_meses = st.sidebar.checkbox("Todos os meses", value=True, key="chk_mes")
    meses_sel_nome = opcoes if todos_meses else st.sidebar.multiselect("Mês", opcoes, default=opcoes[-3:], key="sel_mes")
    meses_sel = [meses_nomes.index(m) + 1 for m in meses_sel_nome]
    if meses_sel:
        df_temp = df_temp[df_temp['Mes_Numero'].isin(meses_sel)]

# 3. COMERCIAL
secao("COMERCIAL")
if not df_temp.empty:
    coms = sorted(df_temp['Comercial'].dropna().unique())
    todos_com = st.sidebar.checkbox("Todos comerciais", value=True, key="chk_com")
    com_sel = coms if todos_com else st.sidebar.multiselect("Comercial", coms, default=coms[:3] if len(coms)>=3 else coms, key="sel_com")
    if com_sel:
        df_temp = df_temp[df_temp['Comercial'].isin(com_sel)]  # Corrigido aqui!

# 4. CLIENTE
secao("CLIENTE")
if not df_temp.empty:
    st.sidebar.info("Aplique filtros anteriores")
else:
    clientes = sorted(df_temp['Nome'].dropna().unique())
    todos_cli = st.sidebar.checkbox("Todos clientes", value=len(clientes)<=30, key="chk_cli")
    cli_sel = clientes if todos_cli else st.sidebar.multiselect("Cliente", clientes, default=clientes[:5], key="sel_cli")
    if cli_sel:
        df_temp = df_temp[df_temp['Nome'].isin(cli_sel)]

# 5. PRODUTO
secao("PRODUTO")
if not df_temp.empty:
    produtos = sorted(df_temp['Artigo'].dropna().unique())
    todos_prod = st.sidebar.checkbox("Todos produtos", value=True, key="chk_prod")
    prod_sel = produtos if todos_prod else st.sidebar.multiselect("Produto", produtos, default=produtos[:10] if len(produtos)>10 else produtos, key="sel_prod")
    if prod_sel:
        df_temp = df_temp[df_temp['Artigo'].isin(prod_sel)]

# BOTÕES DE AÇÃO
st.sidebar.markdown("---")
col1, col2 = st.sidebar.columns(2)
if col1.button("APLICAR FILTROS", type="primary", use_container_width=True):
    st.session_state.df_filtrado = df_temp.copy()
    st.success("Filtros aplicados com sucesso!")
if col2.button("LIMPAR TUDO", use_container_width=True):
    for key in list(st.session_state.keys()):
        if key.startswith(("chk_", "sel_ano", "sel_mes", "sel_com", "sel_cli", "sel_prod")):
            if key in st.session_state:
                del st.session_state[key]
    st.session_state.df_filtrado = df.copy()
    st.rerun()

# Dados finais filtrados
df_filtrado = st.session_state.get("df_filtrado", df.copy())

# Resumo na sidebar
st.sidebar.markdown("**RESUMO**")
st.sidebar.write(f"**Registros:** {len(df_filtrado):,}")
st.sidebar.write(f"**Período:** {df_filtrado['Data'].min().strftime('%d/%m/%Y')} → {df_filtrado['Data'].max().strftime('%d/%m/%Y')}")

# ====================== KPIs ======================
def calcular_kpis(df):
    if df.empty:
        return {}
    total_vendas = df["V Líquido"].sum()
    total_qtd = df["Quantidade"].sum()
    return {
        "total_vendas": total_vendas,
        "total_qtd": total_qtd,
        "clientes": df["Nome"].nunique(),
        "produtos": df["Artigo"].nunique(),
        "transacoes": len(df),
        "ticket_medio": total_vendas / len(df) if len(df) > 0 else 0,
        "venda_dia": total_vendas / df["Data"].dt.date.nunique() if df["Data"].dt.date.nunique() > 0 else 0,
        "valor_por_unidade": total_vendas / total_qtd if total_qtd > 0 else 0,
        "periodo": f"{df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}"
    }

kpis = calcular_kpis(df_filtrado)

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["KPIs PRINCIPAIS", "EVOLUÇÃO TEMPORAL", "TOP 10", "DADOS & EXPORT"])

with tab1:
    st.subheader("Principais Indicadores de Desempenho")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Vendas", f"€{kpis['total_vendas']:,.0f}")
    c2.metric("Quantidade Total", f"{kpis['total_qtd']:,.0f}")
    c3.metric("Clientes Únicos", kpis['clientes'])
    c4.metric("Produtos Vendidos", kpis['produtos'])
    c5.metric("Transações", f"{kpis['transacoes']:,}")
    
    st.divider()
    c6, c7, c8 = st.columns(3)
    c6.metric("Ticket Médio", f"€{kpis['ticket_medio']:,.0f}")
    c7.metric("Venda Média/Dia", f"€{kpis['venda_dia']:,.0f}")
    c8.metric("Valor Médio/Unidade", f"€{kpis['valor_por_unidade']:,.2f}")
    
    st.info(f"**Período analisado:** {kpis['periodo']}")

with tab2:
    st.subheader("Evolução Mensal das Vendas")
    mensal = df_filtrado.groupby('AnoMes')['V Líquido'].sum().reset_index()
    fig = px.bar(mensal, x='AnoMes', y='V Líquido', title="Vendas por Mês",
                 color_discrete_sequence=['#667eea'])
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Clientes")
        top_clientes = df_filtrado.groupby('Nome')['V Líquido'].sum().nlargest(10)
        fig1 = px.bar(x=top_clientes.values, y=top_clientes.index, orientation='h',
                       color=top_clientes.values, color_continuous_scale='Viridis')
        fig1.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Top 10 Produtos")
        top_produtos = df_filtrado.groupby('Artigo')['V Líquido'].sum().nlargest(10)
        fig2 = px.bar(x=top_produtos.values, y=top_produtos.index, orientation='h',
                       color=top_produtos.values, color_continuous_scale='Plasma')
        st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.subheader("Tabela Detalhada")
    ordem = st.selectbox("Ordenar por", ['Data', 'V Líquido', 'Nome', 'Artigo', 'Quantidade'])
    crescente = st.checkbox("Ordem crescente", value=False)
    limite = st.slider("Número de linhas", 10, 1000, 100, 50)

    tabela = df_filtrado[['Data', 'Nome', 'Artigo', 'Quantidade', 'V Líquido', 'PM', 'Comercial']] \
        .sort_values(by=ordem, ascending=crescente).head(limite)

    st.dataframe(tabela.style.format({'V Líquido': '€{:,.2f}', 'PM': '€{:,.2f}'}), 
                 use_container_width=True, height=600)

    st.subheader("Exportar Dados")
    col_a, col_b = st.columns(2)

    csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
    col_a.download_button(
        label="Baixar CSV Completo",
        data=csv_data,
        file_name=f"vendas_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_filtrado.to_excel(writer, sheet_name='Dados', index=False)
        pd.DataFrame([kpis]).to_excel(writer, sheet_name='KPIs', index=False)
    col_b.download_button(
        label="Baixar Excel + KPIs",
        data=buffer.getvalue(),
        file_name=f"relatorio_compras_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ====================== FOOTER ======================
st.markdown("---")
st.markdown(f"<small style='text-align:center; display:block; color:#666;'>Dashboard de Compras • Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</small>", unsafe_allow_html=True)
