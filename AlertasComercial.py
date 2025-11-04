import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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
pagina = st.sidebar.radio("Ir para:", ["Visão Geral", "Gráficos", "Alertas"])

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

agrupado = dados_filtrados.groupby(['cliente', 'comercial', 'ano', 'mes'])['qtd'].sum().reset_index()

# --- Função para exportar Excel ---
def gerar_excel(dados):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dados.to_excel(writer, index=False, sheet_name='Compras')
    return output.getvalue()
if pagina == "Visão Geral":
    st.subheader("📊 Visão Geral das Compras")

    # --- KPIs dinâmicos ---
    total_vl = dados_filtrados['v_liquido'].sum()
    total_qtd = dados_filtrados['qtd'].sum()
    clientes_ativos = dados_filtrados['cliente'].nunique()
    comerciais_ativos = dados_filtrados['comercial'].nunique()
    pm_medio = total_vl / total_qtd if total_qtd > 0 else 0
    media_por_cliente = total_vl / clientes_ativos if clientes_ativos > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total V. Líquido", f"{total_vl:,.2f} €")
    col2.metric("📦 Total Qtd.", f"{total_qtd:,.0f}")
    col3.metric("🧮 PM Médio", f"{pm_medio:,.2f} €")

    col4, col5, col6 = st.columns(3)
    col4.metric("👥 Clientes Ativos", clientes_ativos)
    col5.metric("🧑‍💼 Comerciais Ativos", comerciais_ativos)
    col6.metric("📈 Média por Cliente", f"{media_por_cliente:,.2f} €")

    # --- Tabela com dados filtrados ---
    st.markdown("### 📋 Tabela de Compras Filtradas")
    st.dataframe(dados_filtrados)

    excel_bytes = gerar_excel(dados_filtrados)
    st.download_button("📥 Exportar dados filtrados", data=excel_bytes, file_name="compras_filtradas.xlsx")

    # --- Detalhes do cliente selecionado ---
    if cliente != "Todos":
        st.subheader(f"📋 Detalhes do Cliente: {cliente}")
        dados_cliente = df[df['cliente'] == cliente]

        resumo = dados_cliente.groupby(['cliente', 'comercial', 'categoria', 'ano', 'mes']).agg({
            'qtd': 'sum',
            'pm': 'mean',
            'v_liquido': 'sum'
        }).reset_index()

        resumo.rename(columns={
            'qtd': 'Total Qtd.',
            'pm': 'PM Médio',
            'v_liquido': 'Total V. Líquido'
        }, inplace=True)

        st.dataframe(resumo)

        excel_bytes_cliente = gerar_excel(resumo)
        st.download_button("📥 Exportar resumo do cliente", data=excel_bytes_cliente, file_name=f"resumo_{cliente}.xlsx")
# --- Página: Gráficos ---
elif pagina == "Gráficos":
    st.subheader("📉 Quantidade por Cliente ao Longo dos Meses")

    pivot_cliente = dados_filtrados.pivot_table(
        index='mes', columns='cliente', values='qtd', aggfunc='sum'
    ).fillna(0)

    if pivot_cliente.empty or pivot_cliente.select_dtypes(include='number').shape[1] == 0:
        st.warning("⚠️ Sem dados numéricos para o gráfico de clientes.")
    else:
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        pivot_cliente.plot(kind='bar', stacked=True, ax=ax1, colormap='tab20')
        ax1.set_title('Compras por Cliente')
        ax1.set_xlabel('Mês')
        ax1.set_ylabel('Quantidade Total')
        st.pyplot(fig1)

    st.subheader("📈 Evolução Mensal por Comercial")

    pivot_comercial = dados_filtrados.pivot_table(
        index='mes', columns='comercial', values='qtd', aggfunc='sum'
    ).fillna(0)

    if pivot_comercial.empty or pivot_comercial.select_dtypes(include='number').shape[1] == 0:
        st.warning("⚠️ Sem dados numéricos para o gráfico de comerciais.")
    else:
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        pivot_comercial.plot(kind='line', marker='o', ax=ax2, colormap='Set1')
        ax2.set_title('Evolução Mensal por Comercial')
        ax2.set_xlabel('Mês')
        ax2.set_ylabel('Quantidade Total')
        st.pyplot(fig2)

# --- Página: Alertas ---
elif pagina == "Alertas":
    st.subheader("🚨 Clientes com meses em falta")

    todos_meses = sorted(dados_filtrados['mes'].dropna().unique())
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

        st.dataframe(tabela_alerta.style.applymap(destacar_faltas))

        excel_alerta = gerar_excel(tabela_alerta.reset_index())
        st.download_button("📥 Exportar presença mensal", data=excel_alerta, file_name="presenca_clientes.xlsx")
