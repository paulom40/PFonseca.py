import pandas as pd
import streamlit as st
import plotly.express as px
import io
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ====================== CONFIGURAÇÃO ======================
st.set_page_config(
    page_title="Dashboard Compras - Premium",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="chart_with_upwards_trend"
)

# ====================== CSS ======================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102,126,234,0.3);
    }
    .stMetric {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
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
    <h1>DASHBOARD DE COMPRAS</h1>
    <p>Análise em Tempo Real • Filtros Dinâmicos • KPIs Atualizados Instantaneamente</p>
</div>
""", unsafe_allow_html=True)

# ====================== CARREGAR DADOS ======================
@st.cache_data(show_spinner="Carregando ResumoTR.xlsx...")
def load_data():
    try:
        df = pd.read_excel("ResumoTR.xlsx")
        
        # Padronizar colunas
        col_map = {
            'entidade': 'Entidade', 'nome': 'Nome', 'artigo': 'Artigo',
            'quantidade': 'Quantidade', 'v líquido': 'V Líquido', 'v liquido': 'V Líquido',
            'pm': 'PM', 'data': 'Data', 'comercial': 'Comercial'
        }
        df.columns = [col_map.get(c.lower().strip(), c) for c in df.columns]
        
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df = df.dropna(subset=['Data']).copy()
        
        df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce').fillna(0)
        df['V Líquido'] = pd.to_numeric(df['V Líquido'], errors='coerce').fillna(0)
        df = df[(df['Quantidade'] > 0) & (df['V Líquido'] > 0)].copy()
        
        df['Ano'] = df['Data'].dt.year
        df['Mes_Numero'] = df['Data'].dt.month
        df['Mês'] = df['Data'].dt.strftime('%B')
        df['AnoMes'] = df['Data'].dt.strftime('%Y-%m')
        
        return df.sort_values('Data').reset_index(drop=True)
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return pd.DataFrame()

df_original = load_data()
if df_original.empty:
    st.stop()

# ====================== SIDEBAR - FILTROS DINÂMICOS ======================
st.sidebar.markdown("### FILTROS DINÂMICOS")

df_filt = df_original.copy()

# --- ANO ---
anos = sorted(df_filt['Ano'].unique(), reverse=True)
ano_sel = st.sidebar.multiselect("Ano", options=anos, default=anos[:2])
if ano_sel:
    df_filt = df_filt[df_filt['Ano'].isin(ano_sel)]

# --- MÊS ---
if not df_filt.empty:
    meses_num = sorted(df_filt['Mes_Numero'].unique())
    meses_nome = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                   "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    meses_opcoes = [meses_nome[m-1] for m in meses_num]
    mes_sel = st.sidebar.multiselect("Mês", options=mes_opcoes, default=mes_opcoes[-3:])
    meses_sel_num = [meses_nome.index(m)+1 for m in mes_sel]
    if meses_sel_num:
        df_filt = df_filt[df_filt['Mes_Numero'].isin(meses_sel_num)]

# --- COMERCIAL ---
if not df_filt.empty:
    comerciais = sorted(df_filt['Comercial'].dropna().unique())
    com_sel = st.sidebar.multiselect("Comercial", options=comerciais, default=comerciais[:3] if len(comerciais)>=3 else comerciais)
    if com_sel:
        df_filt = df_filt[df_filt['Comercial'].isin(com_sel)]

# --- CLIENTE ---
if not df_filt.empty:
    clientes = sorted(df_filt['Nome'].dropna().unique())
    cli_sel = st.sidebar.multiselect("Cliente", options=clientes, default=clientes[:5] if len(clientes)>=5 else clientes)
    if cli_sel:
        df_filt = df_filt[df_filt['Nome'].isin(cli_sel)]

# --- PRODUTO ---
if not df_filt.empty:
    produtos = sorted(df_filt['Artigo'].dropna().unique())
    prod_sel = st.sidebar.multiselect("Produto", options=produtos, default=produtos[:10] if len(produtos)>=10 else produtos)
    if prod_sel:
        df_filt = df_filt[df_filt['Artigo'].isin(prod_sel)]

# ====================== KPIs ATUALIZADOS EM TEMPO REAL ======================
def calcular_kpis(df):
    if df.empty:
        return {k: 0 for k in ["total_vendas","qtd","clientes","produtos","trans","ticket","venda_dia","valor_unidade","periodo"]}
    total = df["V Líquido"].sum()
    qtd = df["Quantidade"].sum()
    dias = df["Data"].dt.date.nunique()
    return {
        "total_vendas": total,
        "qtd": qtd,
        "clientes": df["Nome"].nunique(),
        "produtos": df["Artigo"].nunique(),
        "trans": len(df),
        "ticket": total / len(df) if len(df)>0 else 0,
        "venda_dia": total / dias if dias>0 else 0,
        "valor_unidade": total / qtd if qtd>0 else 0,
        "periodo": f"{df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}"
    }

kpis = calcular_kpis(df_filt)

# ====================== DASHBOARD ======================
tab1, tab2, tab3, tab4 = st.tabs(["KPIs PRINCIPAIS", "EVOLUÇÃO", "TOP 10", "DADOS"])

with tab1:
    st.subheader("KPIs em Tempo Real")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Vendas", f"€{kpis['total_vendas']:,.0f}")
    c2.metric("Quantidade Total", f"{kpis['qtd']:,.0f}")
    c3.metric("Clientes Únicos", kpis['clientes'])
    c4.metric("Produtos Vendidos", kpis['produtos'])
    c5.metric("Transações", f"{kpis['trans']:,}")
    
    st.divider()
    
    c6, c7, c8 = st.columns(3)
    c6.metric("Ticket Médio", f"€{kpis['ticket']:,.0f}")
    c7.metric("Venda Média/Dia", f"€{kpis['venda_dia']:,.0f}")
    c8.metric("Valor Médio/Unidade", f"€{kpis['valor_unidade']:,.2f}")
    
    st.info(f"**Período:** {kpis['periodo']}")

with tab2:
    st.subheader("Evolução Mensal")
    if not df_filt.empty:
        mensal = df_filt.groupby('AnoMes')['V Líquido'].sum().reset_index()
        fig = px.line(mensal, x='AnoMes', y='V Líquido', markers=True, title="Vendas por Mês")
        fig.add_bar(x=mensal['AnoMes'], y=mensal['V Líquido'], name="Vendas")
        fig.update_layout(xaxis_title="", yaxis_title="Valor (€)", height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado com os filtros atuais")

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Clientes")
        if not df_filt.empty:
            topc = df_filt.groupby('Nome')['V Líquido'].sum().nlargest(10)
            figc = px.bar(x=topc.values, y=topc.index, orientation='h', color=topc.values, color_continuous_scale='Viridis')
            figc.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(figc, use_container_width=True)
    
    with col2:
        st.subheader("Top 10 Produtos")
        if not df_filt.empty:
            topp = df_filt.groupby('Artigo')['V Líquido'].sum().nlargest(10)
            figp = px.bar(x=topp.values, y=topp.index, orientation='h', color=topp.values, color_continuous_scale='Plasma')
            st.plotly_chart(figp, use_container_width=True)

with tab4:
    st.subheader("Tabela de Dados")
    cols = ['Data','Nome','Artigo','Quantidade','V Líquido','PM','Comercial']
    display_df = df_filt[cols].copy()
    display_df['Data'] = display_df['Data'].dt.strftime('%d/%m/%Y')
    
    st.dataframe(display_df.style.format({'V Líquido': '€{:,.2f}', 'PM': '€{:,.2f}'}), 
                  use_container_width=True, height=600)

    st.subheader("Exportar")
    col1, col2 = st.columns(2)
    csv = df_filt.to_csv(index=False).encode()
    col1.download_button("CSV", data=csv, file_name="dados.csv", mime="text/csv")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_filt.to_excel(writer, sheet_name='Dados', index=False)
        pd.DataFrame([kpis]).to_excel(writer, sheet_name='KPIs')
    col2.download_button("Excel + KPIs", data=buffer.getvalue(), file_name="relatorio.xlsx",
                          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ====================== FOOTER ======================
st.markdown("---")
st.markdown(f"<small style='text-align:center;display:block;color:#666'>Dashboard atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</small>", unsafe_allow_html=True)
