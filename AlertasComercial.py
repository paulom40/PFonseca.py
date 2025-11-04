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

# --- Configuração da página ---
st.set_page_config(page_title="Compras por Cliente", layout="wide")
st.title("📦 Dashboard de Compras")

# --- Função para carregar dados ---
@st.cache_data
def carregar_dados():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    df = pd.read_excel(url)
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df['Ano'] = df['Data'].dt.year
    df['Mes'] = df['Data'].dt.month
    return df

df = carregar_dados()
# --- Sidebar: Filtros e navegação ---
st.sidebar.title("📂 Navegação")
pagina = st.sidebar.radio("Ir para:", ["Visão Geral", "Gráficos", "Alertas"])

anos = sorted(df['Ano'].dropna().unique())
comerciais = sorted(df['Comercial'].dropna().unique())

ano = st.sidebar.selectbox("Seleciona o Ano", anos)
comercial = st.sidebar.selectbox("Seleciona o Comercial", comerciais)

# --- Dados filtrados ---
dados_filtrados = df[(df['Ano'] == ano) & (df['Comercial'] == comercial)]
agrupado = dados_filtrados.groupby(['Cliente', 'Ano', 'Mes'])['Quantidade'].sum().reset_index()

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
    col1.metric("👥 Clientes únicos", df['Cliente'].nunique())
    col2.metric("📅 Meses no período", df['Mes'].nunique())
    col3.metric("🧑‍💼 Comerciais", df['Comercial'].nunique())

    st.dataframe(agrupado)

    excel_bytes = gerar_excel(agrupado)
    st.download_button("📥 Exportar para Excel", data=excel_bytes, file_name="compras_clientes.xlsx")

# --- Página: Alertas ---
elif pagina == "Alertas":
    st.subheader("🚨 Clientes que não compraram todos os meses")

    def clientes_inativos(df):
        todos_meses = sorted(df['Mes'].unique())
        meses_por_cliente = df.groupby('Cliente')['Mes'].unique()
        return [cliente for cliente, meses in meses_por_cliente.items() if len(set(meses)) < len(todos_meses)]

    inativos = clientes_inativos(df)
    st.write(inativos)
    st.markdown(f"**Total de clientes inativos:** {len(inativos)}")
# --- Página: Gráficos ---
elif pagina == "Gráficos":
    st.subheader("📉 Quantidade por Cliente ao Longo dos Meses")

    pivot_cliente = df[df['Ano'] == ano].pivot_table(
        index='Mes', columns='Cliente', values='Quantidade', aggfunc='sum'
    ).fillna(0)

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    pivot_cliente.plot(kind='bar', stacked=True, ax=ax1, colormap='tab20')
    ax1.set_title(f'Compras por Cliente - {ano}')
    ax1.set_xlabel('Mês')
    ax1.set_ylabel('Quantidade Total')
    st.pyplot(fig1)

    st.subheader("📈 Evolução Mensal por Comercial")

    pivot_comercial = df[df['Ano'] == ano].pivot_table(
        index='Mes', columns='Comercial', values='Quantidade', aggfunc='sum'
    ).fillna(0)

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    pivot_comercial.plot(kind='line', marker='o', ax=ax2, colormap='Set1')
    ax2.set_title(f'Evolução Mensal por Comercial - {ano}')
    ax2.set_xlabel('Mês')
    ax2.set_ylabel('Quantidade Total')
    st.pyplot(fig2)
