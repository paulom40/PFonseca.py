import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# --- Estilo CSS moderno ---
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

    # Normalizar nomes de colunas
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(".", "", regex=False)
        .str.normalize('NFKD')
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
    )

    # Verificação de colunas obrigatórias
    obrigatorias = ['cliente', 'comercial', 'ano', 'mes', 'qtd']
    faltantes = [col for col in obrigatorias if col not in df.columns]
    if faltantes:
        st.error(f"⚠️ Colunas ausentes no ficheiro: {faltantes}")
        st.stop()

    df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
    df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
    return df

df = carregar_dados()
# --- Sidebar: Filtros e navegação ---
st.sidebar.title("📂 Navegação")
pagina = st.sidebar.radio("Ir para:", ["Visão Geral", "Gráficos", "Alertas"])

anos = sorted(df['ano'].dropna().unique())
comerciais = sorted(df['comercial'].dropna().unique())
clientes = sorted(df['cliente'].dropna().unique())

ano = st.sidebar.selectbox("Seleciona o Ano", anos)
comercial = st.sidebar.selectbox("Seleciona o Comercial", comerciais)
cliente = st.sidebar.selectbox("Seleciona o Cliente", ["Todos"] + clientes)

# --- Dados filtrados ---
dados_filtrados = df[(df['ano'] == ano) & (df['comercial'] == comercial)]
if cliente != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['cliente'] == cliente]

agrupado = dados_filtrados.groupby(['cliente', 'comercial', 'ano', 'mes'])['qtd'].sum().reset_index()

# --- Função para exportar Excel ---
def gerar_excel(dados):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dados.to_excel(writer, index=False, sheet_name='Compras')
    return output.getvalue()
# --- Página: Visão Geral ---
if pagina == "Visão Geral":
    st.subheader("📊 Compras por Cliente")

    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Clientes únicos", df['cliente'].nunique())
    col2.metric("📅 Meses no período", df['mes'].nunique())
    col3.metric("🧑‍💼 Comerciais", df['comercial'].nunique())

    if cliente != "Todos":
        st.markdown(f"**Cliente selecionado:** {cliente}")

    st.dataframe(agrupado)

    excel_bytes = gerar_excel(agrupado)
    st.download_button("📥 Exportar para Excel", data=excel_bytes, file_name="compras_clientes.xlsx")

# --- Página: Alertas ---
elif pagina == "Alertas":
    st.subheader("🚨 Clientes que não compraram todos os meses")

    def clientes_inativos(df):
        todos_meses = sorted(df['mes'].unique())
        meses_por_cliente = df.groupby('cliente')['mes'].unique()
        return [cliente for cliente, meses in meses_por_cliente.items() if len(set(meses)) < len(todos_meses)]

    inativos = clientes_inativos(dados_filtrados)
    st.write(inativos)
    st.markdown(f"**Total de clientes inativos:** {len(inativos)}")
# --- Página: Gráficos ---
elif pagina == "Gráficos":
    st.subheader("📉 Quantidade por Cliente ao Longo dos Meses")

    pivot_cliente = dados_filtrados.pivot_table(
        index='mes', columns='cliente', values='qtd', aggfunc='sum'
    ).fillna(0)

    if pivot_cliente.empty or not pivot_cliente.select_dtypes(include='number').any().any():
        st.warning("⚠️ Não há dados numéricos disponíveis para o gráfico de clientes.")
    else:
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        pivot_cliente.plot(kind='bar', stacked=True, ax=ax1, colormap='tab20')
        ax1.set_title(f'Compras por Cliente - {ano}')
        ax1.set_xlabel('Mês')
        ax1.set_ylabel('Quantidade Total')
        st.pyplot(fig1)

    st.subheader("📈 Evolução Mensal por Comercial")

    pivot_comercial = dados_filtrados.pivot_table(
        index='mes', columns='comercial', values='qtd', aggfunc='sum'
    ).fillna(0)

    if pivot_comercial.empty or not pivot_comercial.select_dtypes(include='number').any().any():
        st.warning("⚠️ Não há dados numéricos disponíveis para o gráfico de comerciais.")
    else:
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        pivot_comercial.plot(kind='line', marker='o', ax=ax2, colormap='Set1')
        ax2.set_title(f'Evolução Mensal por Comercial - {ano}')
        ax2.set_xlabel('Mês')
        ax2.set_ylabel('Quantidade Total')
        st.pyplot(fig2)
