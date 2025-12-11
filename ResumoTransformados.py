import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Dashboard Compras - KPIs + Análise Detalhada", layout="wide")
st.title("Dashboard de Compras – KPIs + Análise Detalhada")

# === CARREGAR DADOS CORRIGIDO - AJUSTE DAS COLUNAS ===
@st.cache_data
def load_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"
        df_raw = pd.read_excel(url)
        
        st.sidebar.write(f"📊 Dados carregados: {len(df_raw)} registros")
        
        # VERIFICAR ESTRUTURA DO ARQUIVO
        with st.sidebar.expander("🔍 Ver estrutura completa"):
            st.write("**Colunas disponíveis:**")
            for i, col in enumerate(df_raw.columns):
                st.write(f"{i+1}. {col} - Primeiro valor: {df_raw.iloc[0, i] if len(df_raw) > 0 else 'N/A'}")
        
        # Criar DataFrame
        df = pd.DataFrame()
        
        # DEBUG: Mostrar primeiras linhas para identificar colunas
        with st.sidebar.expander("🔍 Primeiras 3 linhas do arquivo"):
            st.write(df_raw.head(3))
        
        # 1. TENTAR IDENTIFICAR A COLUNA DE DATA
        data_encontrada = False
        for i in range(min(3, len(df_raw.columns))):  # Verificar primeiras 3 colunas
            col_teste = df_raw.iloc[:, i]
            # Tentar converter para data
            try:
                temp_dates = pd.to_datetime(col_teste, errors='coerce')
                if temp_dates.notna().sum() > len(col_teste) * 0.5:  # Se mais de 50% são datas válidas
                    df["Data"] = temp_dates
                    st.sidebar.success(f"✅ Data encontrada na coluna {i+1}")
                    data_encontrada = True
                    data_col_idx = i
                    break
            except:
                continue
        
        if not data_encontrada:
            st.sidebar.warning("⚠️ Coluna de data não encontrada automaticamente")
            # Usar primeira coluna como data
            df["Data"] = pd.to_datetime(df_raw.iloc[:, 0], errors='coerce')
            data_col_idx = 0
        
        # 2. IDENTIFICAR CLIENTE - Procurar coluna com texto que parece nome
        cliente_encontrado = False
        for i in range(len(df_raw.columns)):
            if i == data_col_idx:
                continue  # Pular coluna de data
            
            col_teste = df_raw.iloc[:, i]
            # Verificar se a coluna tem strings que parecem nomes de clientes
            if col_teste.dtype == 'object':
                sample_values = col_teste.dropna().head(5).astype(str).tolist()
                # Verificar se alguns valores parecem nomes (contêm letras e não são apenas números)
                if any(any(c.isalpha() for c in str(val)) for val in sample_values):
                    df["Cliente"] = col_teste.fillna("Desconhecido").astype(str).str.strip()
                    st.sidebar.success(f"✅ Cliente encontrado na coluna {i+1}")
                    cliente_encontrado = True
                    cliente_col_idx = i
                    break
        
        if not cliente_encontrado:
            st.sidebar.warning("⚠️ Cliente não identificado automaticamente")
            # Usar segunda coluna (após data)
            col_idx = 1 if data_col_idx == 0 else 0
            if len(df_raw.columns) > col_idx:
                df["Cliente"] = df_raw.iloc[:, col_idx].fillna("Cliente Desconhecido").astype(str).str.strip()
            else:
                df["Cliente"] = "Cliente Desconhecido"
        
        # 3. IDENTIFICAR ARTIGO - Procurar coluna com códigos/nomes de produtos
        artigo_encontrado = False
        for i in range(len(df_raw.columns)):
            if i in [data_col_idx, cliente_col_idx if 'cliente_col_idx' in locals() else -1]:
                continue  # Pular colunas já usadas
            
            col_teste = df_raw.iloc[:, i]
            if len(col_teste.dropna()) > 0:
                df["Artigo"] = col_teste.fillna("Artigo Desconhecido").astype(str).str.strip()
                st.sidebar.success(f"✅ Artigo encontrado na coluna {i+1}")
                artigo_encontrado = True
                artigo_col_idx = i
                break
        
        if not artigo_encontrado:
            st.sidebar.warning("⚠️ Artigo não identificado automaticamente")
            # Usar próxima coluna disponível
            used_cols = [data_col_idx]
            if 'cliente_col_idx' in locals():
                used_cols.append(cliente_col_idx)
            
            for i in range(len(df_raw.columns)):
                if i not in used_cols and len(df_raw.columns) > i:
                    df["Artigo"] = df_raw.iloc[:, i].fillna("Artigo Desconhecido").astype(str).str.strip()
                    break
            else:
                df["Artigo"] = "Artigo Desconhecido"
        
        # 4. IDENTIFICAR QUANTIDADE - Procurar coluna numérica
        quantidade_encontrada = False
        for i in range(len(df_raw.columns)):
            if i in [data_col_idx, 
                    cliente_col_idx if 'cliente_col_idx' in locals() else -1,
                    artigo_col_idx if 'artigo_col_idx' in locals() else -1]:
                continue
            
            col_teste = df_raw.iloc[:, i]
            if pd.api.types.is_numeric_dtype(col_teste):
                df["Quantidade"] = pd.to_numeric(col_teste, errors='coerce').fillna(1)
                st.sidebar.success(f"✅ Quantidade encontrada na coluna {i+1}")
                quantidade_encontrada = True
                quantidade_col_idx = i
                break
        
        if not quantidade_encontrada:
            st.sidebar.warning("⚠️ Quantidade não identificada automaticamente")
            df["Quantidade"] = 1  # Valor padrão
        
        # 5. IDENTIFICAR VALOR - Procurar outra coluna numérica
        valor_encontrado = False
        for i in range(len(df_raw.columns)):
            if i in [data_col_idx,
                    cliente_col_idx if 'cliente_col_idx' in locals() else -1,
                    artigo_col_idx if 'artigo_col_idx' in locals() else -1,
                    quantidade_col_idx if 'quantidade_col_idx' in locals() else -1]:
                continue
            
            col_teste = df_raw.iloc[:, i]
            if pd.api.types.is_numeric_dtype(col_teste):
                df["Valor"] = pd.to_numeric(col_teste, errors='coerce').fillna(0)
                st.sidebar.success(f"✅ Valor encontrado na coluna {i+1}")
                valor_encontrado = True
                valor_col_idx = i
                break
        
        if not valor_encontrado:
            st.sidebar.warning("⚠️ Valor não identificado automaticamente")
            # Criar valor fictício
            df["Valor"] = df["Quantidade"] * np.random.uniform(10, 100, len(df))
        
        # 6. IDENTIFICAR COMERCIAL - Procurar última coluna com texto
        comercial_encontrado = False
        # Primeiro tentar coluna 8 (índice 7) que é mencionada no código original
        if len(df_raw.columns) > 7:
            col_teste = df_raw.iloc[:, 7]
            if col_teste.dtype == 'object' or len(col_teste.dropna()) > 0:
                df["Comercial"] = col_teste.fillna("Comercial Desconhecido").astype(str).str.strip()
                st.sidebar.success(f"✅ Comercial encontrado na coluna 8")
                comercial_encontrado = True
        
        if not comercial_encontrado:
            # Procurar qualquer coluna não usada com texto
            for i in range(len(df_raw.columns)-1, -1, -1):  # Começar do final
                if i in [data_col_idx,
                        cliente_col_idx if 'cliente_col_idx' in locals() else -1,
                        artigo_col_idx if 'artigo_col_idx' in locals() else -1,
                        quantidade_col_idx if 'quantidade_col_idx' in locals() else -1,
                        valor_col_idx if 'valor_col_idx' in locals() else -1]:
                    continue
                
                col_teste = df_raw.iloc[:, i]
                if col_teste.dtype == 'object' and len(col_teste.dropna()) > 0:
                    df["Comercial"] = col_teste.fillna("Comercial Desconhecido").astype(str).str.strip()
                    break
            else:
                df["Comercial"] = "Comercial Desconhecido"
        
        # VERIFICAR E CORRIGIR DATAS
        datas_invalidas = df["Data"].isna().sum()
        if datas_invalidas > 0:
            st.sidebar.warning(f"⚠️ {datas_invalidas} datas inválidas")
        
        # Verificar anos extremos
        if df["Data"].notna().any():
            anos = df["Data"].dt.year.unique()
            st.sidebar.write(f"📅 Anos encontrados: {sorted(anos)}")
            
            # Corrigir anos extremos
            mask_ano_extremo = (df["Data"].dt.year > 2100) | (df["Data"].dt.year < 2000)
            if mask_ano_extremo.any():
                st.sidebar.warning(f"⚠️ Corrigindo {mask_ano_extremo.sum()} datas com anos extremos")
                ano_atual = datetime.now().year
                for idx in df[mask_ano_extremo].index:
                    try:
                        df.loc[idx, "Data"] = pd.to_datetime(
                            f"{ano_atual}-{df.loc[idx, 'Data'].month:02d}-{df.loc[idx, 'Data'].day:02d}"
                        )
                    except:
                        # Se falhar, usar data padrão
                        df.loc[idx, "Data"] = pd.Timestamp(f"{ano_atual}-01-01")
        
        # Se não há datas válidas, criar datas realistas
        if df["Data"].isna().all() or len(df["Data"].dropna()) == 0:
            st.sidebar.warning("⚠️ Criando datas realistas...")
            np.random.seed(42)
            data_inicio = datetime(2023, 1, 1)
            n = len(df)
            dias_aleatorios = np.random.randint(0, 730, n)  # 2 anos
            df["Data"] = [data_inicio + pd.Timedelta(days=int(d)) for d in dias_aleatorios]
        
        # Remover registros inválidos
        df = df[df["Data"].notna()].copy()
        df = df[df["Quantidade"] > 0].copy()
        df = df[df["Valor"] > 0].copy()
        
        # Adicionar colunas de tempo
        df["Ano"] = df["Data"].dt.year
        df["Mes"] = df["Data"].dt.month
        df["MesNumero"] = df["Data"].dt.month
        df["MesNome"] = df["Data"].dt.strftime("%b")
        df["Dia"] = df["Data"].dt.day
        df["Data_Str"] = df["Data"].dt.strftime("%Y-%m-%d")
        
        # MOSTRAR AMOSTRA DOS DADOS PROCESSADOS
        with st.sidebar.expander("🔍 Amostra dos dados processados"):
            st.write(df[["Data", "Cliente", "Artigo", "Quantidade", "Valor", "Comercial"]].head())
        
        st.sidebar.success(f"✅ Dados processados: {len(df)} registros válidos")
        st.sidebar.write(f"📊 Período: {df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}")
        st.sidebar.write(f"📅 Anos disponíveis: {sorted(df['Ano'].unique())}")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        
        # Criar dados de exemplo
        st.info("📊 Criando dados de exemplo...")
        
        np.random.seed(42)
        n = 500
        
        data_inicio = datetime(2023, 1, 1)
        data_fim = datetime(2024, 12, 31)
        date_range = pd.date_range(data_inicio, data_fim, freq='D')
        datas = np.random.choice(date_range, n)
        
        df = pd.DataFrame({
            "Data": sorted(datas),
            "Cliente": np.random.choice(["Cliente A", "Cliente B", "Cliente C", "Cliente D", 
                                        "Cliente E", "Cliente F", "Cliente G"], n),
            "Artigo": np.random.choice(["Produto 001", "Produto 002", "Produto 003", 
                                       "Produto 004", "Produto 005", "Produto 006"], n),
            "Quantidade": np.random.randint(1, 20, n),
            "Valor": np.random.uniform(50, 500, n) * np.random.randint(1, 3, n),
            "Comercial": np.random.choice(["João Silva", "Maria Santos", "Carlos Oliveira"], n)
        })
        
        df["Ano"] = df["Data"].dt.year
        df["Mes"] = df["Data"].dt.month
        df["MesNumero"] = df["Data"].dt.month
        df["MesNome"] = df["Data"].dt.strftime("%b")
        df["Dia"] = df["Data"].dt.day
        df["Data_Str"] = df["Data"].dt.strftime("%Y-%m-%d")
        
        return df

df = load_data()

# === SIDEBAR – FILTROS ===
st.sidebar.header("🎛️ Filtros")

# Mostrar estatísticas iniciais
st.sidebar.write(f"**Clientes únicos:** {df['Cliente'].nunique()}")
st.sidebar.write(f"**Artigos únicos:** {df['Artigo'].nunique()}")
st.sidebar.write(f"**Comerciais:** {df['Comercial'].nunique()}")

# 1. FILTRO DE ANO
st.sidebar.subheader("📅 Ano")
anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)

# Filtrar anos realistas
anos_realistas = [ano for ano in anos_disponiveis if 2000 <= ano <= datetime.now().year + 1]
if anos_realistas:
    anos_disponiveis = sorted(anos_realistas, reverse=True)
    ano_padrao = [anos_disponiveis[0]]
else:
    ano_atual = datetime.now().year
    anos_disponiveis = [ano_atual - 1, ano_atual]
    ano_padrao = [ano_atual]

anos_selecionados = st.sidebar.multiselect(
    "Selecionar anos:",
    options=anos_disponiveis,
    default=ano_padrao,
    help="Selecione um ou mais anos"
)

if not anos_selecionados:
    anos_selecionados = anos_disponiveis

# 2. FILTRO DE MÊS
st.sidebar.subheader("📆 Mês")

meses_nomes = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

meses_abreviados = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

# Obter meses disponíveis
if len(anos_selecionados) > 0:
    mask = df["Ano"].isin(anos_selecionados)
    meses_disponiveis_numeros = sorted(df[mask]["MesNumero"].unique())
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
    meses_selecionados = meses_disponiveis_numeros

# 3. FILTRO DE COMERCIAL
st.sidebar.subheader("👨‍💼 Comercial")

mask = df["Ano"].isin(anos_selecionados) & df["MesNumero"].isin(meses_selecionados)
comerciais_disponiveis = sorted(df[mask]["Comercial"].unique())

todos_comerciais = st.sidebar.checkbox("Todos os comerciais", value=True, key="todos_comerciais")

if todos_comerciais:
    comerciais_selecionados = comerciais_disponiveis
else:
    comerciais_selecionados = st.sidebar.multiselect(
        "Selecionar comerciais:",
        options=comerciais_disponiveis,
        default=comerciais_disponiveis[:min(3, len(comerciais_disponiveis))],
        help="Selecione um ou mais comerciais"
    )
    
    if not comerciais_selecionados:
        comerciais_selecionados = comerciais_disponiveis

# 4. FILTRO DE CLIENTE
st.sidebar.subheader("🏢 Cliente")

mask = (df["Ano"].isin(anos_selecionados) & 
        df["MesNumero"].isin(meses_selecionados) & 
        df["Comercial"].isin(comerciais_selecionados))

clientes_disponiveis = sorted(df[mask]["Cliente"].unique())

todos_clientes = st.sidebar.checkbox("Todos os clientes", value=True, key="todos_clientes")

if todos_clientes:
    clientes_selecionados = clientes_disponiveis
else:
    clientes_selecionados = st.sidebar.multiselect(
        "Selecionar clientes:",
        options=clientes_disponiveis,
        default=clientes_disponiveis[:min(5, len(clientes_disponiveis))],
        help="Selecione um ou mais clientes"
    )
    
    if not clientes_selecionados:
        clientes_selecionados = clientes_disponiveis

# 5. FILTRO DE ARTIGO
st.sidebar.subheader("📦 Artigo")

mask = (df["Ano"].isin(anos_selecionados) & 
        df["MesNumero"].isin(meses_selecionados) & 
        df["Comercial"].isin(comerciais_selecionados) &
        df["Cliente"].isin(clientes_selecionados))

artigos_disponiveis = sorted(df[mask]["Artigo"].unique())

todos_artigos = st.sidebar.checkbox("Todos os artigos", value=True, key="todos_artigos")

if todos_artigos:
    artigos_selecionados = artigos_disponiveis
else:
    artigos_selecionados = st.sidebar.multiselect(
        "Selecionar artigos:",
        options=artigos_disponiveis,
        default=artigos_disponiveis[:min(5, len(artigos_disponiveis))],
        help="Selecione um ou mais artigos"
    )
    
    if not artigos_selecionados:
        artigos_selecionados = artigos_disponiveis

# APLICAR FILTROS
df_filtrado = df[
    df["Ano"].isin(anos_selecionados) &
    df["MesNumero"].isin(meses_selecionados) &
    df["Comercial"].isin(comerciais_selecionados) &
    df["Cliente"].isin(clientes_selecionados) &
    df["Artigo"].isin(artigos_selecionados)
].copy()

# Botão para resetar filtros
if st.sidebar.button("🔄 Resetar Filtros"):
    st.rerun()

# Mostrar estatísticas dos filtros
st.sidebar.divider()
st.sidebar.subheader("📋 Estatísticas Filtradas")
st.sidebar.write(f"**Registros:** {len(df_filtrado):,}")
if len(df_filtrado) > 0:
    st.sidebar.write(f"**Período:** {anos_selecionados[0] if len(anos_selecionados) == 1 else 'Múltiplos'}")
    st.sidebar.write(f"**Clientes:** {df_filtrado['Cliente'].nunique()}")
    st.sidebar.write(f"**Artigos:** {df_filtrado['Artigo'].nunique()}")
else:
    st.sidebar.write("**Período:** N/A")

# === CÁLCULO DOS KPIs ===
if not df_filtrado.empty:
    # KPIs Básicos
    total_vendas_eur = df_filtrado["Valor"].sum()
    total_quantidade = df_filtrado["Quantidade"].sum()
    num_entidades = df_filtrado["Cliente"].nunique()
    num_comerciais = df_filtrado["Comercial"].nunique()
    num_artigos = df_filtrado["Artigo"].nunique()
    num_transacoes = len(df_filtrado)
    dias_com_vendas = df_filtrado["Data_Str"].nunique()
    
    # KPIs Calculados
    ticket_medio_eur = total_vendas_eur / num_transacoes if num_transacoes > 0 else 0
    preco_medio_unitario = total_vendas_eur / total_quantidade if total_quantidade > 0 else 0
    venda_media_transacao = total_vendas_eur / num_transacoes if num_transacoes > 0 else 0
    quantidade_media_transacao = total_quantidade / num_transacoes if num_transacoes > 0 else 0
    venda_media_dia = total_vendas_eur / dias_com_vendas if dias_com_vendas > 0 else 0
    
    # Ticket Médio Mensal
    if not df_filtrado.empty:
        vendas_mensais_group = df_filtrado.groupby(["Ano", "MesNumero"])["Valor"].sum()
        if not vendas_mensais_group.empty:
            ticket_medio_mes = vendas_mensais_group.mean()
        else:
            ticket_medio_mes = 0
    else:
        ticket_medio_mes = 0
else:
    # Valores padrão
    total_vendas_eur = 0
    total_quantidade = 0
    num_entidades = 0
    num_comerciais = 0
    num_artigos = 0
    num_transacoes = 0
    dias_com_vendas = 0
    ticket_medio_eur = 0
    preco_medio_unitario = 0
    venda_media_transacao = 0
    quantidade_media_transacao = 0
    venda_media_dia = 0
    ticket_medio_mes = 0

# === DISPLAY DOS KPIs ===
st.subheader("📊 KPIs Principais")

# Linha 1 de KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Total Vendas (€)",
        f"€{total_vendas_eur:,.0f}" if total_vendas_eur >= 1000 else f"€{total_vendas_eur:,.2f}",
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

# === GRÁFICOS ===
if not df_filtrado.empty:
    st.subheader("📈 Análise Gráfica")
    
    # Mostrar amostra dos dados filtrados
    with st.expander("🔍 Ver amostra dos dados filtrados"):
        st.write(df_filtrado[["Data", "Cliente", "Artigo", "Quantidade", "Valor", "Comercial"]].head(10))
    
    # 1. Evolução mensal de vendas
    vendas_mensais = df_filtrado.groupby(["Ano", "MesNumero"]).agg({
        "Valor": "sum",
        "Quantidade": "sum"
    }).reset_index()
    
    if not vendas_mensais.empty:
        vendas_mensais = vendas_mensais.sort_values(["Ano", "MesNumero"])
        vendas_mensais["MesNome"] = vendas_mensais["MesNumero"].map(meses_abreviados)
        vendas_mensais["Periodo"] = vendas_mensais["Ano"].astype(str) + "-" + vendas_mensais["MesNome"]
        
        fig1, ax1 = plt.subplots(figsize=(14, 6))
        
        x = range(len(vendas_mensais))
        width = 0.35
        
        bars = ax1.bar([i - width/2 for i in x], vendas_mensais["Valor"], width, 
                       label='Valor (€)', color='#2E86AB', alpha=0.7)
        
        ax1.set_xlabel("Período")
        ax1.set_ylabel("Valor (€)", color='#2E86AB')
        ax1.tick_params(axis='y', labelcolor='#2E86AB')
        ax1.set_title("Evolução Mensal de Vendas", fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        
        if len(vendas_mensais) > 6:
            ax1.set_xticklabels(vendas_mensais["Periodo"], rotation=45, ha='right', fontsize=9)
        else:
            ax1.set_xticklabels(vendas_mensais["Periodo"])
        
        ax2 = ax1.twinx()
        line = ax2.plot(x, vendas_mensais["Quantidade"], 'o-', color='#A23B72', 
                        linewidth=2, markersize=6, label='Quantidade')
        ax2.set_ylabel('Quantidade', color='#A23B72')
        ax2.tick_params(axis='y', labelcolor='#A23B72')
        
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax1.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        st.pyplot(fig1)
    else:
        st.info("ℹ️ Não há dados suficientes para o gráfico de evolução mensal.")
    
    # 2. Top Clientes
    if len(df_filtrado["Cliente"].unique()) > 0:
        st.subheader("🏆 Top Clientes")
        
        top_clientes = df_filtrado.groupby("Cliente").agg({
            "Valor": "sum",
            "Quantidade": "sum",
            "Data": "count"
        }).nlargest(min(10, len(df_filtrado["Cliente"].unique())), "Valor")
        
        top_clientes.columns = ["Total Vendas (€)", "Total Quantidade", "Nº Transações"]
        
        fig2, (ax2_1, ax2_2) = plt.subplots(1, 2, figsize=(16, 6))
        
        ax2_1.barh(range(len(top_clientes)), top_clientes["Total Vendas (€)"], 
                   color='#A23B72', alpha=0.7)
        ax2_1.set_yticks(range(len(top_clientes)))
        ax2_1.set_yticklabels(top_clientes.index)
        ax2_1.invert_yaxis()
        ax2_1.set_xlabel("Total Vendas (€)")
        ax2_1.set_title("Top Clientes por Valor", fontsize=12, fontweight='bold')
        ax2_1.grid(True, alpha=0.3, axis='x')
        
        for i, v in enumerate(top_clientes["Total Vendas (€)"]):
            ax2_1.text(v, i, f' €{v:,.0f}', va='center', fontsize=9)
        
        if top_clientes["Total Vendas (€)"].sum() > 0:
            ax2_2.pie(top_clientes["Total Vendas (€)"], labels=top_clientes.index, 
                     autopct='%1.1f%%', startangle=90, colors=plt.cm.Set3(np.linspace(0, 1, len(top_clientes))))
            ax2_2.set_title("Participação no Total de Vendas", fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig2)
    
    # 3. Top Artigos
    if len(df_filtrado["Artigo"].unique()) > 0:
        st.subheader("📦 Top Artigos")
        
        top_artigos = df_filtrado.groupby("Artigo").agg({
            "Valor": "sum",
            "Quantidade": "sum"
        }).nlargest(min(10, len(df_filtrado["Artigo"].unique())), "Valor")
        
        if not top_artigos.empty:
            fig3, ax3 = plt.subplots(figsize=(14, 6))
            
            x = range(len(top_artigos))
            width = 0.35
            
            ax3.bar([i - width/2 for i in x], top_artigos["Valor"], width, 
                    label='Valor (€)', color='#F18F01', alpha=0.7)
            ax3.bar([i + width/2 for i in x], top_artigos["Quantidade"], width, 
                    label='Quantidade', color='#73AB84', alpha=0.7)
            
            ax3.set_xlabel("Artigo")
            ax3.set_ylabel("Valor/Quantidade")
            ax3.set_title("Top Artigos por Performance", fontsize=14, fontweight='bold')
            ax3.set_xticks(x)
            ax3.set_xticklabels(top_artigos.index, rotation=45, ha='right', fontsize=9)
            ax3.legend()
            ax3.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            st.pyplot(fig3)
    
    # 4. Desempenho por Comercial
    if len(df_filtrado["Comercial"].unique()) > 0:
        st.subheader("👨‍💼 Desempenho por Comercial")
        
        desempenho_comercial = df_filtrado.groupby("Comercial").agg({
            "Valor": ["sum", "mean", "count"],
            "Cliente": "nunique"
        }).round(2)
        
        if len(desempenho_comercial) > 0:
            desempenho_comercial.columns = ["Total Vendas (€)", "Ticket Médio (€)", 
                                            "Nº Transações", "Clientes Únicos"]
            
            fig4, ax4 = plt.subplots(figsize=(12, 6))
            
            comerciais = desempenho_comercial.index.tolist()
            x = range(len(comerciais))
            
            ax4.bar(x, desempenho_comercial["Total Vendas (€)"], color='#2E86AB', alpha=0.7)
            
            ax4.set_xlabel("Comercial")
            ax4.set_ylabel("Total Vendas (€)")
            ax4.set_title("Desempenho por Comercial", fontsize=14, fontweight='bold')
            ax4.set_xticks(x)
            ax4.set_xticklabels(comerciais, rotation=45, ha='right')
            ax4.grid(True, alpha=0.3, axis='y')
            
            for i, v in enumerate(desempenho_comercial["Total Vendas (€)"]):
                ax4.text(i, v, f'€{v:,.0f}', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            st.pyplot(fig4)
    
else:
    st.warning("⚠️ Não há dados disponíveis com os filtros selecionados.")
    st.info("💡 Tente ajustar os filtros na sidebar para ver os dados.")

st.divider()

# === EXPORTAR DADOS ===
if not df_filtrado.empty:
    st.subheader("📤 Exportar Dados")
    
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
        csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Dados Filtrados (CSV)",
            data=csv_data,
            file_name=f"dados_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            resumo_kpis.to_excel(writer, sheet_name='KPIs', index=False)
            df_filtrado.to_excel(writer, sheet_name='Dados', index=False)
            if 'vendas_mensais' in locals() and not vendas_mensais.empty:
                vendas_mensais.to_excel(writer, sheet_name='Vendas_Mensais', index=False)
        
        excel_data = output.getvalue()
        
        st.download_button(
            label="📊 Download Relatório Completo (Excel)",
            data=excel_data,
            file_name=f"relatorio_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# === RODAPÉ ===
st.divider()
st.success("✅ Dashboard carregado com sucesso!")

st.info("""
💡 **Como usar este dashboard:**
1. **Filtros na sidebar:** Selecione anos, meses, comerciais, clientes e artigos
2. **KPIs:** Veja os 12 indicadores principais no topo
3. **Gráficos:** Analise evolução temporal e performance
4. **Exportar:** Baixe os dados para análises externas
""")
