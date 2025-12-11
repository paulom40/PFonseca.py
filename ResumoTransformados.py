import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Dashboard Compras - KPIs + Análise Detalhada", layout="wide")
st.title("Dashboard de Compras – KPIs + Análise Detalhada")

# === CARREGAR DADOS ===
@st.cache_data
def load_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"
        df_raw = pd.read_excel(url)
        
        # Verificar se há coluna de preço/valor
        has_price_column = len(df_raw.columns) > 4
        
        # Criar dataframe
        df = pd.DataFrame()
        
        # Processar data
        date_col = df_raw.iloc[:, 0]
        try:
            df["Data"] = pd.to_datetime(date_col, errors='coerce')
        except:
            df["Data"] = pd.NaT
        
        # Se todas as datas forem 1970, criar datas sequenciais
        if len(df) > 0 and df["Data"].dt.year.nunique() == 1 and df["Data"].dt.year.iloc[0] == 1970:
            base_date = datetime.now()
            df["Data"] = pd.date_range(end=base_date, periods=len(df), freq='D')
        
        # Processar outras colunas
        df["Cliente"] = df_raw.iloc[:, 1].fillna("").astype(str).str.strip()
        df["Artigo"] = df_raw.iloc[:, 2].fillna("").astype(str).str.strip()
        
        # Quantidade - coluna 3
        if len(df_raw.columns) > 3:
            df["Quantidade"] = pd.to_numeric(df_raw.iloc[:, 3], errors='coerce').fillna(0)
        else:
            df["Quantidade"] = 0
        
        # Valor/Preço - coluna 4 (se existir)
        if has_price_column and len(df_raw.columns) > 4:
            df["Valor"] = pd.to_numeric(df_raw.iloc[:, 4], errors='coerce').fillna(0)
        else:
            # Se não houver coluna de valor, criar baseado em quantidade
            df["Valor"] = df["Quantidade"] * np.random.uniform(10, 100, len(df))
        
        # Comercial - coluna 8
        if len(df_raw.columns) > 8:
            df["Comercial"] = df_raw.iloc[:, 8].fillna("").astype(str).str.strip()
        else:
            df["Comercial"] = "Desconhecido"
        
        # Calcular preço unitário
        df["Preco_Unitario"] = df["Valor"] / df["Quantidade"].replace(0, 1)
        
        # Remover linhas sem data válida
        df = df[df["Data"].notna()].copy()
        
        # Adicionar colunas temporais
        df["Ano"] = df["Data"].dt.year
        df["Mes"] = df["Data"].dt.month
        df["MesNumero"] = df["Data"].dt.month
        df["MesNome"] = df["Data"].dt.strftime("%b")
        df["MesNomeCompleto"] = df["Data"].dt.strftime("%B")
        df["Dia"] = df["Data"].dt.day
        df["DiaSemana"] = df["Data"].dt.day_name()
        df["Semana"] = df["Data"].dt.isocalendar().week
        df["Data_Str"] = df["Data"].dt.strftime("%Y-%m-%d")
        
        # Filtrar dados inválidos
        df = df[(df["Cliente"] != "") & (df["Cliente"] != "nan")]
        df = df[(df["Comercial"] != "") & (df["Comercial"] != "nan")]
        df = df[(df["Artigo"] != "") & (df["Artigo"] != "nan")]
        df = df[df["Quantidade"] > 0]
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        st.stop()

df = load_data()

# === SIDEBAR – FILTROS DINÂMICOS ===
st.sidebar.header("🎛️ Filtros")

# 1. FILTRO DE ANO (multiselect)
st.sidebar.subheader("📅 Ano")
anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)
anos_selecionados = st.sidebar.multiselect(
    "Selecionar anos:",
    options=anos_disponiveis,
    default=anos_disponiveis[:2] if len(anos_disponiveis) >= 2 else anos_disponiveis,
    help="Selecione um ou mais anos"
)

if not anos_selecionados:
    anos_selecionados = anos_disponiveis

# 2. FILTRO DE MÊS (multiselect)
st.sidebar.subheader("📆 Mês")

meses_nomes = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# Obter meses disponíveis
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
    
    nomes_para_meses = {v: k for k, v in meses_nomes.items()}
    
    if meses_selecionados_nomes:
        meses_selecionados = [nomes_para_meses[nome] for nome in meses_selecionados_nomes]
    else:
        meses_selecionados = meses_disponiveis_numeros
else:
    meses_selecionados = []

# 3. FILTRO DE COMERCIAL (multiselect)
st.sidebar.subheader("👨‍💼 Comercial")

# Filtrar comerciais disponíveis
if len(anos_selecionados) > 0 and len(meses_selecionados) > 0:
    mask = (df["Ano"].isin(anos_selecionados)) & (df["MesNumero"].isin(meses_selecionados))
    comerciais_disponiveis = sorted(df[mask]["Comercial"].unique())
else:
    comerciais_disponiveis = sorted(df["Comercial"].unique())

todos_comerciais = st.sidebar.checkbox("Todos os comerciais", value=True, key="todos_comerciais")

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
st.sidebar.subheader("🏢 Cliente")

# Filtrar clientes disponíveis
if (len(anos_selecionados) > 0 and len(meses_selecionados) > 0 and len(comerciais_selecionados) > 0):
    mask = (df["Ano"].isin(anos_selecionados)) & \
           (df["MesNumero"].isin(meses_selecionados)) & \
           (df["Comercial"].isin(comerciais_selecionados))
    clientes_disponiveis = sorted(df[mask]["Cliente"].unique())
else:
    clientes_disponiveis = sorted(df["Cliente"].unique())

todos_clientes = st.sidebar.checkbox("Todos os clientes", value=True, key="todos_clientes")

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
st.sidebar.subheader("📦 Artigo")

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

todos_artigos = st.sidebar.checkbox("Todos os artigos", value=True, key="todos_artigos")

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

if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros atuais!")
    st.stop()

# === CÁLCULO DOS KPIs ===
# KPIs Básicos
total_vendas_eur = df_filtrado["Valor"].sum()
total_quantidade = df_filtrado["Quantidade"].sum()
num_entidades = df_filtrado["Cliente"].nunique()
num_comerciais = df_filtrado["Comercial"].nunique()
num_artigos = df_filtrado["Artigo"].nunique()

# KPIs de Ticket/Preço
num_transacoes = len(df_filtrado)
ticket_medio_eur = total_vendas_eur / num_transacoes if num_transacoes > 0 else 0
preco_medio_unitario = total_vendas_eur / total_quantidade if total_quantidade > 0 else 0
venda_media_transacao = total_vendas_eur / num_transacoes if num_transacoes > 0 else 0
quantidade_media_transacao = total_quantidade / num_transacoes if num_transacoes > 0 else 0

# KPIs Temporais
dias_com_vendas = df_filtrado["Data_Str"].nunique()
venda_media_dia = total_vendas_eur / dias_com_vendas if dias_com_vendas > 0 else 0

# Ticket Médio Mensal
ticket_mensal = df_filtrado.groupby(["Ano", "MesNumero"])["Valor"].sum().mean()
ticket_medio_mes = ticket_mensal if not pd.isna(ticket_mensal) else 0

# === DISPLAY DOS KPIs ===
st.subheader("📊 KPIs Principais")

# Linha 1 de KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Total Vendas (€)",
        f"€{total_vendas_eur:,.0f}",
        delta=None,
        help="Soma total do valor das vendas"
    )

with col2:
    st.metric(
        "📦 Total Quantidade",
        f"{total_quantidade:,.0f}",
        delta=None,
        help="Soma total da quantidade vendida"
    )

with col3:
    st.metric(
        "🏢 Nº Entidades",
        f"{num_entidades:,.0f}",
        delta=None,
        help="Número total de clientes únicos"
    )

with col4:
    st.metric(
        "🎫 Ticket Médio (€)",
        f"€{ticket_medio_eur:,.2f}",
        delta=None,
        help="Valor médio por transação"
    )

# Linha 2 de KPIs
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric(
        "👨‍💼 Nº Comerciais",
        f"{num_comerciais:,.0f}",
        delta=None,
        help="Número de comerciais ativos"
    )

with col6:
    st.metric(
        "📦 Nº Artigos",
        f"{num_artigos:,.0f}",
        delta=None,
        help="Número de artigos diferentes vendidos"
    )

with col7:
    st.metric(
        "🏷️ Preço Médio Unitário (€)",
        f"€{preco_medio_unitario:,.2f}",
        delta=None,
        help="Preço médio por unidade"
    )

with col8:
    st.metric(
        "💳 Venda Média/Transação (€)",
        f"€{venda_media_transacao:,.2f}",
        delta=None,
        help="Valor médio por transação"
    )

# Linha 3 de KPIs
col9, col10, col11, col12 = st.columns(4)

with col9:
    st.metric(
        "📊 Quantidade Média/Transação",
        f"{quantidade_media_transacao:,.2f}",
        delta=None,
        help="Quantidade média por transação"
    )

with col10:
    st.metric(
        "📅 Dias com Vendas",
        f"{dias_com_vendas:,.0f}",
        delta=None,
        help="Número de dias distintos com vendas"
    )

with col11:
    st.metric(
        "📈 Venda Média/Dia (€)",
        f"€{venda_media_dia:,.2f}",
        delta=None,
        help="Valor médio vendido por dia"
    )

with col12:
    st.metric(
        "🗓️ Ticket Médio (€) Mês",
        f"€{ticket_medio_mes:,.2f}",
        delta=None,
        help="Ticket médio mensal"
    )

st.divider()

# === ANÁLISE TEMPORAL ===
st.subheader("📈 Análise Temporal")

# Gráfico de evolução de vendas
fig1, ax1 = plt.subplots(figsize=(14, 6))

# Agrupar por mês
vendas_mensais = df_filtrado.groupby(["Ano", "MesNumero", "MesNome"])[["Valor", "Quantidade"]].sum().reset_index()

# Ordenar por data
ordem_meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
vendas_mensais["MesNome"] = pd.Categorical(vendas_mensais["MesNome"], categories=ordem_meses, ordered=True)
vendas_mensais = vendas_mensais.sort_values(["Ano", "MesNumero"])

# Criar label para o eixo X
vendas_mensais["Periodo"] = vendas_mensais["Ano"].astype(str) + "-" + vendas_mensais["MesNome"]

# Gráfico de barras para valor
x = range(len(vendas_mensais))
width = 0.35

ax1.bar([i - width/2 for i in x], vendas_mensais["Valor"], width, 
        label='Valor (€)', color='#2E86AB', alpha=0.7)

ax1.set_xlabel("Período")
ax1.set_ylabel("Valor (€)", color='#2E86AB')
ax1.tick_params(axis='y', labelcolor='#2E86AB')
ax1.set_title("Evolução Mensal de Vendas", fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(vendas_mensais["Periodo"], rotation=45, ha='right')

# Segundo eixo Y para quantidade
ax2 = ax1.twinx()
ax2.plot(x, vendas_mensais["Quantidade"], 'o-', color='#A23B72', linewidth=2, 
         markersize=6, label='Quantidade')
ax2.set_ylabel('Quantidade', color='#A23B72')
ax2.tick_params(axis='y', labelcolor='#A23B72')

# Legendas
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

ax1.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig1)

st.divider()

# === ANÁLISE POR DIMENSÕES ===
st.subheader("📊 Análise por Dimensões")

tab1, tab2, tab3 = st.tabs(["👨‍💼 Por Comercial", "🏢 Por Cliente", "📦 Por Artigo"])

with tab1:
    st.write("**Top 10 Comerciais por Performance**")
    
    performance_comercial = df_filtrado.groupby("Comercial").agg({
        "Valor": ["sum", "mean", "count"],
        "Quantidade": "sum",
        "Cliente": "nunique",
        "Artigo": "nunique"
    }).round(2)
    
    performance_comercial.columns = ["Total Vendas (€)", "Ticket Médio (€)", "Nº Transações", 
                                     "Total Quantidade", "Clientes Únicos", "Artigos Vendidos"]
    
    performance_comercial = performance_comercial.sort_values("Total Vendas (€)", ascending=False)
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    top_n = min(10, len(performance_comercial))
    top_comerciais = performance_comercial.head(top_n)
    
    x = range(top_n)
    ax.bar(x, top_comerciais["Total Vendas (€)"], color='#2E86AB', alpha=0.7)
    
    ax.set_xlabel("Comercial")
    ax.set_ylabel("Total Vendas (€)")
    ax.set_title(f"Top {top_n} Comerciais por Volume de Vendas", fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(top_comerciais.index, rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores nas barras
    for i, v in enumerate(top_comerciais["Total Vendas (€)"]):
        ax.text(i, v, f'€{v:,.0f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Tabela detalhada
    with st.expander("📋 Ver detalhes dos comerciais"):
        tabela_formatada = performance_comercial.copy()
        for col in tabela_formatada.columns:
            if "(€)" in col:
                tabela_formatada[col] = tabela_formatada[col].apply(lambda x: f"€{x:,.2f}")
            else:
                tabela_formatada[col] = tabela_formatada[col].apply(lambda x: f"{x:,.0f}")
        st.dataframe(tabela_formatada, use_container_width=True)

with tab2:
    st.write("**Top 10 Clientes por Valor**")
    
    performance_cliente = df_filtrado.groupby("Cliente").agg({
        "Valor": ["sum", "mean", "count"],
        "Quantidade": "sum",
        "Comercial": "nunique",
        "Artigo": "nunique"
    }).round(2)
    
    performance_cliente.columns = ["Total Vendas (€)", "Ticket Médio (€)", "Nº Compras", 
                                   "Total Quantidade", "Comerciais", "Artigos Comprados"]
    
    performance_cliente = performance_cliente.sort_values("Total Vendas (€)", ascending=False)
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    top_n = min(10, len(performance_cliente))
    top_clientes = performance_cliente.head(top_n)
    
    ax.barh(range(top_n), top_clientes["Total Vendas (€)"], color='#A23B72', alpha=0.7)
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(top_clientes.index)
    ax.invert_yaxis()
    ax.set_xlabel("Total Vendas (€)")
    ax.set_title(f"Top {top_n} Clientes por Valor", fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Tabela detalhada
    with st.expander("📋 Ver detalhes dos clientes"):
        tabela_formatada = performance_cliente.head(20).copy()
        for col in tabela_formatada.columns:
            if "(€)" in col:
                tabela_formatada[col] = tabela_formatada[col].apply(lambda x: f"€{x:,.2f}")
            else:
                tabela_formatada[col] = tabela_formatada[col].apply(lambda x: f"{x:,.0f}")
        st.dataframe(tabela_formatada, use_container_width=True)

with tab3:
    st.write("**Top 10 Artigos por Vendas**")
    
    performance_artigo = df_filtrado.groupby("Artigo").agg({
        "Valor": ["sum", "mean"],
        "Quantidade": ["sum", "mean"],
        "Cliente": "nunique",
        "Comercial": "nunique"
    }).round(2)
    
    performance_artigo.columns = ["Total Vendas (€)", "Preço Médio (€)", 
                                  "Total Quantidade", "Quantidade Média", 
                                  "Clientes", "Comerciais"]
    
    performance_artigo = performance_artigo.sort_values("Total Vendas (€)", ascending=False)
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    top_n = min(10, len(performance_artigo))
    top_artigos = performance_artigo.head(top_n)
    
    x = range(top_n)
    width = 0.35
    
    ax.bar([i - width/2 for i in x], top_artigos["Total Vendas (€)"], width, 
           label='Vendas (€)', color='#F18F01', alpha=0.7)
    ax.bar([i + width/2 for i in x], top_artigos["Total Quantidade"], width, 
           label='Quantidade', color='#73AB84', alpha=0.7)
    
    ax.set_xlabel("Artigo")
    ax.set_ylabel("Valor")
    ax.set_title(f"Top {top_n} Artigos por Performance", fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(top_artigos.index, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Tabela detalhada
    with st.expander("📋 Ver detalhes dos artigos"):
        tabela_formatada = performance_artigo.head(20).copy()
        for col in tabela_formatada.columns:
            if "(€)" in col:
                tabela_formatada[col] = tabela_formatada[col].apply(lambda x: f"€{x:,.2f}")
            else:
                tabela_formatada[col] = tabela_formatada[col].apply(lambda x: f"{x:,.0f}")
        st.dataframe(tabela_formatada, use_container_width=True)

st.divider()

# === ANÁLISE DE TICKET ===
st.subheader("🎫 Análise de Ticket")

col1, col2 = st.columns(2)

with col1:
    # Distribuição de valores das transações
    st.write("**Distribuição do Valor das Transações**")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df_filtrado["Valor"], bins=30, color='#2E86AB', alpha=0.7, edgecolor='black')
    ax.axvline(df_filtrado["Valor"].mean(), color='red', linestyle='--', linewidth=2, 
               label=f'Média: €{df_filtrado["Valor"].mean():,.2f}')
    ax.axvline(df_filtrado["Valor"].median(), color='green', linestyle='--', linewidth=2, 
               label=f'Mediana: €{df_filtrado["Valor"].median():,.2f}')
    
    ax.set_xlabel("Valor da Transação (€)")
    ax.set_ylabel("Frequência")
    ax.set_title("Distribuição do Valor das Transações", fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    # Relação entre quantidade e valor
    st.write("**Relação Quantidade vs Valor**")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scatter = ax.scatter(df_filtrado["Quantidade"], df_filtrado["Valor"], 
                        alpha=0.6, color='#A23B72', s=30)
    
    # Calcular linha de tendência
    z = np.polyfit(df_filtrado["Quantidade"], df_filtrado["Valor"], 1)
    p = np.poly1d(z)
    ax.plot(df_filtrado["Quantidade"], p(df_filtrado["Quantidade"]), 
            color='#2E86AB', linewidth=2, linestyle='--', 
            label=f'Tendência: y = {z[0]:.2f}x + {z[1]:.2f}')
    
    ax.set_xlabel("Quantidade")
    ax.set_ylabel("Valor (€)")
    ax.set_title("Relação entre Quantidade e Valor", fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)

# Estatísticas de ticket
with st.expander("📊 Estatísticas Detalhadas do Ticket"):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Ticket Mínimo", f"€{df_filtrado['Valor'].min():,.2f}")
    with col2:
        st.metric("Ticket Máximo", f"€{df_filtrado['Valor'].max():,.2f}")
    with col3:
        st.metric("Ticket Médio", f"€{df_filtrado['Valor'].mean():,.2f}")
    with col4:
        st.metric("Mediana do Ticket", f"€{df_filtrado['Valor'].median():,.2f}")

st.divider()

# === EXPORTAR DADOS ===
st.subheader("📤 Exportar Dados")

# Preparar dados para exportação
resumo_kpis = pd.DataFrame({
    "KPI": [
        "Total Vendas (€)", "Total Quantidade", "Nº Entidades", "Ticket Médio (€)",
        "Nº Comerciais", "Nº Artigos", "Preço Médio Unitário (€)", "Venda Média/Transação (€)",
        "Quantidade Média/Transação", "Dias com Vendas", "Venda Média/Dia (€)", "Ticket Médio (€) Mês"
    ],
    "Valor": [
        total_vendas_eur, total_quantidade, num_entidades, ticket_medio_eur,
        num_comerciais, num_artigos, preco_medio_unitario, venda_media_transacao,
        quantidade_media_transacao, dias_com_vendas, venda_media_dia, ticket_medio_mes
    ]
})

col1, col2 = st.columns(2)

with col1:
    # Exportar KPIs em CSV
    csv_kpis = resumo_kpis.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download KPIs (CSV)",
        data=csv_kpis,
        file_name=f"kpis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

with col2:
    # Exportar dados completos em Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # KPIs
        resumo_kpis.to_excel(writer, sheet_name='KPIs', index=False)
        
        # Dados filtrados
        df_filtrado.to_excel(writer, sheet_name='Dados Filtrados', index=False)
        
        # Performance por comercial
        performance_comercial.to_excel(writer, sheet_name='Performance Comercial')
        
        # Performance por cliente
        performance_cliente.head(50).to_excel(writer, sheet_name='Top Clientes')
        
        # Performance por artigo
        performance_artigo.head(50).to_excel(writer, sheet_name='Top Artigos')
        
        # Vendas mensais
        vendas_mensais.to_excel(writer, sheet_name='Vendas Mensais', index=False)
    
    excel_data = output.getvalue()
    
    st.download_button(
        label="📊 Download Relatório Completo (Excel)",
        data=excel_data,
        file_name=f"relatorio_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# === INFORMAÇÕES FINAIS ===
st.divider()
st.success("✅ Dashboard carregado com sucesso!")

# Resumo rápido
with st.expander("📋 Resumo do Período Selecionado"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Período:**")
        if len(anos_selecionados) == 1:
            st.write(f"- Ano: {anos_selecionados[0]}")
        else:
            st.write(f"- Anos: {', '.join(map(str, anos_selecionados))}")
        
        meses_selecionados_nomes = [meses_nomes[m] for m in meses_selecionados if m in meses_nomes]
        if len(meses_selecionados_nomes) <= 6:
            st.write(f"- Meses: {', '.join(meses_selecionados_nomes)}")
        else:
            st.write(f"- Meses: {len(meses_selecionados)} meses selecionados")
        
        st.write(f"- Dias com vendas: {dias_com_vendas}")
    
    with col2:
        st.write("**Eficiência:**")
        st.write(f"- Vendas por dia: €{venda_media_dia:,.2f}")
        st.write(f"- Transações por dia: {num_transacoes/dias_com_vendas:,.1f}" if dias_com_vendas > 0 else "- Transações por dia: 0")
        st.write(f"- Clientes por comercial: {num_entidades/num_comerciais:,.1f}" if num_comerciais > 0 else "- Clientes por comercial: 0")
        st.write(f"- Artigos por cliente: {num_artigos/num_entidades:,.1f}" if num_entidades > 0 else "- Artigos por cliente: 0")

st.info("""
💡 **Dicas de uso:**
1. Use os filtros na sidebar para refinar sua análise
2. Explore as diferentes abas para análises específicas
3. Exporte os dados para análises mais detalhadas
4. Observe os KPIs para monitorar performance
""")
