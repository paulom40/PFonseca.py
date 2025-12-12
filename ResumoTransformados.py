import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Dashboard Compras - Análise Completa", layout="wide")
st.title("📊 Dashboard de Compras – Análise Completa de KPIs")

# === CARREGAR DADOS ===
@st.cache_data
def load_data():
    try:
        uploaded_file = "ResumoTR.xlsx"
        df_raw = pd.read_excel(uploaded_file)
        
        st.sidebar.write("### 🔍 Debug - Estrutura do Arquivo")
        st.sidebar.write(f"**Total de colunas:** {len(df_raw.columns)}")
        st.sidebar.write(f"**Total de linhas:** {len(df_raw)}")
        
        with st.sidebar.expander("Ver todas as colunas"):
            for i, col in enumerate(df_raw.columns):
                sample = df_raw[col].dropna().head(3).tolist()
                st.write(f"{i}: **{col}** → {sample}")
        
        df = pd.DataFrame()
        
        # 1. DATA
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
            st.sidebar.success(f"✅ Data: {data_col}")
        else:
            st.sidebar.error("❌ Data não encontrada")
            return pd.DataFrame()
        
        # 2. CLIENTE
        cliente_col = None
        for col in df_raw.columns:
            if any(keyword in str(col).lower() for keyword in ['cliente', 'client', 'entidade', 'empresa']):
                cliente_col = col
                break
        
        if cliente_col:
            df["Cliente"] = df_raw[cliente_col].fillna("Desconhecido").astype(str).str.strip()
            st.sidebar.success(f"✅ Cliente: {cliente_col}")
        else:
            st.sidebar.warning("⚠️ Cliente não encontrado")
            df["Cliente"] = "Cliente Desconhecido"
        
        # 3. ARTIGO
        artigo_col = None
        for col in df_raw.columns:
            if any(keyword in str(col).lower() for keyword in ['artigo', 'produto', 'item', 'artig', 'art']):
                artigo_col = col
                break
        
        if artigo_col:
            df["Artigo"] = df_raw[artigo_col].fillna("Desconhecido").astype(str).str.strip()
            st.sidebar.success(f"✅ Artigo: {artigo_col}")
        else:
            st.sidebar.warning("⚠️ Artigo não encontrado")
            df["Artigo"] = "Artigo Desconhecido"
        
        # 4. QUANTIDADE
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
            st.sidebar.success(f"✅ Quantidade: {quantidade_col}")
        else:
            st.sidebar.warning("⚠️ Quantidade não encontrada")
            df["Quantidade"] = 1
        
        # 5. VALOR
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
            st.sidebar.success(f"✅ Valor: {valor_col}")
        else:
            st.sidebar.warning("⚠️ Valor não encontrado")
            df["Valor"] = df["Quantidade"] * 10
        
        # 6. COMERCIAL
        comercial_col = None
        for col in df_raw.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['comercial', 'vendedor', 'seller', 'comerci']):
                comercial_col = col
                break
        
        if comercial_col:
            df["Comercial"] = df_raw[comercial_col].fillna("Desconhecido").astype(str).str.strip()
            st.sidebar.success(f"✅ Comercial: {comercial_col}")
        else:
            st.sidebar.warning("⚠️ Comercial não encontrado")
            df["Comercial"] = "Comercial Desconhecido"
        
        # LIMPEZA
        df = df[df["Data"].notna()].copy()
        df = df[df["Quantidade"] > 0].copy()
        df = df[df["Valor"] > 0].copy()
        
        if (df["Cliente"] != "Desconhecido").any():
            df = df[df["Cliente"] != "Desconhecido"].copy()
        if (df["Artigo"] != "Desconhecido").any():
            df = df[df["Artigo"] != "Desconhecido"].copy()
        
        # COLUNAS DE TEMPO
        df["Ano"] = df["Data"].dt.year
        df["Mes"] = df["Data"].dt.month
        df["MesNumero"] = df["Data"].dt.month
        df["Dia"] = df["Data"].dt.day
        df["MesNome"] = df["Data"].dt.strftime("%b")
        df["Data_Str"] = df["Data"].dt.strftime("%Y-%m-%d")
        df["AnoMes"] = df["Data"].dt.strftime("%Y-%m")
        
        st.sidebar.write("### 📊 Dados Carregados")
        st.sidebar.write(f"**Registros:** {len(df):,}")
        if len(df) > 0:
            st.sidebar.write(f"**Período:** {df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}")
            st.sidebar.write(f"**Clientes:** {df['Cliente'].nunique()}")
            st.sidebar.write(f"**Artigos:** {df['Artigo'].nunique()}")
            st.sidebar.write(f"**Comerciais:** {df['Comercial'].nunique()}")
        
        return df
        
    except Exception as e:
        st.sidebar.error(f"❌ Erro: {str(e)}")
        st.sidebar.write("Criando dados de exemplo...")
        
        np.random.seed(42)
        n = 1000
        dates = pd.date_range('2023-01-01', '2024-12-31', freq='D')
        random_dates = np.random.choice(dates, n)
        
        df = pd.DataFrame({
            "Data": random_dates,
            "Cliente": np.random.choice([
                "Empresa A", "Empresa B", "Cliente C", "Distribuidor D",
                "Fornecedor E", "Parceiro F", "Cliente G", "Empresa H",
                "Grupo I", "Sociedade J", "Firma K", "Cliente L"
            ], n),
            "Artigo": np.random.choice([
                "Produto 001", "Produto 002", "Produto 003", "Produto 004",
                "Produto 005", "Produto 006", "Produto 007", "Produto 008",
                "Item 009", "Item 010", "Item 011", "Item 012"
            ], n),
            "Quantidade": np.random.randint(1, 100, n),
            "Valor": np.random.uniform(10, 1000, n),
            "Comercial": np.random.choice([
                "João Silva", "Maria Santos", "Carlos Oliveira",
                "Ana Costa", "Pedro Almeida", "Sofia Rodrigues"
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

# UPLOAD
try:
    uploaded_file = st.file_uploader("📁 Carregar ResumoTR.xlsx", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        with open("ResumoTR.xlsx", "wb") as f:
            f.write(uploaded_file.getbuffer())
        df = load_data()
    else:
        try:
            url = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"
            df_raw = pd.read_excel(url)
            with open("ResumoTR.xlsx", "wb") as f:
                df_raw.to_excel(f, index=False)
            df = load_data()
        except:
            st.info("💡 Faça upload do arquivo ou dados de exemplo serão usados")
            df = load_data()
except:
    df = load_data()

# === FILTROS INTERATIVOS CORRIGIDOS ===
st.sidebar.header("🎛️ Filtros Interativos")

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
    if st.sidebar.button("🔄 Resetar Todos os Filtros", type="secondary"):
        st.rerun()
    
    st.sidebar.divider()
    
    # === APLICAR FILTROS DE FORMA CASCATA ===
    
    # 1. FILTRO DE ANO
    st.sidebar.subheader("📅 Ano")
    anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)
    st.sidebar.caption(f"Disponíveis: {anos_disponiveis}")
    
    anos_selecionados = st.sidebar.multiselect(
        "Selecionar anos:",
        options=anos_disponiveis,
        default=anos_disponiveis,
        key="filtro_anos"
    )
    
    if not anos_selecionados:
        anos_selecionados = anos_disponiveis
    
    # APLICAR FILTRO 1
    df_temp = df[df["Ano"].isin(anos_selecionados)].copy()
    st.sidebar.info(f"✓ {len(df_temp):,} registros após filtro de ano")
    
    # 2. FILTRO DE MÊS (baseado nos anos selecionados)
    st.sidebar.subheader("📆 Mês")
    meses_disponiveis = sorted(df_temp["MesNumero"].unique())
    meses_nomes_disponiveis = [meses_nomes[m] for m in meses_disponiveis]
    st.sidebar.caption(f"Disponíveis: {len(meses_disponiveis)} meses")
    
    meses_selecionados_nomes = st.sidebar.multiselect(
        "Selecionar meses:",
        options=meses_nomes_disponiveis,
        default=meses_nomes_disponiveis,
        key="filtro_meses"
    )
    
    nomes_para_meses = {v: k for k, v in meses_nomes.items()}
    meses_selecionados = [nomes_para_meses[nome] for nome in meses_selecionados_nomes] if meses_selecionados_nomes else meses_disponiveis
    
    # APLICAR FILTRO 2
    df_temp = df_temp[df_temp["MesNumero"].isin(meses_selecionados)].copy()
    st.sidebar.info(f"✓ {len(df_temp):,} registros após filtro de mês")
    
    # 3. FILTRO DE COMERCIAL (baseado em ano + mês)
    st.sidebar.subheader("👨‍💼 Comercial")
    comerciais_disponiveis = sorted(df_temp["Comercial"].unique())
    st.sidebar.caption(f"Disponíveis: {len(comerciais_disponiveis)} comerciais")
    
    todos_comerciais = st.sidebar.checkbox("✓ Selecionar todos os comerciais", value=True, key="cb_comerciais")
    
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
    
    # APLICAR FILTRO 3
    df_temp = df_temp[df_temp["Comercial"].isin(comerciais_selecionados)].copy()
    st.sidebar.info(f"✓ {len(df_temp):,} registros após filtro de comercial")
    
    # 4. FILTRO DE CLIENTE (baseado em ano + mês + comercial)
    st.sidebar.subheader("🏢 Cliente")
    clientes_disponiveis = sorted(df_temp["Cliente"].unique())
    st.sidebar.caption(f"Disponíveis: {len(clientes_disponiveis)} clientes")
    
    todos_clientes = st.sidebar.checkbox("✓ Selecionar todos os clientes", value=True, key="cb_clientes")
    
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
    
    # APLICAR FILTRO 4
    df_temp = df_temp[df_temp["Cliente"].isin(clientes_selecionados)].copy()
    st.sidebar.info(f"✓ {len(df_temp):,} registros após filtro de cliente")
    
    # 5. FILTRO DE ARTIGO (baseado em todos os filtros anteriores)
    st.sidebar.subheader("📦 Artigo")
    artigos_disponiveis = sorted(df_temp["Artigo"].unique())
    st.sidebar.caption(f"Disponíveis: {len(artigos_disponiveis)} artigos")
    
    todos_artigos = st.sidebar.checkbox("✓ Selecionar todos os artigos", value=True, key="cb_artigos")
    
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
    
    # APLICAR FILTRO FINAL
    df_filtrado = df_temp[df_temp["Artigo"].isin(artigos_selecionados)].copy()
    
    st.sidebar.divider()
    st.sidebar.success(f"🎯 **Total Final: {len(df_filtrado):,} registros**")
    
    # VERIFICAÇÃO DE DADOS
    with st.sidebar.expander("🔍 Verificar cálculos"):
        st.write(f"**Soma Quantidade:** {df_filtrado['Quantidade'].sum():,.2f}")
        st.write(f"**Soma Valor:** €{df_filtrado['Valor'].sum():,.2f}")
        st.write(f"**Linhas:** {len(df_filtrado)}")
        
else:
    df_filtrado = pd.DataFrame()
    st.warning("⚠️ Nenhum dado disponível")

# === KPIs COM CÁLCULOS CORRIGIDOS ===
if not df_filtrado.empty:
    
    # CÁLCULOS GERAIS - CORRIGIDOS
    total_vendas_eur = float(df_filtrado["Valor"].sum())
    total_quantidade = float(df_filtrado["Quantidade"].sum())
    num_entidades = int(df_filtrado["Cliente"].nunique())
    num_comerciais = int(df_filtrado["Comercial"].nunique())
    num_artigos = int(df_filtrado["Artigo"].nunique())
    num_transacoes = int(len(df_filtrado))
    dias_com_vendas = int(df_filtrado["Data_Str"].nunique())
    
    ticket_medio = total_vendas_eur / num_transacoes if num_transacoes > 0 else 0
    preco_medio_unitario = total_vendas_eur / total_quantidade if total_quantidade > 0 else 0
    venda_media_transacao = total_vendas_eur / num_transacoes if num_transacoes > 0 else 0
    quantidade_media_transacao = total_quantidade / num_transacoes if num_transacoes > 0 else 0
    venda_media_dia = total_vendas_eur / dias_com_vendas if dias_com_vendas > 0 else 0
    
    # TICKET MÉDIO MENSAL
    vendas_por_mes = df_filtrado.groupby("AnoMes")["Valor"].sum()
    ticket_medio_mensal = float(vendas_por_mes.mean()) if not vendas_por_mes.empty else 0
    
    # TICKET MÉDIO POR COMERCIAL
    vendas_por_comercial = df_filtrado.groupby("Comercial")["Valor"].sum()
    ticket_medio_comercial = float(vendas_por_comercial.mean()) if not vendas_por_comercial.empty else 0
    
    # === SEÇÃO 1: KPIs PRINCIPAIS ===
    st.subheader("📊 KPIs Principais")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("💰 Total Vendas (€)", f"€{total_vendas_eur:,.2f}")
    with col2:
        st.metric("📦 Total Quantidade", f"{total_quantidade:,.0f}")
    with col3:
        st.metric("🏢 Nº Entidades", f"{num_entidades}")
    with col4:
        st.metric("👨‍💼 Nº Comerciais", f"{num_comerciais}")
    with col5:
        st.metric("📦 Nº Artigos", f"{num_artigos}")
    
    st.divider()
    
    # === SEÇÃO 2: MÉDIAS E TICKETS ===
    st.subheader("📈 Médias e Tickets")
    
    col6, col7, col8, col9, col10 = st.columns(5)
    
    with col6:
        st.metric("🎫 Ticket Médio (€)", f"€{ticket_medio:,.2f}", 
                 help="Valor médio por transação")
    with col7:
        st.metric("🗓️ Ticket Médio Mensal (€)", f"€{ticket_medio_mensal:,.2f}",
                 help="Média de vendas mensais")
    with col8:
        st.metric("👤 Ticket Médio/Comercial (€)", f"€{ticket_medio_comercial:,.2f}",
                 help="Média de vendas por comercial")
    with col9:
        st.metric("🏷️ Preço Médio Unitário (€)", f"€{preco_medio_unitario:,.2f}",
                 help="Valor total / Quantidade total")
    with col10:
        st.metric("💳 Venda Média/Transação (€)", f"€{venda_media_transacao:,.2f}",
                 help="Valor médio por transação")
    
    st.divider()
    
    # === SEÇÃO 3: MÉTRICAS OPERACIONAIS ===
    st.subheader("⚙️ Métricas Operacionais")
    
    col11, col12, col13 = st.columns(3)
    
    with col11:
        st.metric("📊 Quantidade Média/Transação", f"{quantidade_media_transacao:,.2f}",
                 help="Quantidade média por transação")
    with col12:
        st.metric("📅 Dias com Vendas", f"{dias_com_vendas}",
                 help="Número de dias distintos com vendas")
    with col13:
        st.metric("📈 Venda Média/Dia (€)", f"€{venda_media_dia:,.2f}",
                 help="Valor médio vendido por dia")
    
    st.divider()
    
    # === SEÇÃO 4: TOP 15 CLIENTES MENSAIS ===
    st.subheader("🏆 Top 15 Clientes Mensais")
    
    # Agrupar corretamente
    clientes_mensais = df_filtrado.groupby(["Cliente", "AnoMes"]).agg({
        "Valor": "sum",
        "Quantidade": "sum"
    }).reset_index()
    
    clientes_media_mensal = clientes_mensais.groupby("Cliente").agg({
        "Valor": "mean",
        "Quantidade": "mean"
    }).round(2)
    
    clientes_media_mensal.columns = ["Venda Média Mensal (€)", "Quantidade Média Mensal"]
    top15_clientes = clientes_media_mensal.nlargest(15, "Venda Média Mensal (€)")
    
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        if not top15_clientes.empty:
            fig1, ax1 = plt.subplots(figsize=(12, 8))
            y_pos = range(len(top15_clientes))
            ax1.barh(y_pos, top15_clientes["Venda Média Mensal (€)"], color='#2E86AB', alpha=0.8)
            ax1.set_yticks(y_pos)
            ax1.set_yticklabels(top15_clientes.index, fontsize=9)
            ax1.invert_yaxis()
            ax1.set_xlabel("Venda Média Mensal (€)", fontsize=11)
            ax1.set_title("Top 15 Clientes - Venda Média Mensal", fontsize=13, fontweight='bold')
            ax1.grid(True, alpha=0.3, axis='x')
            
            for i, v in enumerate(top15_clientes["Venda Média Mensal (€)"]):
                ax1.text(v, i, f' €{v:,.0f}', va='center', fontsize=9)
            
            plt.tight_layout()
            st.pyplot(fig1)
    
    with col_b:
        st.dataframe(
            top15_clientes.style.format({
                "Venda Média Mensal (€)": "€{:,.2f}",
                "Quantidade Média Mensal": "{:,.2f}"
            }),
            height=400
        )
    
    st.divider()
    
    # === SEÇÃO 5: TOP 15 ARTIGOS MENSAIS ===
    st.subheader("📦 Top 15 Artigos Mensais")
    
    # Agrupar corretamente
    artigos_mensais = df_filtrado.groupby(["Artigo", "AnoMes"]).agg({
        "Valor": "sum",
        "Quantidade": "sum"
    }).reset_index()
    
    artigos_media_mensal = artigos_mensais.groupby("Artigo").agg({
        "Valor": "mean",
        "Quantidade": "mean"
    }).round(2)
    
    artigos_media_mensal.columns = ["Venda Média Mensal (€)", "Quantidade Média Mensal"]
    top15_artigos = artigos_media_mensal.nlargest(15, "Venda Média Mensal (€)")
    
    col_c, col_d = st.columns([2, 1])
    
    with col_c:
        if not top15_artigos.empty:
            fig2, ax2 = plt.subplots(figsize=(12, 8))
            y_pos = range(len(top15_artigos))
            ax2.barh(y_pos, top15_artigos["Venda Média Mensal (€)"], color='#A23B72', alpha=0.8)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(top15_artigos.index, fontsize=9)
            ax2.invert_yaxis()
            ax2.set_xlabel("Venda Média Mensal (€)", fontsize=11)
            ax2.set_title("Top 15 Artigos - Venda Média Mensal", fontsize=13, fontweight='bold')
            ax2.grid(True, alpha=0.3, axis='x')
            
            for i, v in enumerate(top15_artigos["Venda Média Mensal (€)"]):
                ax2.text(v, i, f' €{v:,.0f}', va='center', fontsize=9)
            
            plt.tight_layout()
            st.pyplot(fig2)
    
    with col_d:
        st.dataframe(
            top15_artigos.style.format({
                "Venda Média Mensal (€)": "€{:,.2f}",
                "Quantidade Média Mensal": "{:,.2f}"
            }),
            height=400
        )
    
    st.divider()
    
    # === EVOLUÇÃO MENSAL ===
    st.subheader("📈 Evolução Mensal de Vendas")
    
    vendas_mensais = df_filtrado.groupby(["Ano", "MesNumero"]).agg({
        "Valor": "sum",
        "Quantidade": "sum"
    }).reset_index().sort_values(["Ano", "MesNumero"])
    
    if not vendas_mensais.empty:
        vendas_mensais["MesNome"] = vendas_mensais["MesNumero"].map(meses_abreviados)
        vendas_mensais["Periodo"] = vendas_mensais["Ano"].astype(str) + "-" + vendas_mensais["MesNome"]
        
        fig3, ax3 = plt.subplots(figsize=(14, 6))
        x = range(len(vendas_mensais))
        width = 0.35
        
        ax3.bar([i - width/2 for i in x], vendas_mensais["Valor"], width, 
               label='Valor (€)', color='#2E86AB', alpha=0.7)
        ax3.set_xlabel("Período", fontsize=11)
        ax3.set_ylabel("Valor (€)", color='#2E86AB', fontsize=11)
        ax3.tick_params(axis='y', labelcolor='#2E86AB')
        ax3.set_title("Evolução Mensal - Valor e Quantidade", fontsize=14, fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(vendas_mensais["Periodo"], rotation=45, ha='right')
        
        ax4 = ax3.twinx()
        ax4.plot(x, vendas_mensais["Quantidade"], 'o-', color='#A23B72', 
                linewidth=2, markersize=6, label='Quantidade')
        ax4.set_ylabel('Quantidade', color='#A23B72', fontsize=11)
        ax4.tick_params(axis='y', labelcolor='#A23B72')
        
        lines1, labels1 = ax3.get_legend_handles_labels()
        lines2, labels2 = ax4.get_legend_handles_labels()
        ax3.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        ax3.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        st.pyplot(fig3)
    
    st.divider()
    
    # === DESEMPENHO POR COMERCIAL ===
    st.subheader("👨‍💼 Desempenho por Comercial")
    
    desempenho_comercial = df_filtrado.groupby("Comercial").agg({
        "Valor": ["sum", "mean", "count"],
        "Cliente": "nunique",
        "Quantidade": "sum"
    }).round(2)
    
    desempenho_comercial.columns = ["Total Vendas (€)", "Ticket Médio (€)", 
                                     "Nº Transações", "Clientes Únicos", "Quantidade Total"]
    desempenho_comercial = desempenho_comercial.sort_values("Total Vendas (€)", ascending=False)
    
    col_e, col_f = st.columns([3, 2])
    
    with col_e:
        if not desempenho_comercial.empty:
            fig4, ax5 = plt.subplots(figsize=(12, 6))
            x_pos = range(len(desempenho_comercial))
            ax5.bar(x_pos, desempenho_comercial["Total Vendas (€)"], color='#F18F01', alpha=0.8)
            ax5.set_xticks(x_pos)
            ax5.set_xticklabels(desempenho_comercial.index, rotation=45, ha='right')
            ax5.set_ylabel("Total Vendas (€)", fontsize=11)
            ax5.set_title("Performance de Vendas por Comercial", fontsize=13, fontweight='bold')
            ax5.grid(True, alpha=0.3, axis='y')
            
            for i, v in enumerate(desempenho_comercial["Total Vendas (€)"]):
                ax5.text(i, v, f'€{v:,.0f}', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            st.pyplot(fig4)
    
    with col_f:
        st.dataframe(
            desempenho_comercial.style.format({
                "Total Vendas (€)": "€{:,.2f}",
                "Ticket Médio (€)": "€{:,.2f}",
                "Nº Transações": "{:,.0f}",
                "Clientes Únicos": "{:,.0f}",
                "Quantidade Total": "{:,.0f}"
            }),
            height=350
        )
    
    st.divider()
    
    # === EXPORTAR DADOS ===
    st.subheader("📤 Exportar Dados")
    
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Dados Filtrados (CSV)",
            data=csv_data,
            file_name=f"dados_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_exp2:
        output_kpis = io.BytesIO()
        with pd.ExcelWriter(output_kpis, engine='openpyxl') as writer:
            kpis_completo = pd.DataFrame({
                "Categoria": [
                    "Principais", "Principais", "Principais", "Principais", "Principais",
                    "Médias/Tickets", "Médias/Tickets", "Médias/Tickets", "Médias/Tickets", "Médias/Tickets",
                    "Operacionais", "Operacionais", "Operacionais", "Operacionais"
                ],
                "KPI": [
                    "Total Vendas (€)", "Total Quantidade", "Nº Entidades", "Nº Comerciais", "Nº Artigos",
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
            kpis_completo.to_excel(writer, sheet_name='Todos_KPIs', index=False)
            
            top15_clientes_copy = top15_clientes.copy()
            top15_clientes_copy.insert(0, 'Ranking', range(1, len(top15_clientes) + 1))
            top15_clientes_copy.to_excel(writer, sheet_name='Top15_Clientes')
            
            top15_artigos_copy = top15_artigos.copy()
            top15_artigos_copy.insert(0, 'Ranking', range(1, len(top15_artigos) + 1))
            top15_artigos_copy.to_excel(writer, sheet_name='Top15_Artigos')
            
            desempenho_comercial.to_excel(writer, sheet_name='Desempenho_Comerciais')
        
        excel_kpis_data = output_kpis.getvalue()
        
        st.download_button(
            label="📊 Todos os KPIs (Excel)",
            data=excel_kpis_data,
            file_name=f"kpis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
    
    with col_exp3:
        output_completo = io.BytesIO()
        with pd.ExcelWriter(output_completo, engine='openpyxl') as writer:
            kpis_completo.to_excel(writer, sheet_name='KPIs', index=False)
            df_filtrado.to_excel(writer, sheet_name='Dados_Filtrados', index=False)
            top15_clientes.to_excel(writer, sheet_name='Top15_Clientes')
            top15_artigos.to_excel(writer, sheet_name='Top15_Artigos')
            vendas_mensais.to_excel(writer, sheet_name='Vendas_Mensais', index=False)
            desempenho_comercial.to_excel(writer, sheet_name='Desempenho_Comerciais')
        
        excel_completo_data = output_completo.getvalue()
        
        st.download_button(
            label="📋 Relatório Completo (Excel)",
            data=excel_completo_data,
            file_name=f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

else:
    st.warning("⚠️ Não há dados disponíveis. Ajuste os filtros ou faça upload do arquivo.")

st.divider()
st.success("✅ Dashboard carregado com sucesso!")

with st.expander("ℹ️ Sobre os Cálculos"):
    st.write("""
    ### 📊 Como são calculados os KPIs:
    
    **Total Vendas (€)**: Soma de todos os valores
    **Total Quantidade**: Soma de todas as quantidades
    **Ticket Médio Mensal (€)**: Média das vendas totais por mês
    **Ticket Médio/Comercial (€)**: Média das vendas totais por comercial
    **Preço Médio Unitário (€)**: Valor total ÷ Quantidade total
    
    **Top 15 Clientes/Artigos Mensais**: Baseado na média mensal de vendas
    
    ### 🎛️ Filtros Interativos:
    Os filtros funcionam em cascata - cada filtro só mostra opções válidas baseadas nos filtros anteriores.
    Use os checkboxes "Selecionar todos" para facilitar a seleção.
    """)
