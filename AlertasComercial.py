import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO
import unicodedata

# --- Estilo visual ---
st.set_page_config(page_title="Compras por Cliente", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3 { color: #2c3e50; font-weight: 600; }
    .stSelectbox label { font-weight: bold; color: #34495e; }
    .stDownloadButton button {
        background-color: #3498db; color: white; border-radius: 5px;
        padding: 0.5em 1em; font-weight: bold;
    }
    .stDownloadButton button:hover { background-color: #2980b9; }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Dashboard de Compras")

@st.cache_data
def carregar_dados():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    df = pd.read_excel(url)

    # --- Normalizar nomes de colunas ---
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(".", "", regex=False)
        .map(lambda x: unicodedata.normalize('NFKD', x).encode('ascii', errors='ignore').decode('utf-8'))
    )

    # --- Mapeamento inteligente ---
    esperadas = {
        'cliente': ['cliente'],
        'comercial': ['comercial'],
        'ano': ['ano'],
        'mes': ['mes'],
        'qtd': ['qtd', 'quantidade'],
        'v_liquido': ['v_liquido', 'vl_liquido', 'valor_liquido'],
        'pm': ['pm', 'preco_medio'],
        'categoria': ['categoria', 'segmento']
    }

    detectadas = list(df.columns)
    col_map = {}

    for chave, variantes in esperadas.items():
        for variante in variantes:
            for col in detectadas:
                if variante == col or variante.replace("_", "") in col.replace("_", ""):
                    col_map[chave] = col
                    break
            if chave in col_map:
                break

    faltantes = [chave for chave in esperadas if chave not in col_map]
    if faltantes:
        st.warning(f"⚠️ Colunas não encontradas ou ambíguas: {faltantes}")
        st.write("🔍 Colunas detectadas:", detectadas)
        st.stop()

    df = df.rename(columns=col_map)

    df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
    df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
    df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')
    df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')
    df['pm'] = pd.to_numeric(df['pm'], errors='coerce')

    return df

df = carregar_dados()

# --- Sidebar: Filtros e navegação ---
st.sidebar.title("📂 Navegação")
pagina = st.sidebar.radio("Ir para:", [
    "Visão Geral", "Gráficos", "Alertas", "Histórico do Cliente"
])

# --- FILTROS DINÂMICOS CORRIGIDOS ---
# Criar dados base sem filtros
dados_base = df.copy()

# Inicializar filtros no session state
if 'ano_selecionado' not in st.session_state:
    st.session_state.ano_selecionado = "Todos"
if 'comercial_selecionado' not in st.session_state:
    st.session_state.comercial_selecionado = "Todos"
if 'cliente_selecionado' not in st.session_state:
    st.session_state.cliente_selecionado = "Todos"
if 'mes_selecionado' not in st.session_state:
    st.session_state.mes_selecionado = "Todos"

# Função para aplicar filtros progressivamente
def aplicar_filtros(dados, ano, comercial, cliente, mes):
    resultado = dados.copy()
    
    if ano != "Todos":
        resultado = resultado[resultado['ano'] == ano]
    if comercial != "Todos":
        resultado = resultado[resultado['comercial'] == comercial]
    if cliente != "Todos":
        resultado = resultado[resultado['cliente'] == cliente]
    if mes != "Todos":
        resultado = resultado[resultado['mes'] == mes]
    
    return resultado

# Obter opções disponíveis baseado nos filtros anteriores
def get_opcoes_dinamicas(dados, filtros_atuais):
    """Retorna opções disponíveis para cada filtro"""
    anos_disponiveis = sorted(dados['ano'].dropna().unique())
    comerciais_disponiveis = sorted(dados['comercial'].dropna().unique())
    clientes_disponiveis = sorted(dados['cliente'].dropna().unique())
    meses_disponiveis = sorted(dados['mes'].dropna().unique())
    
    return {
        'anos': anos_disponiveis,
        'comerciais': comerciais_disponiveis,
        'clientes': clientes_disponiveis,
        'meses': meses_disponiveis
    }

opcoes = get_opcoes_dinamicas(dados_base, None)

# Selecionar filtros
anos_lista = list(opcoes['anos'])
ano = st.sidebar.selectbox(
    "Seleciona o Ano",
    ["Todos"] + anos_lista
)
st.session_state.ano_selecionado = ano

# Atualizar dados para próximos filtros
dados_filtrados_ano = aplicar_filtros(dados_base, ano, "Todos", "Todos", "Todos")
opcoes_comercial = sorted(dados_filtrados_ano['comercial'].dropna().unique())

comercial = st.sidebar.selectbox(
    "Seleciona o Comercial",
    ["Todos"] + opcoes_comercial
)
st.session_state.comercial_selecionado = comercial

# Atualizar dados para próximos filtros
dados_filtrados_comercial = aplicar_filtros(dados_base, ano, comercial, "Todos", "Todos")
opcoes_cliente = sorted(dados_filtrados_comercial['cliente'].dropna().unique())

cliente = st.sidebar.selectbox(
    "Seleciona o Cliente",
    ["Todos"] + opcoes_cliente
)
st.session_state.cliente_selecionado = cliente

# Atualizar dados para próximo filtro
dados_filtrados_cliente = aplicar_filtros(dados_base, ano, comercial, cliente, "Todos")
opcoes_mes = sorted(dados_filtrados_cliente['mes'].dropna().unique())

mes = st.sidebar.selectbox(
    "Seleciona o Mês",
    ["Todos"] + opcoes_mes
)
st.session_state.mes_selecionado = mes

# Aplicar todos os filtros
dados_filtrados = aplicar_filtros(dados_base, ano, comercial, cliente, mes)

# --- Corrigir colunas problemáticas para Arrow ---
for col in dados_filtrados.select_dtypes(include='object').columns:
    dados_filtrados[col] = dados_filtrados[col].astype(str)

# --- Função para exportar Excel ---
def gerar_excel(dados):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dados.to_excel(writer, index=False, sheet_name='Compras')
    return output.getvalue()

# --- Página: Visão Geral ---
if pagina == "Visão Geral":
    st.subheader("📊 Visão Geral das Compras")

    total_qtd = dados_filtrados['qtd'].sum()
    clientes_ativos = dados_filtrados['cliente'].nunique()
    comerciais_ativos = dados_filtrados['comercial'].nunique()
    media_por_cliente = total_qtd / clientes_ativos if clientes_ativos > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total Qtd.", f"{total_qtd:,.0f}")
    col2.metric("👥 Clientes Ativos", clientes_ativos)
    col3.metric("🧑‍💼 Comerciais Ativos", comerciais_ativos)

    col4, _, col6 = st.columns(3)
    col4.metric("📈 Média por Cliente", f"{media_por_cliente:,.2f}")
    col6.empty()

    st.markdown("### 📋 Tabela de Compras Filtradas")
    st.dataframe(dados_filtrados)
    st.download_button("📥 Exportar dados filtrados", data=gerar_excel(dados_filtrados), file_name="compras_filtradas.xlsx")

    # --- Detalhes do cliente selecionado ---
    if cliente != "Todos":
        st.subheader(f"📋 Detalhes do Cliente: {cliente}")
        dados_cliente = dados_filtrados[dados_filtrados['cliente'] == cliente]
        resumo = dados_cliente.groupby(['comercial', 'categoria', 'ano', 'mes'])['qtd'].sum().reset_index()
        resumo.rename(columns={'qtd': 'Total Qtd.'}, inplace=True)

        for col in resumo.select_dtypes(include='object').columns:
            resumo[col] = resumo[col].astype(str)

        st.dataframe(resumo)
        st.download_button("📥 Exportar resumo do cliente", data=gerar_excel(resumo), file_name=f"resumo_{cliente}.xlsx")

# --- Página: Gráficos ---
elif pagina == "Gráficos":
    st.subheader("📉 Quantidade por Cliente ao Longo dos Meses")

    pivot_cliente = dados_filtrados.pivot_table(index='mes', columns='cliente', values='qtd', aggfunc='sum').fillna(0)
    if not pivot_cliente.empty:
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        pivot_cliente.plot(kind='bar', stacked=True, ax=ax1, colormap='tab20')
        ax1.set_title('Compras por Cliente')
        ax1.set_xlabel('Mês')
        ax1.set_ylabel('Quantidade Total')
        st.pyplot(fig1)
    else:
        st.warning("⚠️ Sem dados para o gráfico de clientes.")

    st.subheader("📈 Evolução Mensal por Comercial")
    pivot_comercial = dados_filtrados.pivot_table(index='mes', columns='comercial', values='qtd', aggfunc='sum').fillna(0)
    if not pivot_comercial.empty:
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        pivot_comercial.plot(kind='line', marker='o', ax=ax2, colormap='Set1')
        ax2.set_title('Evolução Mensal por Comercial')
        ax2.set_xlabel('Mês')
        ax2.set_ylabel('Quantidade Total')
        st.pyplot(fig2)
    else:
        st.warning("⚠️ Sem dados para o gráfico de comerciais.")

# --- Página: Alertas ---
elif pagina == "Alertas":
    st.subheader("🚨 Clientes com meses em falta")

    todos_meses = sorted(df['mes'].dropna().unique())
    presenca = dados_filtrados.groupby(['cliente', 'mes'])['qtd'].sum().unstack(fill_value=0)
    presenca = presenca.reindex(columns=todos_meses, fill_value=0)

    ausentes = presenca[presenca.eq(0)].astype(bool)
    clientes_inativos = ausentes.any(axis=1)

    if not clientes_inativos.any():
        st.success("✅ Todos os clientes compraram em todos os meses disponíveis.")
    else:
        st.error(f"⚠️ {clientes_inativos.sum()} clientes com meses em falta")

        st.markdown("### 📋 Tabela de presença mensal por cliente")
        tabela_alerta = presenca.copy().astype(int)

        def destacar_faltas(val):
            return 'background-color: #f8d7da' if val == 0 else ''

        tabela_alerta.index = tabela_alerta.index.astype(str)
        st.dataframe(tabela_alerta.style.applymap(destacar_faltas))
        st.download_button("📥 Exportar presença mensal", data=gerar_excel(tabela_alerta.reset_index()), file_name="presenca_clientes.xlsx")

# --- Página: Histórico do Cliente ---
elif pagina == "Histórico do Cliente":
    st.subheader("📅 Histórico Mensal de Compras")

    if cliente == "Todos":
        st.info("👈 Seleciona um cliente na barra lateral para ver o histórico.")
    else:
        dados_cliente = dados_filtrados[dados_filtrados['cliente'] == cliente]

        if dados_cliente.empty:
            st.warning("⚠️ Sem dados disponíveis para este cliente.")
        else:
            historico = (
                dados_cliente
                .groupby(['ano', 'mes'])['qtd']
                .sum()
                .reset_index()
                .sort_values(['ano', 'mes'])
                .rename(columns={'qtd': 'Qtd. Comprada'})
            )

            # Corrigir colunas para Arrow
            for col in historico.select_dtypes(include='object').columns:
                historico[col] = historico[col].astype(str)

            st.markdown("### 📋 Tabela de Compras por Mês")
            st.dataframe(historico)
            st.download_button(
                "📥 Exportar histórico do cliente",
                data=gerar_excel(historico),
                file_name=f"historico_{cliente}.xlsx"
            )

            # Análise de crescimento/queda
            historico['Delta'] = historico['Qtd. Comprada'].diff()
            historico['Crescimento'] = historico['Delta'] > 0
            historico['Queda'] = historico['Delta'] < 0

            fig = px.line(
                historico,
                x='mes',
                y='Qtd. Comprada',
                markers=True,
                title=f"Evolução Mensal - {cliente}",
                labels={'Qtd. Comprada': 'Quantidade', 'mes': 'Mês'}
            )

            fig.add_scatter(
                x=historico.loc[historico['Crescimento'], 'mes'],
                y=historico.loc[historico['Crescimento'], 'Qtd. Comprada'],
                mode='markers',
                marker=dict(color='green', size=10, symbol='circle'),
                name='Crescimento'
            )

            fig.add_scatter(
                x=historico.loc[historico['Queda'], 'mes'],
                y=historico.loc[historico['Queda'], 'Qtd. Comprada'],
                mode='markers',
                marker=dict(color='red', size=10, symbol='x'),
                name='Queda'
            )

            fig.update_layout(xaxis_title="Mês", yaxis_title="Quantidade", legend_title="Indicador")
            st.plotly_chart(fig, use_container_width=True)

            # Comparação com média dos demais clientes
            st.markdown("### 📊 Comparação com Média dos Clientes")
            media_geral = (
                df[df['cliente'] != cliente]
                .groupby(['ano', 'mes'])['qtd']
                .mean()
                .reset_index()
                .rename(columns={'qtd': 'Qtd. Média'})
            )

            comparativo = pd.merge(historico, media_geral, on=['ano', 'mes'], how='left')

            fig_comp = px.line(
                comparativo,
                x='mes',
                y=['Qtd. Comprada', 'Qtd. Média'],
                markers=True,
                labels={'value': 'Quantidade', 'variable': 'Indicador'},
                title=f"Comparativo de Quantidade - {cliente} vs Média"
            )
            fig_comp.update_layout(xaxis_title="Mês", yaxis_title="Quantidade", legend_title="Indicador")
            st.plotly_chart(fig_comp, use_container_width=True)

            # Destaque de crescimento
            st.markdown("### 📈 Destaque de Crescimentos Mensais")
            if st.button("🔍 Mostrar meses com crescimento"):
                crescimentos = historico[historico['Delta'] > 0]
                if crescimentos.empty:
                    st.info("ℹ️ Não houve crescimento em relação ao mês anterior.")
                else:
                    st.success(f"✅ {len(crescimentos)} meses com crescimento detectado:")
                    st.dataframe(crescimentos[['ano', 'mes', 'Qtd. Comprada', 'Delta']])
