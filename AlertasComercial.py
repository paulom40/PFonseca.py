import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO
import unicodedata

# --- Estilo visual ---
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
    .stMarkdown h2 { border-left: 5px solid #3498db; padding-left: 10px; margin-top: 1em; }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Compras por Cliente", layout="wide")
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

anos = sorted(df['ano'].dropna().unique())
comerciais = sorted(df['comercial'].dropna().unique())
clientes = sorted(df['cliente'].dropna().unique())
meses = sorted(df['mes'].dropna().unique())

ano = st.sidebar.selectbox("Seleciona o Ano", ["Todos"] + anos)
comercial = st.sidebar.selectbox("Seleciona o Comercial", ["Todos"] + comerciais)
cliente = st.sidebar.selectbox("Seleciona o Cliente", ["Todos"] + clientes)
mes = st.sidebar.selectbox("Seleciona o Mês", ["Todos"] + meses)

# --- Filtro adaptativo ---
dados_filtrados = df.copy()
if ano != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['ano'] == ano]
if comercial != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['comercial'] == comercial]
if cliente != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['cliente'] == cliente]
if mes != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['mes'] == mes]

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
        dados_cliente = df[df['cliente'] == cliente]
        resumo = dados_cliente.groupby(['cliente', 'comercial', 'categoria', 'ano', 'mes'])['qtd'].sum().reset_index()
        resumo.rename(columns={'qtd': 'Total Qtd.'}, inplace=True)
        st.dataframe(resumo)
        st.download_button("📥 Exportar resumo do cliente", data=gerar_excel(resumo), file_name=f"resumo_{cliente}.xlsx")
# --- Página: Gráficos ---
elif pagina == "Gráficos":
    st.subheader("📉 Quantidade por Cliente ao Longo dos Meses")

    dados_grafico = dados_filtrados.copy()
    if cliente != "Todos":
        dados_grafico = dados_grafico[dados_grafico['cliente'] == cliente]

    pivot_cliente = dados_grafico.pivot_table(index='mes', columns='cliente', values='qtd', aggfunc='sum').fillna(0)
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
    pivot_comercial = dados_grafico.pivot_table(index='mes', columns='comercial', values='qtd', aggfunc='sum').fillna(0)
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

    dados_alerta = dados_filtrados.copy()
    if cliente != "Todos":
        dados_alerta = dados_alerta[dados_alerta['cliente'] == cliente]

    todos_meses = sorted(dados_alerta['mes'].dropna().unique())
    presenca = dados_alerta.groupby(['cliente', 'mes'])['qtd'].sum().unstack(fill_value=0)
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

        st.dataframe(tabela_alerta.style.applymap(destacar_faltas))
        st.download_button("📥 Exportar presença mensal", data=gerar_excel(tabela_alerta.reset_index()), file_name="presenca_clientes.xlsx")
# --- Página: Gráficos ---
elif pagina == "Gráficos":
    st.subheader("📉 Quantidade por Cliente ao Longo dos Meses")

    dados_grafico = dados_filtrados.copy()
    if cliente != "Todos":
        dados_grafico = dados_grafico[dados_grafico['cliente'] == cliente]

    pivot_cliente = dados_grafico.pivot_table(index='mes', columns='cliente', values='qtd', aggfunc='sum').fillna(0)
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
    pivot_comercial = dados_grafico.pivot_table(index='mes', columns='comercial', values='qtd', aggfunc='sum').fillna(0)
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

    dados_alerta = dados_filtrados.copy()
    if cliente != "Todos":
        dados_alerta = dados_alerta[dados_alerta['cliente'] == cliente]

    todos_meses = sorted(dados_alerta['mes'].dropna().unique())
    presenca = dados_alerta.groupby(['cliente', 'mes'])['qtd'].sum().unstack(fill_value=0)
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

        st.dataframe(tabela_alerta.style.applymap(destacar_faltas))
        st.download_button("📥 Exportar presença mensal", data=gerar_excel(tabela_alerta.reset_index()), file_name="presenca_clientes.xlsx")
