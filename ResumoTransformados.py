import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Dashboard Compras - Análise Avançada", layout="wide", initial_sidebar_state="expanded")

# CSS personalizado para modernizar o visual
st.markdown("""
<style>
    .stMetric {
        background-color: #1E1E2E;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #7B68EE;
    }
    .stMetric label {
        font-weight: 600 !important;
        color: #7B68EE !important;
    }
    .stMetric div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    .css-1d391kg {
        background-color: #0E1117;
    }
    h1, h2, h3 {
        color: #7B68EE !important;
        border-bottom: 2px solid #7B68EE;
        padding-bottom: 10px;
    }
    .stButton button {
        background: linear-gradient(135deg, #7B68EE, #9370DB);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(123, 104, 238, 0.4);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E1E2E;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #7B68EE !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard de Compras - Análise Avançada")

# === CARREGAR DADOS CORRIGIDO ===
@st.cache_data
def load_data():
    try:
        # Lendo diretamente do conteúdo do arquivo fornecido
        df_raw = pd.read_excel("ResumoTR.xlsx")
        
        st.sidebar.write("### 🔍 Debug - Estrutura do Arquivo")
        st.sidebar.write(f"**Total de colunas:** {len(df_raw.columns)}")
        st.sidebar.write(f"**Total de linhas:** {len(df_raw)}")
        
        # Renomear colunas para padrão (baseado no arquivo fornecido)
        df = pd.DataFrame()
        
        # Mapeamento das colunas baseado no arquivo fornecido
        column_mapping = {
            'Data': 'Data',
            'Nome': 'Cliente',
            'Artigo': 'Artigo',
            'Quantidade': 'Quantidade',
            'V Líquido': 'Valor',
            'Comercial': 'Comercial',
            'Mês': 'MesNome',
            'Ano': 'Ano'
        }
        
        # Verificar e mapear colunas
        for new_col, possible_names in column_mapping.items():
            if possible_names in df_raw.columns:
                df[new_col] = df_raw[possible_names]
            else:
                # Tentar encontrar por similaridade
                for col in df_raw.columns:
                    if str(col).lower().replace(' ', '') == str(possible_names).lower().replace(' ', ''):
                        df[new_col] = df_raw[col]
                        break
                else:
                    st.sidebar.warning(f"⚠️ Coluna '{possible_names}' não encontrada")
        
        # Se não encontrou todas as colunas, usar as do arquivo
        if df.empty or len(df.columns) < 3:
            df = df_raw.copy()
            # Renomear colunas automaticamente
            rename_dict = {}
            for col in df.columns:
                col_lower = str(col).lower()
                if 'data' in col_lower:
                    rename_dict[col] = 'Data'
                elif any(x in col_lower for x in ['nome', 'entidade', 'cliente']):
                    rename_dict[col] = 'Cliente'
                elif 'artigo' in col_lower:
                    rename_dict[col] = 'Artigo'
                elif 'quantidade' in col_lower or 'qtd' in col_lower:
                    rename_dict[col] = 'Quantidade'
                elif any(x in col_lower for x in ['valor', 'vliquido', 'v líquido', 'v_líquido']):
                    rename_dict[col] = 'Valor'
                elif 'comercial' in col_lower:
                    rename_dict[col] = 'Comercial'
            
            df = df.rename(columns=rename_dict)
        
        # Converter Data
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        else:
            # Tentar encontrar coluna de data
            for col in df.columns:
                try:
                    temp = pd.to_datetime(df[col], errors='coerce')
                    if temp.notna().sum() > len(df) * 0.3:
                        df['Data'] = temp
                        break
                except:
                    continue
        
        # Garantir que temos as colunas essenciais
        essential_cols = ['Data', 'Cliente', 'Artigo', 'Quantidade', 'Valor']
        for col in essential_cols:
            if col not in df.columns:
                if col == 'Quantidade':
                    df[col] = 1
                elif col == 'Valor':
                    df[col] = 0
                else:
                    df[col] = f'{col} Desconhecido'
        
        # Adicionar Comercial se não existir
        if 'Comercial' not in df.columns:
            df['Comercial'] = 'Comercial Desconhecido'
        
        # Limpeza dos dados
        df['Cliente'] = df['Cliente'].fillna('Cliente Desconhecido').astype(str).str.strip()
        df['Artigo'] = df['Artigo'].fillna('Artigo Desconhecido').astype(str).str.strip()
        df['Comercial'] = df['Comercial'].fillna('Comercial Desconhecido').astype(str).str.strip()
        df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce').fillna(1)
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
        
        # Remover linhas com valores inválidos
        df = df[df['Data'].notna()].copy()
        df = df[df['Quantidade'] > 0].copy()
        df = df[df['Valor'] > 0].copy()
        
        # Criar colunas de tempo
        df['Ano'] = df['Data'].dt.year
        df['Mes'] = df['Data'].dt.month
        df['MesNumero'] = df['Data'].dt.month
        df['Dia'] = df['Data'].dt.day
        df['MesNome'] = df['Data'].dt.strftime("%b")
        df['Data_Str'] = df['Data'].dt.strftime("%Y-%m-%d")
        df['AnoMes'] = df['Data'].dt.strftime("%Y-%m")
        df['DiaSemana'] = df['Data'].dt.strftime("%A")
        
        st.sidebar.success("✅ Dados carregados com sucesso!")
        st.sidebar.write(f"**Período:** {df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}")
        st.sidebar.write(f"**Registros:** {len(df):,}")
        st.sidebar.write(f"**Clientes:** {df['Cliente'].nunique()}")
        st.sidebar.write(f"**Artigos:** {df['Artigo'].nunique()}")
        
        return df
        
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao carregar dados: {str(e)}")
        # Criar dados de exemplo se houver erro
        np.random.seed(42)
        n = 1000
        dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
        random_dates = np.random.choice(dates, n)
        
        df = pd.DataFrame({
            "Data": random_dates,
            "Cliente": np.random.choice([
                "Empresa A", "Empresa B", "Cliente C", "Distribuidor D",
                "Fornecedor E", "Parceiro F", "Cliente G", "Empresa H",
                "Grupo I", "Sociedade J", "Firma K", "Cliente L"
            ], n),
            "Artigo": np.random.choice([
                "Suíno Bucho Cozido", "Chouriço Crioulo 1Kg", "Filete Afiambrado",
                "Chourição", "Chouriço Colorau Ne", "Fiambre Perna Mini",
                "Bacon Inteiro Extra", "Cabeça Fumada", "Mortadela",
                "Linguiça Pares", "Salpicão", "Morcela"
            ], n),
            "Quantidade": np.random.randint(1, 100, n),
            "Valor": np.random.uniform(10, 1000, n),
            "Comercial": np.random.choice([
                "Joana Reis", "Pedro Fonseca", "Ricardo G.Silva",
                "Bruno Araujo", "Renato Ferreira", "Paulo Costa"
            ], n)
        })
        
        df["Ano"] = df["Data"].dt.year
        df["Mes"] = df["Data"].dt.month
        df["MesNumero"] = df["Data"].dt.month
        df["MesNome"] = df["Data"].dt.strftime("%b")
        df["Dia"] = df["Data"].dt.day
        df["Data_Str"] = df["Data"].dt.strftime("%Y-%m-%d")
        df["AnoMes"] = df["Data"].dt.strftime("%Y-%m")
        
        return df

# Carregar dados
df = load_data()

# === FILTROS INTERATIVOS MODERNOS ===
st.sidebar.header("🎛️ Filtros Interativos")

# Adicionar logo/header no sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Período")

# Filtro de período
if len(df) > 0:
    min_date = df['Data'].min().date()
    max_date = df['Data'].max().date()
    
    date_range = st.sidebar.date_input(
        "Selecionar período:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df['Data'].dt.date >= start_date) & (df['Data'].dt.date <= end_date)].copy()

# Filtro de Ano
st.sidebar.markdown("### 📅 Ano")
anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)
anos_selecionados = st.sidebar.multiselect(
    "Selecionar anos:",
    options=anos_disponiveis,
    default=anos_disponiveis,
    key="filtro_anos"
)

if anos_selecionados:
    df = df[df["Ano"].isin(anos_selecionados)].copy()

# Filtro de Mês
st.sidebar.markdown("### 📆 Mês")
meses_nomes = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

meses_disponiveis = sorted(df["MesNumero"].unique())
meses_nomes_disponiveis = [meses_nomes[m] for m in meses_disponiveis]

meses_selecionados_nomes = st.sidebar.multiselect(
    "Selecionar meses:",
    options=meses_nomes_disponiveis,
    default=meses_nomes_disponiveis,
    key="filtro_meses"
)

if meses_selecionados_nomes:
    nomes_para_meses = {v: k for k, v in meses_nomes.items()}
    meses_selecionados = [nomes_para_meses[nome] for nome in meses_selecionados_nomes]
    df = df[df["MesNumero"].isin(meses_selecionados)].copy()

# Filtro de Comercial
st.sidebar.markdown("### 👨‍💼 Comercial")
comerciais_disponiveis = sorted(df["Comercial"].unique())
comerciais_selecionados = st.sidebar.multiselect(
    "Selecionar comerciais:",
    options=comerciais_disponiveis,
    default=comerciais_disponiveis,
    key="filtro_comerciais"
)

if comerciais_selecionados:
    df = df[df["Comercial"].isin(comerciais_selecionados)].copy()

# Filtro de Cliente
st.sidebar.markdown("### 🏢 Cliente")
clientes_disponiveis = sorted(df["Cliente"].unique())
clientes_selecionados = st.sidebar.multiselect(
    "Selecionar clientes:",
    options=clientes_disponiveis,
    default=clientes_disponiveis[:min(10, len(clientes_disponiveis))],
    key="filtro_clientes"
)

if clientes_selecionados:
    df = df[df["Cliente"].isin(clientes_selecionados)].copy()

# Filtro de Artigo
st.sidebar.markdown("### 📦 Artigo")
artigos_disponiveis = sorted(df["Artigo"].unique())
artigos_selecionados = st.sidebar.multiselect(
    "Selecionar artigos:",
    options=artigos_disponiveis,
    default=artigos_disponiveis[:min(10, len(artigos_disponiveis))],
    key="filtro_artigos"
)

if artigos_selecionados:
    df = df[df["Artigo"].isin(artigos_selecionados)].copy()

st.sidebar.markdown("---")
st.sidebar.success(f"**📊 Dados Filtrados:** {len(df):,} registros")

# === CÁLCULOS CORRIGIDOS ===
if not df.empty:
    # Cálculos principais CORRIGIDOS
    total_vendas_eur = float(df["Valor"].sum())
    total_quantidade = float(df["Quantidade"].sum())
    num_entidades = int(df["Cliente"].nunique())
    num_comerciais = int(df["Comercial"].nunique())
    num_artigos = int(df["Artigo"].nunique())
    num_transacoes = int(len(df))
    dias_com_vendas = int(df["Data_Str"].nunique())
    
    # Médias CORRIGIDAS
    ticket_medio = total_vendas_eur / num_transacoes if num_transacoes > 0 else 0
    preco_medio_unitario = total_vendas_eur / total_quantidade if total_quantidade > 0 else 0
    venda_media_transacao = total_vendas_eur / num_transacoes if num_transacoes > 0 else 0
    quantidade_media_transacao = total_quantidade / num_transacoes if num_transacoes > 0 else 0
    venda_media_dia = total_vendas_eur / dias_com_vendas if dias_com_vendas > 0 else 0
    
    # Ticket médio mensal
    vendas_por_mes = df.groupby("AnoMes")["Valor"].sum()
    ticket_medio_mensal = float(vendas_por_mes.mean()) if not vendas_por_mes.empty else 0
    
    # Ticket médio por comercial
    vendas_por_comercial = df.groupby("Comercial")["Valor"].sum()
    ticket_medio_comercial = float(vendas_por_comercial.mean()) if not vendas_por_comercial.empty else 0
    
    # === DASHBOARD COM TABS ===
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard Geral", 
        "🏆 Top Performers", 
        "📈 Evolução Temporal", 
        "👥 Análise Comercial",
        "📋 Dados Detalhados"
    ])
    
    with tab1:
        # KPIs PRINCIPAIS
        st.subheader("📊 KPIs Principais")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💰 Total Vendas",
                value=f"€{total_vendas_eur:,.2f}",
                delta=None
            )
            
        with col2:
            st.metric(
                label="📦 Quantidade Total",
                value=f"{total_quantidade:,.0f}",
                delta=None
            )
            
        with col3:
            st.metric(
                label="🏢 Clientes Ativos",
                value=f"{num_entidades}",
                delta=None
            )
            
        with col4:
            st.metric(
                label="📦 Artigos Vendidos",
                value=f"{num_artigos}",
                delta=None
            )
        
        st.divider()
        
        # MÉTRICAS DE PERFORMANCE
        st.subheader("📈 Métricas de Performance")
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric(
                label="🎫 Ticket Médio",
                value=f"€{ticket_medio:,.2f}",
                help="Valor médio por transação"
            )
            
        with col6:
            st.metric(
                label="🏷️ Preço Médio Unitário",
                value=f"€{preco_medio_unitario:,.2f}",
                help="Valor total ÷ Quantidade total"
            )
            
        with col7:
            st.metric(
                label="📅 Venda Média Diária",
                value=f"€{venda_media_dia:,.2f}",
                help="Média de vendas por dia útil"
            )
            
        with col8:
            st.metric(
                label="🔄 Transações/Dia",
                value=f"{num_transacoes/dias_com_vendas:.1f}" if dias_com_vendas > 0 else "0",
                help="Média de transações por dia"
            )
        
        st.divider()
        
        # VISÃO GERAL DAS VENDAS
        st.subheader("📊 Visão Geral das Vendas")
        
        col9, col10 = st.columns([2, 1])
        
        with col9:
            # Distribuição de vendas por mês
            vendas_mensais = df.groupby(["Ano", "MesNumero"]).agg({
                "Valor": "sum",
                "Quantidade": "sum"
            }).reset_index()
            
            if not vendas_mensais.empty:
                vendas_mensais["Periodo"] = vendas_mensais["Ano"].astype(str) + "-" + vendas_mensais["MesNumero"].astype(str).str.zfill(2)
                
                fig = px.bar(
                    vendas_mensais,
                    x="Periodo",
                    y="Valor",
                    title="Vendas Mensais (€)",
                    color_discrete_sequence=["#7B68EE"],
                    labels={"Valor": "Valor (€)", "Periodo": "Período"}
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="white"),
                    xaxis=dict(tickangle=45)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col10:
            # Cards de resumo
            st.metric(
                label="🗓️ Ticket Médio Mensal",
                value=f"€{ticket_medio_mensal:,.2f}"
            )
            
            st.metric(
                label="👤 Ticket Médio/Comercial",
                value=f"€{ticket_medio_comercial:,.2f}"
            )
            
            st.metric(
                label="📊 Transações Totais",
                value=f"{num_transacoes:,}"
            )
    
    with tab2:
        st.subheader("🏆 Top Performers")
        
        # TOP 10 CLIENTES
        col11, col12 = st.columns(2)
        
        with col11:
            top_clientes = df.groupby("Cliente").agg({
                "Valor": "sum",
                "Quantidade": "sum",
                "Data": "count"
            }).nlargest(10, "Valor")
            
            top_clientes.columns = ["Total Vendas (€)", "Quantidade Total", "Nº Transações"]
            
            fig_clientes = px.bar(
                top_clientes,
                x="Total Vendas (€)",
                y=top_clientes.index,
                orientation='h',
                title="Top 10 Clientes por Vendas",
                color="Total Vendas (€)",
                color_continuous_scale="Viridis"
            )
            fig_clientes.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig_clientes, use_container_width=True)
        
        with col12:
            # TOP 10 ARTIGOS
            top_artigos = df.groupby("Artigo").agg({
                "Valor": "sum",
                "Quantidade": "sum"
            }).nlargest(10, "Valor")
            
            fig_artigos = px.pie(
                top_artigos,
                values="Valor",
                names=top_artigos.index,
                title="Distribuição por Artigo (Top 10)",
                hole=0.4
            )
            fig_artigos.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            fig_artigos.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_artigos, use_container_width=True)
        
        st.divider()
        
        # DETALHES DOS TOPS
        col13, col14 = st.columns(2)
        
        with col13:
            st.markdown("### 📋 Top Clientes - Detalhes")
            top_clientes_detalhes = top_clientes.copy()
            top_clientes_detalhes["Ticket Médio"] = top_clientes_detalhes["Total Vendas (€)"] / top_clientes_detalhes["Nº Transações"]
            st.dataframe(
                top_clientes_detalhes.style.format({
                    "Total Vendas (€)": "€{:,.2f}",
                    "Quantidade Total": "{:,.0f}",
                    "Ticket Médio": "€{:,.2f}"
                }),
                use_container_width=True
            )
        
        with col14:
            st.markdown("### 📦 Top Artigos - Detalhes")
            top_artigos_detalhes = top_artigos.copy()
            top_artigos_detalhes["Preço Médio"] = top_artigos_detalhes["Valor"] / top_artigos_detalhes["Quantidade"]
            st.dataframe(
                top_artigos_detalhes.style.format({
                    "Valor": "€{:,.2f}",
                    "Quantidade": "{:,.0f}",
                    "Preço Médio": "€{:,.2f}"
                }),
                use_container_width=True
            )
    
    with tab3:
        st.subheader("📈 Evolução Temporal")
        
        # SELEÇÃO DE PERÍODO PARA ANÁLISE
        periodo_analise = st.selectbox(
            "Período de análise:",
            ["Diária", "Semanal", "Mensal", "Anual"],
            index=2
        )
        
        if periodo_analise == "Diária":
            df_periodo = df.groupby("Data_Str").agg({
                "Valor": "sum",
                "Quantidade": "sum"
            }).reset_index()
            df_periodo["Data_Str"] = pd.to_datetime(df_periodo["Data_Str"])
            df_periodo = df_periodo.sort_values("Data_Str")
            x_col = "Data_Str"
            title_suffix = "Diária"
            
        elif periodo_analise == "Semanal":
            df["Semana"] = df["Data"].dt.strftime("%Y-%U")
            df_periodo = df.groupby("Semana").agg({
                "Valor": "sum",
                "Quantidade": "sum"
            }).reset_index()
            x_col = "Semana"
            title_suffix = "Semanal"
            
        elif periodo_analise == "Mensal":
            df_periodo = df.groupby("AnoMes").agg({
                "Valor": "sum",
                "Quantidade": "sum"
            }).reset_index()
            x_col = "AnoMes"
            title_suffix = "Mensal"
            
        else:  # Anual
            df_periodo = df.groupby("Ano").agg({
                "Valor": "sum",
                "Quantidade": "sum"
            }).reset_index()
            x_col = "Ano"
            title_suffix = "Anual"
        
        # GRÁFICO DE LINHAS
        fig_evolucao = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_evolucao.add_trace(
            go.Scatter(
                x=df_periodo[x_col],
                y=df_periodo["Valor"],
                name="Valor (€)",
                line=dict(color="#7B68EE", width=3),
                mode="lines+markers"
            ),
            secondary_y=False
        )
        
        fig_evolucao.add_trace(
            go.Bar(
                x=df_periodo[x_col],
                y=df_periodo["Quantidade"],
                name="Quantidade",
                marker_color="#9370DB",
                opacity=0.7
            ),
            secondary_y=True
        )
        
        fig_evolucao.update_layout(
            title=f"Evolução {title_suffix} - Valor vs Quantidade",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            height=500
        )
        
        fig_evolucao.update_xaxes(title_text="Período")
        fig_evolucao.update_yaxes(title_text="Valor (€)", secondary_y=False)
        fig_evolucao.update_yaxes(title_text="Quantidade", secondary_y=True)
        
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        # ESTATÍSTICAS DE TENDÊNCIA
        st.subheader("📊 Estatísticas de Tendência")
        
        if len(df_periodo) > 1:
            crescimento_valor = ((df_periodo["Valor"].iloc[-1] / df_periodo["Valor"].iloc[0]) - 1) * 100
            crescimento_qtd = ((df_periodo["Quantidade"].iloc[-1] / df_periodo["Quantidade"].iloc[0]) - 1) * 100
            
            col15, col16, col17 = st.columns(3)
            
            with col15:
                st.metric(
                    label=f"Crescimento do Valor ({title_suffix})",
                    value=f"{crescimento_valor:+.1f}%",
                    delta=f"{crescimento_valor:+.1f}%"
                )
            
            with col16:
                st.metric(
                    label=f"Crescimento da Quantidade ({title_suffix})",
                    value=f"{crescimento_qtd:+.1f}%",
                    delta=f"{crescimento_qtd:+.1f}%"
                )
            
            with col17:
                st.metric(
                    label="Média Móvel (3 períodos)",
                    value=f"€{df_periodo['Valor'].tail(3).mean():,.2f}",
                    delta=None
                )
    
    with tab4:
        st.subheader("👥 Análise Comercial")
        
        # DESEMPENHO POR COMERCIAL
        desempenho_comercial = df.groupby("Comercial").agg({
            "Valor": ["sum", "mean", "count"],
            "Cliente": "nunique",
            "Quantidade": "sum"
        }).round(2)
        
        desempenho_comercial.columns = ["Total Vendas (€)", "Ticket Médio (€)", 
                                         "Nº Transações", "Clientes Únicos", "Quantidade Total"]
        desempenho_comercial = desempenho_comercial.sort_values("Total Vendas (€)", ascending=False)
        
        # GRÁFICO DE BARRAS
        fig_comercial = px.bar(
            desempenho_comercial.reset_index(),
            x="Comercial",
            y="Total Vendas (€)",
            title="Performance por Comercial",
            color="Total Vendas (€)",
            color_continuous_scale="Plasma"
        )
        fig_comercial.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis=dict(tickangle=45)
        )
        st.plotly_chart(fig_comercial, use_container_width=True)
        
        # MÉTRICAS POR COMERCIAL
        st.subheader("📊 Métricas por Comercial")
        
        col18, col19, col20 = st.columns(3)
        
        with col18:
            top_comercial = desempenho_comercial.iloc[0]
            st.metric(
                label="🏆 Top Comercial",
                value=desempenho_comercial.index[0],
                delta=f"€{top_comercial['Total Vendas (€)']:,.0f}"
            )
        
        with col19:
            avg_ticket_comercial = desempenho_comercial["Ticket Médio (€)"].mean()
            st.metric(
                label="🎫 Ticket Médio/Comercial",
                value=f"€{avg_ticket_comercial:,.2f}",
                delta=None
            )
        
        with col20:
            avg_clientes_comercial = desempenho_comercial["Clientes Únicos"].mean()
            st.metric(
                label="👥 Clientes/Comercial (média)",
                value=f"{avg_clientes_comercial:.1f}",
                delta=None
            )
        
        # TABELA DETALHADA
        st.subheader("📋 Detalhes por Comercial")
        st.dataframe(
            desempenho_comercial.style.format({
                "Total Vendas (€)": "€{:,.2f}",
                "Ticket Médio (€)": "€{:,.2f}",
                "Nº Transações": "{:,.0f}",
                "Clientes Únicos": "{:,.0f}",
                "Quantidade Total": "{:,.0f}"
            }).background_gradient(subset=["Total Vendas (€)"], cmap="Blues"),
            use_container_width=True,
            height=400
        )
    
    with tab5:
        st.subheader("📋 Dados Detalhados")
        
        # FILTROS ADICIONAIS PARA A TABELA
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            sort_by = st.selectbox(
                "Ordenar por:",
                ["Data", "Valor", "Quantidade", "Cliente", "Artigo"],
                index=0
            )
        
        with col_filtro2:
            sort_order = st.selectbox(
                "Ordem:",
                ["Ascendente", "Descendente"],
                index=1
            )
        
        # PREPARAR DADOS PARA EXIBIÇÃO
        df_display = df[["Data", "Cliente", "Artigo", "Quantidade", "Valor", "Comercial"]].copy()
        
        if sort_order == "Descendente":
            df_display = df_display.sort_values(sort_by, ascending=False)
        else:
            df_display = df_display.sort_values(sort_by, ascending=True)
        
        # EXIBIR TABELA
        st.dataframe(
            df_display.style.format({
                "Valor": "€{:,.2f}",
                "Quantidade": "{:,.0f}"
            }),
            use_container_width=True,
            height=600
        )
        
        # ESTATÍSTICAS DA TABELA
        st.subheader("📊 Estatísticas dos Dados Filtrados")
        
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        
        with col_stats1:
            st.metric("📈 Valor Médio", f"€{df_display['Valor'].mean():,.2f}")
        
        with col_stats2:
            st.metric("📊 Quantidade Média", f"{df_display['Quantidade'].mean():,.1f}")
        
        with col_stats3:
            st.metric("📅 Período", f"{len(df_display):,} registros")
    
    # === DOWNLOAD DE RELATÓRIOS ===
    st.divider()
    st.subheader("📥 Exportar Relatórios")
    
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    with col_dl1:
        # CSV dos dados filtrados
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Dados Filtrados (CSV)",
            data=csv_data,
            file_name=f"dados_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_dl2:
        # Relatório de KPIs
        output_kpis = io.BytesIO()
        with pd.ExcelWriter(output_kpis, engine='openpyxl') as writer:
            # Sheet de KPIs
            kpis_df = pd.DataFrame({
                "KPI": [
                    "Total Vendas (€)", "Total Quantidade", "Nº Clientes", "Nº Comerciais", "Nº Artigos",
                    "Ticket Médio (€)", "Ticket Médio Mensal (€)", "Ticket Médio/Comercial (€)",
                    "Preço Médio Unitário (€)", "Venda Média/Transação (€)",
                    "Quantidade Média/Transação", "Dias com Vendas", "Venda Média/Dia (€)", "Nº Transações"
                ],
                "Valor": [
                    total_vendas_eur, total_quantidade, num_entidades, num_comerciais, num_artigos,
                    ticket_medio, ticket_medio_mensal, ticket_medio_comercial,
                    preco_medio_unitario, venda_media_transacao,
                    quantidade_media_transacao, dias_com_vendas, venda_media_dia, num_transacoes
                ]
            })
            kpis_df.to_excel(writer, sheet_name='KPIs', index=False)
            
            # Sheet de top clientes
            top_clientes.to_excel(writer, sheet_name='Top_Clientes')
            
            # Sheet de top artigos
            top_artigos.to_excel(writer, sheet_name='Top_Artigos')
            
            # Sheet de desempenho comercial
            desempenho_comercial.to_excel(writer, sheet_name='Desempenho_Comercial')
        
        excel_kpis_data = output_kpis.getvalue()
        
        st.download_button(
            label="📈 Relatório de KPIs (Excel)",
            data=excel_kpis_data,
            file_name=f"relatorio_kpis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col_dl3:
        # Relatório completo
        output_completo = io.BytesIO()
        with pd.ExcelWriter(output_completo, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Dados_Completos', index=False)
            
            # Adicionar todas as análises
            kpis_df.to_excel(writer, sheet_name='KPIs', index=False)
            top_clientes.to_excel(writer, sheet_name='Top_Clientes')
            top_artigos.to_excel(writer, sheet_name='Top_Artigos')
            desempenho_comercial.to_excel(writer, sheet_name='Desempenho_Comercial')
            
            # Adicionar vendas mensais
            vendas_mensais.to_excel(writer, sheet_name='Vendas_Mensais', index=False)
        
        excel_completo_data = output_completo.getvalue()
        
        st.download_button(
            label="📋 Relatório Completo (Excel)",
            data=excel_completo_data,
            file_name=f"relatorio_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

else:
    st.warning("⚠️ Não há dados disponíveis para análise. Ajuste os filtros.")

# === FOOTER ===
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>📊 <strong>Dashboard de Compras - Análise Avançada</strong> | Desenvolvido com Streamlit</p>
    <p>Última atualização: {}</p>
</div>
""".format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)
