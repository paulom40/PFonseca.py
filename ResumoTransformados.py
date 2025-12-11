import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Dashboard Compras - KPIs + YoY", layout="wide")
st.title("Dashboard de Compras – KPIs + Análise Detalhada")

# === CARREGAR DADOS ===
@st.cache_data
def load_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"
        df_raw = pd.read_excel(url)
        
        # Verificar as colunas disponíveis
        st.sidebar.info(f"Colunas no arquivo: {df_raw.columns.tolist()}")
        
        # Criar dataframe com verificação robusta
        df = pd.DataFrame()
        
        # Verificar se há dados na coluna de data
        date_col = df_raw.iloc[:, 0]
        st.sidebar.info(f"Primeiras datas brutas: {date_col.head().tolist()}")
        
        # Tentar diferentes métodos de parsing de data
        try:
            df["Data"] = pd.to_datetime(date_col, errors='coerce')
            # Verificar se as datas foram parseadas corretamente
            valid_dates = df["Data"].notna().sum()
            st.sidebar.info(f"Datas válidas: {valid_dates}/{len(df)}")
        except:
            # Se falhar, tentar extrair ano e mês de outras formas
            df["Data"] = pd.NaT
        
        # Preencher colunas com fallbacks
        df["Cliente"] = df_raw.iloc[:, 1].fillna("").astype(str).str.strip()
        df["Artigo"] = df_raw.iloc[:, 2].fillna("").astype(str).str.strip()
        
        # Para quantidade, tentar várias colunas se necessário
        if len(df_raw.columns) > 3:
            df["Quantidade"] = pd.to_numeric(df_raw.iloc[:, 3], errors='coerce').fillna(0)
        else:
            df["Quantidade"] = 0
        
        # Para comercial
        if len(df_raw.columns) > 8:
            df["Comercial"] = df_raw.iloc[:, 8].fillna("").astype(str).str.strip()
        else:
            df["Comercial"] = "Desconhecido"
        
        # Remover linhas sem data válida
        initial_count = len(df)
        df = df[df["Data"].notna()].copy()
        
        # Se todas as datas forem 1970, criar um ano/mês fictício baseado no índice
        if len(df) > 0 and df["Data"].dt.year.nunique() == 1 and df["Data"].dt.year.iloc[0] == 1970:
            st.sidebar.warning("⚠️ Datas parecem estar no formato padrão (1970). Criando período baseado no índice.")
            
            # Criar datas sequenciais começando de hoje para trás
            base_date = datetime.now()
            df["Data"] = pd.date_range(end=base_date, periods=len(df), freq='D')
        
        # Adicionar colunas temporais
        df["Ano"] = df["Data"].dt.year
        df["Mes"] = df["Data"].dt.month
        df["MesNumero"] = df["Data"].dt.month
        df["MesNome"] = df["Data"].dt.strftime("%b")
        df["MesNomeCompleto"] = df["Data"].dt.strftime("%B")
        df["Dia"] = df["Data"].dt.day
        df["DiaSemana"] = df["Data"].dt.day_name()
        df["Semana"] = df["Data"].dt.isocalendar().week
        
        # Filtrar dados inválidos
        df = df[(df["Cliente"] != "") & (df["Cliente"] != "nan")]
        df = df[(df["Comercial"] != "") & (df["Comercial"] != "nan")]
        df = df[(df["Artigo"] != "") & (df["Artigo"] != "nan")]
        df = df[df["Quantidade"] > 0]
        
        final_count = len(df)
        st.sidebar.success(f"✅ Dados processados: {final_count} registros válidos")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        st.stop()

df = load_data()

# Verificar se há dados
if df.empty:
    st.error("⚠️ Não há dados válidos para análise.")
    
    # Criar dados de exemplo para demonstração
    st.info("📊 Criando dados de exemplo para demonstração...")
    
    # Dados de exemplo
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    n_samples = min(1000, len(dates))
    
    sample_dates = np.random.choice(dates, n_samples, replace=True)
    
    df = pd.DataFrame({
        "Data": sample_dates,
        "Cliente": np.random.choice(["Cliente A", "Cliente B", "Cliente C", "Cliente D", "Cliente E"], n_samples),
        "Artigo": np.random.choice(["Artigo 1", "Artigo 2", "Artigo 3", "Artigo 4", "Artigo 5"], n_samples),
        "Quantidade": np.random.randint(1, 100, n_samples),
        "Comercial": np.random.choice(["João", "Maria", "Carlos", "Ana", "Pedro"], n_samples),
    })
    
    df["Ano"] = df["Data"].dt.year
    df["Mes"] = df["Data"].dt.month
    df["MesNumero"] = df["Data"].dt.month
    df["MesNome"] = df["Data"].dt.strftime("%b")
    df["MesNomeCompleto"] = df["Data"].dt.strftime("%B")
    df["Dia"] = df["Data"].dt.day
    df["DiaSemana"] = df["Data"].dt.day_name()
    df["Semana"] = df["Data"].dt.isocalendar().week
    
    st.warning("⚠️ Usando dados de exemplo. Os dados reais podem ter problemas de formato.")

# === SIDEBAR – FILTROS DINÂMICOS ===
st.sidebar.header("🎛️ Filtros Dinâmicos")

# Informações sobre os dados
st.sidebar.subheader("📊 Dados Disponíveis")
if not df.empty:
    min_date = df["Data"].min()
    max_date = df["Data"].max()
    st.sidebar.write(f"**Período:** {min_date.strftime('%d/%m/%Y')} a {max_date.strftime('%d/%m/%Y')}")
    
    anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)
    st.sidebar.write(f"**Anos:** {', '.join(map(str, anos_disponiveis))}")
    st.sidebar.write(f"**Total registros:** {len(df):,}")
    st.sidebar.write(f"**Clientes únicos:** {df['Cliente'].nunique():,}")
    st.sidebar.write(f"**Artigos únicos:** {df['Artigo'].nunique():,}")
    st.sidebar.write(f"**Comerciais:** {df['Comercial'].nunique():,}")
else:
    st.sidebar.warning("⚠️ Nenhum dado disponível")

st.sidebar.divider()

# 1. FILTRO DE ANO (multiselect)
st.sidebar.subheader("📅 Filtro por Ano")

if len(anos_disponiveis) == 1:
    st.sidebar.info(f"✅ Ano disponível: {anos_disponiveis[0]}")
    anos_selecionados = anos_disponiveis
else:
    anos_selecionados = st.sidebar.multiselect(
        "Selecionar anos para análise:",
        options=anos_disponiveis,
        default=anos_disponiveis[:2] if len(anos_disponiveis) >= 2 else anos_disponiveis,
        help="Selecione um ou mais anos para análise"
    )

# Se não selecionou nenhum ano, usar todos
if not anos_selecionados:
    anos_selecionados = anos_disponiveis

# 2. FILTRO DE MÊS (multiselect)
st.sidebar.subheader("📆 Filtro por Mês")

# Mapeamento de números para nomes completos
meses_nomes = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# Obter meses disponíveis nos anos selecionados
if len(anos_selecionados) > 0:
    meses_disponiveis_numeros = sorted(df[df["Ano"].isin(anos_selecionados)]["MesNumero"].unique())
    opcoes_meses = [meses_nomes[mes] for mes in meses_disponiveis_numeros if mes in meses_nomes]
else:
    meses_disponiveis_numeros = sorted(df["MesNumero"].unique())
    opcoes_meses = [meses_nomes[mes] for mes in meses_disponiveis_numeros if mes in meses_nomes]

if opcoes_meses:
    meses_selecionados_nomes = st.sidebar.multiselect(
        "Selecionar meses:",
        options=opcoes_meses,
        default=opcoes_meses,
        help="Selecione um ou mais meses"
    )
    
    # Converter nomes dos meses para números
    nomes_para_meses = {v: k for k, v in meses_nomes.items()}
    
    if meses_selecionados_nomes:
        meses_selecionados = [nomes_para_meses[nome] for nome in meses_selecionados_nomes]
    else:
        meses_selecionados = meses_disponiveis_numeros
else:
    meses_selecionados = []
    st.sidebar.warning("Nenhum mês disponível")

# 3. FILTRO DE COMERCIAL (multiselect)
st.sidebar.subheader("👨‍💼 Filtro por Comercial")

# Filtrar comerciais disponíveis
if len(anos_selecionados) > 0 and len(meses_selecionados) > 0:
    mask = (df["Ano"].isin(anos_selecionados)) & (df["MesNumero"].isin(meses_selecionados))
    comerciais_disponiveis = sorted(df[mask]["Comercial"].unique())
else:
    comerciais_disponiveis = sorted(df["Comercial"].unique())

# Checkbox para "Todos"
todos_comerciais = st.sidebar.checkbox("Selecionar todos os comerciais", value=True, key="todos_comerciais")

if todos_comerciais:
    comerciais_selecionados = comerciais_disponiveis
else:
    comerciais_selecionados = st.sidebar.multiselect(
        "Selecionar comerciais:",
        options=comerciais_disponiveis,
        default=comerciais_disponiveis[:min(5, len(comerciais_disponiveis))] if comerciais_disponiveis else [],
        help="Selecione um ou mais comerciais"
    )
    
    if not comerciais_selecionados:
        comerciais_selecionados = comerciais_disponiveis

# 4. FILTRO DE CLIENTE (multiselect)
st.sidebar.subheader("🏢 Filtro por Cliente")

# Filtrar clientes disponíveis
if (len(anos_selecionados) > 0 and len(meses_selecionados) > 0 and len(comerciais_selecionados) > 0):
    mask = (df["Ano"].isin(anos_selecionados)) & \
           (df["MesNumero"].isin(meses_selecionados)) & \
           (df["Comercial"].isin(comerciais_selecionados))
    clientes_disponiveis = sorted(df[mask]["Cliente"].unique())
else:
    clientes_disponiveis = sorted(df["Cliente"].unique())

# Checkbox para "Todos"
todos_clientes = st.sidebar.checkbox("Selecionar todos os clientes", value=True, key="todos_clientes")

if todos_clientes:
    clientes_selecionados = clientes_disponiveis
else:
    clientes_selecionados = st.sidebar.multiselect(
        "Selecionar clientes:",
        options=clientes_disponiveis,
        default=clientes_disponiveis[:min(5, len(clientes_disponiveis))] if clientes_disponiveis else [],
        help="Selecione um ou mais clientes"
    )
    
    if not clientes_selecionados:
        clientes_selecionados = clientes_disponiveis

# 5. FILTRO DE ARTIGO (multiselect)
st.sidebar.subheader("📦 Filtro por Artigo")

# Filtrar artigos disponíveis
if (len(anos_selecionados) > 0 and len(meses_selecionados) > 0 and 
    len(comerciais_selecionados) > 0 and len(clientes_selecionados) > 0):
    mask = (df["Ano"].isin(anos_selecionados)) & \
           (df["MesNumero"].isin(meses_selecionados)) & \
           (df["Comercial"].isin(comerciais_selecionados)) & \
           (df["Cliente"].isin(clientes_selecionados))
    artigos_disponiveis = sorted(df[mask]["Artigo"].unique())
else:
    artigos_disponiveis = sorted(df["Artigo"].unique())

# Checkbox para "Todos"
todos_artigos = st.sidebar.checkbox("Selecionar todos os artigos", value=True, key="todos_artigos")

if todos_artigos:
    artigos_selecionados = artigos_disponiveis
else:
    artigos_selecionados = st.sidebar.multiselect(
        "Selecionar artigos:",
        options=artigos_disponiveis,
        default=artigos_disponiveis[:min(5, len(artigos_disponiveis))] if artigos_disponiveis else [],
        help="Selecione um ou mais artigos"
    )
    
    if not artigos_selecionados:
        artigos_selecionados = artigos_disponiveis

# === RESUMO DOS FILTROS ===
st.sidebar.divider()
st.sidebar.subheader("🎯 Filtros Aplicados")

# Formatar exibição
def formatar_lista(lista, max_items=3):
    if len(lista) > max_items:
        return ', '.join(map(str, lista[:max_items])) + f'... (+{len(lista)-max_items})'
    return ', '.join(map(str, lista))

# Formatar meses
meses_formatados = [meses_nomes[m] for m in meses_selecionados if m in meses_nomes]

st.sidebar.write(f"**Anos:** {formatar_lista(anos_selecionados)}")
st.sidebar.write(f"**Meses:** {formatar_lista(meses_formatados)}")
st.sidebar.write(f"**Comerciais:** {formatar_lista(comerciais_selecionados, 2)}")
st.sidebar.write(f"**Clientes:** {len(clientes_selecionados)} selecionados")
st.sidebar.write(f"**Artigos:** {len(artigos_selecionados)} selecionados")

# Botão para resetar filtros
if st.sidebar.button("🔄 Resetar Filtros", type="secondary"):
    st.rerun()

# === APLICAR FILTROS ===
df_filtrado = df[
    (df["Ano"].isin(anos_selecionados)) &
    (df["MesNumero"].isin(meses_selecionados)) &
    (df["Comercial"].isin(comerciais_selecionados)) &
    (df["Cliente"].isin(clientes_selecionados)) &
    (df["Artigo"].isin(artigos_selecionados))
].copy()

# Verificar se há dados após filtragem
if df_filtrado.empty:
    st.warning("""
    ⚠️ **Nenhum dado encontrado com os filtros atuais!**
    
    **Sugestões:**
    1. Verifique se os filtros não estão muito restritivos
    2. Tente selecionar mais anos, meses ou comerciais
    3. Verifique se há dados para o período selecionado
    
    **Dados disponíveis:**
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Anos", len(anos_disponiveis))
    with col2:
        st.metric("Total Comerciais", df["Comercial"].nunique())
    with col3:
        st.metric("Total Clientes", df["Cliente"].nunique())
    
    st.stop()

# === DASHBOARD PRINCIPAL ===

# Estatísticas rápidas
st.subheader("📈 Estatísticas do Período Selecionado")

# KPIs principais
total_quantidade = df_filtrado["Quantidade"].sum()
total_vendas = len(df_filtrado)
clientes_unicos = df_filtrado["Cliente"].nunique()
artigos_unicos = df_filtrado["Artigo"].nunique()
comerciais_unicos = df_filtrado["Comercial"].nunique()
ticket_medio = total_quantidade / total_vendas if total_vendas > 0 else 0

# Top cliente
top_cliente_info = df_filtrado.groupby("Cliente")["Quantidade"].sum().nlargest(1)
if not top_cliente_info.empty:
    top_cliente = top_cliente_info.index[0]
    top_cliente_qtd = top_cliente_info.iloc[0]
else:
    top_cliente = "N/A"
    top_cliente_qtd = 0

# Display KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📊 Total Quantidade", f"{total_quantidade:,.0f}")
with col2:
    st.metric("🛒 Total Vendas", f"{total_vendas:,.0f}")
with col3:
    st.metric("👥 Clientes Únicos", f"{clientes_unicos:,.0f}")
with col4:
    st.metric("📦 Artigos Únicos", f"{artigos_unicos:,.0f}")

col5, col6, col7, col8 = st.columns(4)
with col5:
    st.metric("👨‍💼 Comerciais", f"{comerciais_unicos:,.0f}")
with col6:
    st.metric("💰 Ticket Médio", f"{ticket_medio:,.2f}")
with col7:
    st.metric("🏆 Top Cliente", top_cliente[:20] + "..." if len(top_cliente) > 20 else top_cliente)
with col8:
    st.metric("🎯 Qtd Top Cliente", f"{top_cliente_qtd:,.0f}")

st.divider()

# === ANÁLISE TEMPORAL ===
st.subheader("📅 Análise Temporal")

# Selecionar tipo de análise temporal
analise_tipo = st.radio(
    "Selecione o tipo de análise temporal:",
    ["📈 Evolução Mensal", "📊 Comparativo Anual", "📅 Análise por Trimestre", "📆 Análise por Semana"],
    horizontal=True
)

if analise_tipo == "📈 Evolução Mensal":
    # Evolução mensal
    evolucao_mensal = df_filtrado.groupby(["Ano", "MesNumero", "MesNome"])["Quantidade"].sum().reset_index()
    
    # Ordenar corretamente
    ordem_meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    evolucao_mensal["MesNome"] = pd.Categorical(evolucao_mensal["MesNome"], categories=ordem_meses, ordered=True)
    evolucao_mensal = evolucao_mensal.sort_values(["Ano", "MesNumero"])
    
    # Criar gráfico
    fig, ax = plt.subplots(figsize=(14, 6))
    
    if len(anos_selecionados) > 1:
        # Múltiplos anos - linha para cada ano
        cores = plt.cm.Set3(np.linspace(0, 1, len(anos_selecionados)))
        
        for idx, ano in enumerate(sorted(anos_selecionados)):
            dados_ano = evolucao_mensal[evolucao_mensal["Ano"] == ano]
            if not dados_ano.empty:
                ax.plot(dados_ano["MesNome"], dados_ano["Quantidade"], 
                       marker='o', linewidth=2, label=str(ano), color=cores[idx])
        
        ax.set_title(f"Evolução Mensal por Ano", fontsize=14, fontweight='bold')
        ax.legend(title="Ano", bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        # Apenas um ano - gráfico de barras
        dados = evolucao_mensal[evolucao_mensal["Ano"] == anos_selecionados[0]]
        ax.bar(dados["MesNome"], dados["Quantidade"], color='skyblue', alpha=0.7)
        ax.plot(dados["MesNome"], dados["Quantidade"], marker='o', color='darkblue', linewidth=2)
        ax.set_title(f"Evolução Mensal - {anos_selecionados[0]}", fontsize=14, fontweight='bold')
    
    ax.set_xlabel("Mês")
    ax.set_ylabel("Quantidade")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    
    # Tabela de dados
    with st.expander("📋 Ver dados detalhados"):
        tabela_dados = evolucao_mensal.copy()
        tabela_dados["Quantidade"] = tabela_dados["Quantidade"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(tabela_dados, use_container_width=True)

elif analise_tipo == "📊 Comparativo Anual":
    # Comparativo anual
    if len(anos_selecionados) >= 2:
        comparativo_anual = df_filtrado.groupby("Ano").agg({
            "Quantidade": "sum",
            "Cliente": "nunique",
            "Artigo": "nunique",
            "Comercial": "nunique"
        }).reset_index()
        
        comparativo_anual.columns = ["Ano", "Total Quantidade", "Clientes Únicos", "Artigos Vendidos", "Comerciais Ativos"]
        
        # Gráfico comparativo
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Comparativo Anual", fontsize=16, fontweight='bold')
        
        metrics = ["Total Quantidade", "Clientes Únicos", "Artigos Vendidos", "Comerciais Ativos"]
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#73AB84']
        
        for idx, (ax, metric, color) in enumerate(zip(axes.flat, metrics, colors)):
            ax.bar(comparativo_anual["Ano"].astype(str), comparativo_anual[metric], color=color, alpha=0.7)
            ax.set_title(metric)
            ax.set_ylabel("Valor")
            ax.grid(True, alpha=0.3)
            
            # Adicionar valores nas barras
            for i, v in enumerate(comparativo_anual[metric]):
                ax.text(i, v, f'{v:,.0f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Tabela comparativa
        with st.expander("📋 Ver tabela comparativa"):
            tabela_comparativa = comparativo_anual.copy()
            for col in tabela_comparativa.columns[1:]:
                tabela_comparativa[col] = tabela_comparativa[col].apply(lambda x: f"{x:,.0f}")
            st.dataframe(tabela_comparativa, use_container_width=True)
    else:
        st.info("ℹ️ Selecione pelo menos 2 anos para ver o comparativo anual.")

elif analise_tipo == "📅 Análise por Trimestre":
    # Análise por trimestre
    df_filtrado["Trimestre"] = df_filtrado["MesNumero"].apply(lambda x: (x-1)//3 + 1)
    
    analise_trimestral = df_filtrado.groupby(["Ano", "Trimestre"]).agg({
        "Quantidade": "sum",
        "Cliente": "nunique"
    }).reset_index()
    
    analise_trimestral["Período"] = analise_trimestral["Ano"].astype(str) + "-T" + analise_trimestral["Trimestre"].astype(str)
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(14, 6))
    
    x = range(len(analise_trimestral))
    width = 0.35
    
    ax.bar([i - width/2 for i in x], analise_trimestral["Quantidade"], width, label='Quantidade', color='#2E86AB', alpha=0.7)
    ax.bar([i + width/2 for i in x], analise_trimestral["Cliente"], width, label='Clientes Únicos', color='#A23B72', alpha=0.7)
    
    ax.set_xlabel("Trimestre")
    ax.set_ylabel("Valor")
    ax.set_title("Análise Trimestral", fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(analise_trimestral["Período"], rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)

elif analise_tipo == "📆 Análise por Semana":
    # Análise por semana
    analise_semanal = df_filtrado.groupby(["Ano", "Semana"]).agg({
        "Quantidade": "sum",
        "Cliente": "nunique"
    }).reset_index()
    
    # Criar período
    analise_semanal["Período"] = analise_semanal["Ano"].astype(str) + "-S" + analise_semanal["Semana"].astype(str).str.zfill(2)
    
    # Limitar a 20 semanas para legibilidade
    if len(analise_semanal) > 20:
        st.info(f"Mostrando as últimas 20 semanas de {len(analise_semanal)} disponíveis")
        analise_semanal = analise_semanal.tail(20)
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(14, 6))
    
    x = range(len(analise_semanal))
    ax.bar(x, analise_semanal["Quantidade"], color='skyblue', alpha=0.7)
    
    ax.set_xlabel("Semana")
    ax.set_ylabel("Quantidade")
    ax.set_title("Análise Semanal", fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(analise_semanal["Período"], rotation=90, fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)

st.divider()

# === ANÁLISE POR DIMENSÕES ===
st.subheader("📊 Análise por Dimensões")

tab1, tab2, tab3, tab4 = st.tabs(["👨‍💼 Por Comercial", "🏢 Por Cliente", "📦 Por Artigo", "📅 Por Período"])

with tab1:
    st.write("**Desempenho por Comercial**")
    
    desempenho_comercial = df_filtrado.groupby("Comercial").agg({
        "Quantidade": ["sum", "mean", "count"],
        "Cliente": "nunique",
        "Artigo": "nunique"
    }).round(2)
    
    desempenho_comercial.columns = ["Total Qtd", "Média por Venda", "Nº Vendas", "Clientes Únicos", "Artigos Vendidos"]
    desempenho_comercial = desempenho_comercial.sort_values("Total Qtd", ascending=False)
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    top_n = min(10, len(desempenho_comercial))
    top_comerciais = desempenho_comercial.head(top_n)
    
    ax.barh(range(top_n), top_comerciais["Total Qtd"], color='#2E86AB', alpha=0.7)
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(top_comerciais.index)
    ax.invert_yaxis()
    ax.set_xlabel("Quantidade Total")
    ax.set_title(f"Top {top_n} Comerciais por Volume", fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Tabela
    with st.expander("📋 Ver todos os comerciais"):
        tabela_formatada = desempenho_comercial.copy()
        for col in tabela_formatada.columns[:3]:  # Colunas numéricas
            tabela_formatada[col] = tabela_formatada[col].apply(lambda x: f"{x:,.0f}")
        st.dataframe(tabela_formatada, use_container_width=True)

with tab2:
    st.write("**Análise por Cliente**")
    
    analise_cliente = df_filtrado.groupby("Cliente").agg({
        "Quantidade": ["sum", "mean", "count"],
        "Comercial": "nunique",
        "Artigo": "nunique"
    }).round(2)
    
    analise_cliente.columns = ["Total Qtd", "Ticket Médio", "Nº Compras", "Comerciais", "Artigos Comprados"]
    analise_cliente = analise_cliente.sort_values("Total Qtd", ascending=False)
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    top_n = min(15, len(analise_cliente))
    top_clientes = analise_cliente.head(top_n)
    
    ax.barh(range(top_n), top_clientes["Total Qtd"], color='#A23B72', alpha=0.7)
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(top_clientes.index)
    ax.invert_yaxis()
    ax.set_xlabel("Quantidade Total")
    ax.set_title(f"Top {top_n} Clientes por Volume", fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Tabela
    with st.expander("📋 Ver todos os clientes"):
        tabela_formatada = analise_cliente.head(50).copy()
        for col in tabela_formatada.columns[:3]:  # Colunas numéricas
            tabela_formatada[col] = tabela_formatada[col].apply(lambda x: f"{x:,.0f}")
        st.dataframe(tabela_formatada, use_container_width=True)

with tab3:
    st.write("**Análise por Artigo**")
    
    analise_artigo = df_filtrado.groupby("Artigo").agg({
        "Quantidade": ["sum", "mean", "count"],
        "Cliente": "nunique",
        "Comercial": "nunique"
    }).round(2)
    
    analise_artigo.columns = ["Total Qtd", "Média por Venda", "Nº Vendas", "Clientes", "Comerciais"]
    analise_artigo = analise_artigo.sort_values("Total Qtd", ascending=False)
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    top_n = min(15, len(analise_artigo))
    top_artigos = analise_artigo.head(top_n)
    
    ax.barh(range(top_n), top_artigos["Total Qtd"], color='#F18F01', alpha=0.7)
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(top_artigos.index)
    ax.invert_yaxis()
    ax.set_xlabel("Quantidade Total")
    ax.set_title(f"Top {top_n} Artigos por Volume", fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Tabela
    with st.expander("📋 Ver todos os artigos"):
        tabela_formatada = analise_artigo.head(50).copy()
        for col in tabela_formatada.columns[:3]:  # Colunas numéricas
            tabela_formatada[col] = tabela_formatada[col].apply(lambda x: f"{x:,.0f}")
        st.dataframe(tabela_formatada, use_container_width=True)

with tab4:
    st.write("**Análise por Período Detalhada**")
    
    periodo_analise = st.selectbox(
        "Selecione o nível de detalhe:",
        ["Diário", "Semanal", "Mensal", "Trimestral", "Anual"]
    )
    
    if periodo_analise == "Diário":
        grupo = ["Data"]
        titulo = "Evolução Diária"
    elif periodo_analise == "Semanal":
        grupo = ["Ano", "Semana"]
        titulo = "Evolução Semanal"
    elif periodo_analise == "Mensal":
        grupo = ["Ano", "MesNumero", "MesNome"]
        titulo = "Evolução Mensal"
    elif periodo_analise == "Trimestral":
        df_filtrado["Trimestre"] = df_filtrado["MesNumero"].apply(lambda x: (x-1)//3 + 1)
        grupo = ["Ano", "Trimestre"]
        titulo = "Evolução Trimestral"
    else:  # Anual
        grupo = ["Ano"]
        titulo = "Evolução Anual"
    
    analise_periodo = df_filtrado.groupby(grupo).agg({
        "Quantidade": ["sum", "count", "mean"],
        "Cliente": "nunique",
        "Artigo": "nunique"
    }).round(2)
    
    analise_periodo.columns = ["Total Qtd", "Nº Vendas", "Ticket Médio", "Clientes Únicos", "Artigos Vendidos"]
    
    # Formatar índice para exibição
    if len(grupo) > 1:
        analise_periodo.index = analise_periodo.index.map(lambda x: " - ".join(map(str, x)))
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(14, 6))
    
    x = range(len(analise_periodo))
    ax.bar(x, analise_periodo["Total Qtd"], color='#73AB84', alpha=0.7)
    
    ax.set_xlabel("Período")
    ax.set_ylabel("Quantidade Total")
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    
    if len(analise_periodo) <= 20:
        ax.set_xticklabels(analise_periodo.index, rotation=45, ha='right')
    else:
        ax.set_xticklabels([])  # Não mostrar labels se muitos períodos
    
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Tabela
    st.dataframe(analise_periodo, use_container_width=True)

st.divider()

# === EXPORTAR DADOS ===
st.subheader("📤 Exportar Dados")

col1, col2, col3 = st.columns(3)

with col1:
    # Exportar CSV
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"dados_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        help="Baixar dados filtrados em formato CSV"
    )

with col2:
    # Exportar Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Dados filtrados
        df_filtrado.to_excel(writer, sheet_name='Dados Filtrados', index=False)
        
        # Resumo por comercial
        resumo_comercial = df_filtrado.groupby("Comercial").agg({
            "Quantidade": ["sum", "count", "mean"],
            "Cliente": "nunique",
            "Artigo": "nunique"
        }).round(2)
        resumo_comercial.to_excel(writer, sheet_name='Resumo Comercial')
        
        # Resumo por cliente
        resumo_cliente = df_filtrado.groupby("Cliente").agg({
            "Quantidade": ["sum", "count", "mean"],
            "Comercial": "nunique",
            "Artigo": "nunique"
        }).round(2)
        resumo_cliente.to_excel(writer, sheet_name='Resumo Cliente')
        
        # Resumo por artigo
        resumo_artigo = df_filtrado.groupby("Artigo").agg({
            "Quantidade": ["sum", "count", "mean"],
            "Cliente": "nunique",
            "Comercial": "nunique"
        }).round(2)
        resumo_artigo.to_excel(writer, sheet_name='Resumo Artigo')
    
    excel_data = output.getvalue()
    
    st.download_button(
        label="📊 Download Excel",
        data=excel_data,
        file_name=f"relatorio_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Baixar relatório completo em formato Excel"
    )

with col3:
    # Exportar resumo em JSON
    json_data = df_filtrado.to_json(orient='records', force_ascii=False)
    st.download_button(
        label="📄 Download JSON",
        data=json_data,
        file_name=f"dados_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        help="Baixar dados filtrados em formato JSON"
    )

# === INFORMAÇÕES FINAIS ===
st.divider()
st.success("✅ Dashboard carregado com sucesso!")

# Estatísticas finais
with st.expander("📊 Estatísticas Finais do Período Selecionado"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Total de Registros", f"{len(df_filtrado):,}")
        st.metric("👥 Clientes Ativos", f"{df_filtrado['Cliente'].nunique():,}")
    
    with col2:
        st.metric("🛒 Volume Total", f"{df_filtrado['Quantidade'].sum():,}")
        st.metric("📦 Diversidade de Artigos", f"{df_filtrado['Artigo'].nunique():,}")
    
    with col3:
        st.metric("💰 Ticket Médio", f"{df_filtrado['Quantidade'].sum()/len(df_filtrado):,.2f}")
        st.metric("👨‍💼 Comerciais Envolvidos", f"{df_filtrado['Comercial'].nunique():,}")

st.info("""
💡 **Dicas de uso:**
1. Use os filtros na sidebar para refinar sua análise
2. Explore as diferentes abas para análises específicas
3. Exporte os dados para análises mais detalhadas
4. Clique nos gráficos para ampliar
""")
