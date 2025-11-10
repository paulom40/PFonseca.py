# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(page_title="Dashboard Comercial", page_icon="📊", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .main-header {font-size:2.8rem; color:#1f77b4; text-align:center; margin:2rem 0; font-weight:700;}
    .section-header {font-size:1.7rem; color:#2c3e50; margin:2rem 0 1rem; padding-bottom:0.5rem;
                     border-bottom:3px solid #3498db; font-weight:600;}
    .metric-card {background-color:#f8f9fa; padding:1rem; border-radius:10px; text-align:center;}
    .alert-box {background-color:#fff3cd; padding:1rem; border-radius:8px; border-left:4px solid #ffc107; margin:1rem 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>📊 Dashboard Comercial</h1>", unsafe_allow_html=True)

# --- Inicializar Session State ---
if 'df' not in st.session_state:
    st.session_state.df = None

# --- Funções de Carregamento ---
def carregar_excel_com_opcoes(uploaded_file):
    """Tenta carregar Excel com diferentes opções"""
    try:
        # Primeiro tenta a primeira sheet
        df = pd.read_excel(uploaded_file, sheet_name=0)
        return df
    except Exception as e1:
        try:
            # Se falhar, lista as sheets disponíveis
            xls = pd.ExcelFile(uploaded_file)
            st.warning(f"Erro na primeira sheet. Sheets disponíveis: {xls.sheet_names}")
            sheet = st.selectbox("Escolha a sheet:", xls.sheet_names)
            df = pd.read_excel(uploaded_file, sheet_name=sheet)
            return df
        except Exception as e2:
            st.error(f"Erro ao carregar: {str(e2)}")
            return None

def mapear_colunas(df):
    """Tenta identificar automaticamente as colunas relevantes"""
    colunas_lower = {col.lower().strip(): col for col in df.columns}
    
    # Mapeamento de possíveis nomes
    mapeamento = {
        'mes': ['mes', 'mês', 'month', 'mês'],
        'ano': ['ano', 'year', 'ano'],
        'cliente': ['cliente', 'client', 'customer', 'nome_cliente'],
        'qtd': ['qtd', 'quantidade', 'qty', 'volume', 'vendas']
    }
    
    colunas_encontradas = {}
    for chave, opcoes in mapeamento.items():
        for opcao in opcoes:
            if opcao in colunas_lower:
                colunas_encontradas[chave] = colunas_lower[opcao]
                break
    
    return colunas_encontradas

# --- Upload de Dados ---
with st.expander("📁 Carregar Dados (CSV/Excel)", expanded=True):
    tab_upload, tab_url = st.tabs(["📤 Upload Local", "🔗 URL do GitHub"])
    
    df_loaded = False
    
    with tab_upload:
        uploaded_file = st.file_uploader("Escolha um arquivo", type=["csv", "xlsx"])
        if uploaded_file:
            df_loaded = True
            df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    
    with tab_url:
        github_url = st.text_input("Cole o link do GitHub:", 
                                   value="https://github.com/paulom40/PFonseca.py/blob/main/VendasGeraisTranf.xlsx")
        
        if st.button("📥 Carregar do GitHub"):
            try:
                with st.spinner("Carregando ficheiro..."):
                    # Converter link /blob/ para /raw/
                    raw_url = github_url.replace("/blob/", "/raw/")
                    st.write(f"🔗 URL convertida: {raw_url}")
                    
                    if raw_url.endswith('.xlsx'):
                        df = pd.read_excel(raw_url)
                    else:
                        df = pd.read_csv(raw_url)
                    df_loaded = True
                    st.success("✅ Ficheiro carregado com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao carregar: {str(e)}")
                st.info("💡 O link será automaticamente convertido de /blob/ para /raw/")
                st.write(f"URL convertida: {github_url.replace('/blob/', '/raw/')}")
    
    if df_loaded:
        try:
            st.info(f"📊 Ficheiro carregado: {len(df)} linhas, {len(df.columns)} colunas")
            st.write("**Colunas disponíveis:**", list(df.columns))
            
            # Tentar mapear colunas automaticamente
            mapa = mapear_colunas(df)
            
            if len(mapa) < 4:
                st.warning("❌ Nem todas as colunas foram identificadas automaticamente")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    mes_col = st.selectbox("Coluna Mês:", df.columns, index=list(df.columns).index(mapa.get('mes', df.columns[0])) if 'mes' in mapa else 0)
                with col2:
                    ano_col = st.selectbox("Coluna Ano:", df.columns, index=list(df.columns).index(mapa.get('ano', df.columns[0])) if 'ano' in mapa else 1)
                with col3:
                    cliente_col = st.selectbox("Coluna Cliente:", df.columns, index=list(df.columns).index(mapa.get('cliente', df.columns[0])) if 'cliente' in mapa else 2)
                with col4:
                    qtd_col = st.selectbox("Coluna Qtd:", df.columns, index=list(df.columns).index(mapa.get('qtd', df.columns[0])) if 'qtd' in mapa else 3)
            else:
                mes_col = mapa['mes']
                ano_col = mapa['ano']
                cliente_col = mapa['cliente']
                qtd_col = mapa['qtd']
                st.success("✅ Colunas identificadas automaticamente!")
            
            # Renomear colunas para o padrão esperado
            df.rename(columns={
                mes_col: 'Mes',
                ano_col: 'Ano',
                cliente_col: 'Cliente',
                qtd_col: 'Qtd'
            }, inplace=True)
            
            st.session_state.df = df[['Mes', 'Ano', 'Cliente', 'Qtd']].copy()
            st.success(f"✅ Dados mapeados com sucesso!")
            
        except Exception as e:
            st.error(f"❌ Erro ao processar dados: {str(e)}")
            st.stop()
    else:
        st.info("📥 Carregue um arquivo ou use uma URL do GitHub para começar.")
        st.stop()

df = st.session_state.df.copy()

# --- Padronização de Mês/Ano ---
meses_map = {
    'jan':1,'fev':2,'mar':3,'abr':4,'mai':5,'jun':6,'jul':7,'ago':8,'set':9,'out':10,'nov':11,'dez':12,
    'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,'julho':7,'agosto':8,
    'setembro':9,'outubro':10,'novembro':11,'dezembro':12,
    '1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'11':11,'12':12
}

def norm_mes(x):
    try:
        x_str = str(x).lower().strip()
        x_clean = re.sub(r'\D', '', x_str)
        mes_num = meses_map.get(x_str, meses_map.get(x_clean, None))
        return f"{mes_num:02d}" if mes_num else None
    except:
        return None

def norm_ano(x):
    try:
        x_clean = re.sub(r'\D', '', str(x).strip())
        if len(x_clean) == 4:
            return x_clean
        elif len(x_clean) == 2:
            ano_int = int(x_clean)
            return f"20{x_clean}" if ano_int < 50 else f"19{x_clean}"
        return None
    except:
        return None

# Aplicar normalizações
df['Mes'] = df['Mes'].apply(norm_mes)
df['Ano'] = df['Ano'].apply(norm_ano)
df['Qtd'] = pd.to_numeric(df['Qtd'], errors='coerce')

# Remover linhas inválidas
rows_before = len(df)
df = df.dropna(subset=['Mes', 'Ano', 'Cliente', 'Qtd']).copy()
df = df[df['Qtd'] > 0].copy()

if len(df) == 0:
    st.error("❌ Nenhum dado válido após processamento")
    st.stop()

if len(df) < rows_before:
    st.warning(f"⚠️ {rows_before - len(df)} linhas removidas por dados inválidos")

df['Periodo'] = df['Ano'] + '-' + df['Mes']
df['Cliente'] = df['Cliente'].str.strip()

# --- Análise de Tendências ---
has_multiple_periods = df['Periodo'].nunique() >= 2

if not has_multiple_periods:
    st.warning("⚠️ São necessários pelo menos 2 períodos para análise de alertas.")
    subidas = descidas = inativos = pd.DataFrame()
else:
    agg = df.groupby(['Cliente', 'Periodo'])['Qtd'].sum().reset_index()
    periodos = sorted(agg['Periodo'].unique())
    atual, anterior = periodos[-1], periodos[-2]

    pivot = agg.pivot(index='Cliente', columns='Periodo', values='Qtd').fillna(0)
    pivot['Atual'] = pivot[atual]
    pivot['Anterior'] = pivot[anterior]
    pivot['Var_%'] = ((pivot['Atual'] - pivot['Anterior']) / pivot['Anterior'].replace(0, 1)) * 100

    subidas = pivot[pivot['Var_%'] > 20].copy()
    descidas = pivot[pivot['Var_%'] < -20].copy()
    inativos = pivot[(pivot['Anterior'] > 0) & (pivot['Atual'] == 0)].copy()

    subidas = subidas.sort_values('Var_%', ascending=False)[['Anterior', 'Atual', 'Var_%']].reset_index()
    descidas = descidas.sort_values('Var_%')[['Anterior', 'Atual', 'Var_%']].reset_index()
    inativos = inativos.sort_values('Anterior', ascending=False)[['Anterior', 'Atual']].reset_index()
    inativos['Var_%'] = -100

# --- Abas ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Resumo",
    "📈 Subidas",
    "📉 Descidas",
    "❌ Inativos",
    "📋 Dados Brutos"
])

# --- Aba 1: Resumo ---
with tab1:
    st.markdown("<div class='section-header'>Resumo Geral</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Clientes", df['Cliente'].nunique())
    with col2:
        st.metric("📅 Períodos", df['Periodo'].nunique())
    with col3:
        st.metric("📦 Volume Total", f"{df['Qtd'].sum():,.0f}")
    with col4:
        st.metric("🕐 Atualização", datetime.now().strftime("%d/%m/%Y %H:%M"))

    if has_multiple_periods:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📈 Subidas (>20%)", len(subidas), delta="+", delta_color="normal")
        with col2:
            st.metric("📉 Descidas (>20%)", len(descidas), delta="-", delta_color="inverse")
        with col3:
            st.metric("❌ Inativos", len(inativos), delta="-", delta_color="inverse")
        
        # Gráfico de evolução geral
        st.markdown("<div class='section-header'>Evolução Geral de Vendas</div>", unsafe_allow_html=True)
        evolucao = df.groupby('Periodo')['Qtd'].sum().reset_index()
        fig_evolucao = px.line(evolucao, x='Periodo', y='Qtd', markers=True,
                              title="Volume Total por Período",
                              labels={'Qtd': 'Volume', 'Periodo': 'Período'})
        fig_evolucao.update_traces(line=dict(color='#1f77b4', width=3), marker=dict(size=8))
        st.plotly_chart(fig_evolucao, use_container_width=True)

# --- Aba 2: Subidas ---
with tab2:
    st.markdown("<div class='section-header'>📈 Clientes com Subida Significativa (>20%)</div>", unsafe_allow_html=True)
    if not has_multiple_periods:
        st.info("ℹ️ Carregue dados com pelo menos 2 períodos.")
    elif subidas.empty:
        st.success("✅ Nenhum cliente com subida > 20%")
    else:
        st.dataframe(subidas.style.format({'Anterior': '{:.0f}', 'Atual': '{:.0f}', 'Var_%': '{:.1f}%'}),
                    use_container_width=True, hide_index=True)
        
        fig = px.bar(subidas.head(10), x='Var_%', y='Cliente', orientation='h',
                     title="🔝 Top 10 Maiores Subidas", color='Var_%',
                     color_continuous_scale='Greens', labels={'Var_%': 'Variação %', 'Cliente': ''})
        st.plotly_chart(fig, use_container_width=True)

# --- Aba 3: Descidas ---
with tab3:
    st.markdown("<div class='section-header'>📉 Clientes com Descida Significativa (>20%)</div>", unsafe_allow_html=True)
    if not has_multiple_periods:
        st.info("ℹ️ Carregue dados com pelo menos 2 períodos.")
    elif descidas.empty:
        st.success("✅ Nenhum cliente com descida > 20%")
    else:
        st.dataframe(descidas.style.format({'Anterior': '{:.0f}', 'Atual': '{:.0f}', 'Var_%': '{:.1f}%'}),
                    use_container_width=True, hide_index=True)
        
        fig = px.bar(descidas.head(10), x='Var_%', y='Cliente', orientation='h',
                     title="🔻 Top 10 Maiores Descidas", color='Var_%',
                     color_continuous_scale='Reds', labels={'Var_%': 'Variação %', 'Cliente': ''})
        st.plotly_chart(fig, use_container_width=True)

# --- Aba 4: Inativos ---
with tab4:
    st.markdown("<div class='section-header'>❌ Clientes que Pararam de Comprar</div>", unsafe_allow_html=True)
    if not has_multiple_periods:
        st.info("ℹ️ Carregue dados com pelo menos 2 períodos.")
    elif inativos.empty:
        st.success("✅ Nenhum cliente inativo")
    else:
        st.dataframe(inativos[['Cliente', 'Anterior', 'Var_%']].style.format({'Anterior': '{:.0f}', 'Var_%': '{:.0f}%'}),
                    use_container_width=True, hide_index=True)
        
        fig = px.bar(inativos.head(10), x='Anterior', y='Cliente', orientation='h',
                     title="💔 Top 10 Maiores Volumes Perdidos", color='Anterior',
                     color_continuous_scale='Oranges', labels={'Anterior': 'Volume Perdido', 'Cliente': ''})
        st.plotly_chart(fig, use_container_width=True)

# --- Aba 5: Dados Brutos ---
with tab5:
    st.markdown("<div class='section-header'>📋 Tabela de Dados Processados</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        cliente_filter = st.multiselect("Filtrar por Cliente:", sorted(df['Cliente'].unique()), key="cliente_filter")
    with col2:
        periodo_filter = st.multiselect("Filtrar por Período:", sorted(df['Periodo'].unique()), key="periodo_filter")
    
    df_filtered = df.copy()
    if cliente_filter:
        df_filtered = df_filtered[df_filtered['Cliente'].isin(cliente_filter)]
    if periodo_filter:
        df_filtered = df_filtered[df_filtered['Periodo'].isin(periodo_filter)]
    
    st.dataframe(df_filtered.sort_values('Periodo', ascending=False), use_container_width=True, hide_index=True)
    
    # Exportar dados
    csv = df_filtered.to_csv(index=False)
    st.download_button(label="📥 Baixar CSV", data=csv, file_name="dados_comerciais.csv", mime="text/csv")

# --- Footer ---
st.markdown("---")
st.caption(f"Dashboard atualizado em: {datetime.now():%d/%m/%Y %H:%M} | Portugal (WET) | Versão 2.0")
