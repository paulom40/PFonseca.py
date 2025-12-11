import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io
from datetime import datetime

st.set_page_config(page_title="Dashboard Compras - KPIs + YoY", layout="wide")
st.title("Dashboard de Compras – KPIs + Comparativo Temporal")

# === CARREGAR DADOS ===
@st.cache_data
def load_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"
        df_raw = pd.read_excel(url)

        df = pd.DataFrame({
            "Data":       pd.to_datetime(df_raw.iloc[:, 0], errors="coerce"),
            "Cliente":    df_raw.iloc[:, 1].astype(str).str.strip(),
            "Artigo":     df_raw.iloc[:, 2].astype(str).str.strip(),
            "Quantidade": pd.to_numeric(df_raw.iloc[:, 3], errors="coerce").fillna(0),
            "Comercial":  df_raw.iloc[:, 8].astype(str).str.strip(),
        })

        df = df.dropna(subset=["Data"])
        df = df[(df["Cliente"] != "nan") & (df["Comercial"] != "nan") & (df["Artigo"] != "nan")]
        df["Ano"] = df["Data"].dt.year
        df["Mes"] = df["Data"].dt.month
        df["MesNumero"] = df["Data"].dt.month
        df["MesNome"] = df["Data"].dt.strftime("%b")   # Jan, Feb, Mar…
        df["MesNomeCompleto"] = df["Data"].dt.strftime("%B")  # Janeiro, Fevereiro...
        df["Trimestre"] = df["Data"].dt.quarter
        df["Semana"] = df["Data"].dt.isocalendar().week
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()

# Verificar se há dados
if df.empty:
    st.error("Não foi possível carregar os dados. Verifique a fonte.")
    st.stop()

# === SIDEBAR – FILTROS DINÂMICOS MULTISELECÇÃO ===
st.sidebar.header("Filtros Dinâmicos")

# Exibir informações sobre os dados disponíveis
st.sidebar.subheader("📊 Dados Disponíveis")
st.sidebar.write(f"**Período:** {df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}")
st.sidebar.write(f"**Anos:** {', '.join(map(str, sorted(df['Ano'].unique())))}")
st.sidebar.write(f"**Total de registros:** {len(df):,}")
st.sidebar.write(f"**Clientes únicos:** {df['Cliente'].nunique():,}")
st.sidebar.divider()

# 1. FILTRO DE ANO (multiselect)
st.sidebar.subheader("📅 Filtro por Ano")
anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)

if len(anos_disponiveis) == 1:
    st.sidebar.info(f"⚠️ Apenas um ano disponível: {anos_disponiveis[0]}")
    anos_selecionados = anos_disponiveis
else:
    anos_selecionados = st.sidebar.multiselect(
        "Selecionar Anos",
        options=anos_disponiveis,
        default=[anos_disponiveis[0]] if anos_disponiveis else []
    )

# Se não selecionou nenhum ano, usar todos
if not anos_selecionados:
    anos_selecionados = anos_disponiveis

# 2. FILTRO DE MÊS (multiselect com nomes completos)
st.sidebar.subheader("📆 Filtro por Mês")

# Mapeamento de números para nomes completos
meses_nomes = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# Obter meses disponíveis nos anos selecionados
meses_disponiveis_numeros = sorted(df[df["Ano"].isin(anos_selecionados)]["MesNumero"].unique())
opcoes_meses = [meses_nomes[mes] for mes in meses_disponiveis_numeros if mes in meses_nomes]

# Inverter mapeamento para obter número do mês a partir do nome
nomes_para_meses = {v: k for k, v in meses_nomes.items()}

if meses_disponiveis_numeros:
    meses_selecionados_nomes = st.sidebar.multiselect(
        "Selecionar Meses",
        options=opcoes_meses,
        default=opcoes_meses  # Por padrão, selecionar todos os meses disponíveis
    )
    
    # Converter nomes dos meses para números
    if meses_selecionados_nomes:
        meses_selecionados = [nomes_para_meses[nome] for nome in meses_selecionados_nomes]
    else:
        meses_selecionados = meses_disponiveis_numeros
else:
    meses_selecionados = []
    st.sidebar.warning("Nenhum mês disponível para os anos selecionados")

# 3. FILTRO DE COMERCIAL (multiselect com checkbox "Todos")
st.sidebar.subheader("👨‍💼 Filtro por Comercial")

# Filtrar comerciais disponíveis nos anos e meses selecionados
if len(anos_selecionados) > 0 and len(meses_selecionados) > 0:
    comerciais_disponiveis = sorted(df[
        (df["Ano"].isin(anos_selecionados)) & 
        (df["MesNumero"].isin(meses_selecionados))
    ]["Comercial"].unique())
else:
    comerciais_disponiveis = sorted(df["Comercial"].unique())

todos_comerciais = st.sidebar.checkbox("Todos os Comerciais", value=True, key="todos_comerciais")

if todos_comerciais:
    comerciais_selecionados = comerciais_disponiveis
else:
    comerciais_selecionados = st.sidebar.multiselect(
        "Selecionar Comerciais",
        options=comerciais_disponiveis,
        default=comerciais_disponiveis[:min(10, len(comerciais_disponiveis))] if comerciais_disponiveis else []
    )
    
    if not comerciais_selecionados:
        comerciais_selecionados = comerciais_disponiveis

# 4. FILTRO DE CLIENTE (multiselect com checkbox "Todos")
st.sidebar.subheader("🏢 Filtro por Cliente")

# Filtrar clientes disponíveis nos filtros anteriores
if len(anos_selecionados) > 0 and len(meses_selecionados) > 0 and len(comerciais_selecionados) > 0:
    clientes_disponiveis = sorted(df[
        (df["Ano"].isin(anos_selecionados)) & 
        (df["MesNumero"].isin(meses_selecionados)) &
        (df["Comercial"].isin(comerciais_selecionados))
    ]["Cliente"].unique())
else:
    clientes_disponiveis = sorted(df["Cliente"].unique())

todos_clientes = st.sidebar.checkbox("Todos os Clientes", value=True, key="todos_clientes")

if todos_clientes:
    clientes_selecionados = clientes_disponiveis
else:
    clientes_selecionados = st.sidebar.multiselect(
        "Selecionar Clientes",
        options=clientes_disponiveis,
        default=clientes_disponiveis[:min(10, len(clientes_disponiveis))] if clientes_disponiveis else []
    )
    
    if not clientes_selecionados:
        clientes_selecionados = clientes_disponiveis

# 5. FILTRO DE ARTIGO (multiselect com checkbox "Todos")
st.sidebar.subheader("📦 Filtro por Artigo")

# Filtrar artigos disponíveis nos filtros anteriores
if (len(anos_selecionados) > 0 and len(meses_selecionados) > 0 and 
    len(comerciais_selecionados) > 0 and len(clientes_selecionados) > 0):
    artigos_disponiveis = sorted(df[
        (df["Ano"].isin(anos_selecionados)) & 
        (df["MesNumero"].isin(meses_selecionados)) &
        (df["Comercial"].isin(comerciais_selecionados)) &
        (df["Cliente"].isin(clientes_selecionados))
    ]["Artigo"].unique())
else:
    artigos_disponiveis = sorted(df["Artigo"].unique())

todos_artigos = st.sidebar.checkbox("Todos os Artigos", value=True, key="todos_artigos")

if todos_artigos:
    artigos_selecionados = artigos_disponiveis
else:
    artigos_selecionados = st.sidebar.multiselect(
        "Selecionar Artigos",
        options=artigos_disponiveis,
        default=artigos_disponiveis[:min(10, len(artigos_disponiveis))] if artigos_disponiveis else []
    )
    
    if not artigos_selecionados:
        artigos_selecionados = artigos_disponiveis

# === RESUMO DOS FILTROS APLICADOS ===
st.sidebar.divider()
st.sidebar.subheader("🎯 Resumo dos Filtros")

# Formatar exibição dos meses
meses_formatados = [meses_nomes[m] for m in meses_selecionados if m in meses_nomes]

st.sidebar.write(f"**Anos:** {', '.join(map(str, anos_selecionados))}")
st.sidebar.write(f"**Meses:** {', '.join(meses_formatados[:3])}{'...' if len(meses_formatados) > 3 else ''}")
st.sidebar.write(f"**Comerciais:** {len(comerciais_selecionados)} selecionados")
st.sidebar.write(f"**Clientes:** {len(clientes_selecionados)} selecionados")
st.sidebar.write(f"**Artigos:** {len(artigos_selecionados)} selecionados")

# Botão para limpar filtros
if st.sidebar.button("🔄 Limpar Todos os Filtros"):
    st.rerun()

# === DADOS FILTRADOS ===
df_filtrado = df[
    (df["Ano"].isin(anos_selecionados)) &
    (df["MesNumero"].isin(meses_selecionados)) &
    (df["Comercial"].isin(comerciais_selecionados)) &
    (df["Cliente"].isin(clientes_selecionados)) &
    (df["Artigo"].isin(artigos_selecionados))
].copy()

# Verificar se há dados após filtragem
if df_filtrado.empty:
    st.warning("⚠️ Não há dados disponíveis com os filtros selecionados. Tente ajustar os filtros.")
    
    # Mostrar estatísticas para ajudar o usuário
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Anos disponíveis:** {', '.join(map(str, anos_disponiveis))}")
    with col2:
        st.info(f"**Comerciais disponíveis:** {len(comerciais_disponiveis)}")
    with col3:
        st.info(f"**Clientes disponíveis:** {len(clientes_disponiveis)}")
    
    st.stop()

# === ANÁLISE TEMPORAL ===
# Determinar anos para comparação
if len(anos_selecionados) >= 2:
    # Se múltiplos anos selecionados, comparar o mais recente com o segundo mais recente
    anos_ordenados = sorted(anos_selecionados, reverse=True)
    ano_atual = anos_ordenados[0]
    ano_anterior = anos_ordenados[1]
    tem_comparacao = True
    tipo_comparacao = "multiplos_anos"
elif len(anos_selecionados) == 1:
    # Se apenas um ano, tentar comparar com ano anterior se disponível
    ano_atual = anos_selecionados[0]
    ano_anterior_possivel = ano_atual - 1
    tem_ano_anterior_disponivel = ano_anterior_possivel in df["Ano"].unique()
    
    if tem_ano_anterior_disponivel:
        ano_anterior = ano_anterior_possivel
        tem_comparacao = True
        tipo_comparacao = "ano_anterior"
    else:
        tem_comparacao = False
        tipo_comparacao = "unico_ano"
else:
    tem_comparacao = False
    tipo_comparacao = "sem_dados"

# Separar dados
df_atual = df_filtrado[df_filtrado["Ano"] == ano_atual].copy()

if tem_comparacao:
    if tipo_comparacao == "ano_anterior":
        df_anterior = df[
            (df["Ano"] == ano_anterior) &
            (df["MesNumero"].isin(meses_selecionados)) &
            (df["Comercial"].isin(comerciais_selecionados)) &
            (df["Cliente"].isin(clientes_selecionados)) &
            (df["Artigo"].isin(artigos_selecionados))
        ].copy()
    else:  # multiplos_anos
        df_anterior = df_filtrado[df_filtrado["Ano"] == ano_anterior].copy()
else:
    df_anterior = pd.DataFrame(columns=df.columns)

# === CÁLCULO DOS KPIs ===
# KPIs para ano atual
total_atual = df_atual["Quantidade"].sum()
n_clientes_atual = df_atual["Cliente"].nunique()
n_artigos_atual = df_atual["Artigo"].nunique()
n_comerciais_atual = df_atual["Comercial"].nunique()
ticket_atual = total_atual / len(df_atual) if len(df_atual) > 0 else 0

# Encontrar top cliente atual
if not df_atual.empty:
    top_cliente_series = df_atual.groupby("Cliente")["Quantidade"].sum()
    top_cliente = top_cliente_series.idxmax()
    top_qtd = top_cliente_series.max()
else:
    top_cliente = "—"
    top_qtd = 0

# KPIs para comparação (se houver)
if tem_comparacao and not df_anterior.empty:
    total_anterior = df_anterior["Quantidade"].sum()
    n_clientes_anterior = df_anterior["Cliente"].nunique()
    n_artigos_anterior = df_anterior["Artigo"].nunique()
    ticket_anterior = total_anterior / len(df_anterior) if len(df_anterior) > 0 else 0
    
    # Cálculos de variação
    var_total = total_atual - total_anterior
    var_pct = (var_total / total_anterior * 100) if total_anterior > 0 else 0
    var_clientes = n_clientes_atual - n_clientes_anterior
    var_artigos = n_artigos_atual - n_artigos_anterior
    var_ticket = ticket_atual - ticket_anterior
else:
    total_anterior = 0
    n_clientes_anterior = 0
    n_artigos_anterior = 0
    ticket_anterior = 0
    var_total = 0
    var_pct = 0
    var_clientes = 0
    var_artigos = 0
    var_ticket = 0

# === 8 KPIs BONITOS NO TOPO ===
# Título dinâmico baseado no tipo de comparação
if tipo_comparacao == "multiplos_anos":
    st.markdown(f"### 📊 Resumo Executivo – Comparativo {ano_anterior} vs {ano_atual}")
elif tipo_comparacao == "ano_anterior":
    st.markdown(f"### 📊 Resumo Executivo – {ano_atual} vs {ano_anterior}")
else:
    st.markdown(f"### 📊 Resumo Executivo – {ano_atual}")

c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

with c1:
    if tem_comparacao:
        st.metric("Total Quantidade", f"{total_atual:,.0f}", f"{var_total:+,.0f}")
    else:
        st.metric("Total Quantidade", f"{total_atual:,.0f}")

with c2:
    if tem_comparacao:
        st.metric("Variação %", f"{var_pct:+.1f}%", delta_color="normal")
    else:
        st.metric("Variação %", "—")

with c3:
    if tem_comparacao:
        st.metric("Clientes Únicos", n_clientes_atual, f"{var_clientes:+d}")
    else:
        st.metric("Clientes Únicos", n_clientes_atual)

with c4:
    if tem_comparacao:
        st.metric("Artigos Vendidos", n_artigos_atual, f"{var_artigos:+d}")
    else:
        st.metric("Artigos Vendidos", n_artigos_atual)

with c5:
    st.metric("Comerciais Ativos", n_comerciais_atual)

with c6:
    if tem_comparacao:
        st.metric("Ticket Médio", f"{ticket_atual:,.1f}", f"{var_ticket:+.1f}")
    else:
        st.metric("Ticket Médio", f"{ticket_atual:,.1f}")

with c7:
    st.metric("Top Cliente", top_cliente[:15] + "..." if len(top_cliente) > 15 else top_cliente)

with c8:
    st.metric("Qtd Top Cliente", f"{top_qtd:,.0f}")

st.divider()

# === EVOLUÇÃO MENSAL ===
st.subheader("📈 Evolução Mensal")

# Preparar dados para gráfico
ordem_meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

if tipo_comparacao == "multiplos_anos":
    # Gráfico com múltiplos anos selecionados
    anos_para_grafico = sorted(anos_selecionados, reverse=True)[:5]  # Limitar a 5 anos para legibilidade
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    cores = ["#2E86AB", "#A23B72", "#F18F01", "#73AB84", "#C14953"]
    
    for idx, ano in enumerate(anos_para_grafico):
        df_ano = df_filtrado[df_filtrado["Ano"] == ano]
        if not df_ano.empty:
            evol_ano = df_ano.groupby("MesNome")["Quantidade"].sum().reindex(ordem_meses, fill_value=0)
            ax.plot(ordem_meses, evol_ano.values, 
                   marker="o", linewidth=3, label=str(ano), 
                   color=cores[idx % len(cores)])
    
    ax.set_title(f"Evolução Mensal por Ano", fontsize=15, fontweight="bold")
    ax.set_ylabel("Quantidade")
    ax.legend(title="Ano", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    
elif tem_comparacao:
    # Gráfico comparativo de dois anos
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Ano atual
    evol_atual = df_atual.groupby("MesNome")["Quantidade"].sum().reindex(ordem_meses, fill_value=0)
    ax.plot(ordem_meses, evol_atual.values, marker="o", linewidth=4, label=str(ano_atual), color="#2E86AB")
    
    # Ano anterior
    if not df_anterior.empty:
        evol_ant = df_anterior.groupby("MesNome")["Quantidade"].sum().reindex(ordem_meses, fill_value=0)
        ax.plot(ordem_meses, evol_ant.values, marker="o", linewidth=4, label=str(ano_anterior), color="#A23B72", alpha=0.7)
    
    ax.set_title(f"Evolução Mensal – {ano_atual} vs {ano_anterior}", fontsize=15, fontweight="bold")
    ax.set_ylabel("Quantidade")
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    
else:
    # Apenas um ano
    fig, ax = plt.subplots(figsize=(14, 6))
    
    evol_atual = df_atual.groupby("MesNome")["Quantidade"].sum().reindex(ordem_meses, fill_value=0)
    ax.bar(ordem_meses, evol_atual.values, color="#2E86AB", alpha=0.7)
    
    # Adicionar linha de tendência
    ax.plot(ordem_meses, evol_atual.values, marker="o", color="#2E86AB", linewidth=2)
    
    ax.set_title(f"Evolução Mensal – {ano_atual}", fontsize=15, fontweight="bold")
    ax.set_ylabel("Quantidade")
    ax.grid(alpha=0.3, axis='y')
    st.pyplot(fig)

st.divider()

# === TOP 10 CLIENTES ===
st.subheader("🏆 Top 10 Clientes")

if tipo_comparacao == "multiplos_anos" and len(anos_selecionados) >= 2:
    # Top 10 clientes comparando múltiplos anos
    anos_top = sorted(anos_selecionados, reverse=True)[:3]  # Limitar a 3 anos para legibilidade
    
    top_clientes_data = {}
    for ano in anos_top:
        df_ano = df_filtrado[df_filtrado["Ano"] == ano]
        if not df_ano.empty:
            top10 = df_ano.groupby("Cliente")["Quantidade"].sum().nlargest(10)
            top_clientes_data[ano] = top10
    
    if top_clientes_data:
        # Combinar todos os clientes que aparecem no top 10 de qualquer ano
        todos_clientes_top = set()
        for top10 in top_clientes_data.values():
            todos_clientes_top.update(top10.index)
        
        # Criar DataFrame comparativo
        comp = pd.DataFrame(index=list(todos_clientes_top))
        for ano in anos_top:
            if ano in top_clientes_data:
                comp[ano] = top_clientes_data[ano].reindex(comp.index).fillna(0)
        
        # Ordenar pela soma total
        comp["Total"] = comp.sum(axis=1)
        comp = comp.sort_values("Total", ascending=False).head(10).drop(columns="Total")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            comp.plot(kind="barh", ax=ax2, width=0.8)
            ax2.set_title(f"Top 10 Clientes - Comparativo por Ano")
            ax2.invert_yaxis()
            ax2.legend(title="Ano", bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            st.pyplot(fig2)
        
        with col2:
            st.write("**Dados Comparativos:**")
            disp = comp.copy()
            for col in disp.columns:
                disp[col] = disp[col].apply(lambda x: f"{x:,.0f}")
            st.dataframe(disp, use_container_width=True, height=400)
    
elif tem_comparacao:
    # Comparativo entre dois anos
    if not df_atual.empty:
        top10_atual = df_atual.groupby("Cliente")["Quantidade"].sum().nlargest(10)
        
        comp = pd.DataFrame({
            str(ano_atual): top10_atual
        })
        
        # Adicionar dados do ano anterior se disponível
        if not df_anterior.empty:
            top10_anterior = df_anterior.groupby("Cliente")["Quantidade"].sum()
            comp[str(ano_anterior)] = top10_anterior.reindex(comp.index).fillna(0)
            
            # Calcular variações
            comp["Variação"] = comp[str(ano_atual)] - comp[str(ano_anterior)]
            comp["Var %"] = (comp["Variação"] / comp[str(ano_anterior)].replace(0, 1) * 100).round(1)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            
            if tem_comparacao and not df_anterior.empty:
                comp[[str(ano_anterior), str(ano_atual)]].plot(
                    kind="barh", ax=ax2, color=["#A23B72", "#2E86AB"]
                )
                ax2.set_title(f"Top 10 Clientes - {ano_anterior} vs {ano_atual}")
            else:
                comp[[str(ano_atual)]].plot(kind="barh", ax=ax2, color="#2E86AB")
                ax2.set_title(f"Top 10 Clientes - {ano_atual}")
            
            ax2.invert_yaxis()
            st.pyplot(fig2)
        
        with col2:
            st.write("**Detalhes:**")
            disp = comp.copy()
            
            # Formatar números
            for col in disp.columns:
                if disp[col].dtype in ['int64', 'float64']:
                    if col in ["Variação", str(ano_atual), str(ano_anterior)]:
                        disp[col] = disp[col].apply(lambda x: f"{x:,.0f}")
                    elif col == "Var %":
                        disp[col] = disp[col].apply(lambda x: f"{x:+.1f}%" if pd.notnull(x) else "—")
            
            st.dataframe(disp, use_container_width=True, height=400)
    
else:
    # Apenas um ano
    if not df_atual.empty:
        top10 = df_atual.groupby("Cliente")["Quantidade"].sum().nlargest(10)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            top10.plot(kind="barh", ax=ax2, color="#2E86AB")
            ax2.set_title(f"Top 10 Clientes - {ano_atual}")
            ax2.invert_yaxis()
            ax2.set_xlabel("Quantidade")
            st.pyplot(fig2)
        
        with col2:
            st.write("**Ranking:**")
            ranking_df = pd.DataFrame({
                "Cliente": top10.index,
                "Quantidade": top10.values
            })
            ranking_df["Quantidade"] = ranking_df["Quantidade"].apply(lambda x: f"{x:,.0f}")
            ranking_df.index = range(1, len(ranking_df) + 1)
            st.dataframe(ranking_df, use_container_width=True, height=400)

st.divider()

# === ANÁLISE ADICIONAL ===
st.subheader("📋 Análise Detalhada")

tab1, tab2, tab3 = st.tabs(["📊 Por Comercial", "📦 Por Artigo", "📅 Por Período"])

with tab1:
    st.write("**Desempenho por Comercial:**")
    if not df_filtrado.empty:
        por_comercial = df_filtrado.groupby("Comercial").agg({
            "Quantidade": "sum",
            "Cliente": "nunique",
            "Artigo": "nunique"
        }).sort_values("Quantidade", ascending=False)
        
        por_comercial.columns = ["Total Quantidade", "Clientes Únicos", "Artigos Vendidos"]
        por_comercial["Total Quantidade"] = por_comercial["Total Quantidade"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(por_comercial, use_container_width=True)

with tab2:
    st.write("**Artigos Mais Vendidos:**")
    if not df_filtrado.empty:
        por_artigo = df_filtrado.groupby("Artigo").agg({
            "Quantidade": "sum",
            "Cliente": "nunique"
        }).sort_values("Quantidade", ascending=False).head(20)
        
        por_artigo.columns = ["Total Quantidade", "Clientes Compradores"]
        por_artigo["Total Quantidade"] = por_artigo["Total Quantidade"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(por_artigo, use_container_width=True)

with tab3:
    st.write("**Análise por Período:**")
    if not df_filtrado.empty:
        por_periodo = df_filtrado.groupby(["Ano", "MesNumero"]).agg({
            "Quantidade": "sum",
            "Cliente": "nunique"
        }).sort_values(["Ano", "MesNumero"], ascending=[False, True])
        
        por_periodo.columns = ["Total Quantidade", "Clientes Únicos"]
        por_periodo["Total Quantidade"] = por_periodo["Total Quantidade"].apply(lambda x: f"{x:,.0f}")
        por_periodo.index.names = ["Ano", "Mês"]
        st.dataframe(por_periodo, use_container_width=True)

st.divider()

# === EXPORTAR EXCEL ===
st.subheader("📤 Exportar Relatório")

if not df_filtrado.empty:
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        # Resumo dos filtros
        resumo_filtros = pd.DataFrame({
            "Parâmetro": ["Data Exportação", "Anos Selecionados", "Meses Selecionados", 
                         "Comerciais Selecionados", "Clientes Selecionados", "Artigos Selecionados",
                         "Total Registros", "Total Quantidade"],
            "Valor": [
                datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                ", ".join(map(str, anos_selecionados)),
                ", ".join(meses_formatados),
                f"{len(comerciais_selecionados)} comerciais",
                f"{len(clientes_selecionados)} clientes",
                f"{len(artigos_selecionados)} artigos",
                f"{len(df_filtrado):,}",
                f"{df_filtrado['Quantidade'].sum():,.0f}"
            ]
        })
        resumo_filtros.to_excel(writer, sheet_name="Resumo", index=False)
        
        # KPIs
        kpis_data = pd.DataFrame({
            "KPI": ["Total Quantidade", "Clientes Únicos", "Artigos Vendidos", 
                   "Comerciais Ativos", "Ticket Médio", "Top Cliente", "Quantidade Top Cliente"],
            f"{ano_atual}": [total_atual, n_clientes_atual, n_artigos_atual, 
                           n_comerciais_atual, ticket_atual, top_cliente, top_qtd]
        })
        
        if tem_comparacao:
            kpis_data[f"{ano_anterior}"] = [total_anterior, n_clientes_anterior, 
                                          n_artigos_anterior, "—", ticket_anterior, "—", "—"]
            kpis_data["Variação"] = [var_total, var_clientes, var_artigos, 
                                   "—", var_ticket, "—", "—"]
            kpis_data["Var %"] = [var_pct, f"{(var_clientes/n_clientes_anterior*100):.1f}%" if n_clientes_anterior > 0 else "—",
                                f"{(var_artigos/n_artigos_anterior*100):.1f}%" if n_artigos_anterior > 0 else "—",
                                "—", f"{(var_ticket/ticket_anterior*100):.1f}%" if ticket_anterior > 0 else "—",
                                "—", "—"]
        
        kpis_data.to_excel(writer, sheet_name="KPIs", index=False)
        
        # Dados detalhados
        df_filtrado[["Data", "Ano", "MesNome", "Comercial", "Cliente", "Artigo", "Quantidade"]].to_excel(
            writer, sheet_name="Dados Detalhados", index=False)
        
        # Top 10 clientes
        if not df_filtrado.empty:
            top_clientes_export = df_filtrado.groupby("Cliente")["Quantidade"].sum().nlargest(20)
            top_clientes_export.to_excel(writer, sheet_name="Top_Clientes")
        
        # Top 10 artigos
        if not df_filtrado.empty:
            top_artigos_export = df_filtrado.groupby("Artigo")["Quantidade"].sum().nlargest(20)
            top_artigos_export.to_excel(writer, sheet_name="Top_Artigos")
    
    # Botão de download
    st.download_button(
        "⬇️ Baixar Relatório Completo (Excel)",
        data=output.getvalue(),
        file_name=f"Dashboard_Compras_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.success("✅ Dashboard carregado com sucesso! Use os filtros na sidebar para explorar os dados.")
