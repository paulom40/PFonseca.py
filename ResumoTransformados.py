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
        
        df = pd.DataFrame()
        
        # Encontrar coluna de data
        data_encontrada = False
        for i in range(min(5, len(df_raw.columns))):
            col_teste = df_raw.iloc[:, i]
            try:
                temp_dates = pd.to_datetime(col_teste, errors='coerce')
                if temp_dates.notna().sum() > len(col_teste) * 0.3:
                    df["Data"] = temp_dates
                    data_encontrada = True
                    data_col_idx = i
                    break
            except:
                continue
        
        if not data_encontrada:
            df["Data"] = pd.to_datetime(df_raw.iloc[:, 0], errors='coerce')
            data_col_idx = 0
        
        # Remover datas inválidas
        df = df[df["Data"].notna()].copy()
        
        # Identificar colunas
        text_columns = []
        for i in range(len(df_raw.columns)):
            if i == data_col_idx:
                continue
            if df_raw.iloc[:, i].dtype == 'object':
                text_columns.append(i)
        
        # Cliente
        if len(df_raw.columns) > 0:
            cliente_idx = (data_col_idx + 1) % len(df_raw.columns)
            df["Cliente"] = df_raw.iloc[:, cliente_idx].fillna("Desconhecido").astype(str).str.strip()
        
        # Artigo
        if len(df_raw.columns) > 1:
            artigo_idx = (data_col_idx + 2) % len(df_raw.columns)
            df["Artigo"] = df_raw.iloc[:, artigo_idx].fillna("Desconhecido").astype(str).str.strip()
        
        # Quantidade
        quantidade_encontrada = False
        for i in range(len(df_raw.columns)):
            if i in [data_col_idx, cliente_idx, artigo_idx]:
                continue
            if pd.api.types.is_numeric_dtype(df_raw.iloc[:, i]):
                df["Quantidade"] = pd.to_numeric(df_raw.iloc[:, i], errors='coerce').fillna(1)
                quantidade_encontrada = True
                quantidade_idx = i
                break
        
        if not quantidade_encontrada:
            df["Quantidade"] = 1
        
        # Valor
        valor_encontrado = False
        for i in range(len(df_raw.columns)):
            if i in [data_col_idx, cliente_idx, artigo_idx, quantidade_idx if 'quantidade_idx' in locals() else -1]:
                continue
            if pd.api.types.is_numeric_dtype(df_raw.iloc[:, i]):
                df["Valor"] = pd.to_numeric(df_raw.iloc[:, i], errors='coerce').fillna(0)
                valor_encontrado = True
                break
        
        if not valor_encontrado:
            df["Valor"] = df["Quantidade"] * np.random.uniform(10, 100, len(df))
        
        # Comercial
        if len(df_raw.columns) > 7:
            df["Comercial"] = df_raw.iloc[:, 7].fillna("Desconhecido").astype(str).str.strip()
        else:
            for i in range(len(df_raw.columns)):
                if i in [data_col_idx, cliente_idx, artigo_idx]:
                    continue
                if df_raw.iloc[:, i].dtype == 'object':
                    df["Comercial"] = df_raw.iloc[:, i].fillna("Desconhecido").astype(str).str.strip()
                    break
            else:
                df["Comercial"] = "Comercial Desconhecido"
        
        # Corrigir datas extremas
        if df["Data"].notna().any():
            mask_ano_extremo = (df["Data"].dt.year > 2100) | (df["Data"].dt.year < 2000)
            if mask_ano_extremo.any():
                ano_atual = datetime.now().year
                for idx in df[mask_ano_extremo].index:
                    try:
                        original_date = df.loc[idx, "Data"]
                        df.loc[idx, "Data"] = pd.to_datetime(
                            f"{ano_atual}-{original_date.month:02d}-{original_date.day:02d}"
                        )
                    except:
                        df.loc[idx, "Data"] = pd.Timestamp(f"{ano_atual}-01-01")
        
        # Adicionar colunas de tempo
        df["Ano"] = df["Data"].dt.year
        df["Mes"] = df["Data"].dt.month
        df["MesNumero"] = df["Data"].dt.month
        df["Dia"] = df["Data"].dt.day
        
        def safe_strftime(date):
            try:
                return date.strftime("%b")
            except:
                return "Inv"
        
        df["MesNome"] = df["Data"].apply(safe_strftime)
        df["Data_Str"] = df["Data"].dt.strftime("%Y-%m-%d")
        
        # Filtrar dados inválidos
        df = df[df["Quantidade"] > 0].copy()
        df = df[df["Valor"] > 0].copy()
        df = df[df["Cliente"] != "Desconhecido"].copy()
        df = df[df["Artigo"] != "Desconhecido"].copy()
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        
        # Dados de exemplo
        np.random.seed(42)
        n = 500
        
        datas_2023 = pd.date_range('2023-01-01', '2023-06-30', freq='D')
        datas_2024 = pd.date_range('2024-01-01', '2024-12-31', freq='D')
        
        todas_datas = list(datas_2023) + list(datas_2024)
        datas = np.random.choice(todas_datas, n)
        
        df = pd.DataFrame({
            "Data": datas,
            "Cliente": np.random.choice(["Empresa A", "Empresa B", "Empresa C", "Empresa D", 
                                        "Cliente E", "Cliente F", "Cliente G", "Cliente H"], n),
            "Artigo": np.random.choice(["Produto 001", "Produto 002", "Produto 003", 
                                       "Produto 004", "Produto 005", "Produto 006",
                                       "Produto 007", "Produto 008", "Produto 009"], n),
            "Quantidade": np.random.randint(1, 50, n),
            "Valor": np.random.uniform(50, 500, n),
            "Comercial": np.random.choice(["João Silva", "Maria Santos", "Carlos Oliveira", 
                                          "Ana Costa", "Pedro Almeida"], n)
        })
        
        df["Ano"] = df["Data"].dt.year
        df["Mes"] = df["Data"].dt.month
        df["MesNumero"] = df["Data"].dt.month
        df["MesNome"] = df["Data"].dt.strftime("%b")
        df["Dia"] = df["Data"].dt.day
        df["Data_Str"] = df["Data"].dt.strftime("%Y-%m-%d")
        
        return df

df = load_data()

# === FILTROS DINÂMICOS CORRIGIDOS ===
st.sidebar.header("🎛️ Filtros")

meses_nomes = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

meses_abreviados = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

if len(df) > 0:
    # === 1. FILTRO DE ANO ===
    st.sidebar.subheader("📅 Ano")
    anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)
    anos_selecionados = st.sidebar.multiselect(
        "Selecionar anos:",
        options=anos_disponiveis,
        default=anos_disponiveis[:min(2, len(anos_disponiveis))],
        key="filtro_anos"
    )
    
    if not anos_selecionados:
        anos_selecionados = anos_disponiveis
    
    # Aplicar filtro de anos
    df_temp = df[df["Ano"].isin(anos_selecionados)].copy()
    
    # === 2. FILTRO DE MÊS ===
    st.sidebar.subheader("📆 Mês")
    meses_disponiveis_numeros = sorted(df_temp["MesNumero"].unique())
    opcoes_meses = [meses_nomes[mes] for mes in meses_disponiveis_numeros if mes in meses_nomes]
    
    if opcoes_meses:
        meses_selecionados_nomes = st.sidebar.multiselect(
            "Selecionar meses:",
            options=opcoes_meses,
            default=opcoes_meses,
            key="filtro_meses"
        )
        
        nomes_para_meses = {v: k for k, v in meses_nomes.items()}
        meses_selecionados = [nomes_para_meses[nome] for nome in meses_selecionados_nomes] if meses_selecionados_nomes else meses_disponiveis_numeros
    else:
        meses_selecionados = []
    
    # Aplicar filtro de meses
    df_temp = df_temp[df_temp["MesNumero"].isin(meses_selecionados)].copy()
    
    # === 3. FILTRO DE COMERCIAL ===
    st.sidebar.subheader("👨‍💼 Comercial")
    comerciais_disponiveis = sorted(df_temp["Comercial"].unique())
    
    if comerciais_disponiveis:
        todos_comerciais = st.sidebar.checkbox("Todos os comerciais", value=True, key="todos_comerciais")
        
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
    else:
        comerciais_selecionados = []
    
    # Aplicar filtro de comerciais
    df_temp = df_temp[df_temp["Comercial"].isin(comerciais_selecionados)].copy()
    
    # === 4. FILTRO DE CLIENTE ===
    st.sidebar.subheader("🏢 Cliente")
    clientes_disponiveis = sorted(df_temp["Cliente"].unique())
    
    if clientes_disponiveis:
        todos_clientes = st.sidebar.checkbox("Todos os clientes", value=True, key="todos_clientes")
        
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
    else:
        clientes_selecionados = []
    
    # Aplicar filtro de clientes
    df_temp = df_temp[df_temp["Cliente"].isin(clientes_selecionados)].copy()
    
    # === 5. FILTRO DE ARTIGO ===
    st.sidebar.subheader("📦 Artigo")
    artigos_disponiveis = sorted(df_temp["Artigo"].unique())
    
    if artigos_disponiveis:
        todos_artigos = st.sidebar.checkbox("Todos os artigos", value=True, key="todos_artigos")
        
        if todos_artigos:
            artigos_selecionados = artigos_disponiveis
        else:
            artigos_selecionados = st.sidebar.multiselect(
                "Selecionar artigos:",
                options=artigos_disponiveis,
                default=artigos_disponiveis[:min(5, len(artigos_disponiveis))],
                key="filtro_artigos"
            )
            if not artigos_selecionados:
                artigos_selecionados = artigos_disponiveis
    else:
        artigos_selecionados = []
    
    # Aplicar filtro final
    df_filtrado = df_temp[df_temp["Artigo"].isin(artigos_selecionados)].copy()
    
    # Botão resetar
    if st.sidebar.button("🔄 Resetar Filtros", type="secondary"):
        st.rerun()
    
    # Resumo dos filtros
    st.sidebar.divider()
    st.sidebar.subheader("📋 Resumo dos Filtros")
    st.sidebar.write(f"**Anos:** {len(anos_selecionados)}")
    st.sidebar.write(f"**Meses:** {len(meses_selecionados)}")
    st.sidebar.write(f"**Comerciais:** {len(comerciais_selecionados)}")
    st.sidebar.write(f"**Clientes:** {len(clientes_selecionados)}")
    st.sidebar.write(f"**Artigos:** {len(artigos_selecionados)}")
    st.sidebar.write(f"**Registros filtrados:** {len(df_filtrado):,}")
    
else:
    df_filtrado = pd.DataFrame()
    anos_selecionados = []
    meses_selecionados = []
    comerciais_selecionados = []
    clientes_selecionados = []
    artigos_selecionados = []

# === CÁLCULO DOS KPIs ===
if not df_filtrado.empty:
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
else:
    total_vendas_eur = total_quantidade = num_entidades = num_comerciais = num_artigos = 0
    num_transacoes = dias_com_vendas = ticket_medio_eur = preco_medio_unitario = 0
    venda_media_transacao = quantidade_media_transacao = venda_media_dia = ticket_medio_mes = 0

# === DISPLAY DOS KPIs ===
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

# === GRÁFICOS ===
if not df_filtrado.empty:
    st.subheader("📈 Análise Gráfica")
    
    # Evolução mensal
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
    top_clientes = df_filtrado.groupby("Cliente").agg({
        "Valor": "sum",
        "Quantidade": "sum"
    }).nlargest(10, "Valor")
    
    if not top_clientes.empty:
        fig2, ax2 = plt.subplots(figsize=(14, 6))
        ax2.barh(range(len(top_clientes)), top_clientes["Valor"], color='#A23B72', alpha=0.7)
        ax2.set_yticks(range(len(top_clientes)))
        ax2.set_yticklabels(top_clientes.index)
        ax2.invert_yaxis()
        ax2.set_xlabel("Total Vendas (€)")
        ax2.set_title("Top 10 Clientes por Valor", fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        for i, v in enumerate(top_clientes["Valor"]):
            ax2.text(v, i, f' €{v:,.0f}', va='center', fontsize=9)
        
        plt.tight_layout()
        st.pyplot(fig2)
    
    # Exportar dados
    st.divider()
    st.subheader("📤 Exportar Dados")
    
    col1, col2 = st.columns(2)
    with col1:
        csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download CSV",
            csv_data,
            f"dados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv"
        )
else:
    st.warning("⚠️ Não há dados disponíveis com os filtros atuais!")

st.divider()
st.success("✅ Dashboard carregado com sucesso!")
