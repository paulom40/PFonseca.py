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
        # Tentar ler o arquivo Excel
        uploaded_file = "ResumoTR.xlsx"
        
        # Ler arquivo
        df_raw = pd.read_excel(uploaded_file)
        
        st.sidebar.write("### 🔍 Debug - Estrutura do Arquivo")
        st.sidebar.write(f"**Total de colunas:** {len(df_raw.columns)}")
        st.sidebar.write(f"**Total de linhas:** {len(df_raw)}")
        
        # Mostrar colunas
        with st.sidebar.expander("Ver todas as colunas"):
            for i, col in enumerate(df_raw.columns):
                sample = df_raw[col].dropna().head(3).tolist()
                st.write(f"{i}: **{col}** → {sample}")
        
        # Criar DataFrame limpo
        df = pd.DataFrame()
        
        # === MAPEAR COLUNAS AUTOMATICAMENTE ===
        
        # 1. PROCURAR COLUNA DE DATA
        data_col = None
        for col in df_raw.columns:
            if any(keyword in str(col).lower() for keyword in ['data', 'date', 'dt']):
                try:
                    temp = pd.to_datetime(df_raw[col], errors='coerce')
                    if temp.notna().sum() > len(df_raw) * 0.5:
                        data_col = col
                        break
                except:
                    continue
        
        # Se não encontrou por nome, tentar por tipo
        if data_col is None:
            for col in df_raw.columns:
                try:
                    temp = pd.to_datetime(df_raw[col], errors='coerce')
                    if temp.notna().sum() > len(df_raw) * 0.5:
                        data_col = col
                        break
                except:
                    continue
        
        if data_col:
            df["Data"] = pd.to_datetime(df_raw[data_col], errors='coerce')
            st.sidebar.success(f"✅ Data encontrada: {data_col}")
        else:
            st.sidebar.error("❌ Coluna de data não encontrada")
            return pd.DataFrame()
        
        # 2. PROCURAR COLUNA DE CLIENTE
        cliente_col = None
        for col in df_raw.columns:
            if any(keyword in str(col).lower() for keyword in ['cliente', 'client', 'entidade', 'empresa']):
                cliente_col = col
                break
        
        if cliente_col:
            df["Cliente"] = df_raw[cliente_col].fillna("Desconhecido").astype(str).str.strip()
            st.sidebar.success(f"✅ Cliente encontrado: {cliente_col}")
        else:
            st.sidebar.warning("⚠️ Coluna de cliente não encontrada")
            df["Cliente"] = "Cliente Desconhecido"
        
        # 3. PROCURAR COLUNA DE ARTIGO
        artigo_col = None
        for col in df_raw.columns:
            if any(keyword in str(col).lower() for keyword in ['artigo', 'produto', 'item', 'artig', 'art']):
                artigo_col = col
                break
        
        if artigo_col:
            df["Artigo"] = df_raw[artigo_col].fillna("Desconhecido").astype(str).str.strip()
            st.sidebar.success(f"✅ Artigo encontrado: {artigo_col}")
        else:
            st.sidebar.warning("⚠️ Coluna de artigo não encontrada")
            df["Artigo"] = "Artigo Desconhecido"
        
        # 4. PROCURAR COLUNA DE QUANTIDADE
        quantidade_col = None
        for col in df_raw.columns:
            if any(keyword in str(col).lower() for keyword in ['quantidade', 'qtd', 'qty', 'quant']):
                try:
                    if pd.api.types.is_numeric_dtype(df_raw[col]):
                        quantidade_col = col
                        break
                except:
                    continue
        
        if quantidade_col:
            df["Quantidade"] = pd.to_numeric(df_raw[quantidade_col], errors='coerce').fillna(0)
            st.sidebar.success(f"✅ Quantidade encontrada: {quantidade_col}")
        else:
            st.sidebar.warning("⚠️ Coluna de quantidade não encontrada, usando 1")
            df["Quantidade"] = 1
        
        # 5. PROCURAR COLUNA DE VALOR
        valor_col = None
        for col in df_raw.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['valor', 'value', 'price', 'preco', 'preço', 'total', 'vlr']):
                try:
                    if pd.api.types.is_numeric_dtype(df_raw[col]):
                        valor_col = col
                        break
                except:
                    continue
        
        if valor_col:
            df["Valor"] = pd.to_numeric(df_raw[valor_col], errors='coerce').fillna(0)
            st.sidebar.success(f"✅ Valor encontrado: {valor_col}")
        else:
            st.sidebar.warning("⚠️ Coluna de valor não encontrada")
            df["Valor"] = df["Quantidade"] * 10
        
        # 6. PROCURAR COLUNA DE COMERCIAL
        comercial_col = None
        for col in df_raw.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['comercial', 'vendedor', 'seller', 'comerci']):
                comercial_col = col
                break
        
        if comercial_col:
            df["Comercial"] = df_raw[comercial_col].fillna("Desconhecido").astype(str).str.strip()
            st.sidebar.success(f"✅ Comercial encontrado: {comercial_col}")
        else:
            st.sidebar.warning("⚠️ Coluna de comercial não encontrada")
            df["Comercial"] = "Comercial Desconhecido"
        
        # === LIMPEZA DE DADOS ===
        
        # Remover linhas com datas inválidas
        linhas_antes = len(df)
        df = df[df["Data"].notna()].copy()
        if len(df) < linhas_antes:
            st.sidebar.warning(f"⚠️ Removidas {linhas_antes - len(df)} linhas com datas inválidas")
        
        # Remover valores negativos ou zero
        df = df[df["Quantidade"] > 0].copy()
        df = df[df["Valor"] > 0].copy()
        
        # Remover "Desconhecido" se houver dados válidos
        if (df["Cliente"] != "Desconhecido").any():
            df = df[df["Cliente"] != "Desconhecido"].copy()
        
        if (df["Artigo"] != "Desconhecido").any():
            df = df[df["Artigo"] != "Desconhecido"].copy()
        
        # === CRIAR COLUNAS DE TEMPO ===
        df["Ano"] = df["Data"].dt.year
        df["Mes"] = df["Data"].dt.month
        df["MesNumero"] = df["Data"].dt.month
        df["Dia"] = df["Data"].dt.day
        df["MesNome"] = df["Data"].dt.strftime("%b")
        df["Data_Str"] = df["Data"].dt.strftime("%Y-%m-%d")
        
        # === ESTATÍSTICAS FINAIS ===
        st.sidebar.write("### 📊 Dados Carregados")
        st.sidebar.write(f"**Total de registros:** {len(df):,}")
        
        if len(df) > 0:
            st.sidebar.write(f"**Período:** {df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}")
            st.sidebar.write(f"**Anos:** {sorted(df['Ano'].unique())}")
            st.sidebar.write(f"**Meses únicos:** {df['MesNumero'].nunique()}")
            st.sidebar.write(f"**Clientes:** {df['Cliente'].nunique()}")
            st.sidebar.write(f"**Artigos:** {df['Artigo'].nunique()}")
            st.sidebar.write(f"**Comerciais:** {df['Comercial'].nunique()}")
            
            # Mostrar amostra
            with st.sidebar.expander("Ver amostra dos dados processados"):
                st.dataframe(df.head(10))
        
        return df
        
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao carregar dados: {str(e)}")
        st.sidebar.write("Criando dados de exemplo...")
        
        # Dados de exemplo robustos
        np.random.seed(42)
        n = 1000
        
        # Criar datas variadas (2023-2024)
        start_date = pd.Timestamp('2023-01-01')
        end_date = pd.Timestamp('2024-12-31')
        dates = pd.date_range(start_date, end_date, freq='D')
        random_dates = np.random.choice(dates, n)
        
        df = pd.DataFrame({
            "Data": random_dates,
            "Cliente": np.random.choice([
                "Empresa A Lda", "Empresa B SA", "Cliente C", "Distribuidor D",
                "Fornecedor E", "Parceiro F", "Cliente G", "Empresa H",
                "Grupo I", "Sociedade J", "Firma K", "Cliente L"
            ], n),
            "Artigo": np.random.choice([
                "Produto 001", "Produto 002", "Produto 003", "Produto 004",
                "Produto 005", "Produto 006", "Produto 007", "Produto 008",
                "Item 009", "Item 010", "Item 011", "Item 012",
                "Artigo 013", "Artigo 014", "Artigo 015"
            ], n),
            "Quantidade": np.random.randint(1, 100, n),
            "Valor": np.random.uniform(10, 1000, n),
            "Comercial": np.random.choice([
                "João Silva", "Maria Santos", "Carlos Oliveira",
                "Ana Costa", "Pedro Almeida", "Sofia Rodrigues",
                "Miguel Ferreira", "Beatriz Martins"
            ], n)
        })
        
        # Adicionar colunas de tempo
        df["Ano"] = df["Data"].dt.year
        df["Mes"] = df["Data"].dt.month
        df["MesNumero"] = df["Data"].dt.month
        df["MesNome"] = df["Data"].dt.strftime("%b")
        df["Dia"] = df["Data"].dt.day
        df["Data_Str"] = df["Data"].dt.strftime("%Y-%m-%d")
        
        st.sidebar.warning("⚠️ Usando dados de exemplo")
        
        return df

# Tentar ler arquivo do usuário primeiro
try:
    uploaded_file = st.file_uploader("📁 Carregar arquivo Excel (ResumoTR.xlsx)", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        # Salvar temporariamente
        with open("ResumoTR.xlsx", "wb") as f:
            f.write(uploaded_file.getbuffer())
        df = load_data()
    else:
        # Tentar carregar do GitHub
        @st.cache_data
        def load_from_github():
            url = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"
            return pd.read_excel(url)
        
        try:
            df_raw = load_from_github()
            # Processar da mesma forma
            with open("ResumoTR.xlsx", "wb") as f:
                df_raw.to_excel(f, index=False)
            df = load_data()
        except:
            st.info("💡 Por favor, faça upload do arquivo Excel ou os dados de exemplo serão usados")
            df = load_data()
except:
    df = load_data()

# === FILTROS DINÂMICOS ===
st.sidebar.header("🎛️ Filtros")

meses_nomes = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

meses_abreviados = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
}

if len(df) > 0:
    # Resetar filtros
    if st.sidebar.button("🔄 Resetar Todos os Filtros", type="secondary"):
        st.rerun()
    
    st.sidebar.divider()
    
    # === 1. FILTRO DE ANO ===
    st.sidebar.subheader("📅 Período: Ano")
    anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)
    st.sidebar.write(f"📊 **{len(anos_disponiveis)} anos disponíveis:** {anos_disponiveis}")
    
    anos_selecionados = st.sidebar.multiselect(
        "Selecionar anos:",
        options=anos_disponiveis,
        default=anos_disponiveis,
        key="filtro_anos"
    )
    
    if not anos_selecionados:
        anos_selecionados = anos_disponiveis
    
    # Filtro 1: Anos
    df_filtrado = df[df["Ano"].isin(anos_selecionados)].copy()
    st.sidebar.caption(f"✓ {len(df_filtrado):,} registros após filtro de ano")
    
    # === 2. FILTRO DE MÊS ===
    st.sidebar.subheader("📆 Período: Mês")
    meses_disponiveis = sorted(df_filtrado["MesNumero"].unique())
    st.sidebar.write(f"📊 **{len(meses_disponiveis)} meses disponíveis:** {[meses_nomes[m] for m in meses_disponiveis]}")
    
    opcoes_meses = [meses_nomes[mes] for mes in meses_disponiveis]
    meses_selecionados_nomes = st.sidebar.multiselect(
        "Selecionar meses:",
        options=opcoes_meses,
        default=opcoes_meses,
        key="filtro_meses"
    )
    
    nomes_para_meses = {v: k for k, v in meses_nomes.items()}
    meses_selecionados = [nomes_para_meses[nome] for nome in meses_selecionados_nomes] if meses_selecionados_nomes else meses_disponiveis
    
    # Filtro 2: Meses
    df_filtrado = df_filtrado[df_filtrado["MesNumero"].isin(meses_selecionados)].copy()
    st.sidebar.caption(f"✓ {len(df_filtrado):,} registros após filtro de mês")
    
    # === 3. FILTRO DE COMERCIAL ===
    st.sidebar.subheader("👨‍💼 Comercial")
    comerciais_disponiveis = sorted(df_filtrado["Comercial"].unique())
    st.sidebar.write(f"📊 **{len(comerciais_disponiveis)} comerciais disponíveis**")
    
    todos_comerciais = st.sidebar.checkbox("✓ Todos os comerciais", value=True, key="cb_todos_comerciais")
    
    if todos_comerciais:
        comerciais_selecionados = comerciais_disponiveis
    else:
        comerciais_selecionados = st.sidebar.multiselect(
            "Selecionar comerciais:",
            options=comerciais_disponiveis,
            default=comerciais_disponiveis[:min(3, len(comerciais_disponiveis))],
            key="filtro_comerciais"
        )
        if not comerciais_selecionados:
            comerciais_selecionados = comerciais_disponiveis
    
    # Filtro 3: Comerciais
    df_filtrado = df_filtrado[df_filtrado["Comercial"].isin(comerciais_selecionados)].copy()
    st.sidebar.caption(f"✓ {len(df_filtrado):,} registros após filtro de comercial")
    
    # === 4. FILTRO DE CLIENTE ===
    st.sidebar.subheader("🏢 Cliente")
    clientes_disponiveis = sorted(df_filtrado["Cliente"].unique())
    st.sidebar.write(f"📊 **{len(clientes_disponiveis)} clientes disponíveis**")
    
    todos_clientes = st.sidebar.checkbox("✓ Todos os clientes", value=True, key="cb_todos_clientes")
    
    if todos_clientes:
        clientes_selecionados = clientes_disponiveis
    else:
        clientes_selecionados = st.sidebar.multiselect(
            "Selecionar clientes:",
            options=clientes_disponiveis,
            default=clientes_disponiveis[:min(5, len(clientes_disponiveis))],
            key="filtro_clientes"
        )
        if not clientes_selecionados:
            clientes_selecionados = clientes_disponiveis
    
    # Filtro 4: Clientes
    df_filtrado = df_filtrado[df_filtrado["Cliente"].isin(clientes_selecionados)].copy()
    st.sidebar.caption(f"✓ {len(df_filtrado):,} registros após filtro de cliente")
    
    # === 5. FILTRO DE ARTIGO ===
    st.sidebar.subheader("📦 Artigo")
    artigos_disponiveis = sorted(df_filtrado["Artigo"].unique())
    st.sidebar.write(f"📊 **{len(artigos_disponiveis)} artigos disponíveis**")
    
    todos_artigos = st.sidebar.checkbox("✓ Todos os artigos", value=True, key="cb_todos_artigos")
    
    if todos_artigos:
        artigos_selecionados = artigos_disponiveis
    else:
        artigos_selecionados = st.sidebar.multiselect(
            "Selecionar artigos:",
            options=artigos_disponiveis,
            default=artigos_disponiveis[:min(10, len(artigos_disponiveis))],
            key="filtro_artigos"
        )
        if not artigos_selecionados:
            artigos_selecionados = artigos_disponiveis
    
    # Filtro 5: Artigos (FINAL)
    df_filtrado = df_filtrado[df_filtrado["Artigo"].isin(artigos_selecionados)].copy()
    
    # === RESUMO FINAL ===
    st.sidebar.divider()
    st.sidebar.subheader("📋 Resumo dos Filtros")
    st.sidebar.metric("🔢 Total de Registros", f"{len(df_filtrado):,}")
    st.sidebar.write(f"📅 **Anos:** {len(anos_selecionados)}/{len(anos_disponiveis)}")
    st.sidebar.write(f"📆 **Meses:** {len(meses_selecionados)}/{len(meses_disponiveis)}")
    st.sidebar.write(f"👨‍💼 **Comerciais:** {len(comerciais_selecionados)}/{len(comerciais_disponiveis)}")
    st.sidebar.write(f"🏢 **Clientes:** {len(clientes_selecionados)}/{len(clientes_disponiveis)}")
    st.sidebar.write(f"📦 **Artigos:** {len(artigos_selecionados)}/{len(artigos_disponiveis)}")
    
else:
    df_filtrado = pd.DataFrame()
    st.warning("⚠️ Nenhum dado disponível. Por favor, faça upload do arquivo Excel.")

# === RESTO DO CÓDIGO (KPIs e GRÁFICOS) ===
if not df_filtrado.empty:
    # KPIS
    total_vendas_eur = df_filtrado["Valor"].sum()
    total_quantidade = df_filtrado["Quantidade"].sum()
    num_entidades = df_filtrado["Cliente"].nunique()
    num_comerciais = df_filtrado["Comercial"].nunique()
    num_artigos = df_filtrado["Artigo"].nunique()
    num_transacoes = len(df_filtrado)
    dias_com_vendas = df_filtrado["Data_Str"].nunique()
    
    ticket_medio_eur = total_vendas_eur / num_transacoes if num_transacoes > 0 else 0
    preco_medio_unitario = total_vendas_eur / total_quantidade if total_quantidade > 0 else 0
    venda_media_transacao = total_vendas_eur / num_transacoes if num_transacoes > 0 else 0
    quantidade_media_transacao = total_quantidade / num_transacoes if num_transacoes > 0 else 0
    venda_media_dia = total_vendas_eur / dias_com_vendas if dias_com_vendas > 0 else 0
    
    vendas_mensais_group = df_filtrado.groupby(["Ano", "MesNumero"])["Valor"].sum()
    ticket_medio_mes = vendas_mensais_group.mean() if not vendas_mensais_group.empty else 0
    
    # Display KPIs
    st.subheader("📊 KPIs Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Vendas (€)", f"€{total_vendas_eur:,.2f}")
    with col2:
        st.metric("📦 Total Quantidade", f"{total_quantidade:,.0f}")
    with col3:
        st.metric("🏢 Nº Entidades", f"{num_entidades:,.0f}")
    with col4:
        st.metric("🎫 Ticket Médio (€)", f"€{ticket_medio_eur:,.2f}")
    
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("👨‍💼 Nº Comerciais", f"{num_comerciais:,.0f}")
    with col6:
        st.metric("📦 Nº Artigos", f"{num_artigos:,.0f}")
    with col7:
        st.metric("🏷️ Preço Médio Unitário (€)", f"€{preco_medio_unitario:,.2f}")
    with col8:
        st.metric("💳 Venda Média/Transação (€)", f"€{venda_media_transacao:,.2f}")
    
    col9, col10, col11, col12 = st.columns(4)
    with col9:
        st.metric("📊 Quantidade Média/Transação", f"{quantidade_media_transacao:,.2f}")
    with col10:
        st.metric("📅 Dias com Vendas", f"{dias_com_vendas:,.0f}")
    with col11:
        st.metric("📈 Venda Média/Dia (€)", f"€{venda_media_dia:,.2f}")
    with col12:
        st.metric("🗓️ Ticket Médio (€) Mês", f"€{ticket_medio_mes:,.2f}")
    
    st.divider()
    
    # GRÁFICOS
    st.subheader("📈 Análise Gráfica")
    
    # Evolução mensal
    vendas_mensais = df_filtrado.groupby(["Ano", "MesNumero"]).agg({
        "Valor": "sum",
        "Quantidade": "sum"
    }).reset_index().sort_values(["Ano", "MesNumero"])
    
    if not vendas_mensais.empty:
        vendas_mensais["MesNome"] = vendas_mensais["MesNumero"].map(meses_abreviados)
        vendas_mensais["Periodo"] = vendas_mensais["Ano"].astype(str) + "-" + vendas_mensais["MesNome"]
        
        fig1, ax1 = plt.subplots(figsize=(14, 6))
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
        
        ax2 = ax1.twinx()
        ax2.plot(x, vendas_mensais["Quantidade"], 'o-', color='#A23B72', 
                linewidth=2, markersize=6, label='Quantidade')
        ax2.set_ylabel('Quantidade', color='#A23B72')
        ax2.tick_params(axis='y', labelcolor='#A23B72')
        
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        ax1.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        st.pyplot(fig1)
    
    # Top Clientes
    st.subheader("🏆 Top Clientes")
    top_clientes = df_filtrado.groupby("Cliente")["Valor"].sum().nlargest(10)
    
    if not top_clientes.empty:
        fig2, ax2 = plt.subplots(figsize=(14, 6))
        ax2.barh(range(len(top_clientes)), top_clientes.values, color='#A23B72', alpha=0.7)
        ax2.set_yticks(range(len(top_clientes)))
        ax2.set_yticklabels(top_clientes.index)
        ax2.invert_yaxis()
        ax2.set_xlabel("Total Vendas (€)")
        ax2.set_title("Top 10 Clientes", fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        for i, v in enumerate(top_clientes.values):
            ax2.text(v, i, f' €{v:,.0f}', va='center')
        
        plt.tight_layout()
        st.pyplot(fig2)
    
    # Exportar
    st.divider()
    st.subheader("📤 Exportar Dados")
    
    csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download CSV",
        csv_data,
        f"dados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv"
    )
else:
    st.warning("⚠️ Não há dados para exibir!")

st.divider()
st.success("✅ Dashboard pronto!")
