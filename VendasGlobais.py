import streamlit as st
import pandas as pd
from io import BytesIO
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Custom CSS for professional and modern styling
custom_css = """
<style>
/* General styling */
body {
    font-family: 'Inter', sans-serif;
    background-color: #F3F4F6;
    color: #1E293B;
}

/* Main container */
.stApp {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* Headers */
h1, h2, h3 {
    color: #1E3A8A;
    font-weight: 600;
    margin-bottom: 15px;
}
h1 {
    font-size: 2.5rem;
    border-bottom: 2px solid #F97316;
    padding-bottom: 10px;
}
h2 {
    font-size: 1.8rem;
}
h3 {
    font-size: 1.4rem;
}

/* Cards for sections */
.stMarkdown, .stDataFrame, .stMetric, .stExpander {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-bottom: 20px;
}

/* Metrics */
.stMetric {
    border: 1px solid #E5E7EB;
    transition: transform 0.2s;
}
.stMetric:hover {
    transform: translateY(-2px);
}
.stMetric label {
    font-size: 1rem;
    color: #4B5563;
}
.stMetric .metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1E3A8A;
}

/* Buttons */
button[kind="primary"] {
    background-color: #1E3A8A;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 500;
    transition: background-color 0.2s;
}
button[kind="primary"]:hover {
    background-color: #3B82F6;
}
button[kind="secondary"] {
    background-color: #E5E7EB;
    color: #1E293B;
    border-radius: 8px;
    padding: 10px 20px;
}

/* Dataframe */
.stDataFrame {
    border: 1px solid #E5E7EB;
}
.stDataFrame table {
    width: 100%;
    border-collapse: collapse;
}
.stDataFrame th {
    background-color: #1E3A8A;
    color: white;
    padding: 12px;
}
.stDataFrame td {
    padding: 12px;
    border-bottom: 1px solid #E5E7EB;
}

/* Expander */
.stExpander {
    border: 1px solid #E5E7EB;
}
.stExpander summary {
    background-color: #F9FAFB;
    font-weight: 500;
    color: #1E3A8A;
}

/* Alerts */
.alert-success {
    background-color: #DCFCE7;
    color: #166534;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 10px;
}
.alert-error {
    background-color: #FEE2E2;
    color: #991B1B;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 10px;
}

/* Responsive design */
@media (max-width: 768px) {
    .stApp {
        padding: 10px;
    }
    h1 {
        font-size: 2rem;
    }
    h2 {
        font-size: 1.5rem;
    }
    .stMetric {
        padding: 15px;
    }
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Meses em português
meses_pt = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def obter_numero_mes(nome_mes):
    if not isinstance(nome_mes, str):
        return None
    nome_mes = nome_mes.strip().lower()
    for k, v in meses_pt.items():
        nome_mes_ref = v.lower()
        if nome_mes == nome_mes_ref or nome_mes.startswith(nome_mes_ref[:3]):
            return k
    return None

def validar_colunas(df):
    colunas_esperadas = {
        'Código': ['código', 'codigo'],
        'Cliente': ['cliente', 'cliente nome', 'nome cliente'],
        'Qtd.': ['qtd.', 'quantidade', 'qtd', 'qtde'],
        'UN': ['un', 'unidade'],
        'V. Líquido': ['v. líquido', 'valor líquido', 'valor liquido'],
        'PM': ['pm', 'preço médio', 'preco medio'],
        'Artigo': ['artigo', 'produto', 'item', 'artigo vendido'],
        'Comercial': ['comercial', 'vendedor'],
        'Categoria': ['categoria', 'tipo'],
        'Mês': ['mês', 'mes', 'mês de venda', 'month'],
        'Ano': ['ano', 'year']
    }

    df.columns = df.columns.str.strip().str.lower()
    renomear = {}
    colunas_detectadas = {}

    for padrao, alternativas in colunas_esperadas.items():
        for alt in alternativas:
            if alt.lower() in df.columns:
                renomear[alt.lower()] = padrao
                colunas_detectadas[padrao] = alt
                break

    df = df.rename(columns=renomear)
    faltando = [col for col in ['Código', 'Cliente', 'Qtd.', 'Artigo', 'Mês', 'Ano'] if col not in df.columns]
    return df, colunas_detectadas, faltando

@st.cache_data
def load_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
        response = requests.get(url)
        response.raise_for_status()
        xls = pd.ExcelFile(BytesIO(response.content))
        df_raw = pd.read_excel(xls, sheet_name=0)

        # Debug: Show raw data
        if st.checkbox("Mostrar dados brutos para depuração"):
            st.write("**Colunas no arquivo bruto**:")
            st.write(df_raw.columns.tolist())
            for col in df_raw.columns:
                st.write(f"**{col} (valores únicos)**: {df_raw[col].dropna().unique()[:10]}")

        df, colunas_detectadas, faltando = validar_colunas(df_raw)

        st.markdown("### ✅ Validação de Estrutura do Ficheiro")
        for padrao, original in colunas_detectadas.items():
            st.success(f"✔ Coluna '{padrao}' detectada como '{original}'")

        if faltando:
            for col in faltando:
                st.error(f"❌ Coluna obrigatória ausente: '{col}'")
            st.stop()

        # Convert month names to numbers if necessary
        if df['Mês'].dtype == 'object':
            df['Mês'] = df['Mês'].apply(obter_numero_mes)

        df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
        df = df.dropna(subset=['Mês'])
        df = df[df['Mês'].between(1, 12)]
        df['Mês'] = df['Mês'].astype(int)

        # Ensure Ano is numeric
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
        df = df.dropna(subset=['Ano'])
        df['Ano'] = df['Ano'].astype(int)

        # Ensure other columns are properly typed
        df['Código'] = df['Código'].astype(str)
        df['Cliente'] = df['Cliente'].astype(str)
        df['Artigo'] = df['Artigo'].astype(str)
        df['Categoria'] = df['Categoria'].astype(str) if 'Categoria' in df.columns else ''
        df['Comercial'] = df['Comercial'].astype(str) if 'Comercial' in df.columns else ''
        df['Qtd.'] = pd.to_numeric(df['Qtd.'], errors='coerce')
        df['V. Líquido'] = pd.to_numeric(df['V. Líquido'], errors='coerce') if 'V. Líquido' in df.columns else 0
        df['PM'] = pd.to_numeric(df['PM'], errors='coerce') if 'PM' in df.columns else 0
        df['UN'] = df['UN'].astype(str) if 'UN' in df.columns else ''

        df = df.dropna(subset=['Código', 'Cliente', 'Qtd.', 'Artigo', 'Mês', 'Ano'])

        # Debug: Show processed data
        if st.checkbox("Mostrar dados processados para depuração"):
            st.write("**Colunas após processamento**:")
            for col in df.columns:
                st.write(f"**{col} (valores únicos)**: {df[col].dropna().unique()[:10]}")

        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        st.stop()

df = load_data()

st.title("📊 Dashboard Comercial")

# Painel de valores únicos
with st.expander("📋 Ver valores únicos por coluna"):
    for col in ['Mês', 'Ano', 'Cliente', 'Artigo', 'Categoria', 'Comercial']:
        if col in df.columns and df[col].notna().any():
            try:
                valores = sorted([str(val) for val in df[col].dropna().unique() if pd.notna(val)])
                if col == 'Mês':
                    nomes = [meses_pt.get(int(float(val)), str(val)) for val in valores]
                    st.write(f"**{col}**: {', '.join(nomes[:20])} {'...' if len(nomes) > 20 else ''}")
                else:
                    st.write(f"**{col}**: {', '.join(valores[:20])} {'...' if len(valores) > 20 else ''}")
            except Exception as e:
                st.warning(f"⚠️ Não foi possível exibir valores únicos para '{col}': {str(e)}")

# Função para calcular alertas
def calcular_alertas(df, mes_num, ano, threshold_aumento=50, threshold_reducao=-50):
    mes_anterior = mes_num - 1 if mes_num > 1 else 12
    ano_anterior = ano if mes_num > 1 else ano - 1

    df_atual = df[(df['Mês'] == mes_num) & (df['Ano'] == ano)]
    df_anterior = df[(df['Mês'] == mes_anterior) & (df['Ano'] == ano_anterior)]

    # Alertas para Cliente
    totais_cliente_atual = df_atual.groupby('Cliente')['Qtd.'].sum().reset_index()
    totais_cliente_anterior = df_anterior.groupby('Cliente')['Qtd.'].sum().reset_index()
    merged_clientes = totais_cliente_atual.merge(totais_cliente_anterior, on='Cliente', how='outer', suffixes=('_Atual', '_Anterior'))
    merged_clientes.fillna({'Qtd._Atual': 0, 'Qtd._Anterior': 0}, inplace=True)
    merged_clientes['Variação (%)'] = ((merged_clientes['Qtd._Atual'] - merged_clientes['Qtd._Anterior']) / merged_clientes['Qtd._Anterior'].replace(0, np.nan) * 100).round(2)
    alertas_clientes = merged_clientes[
        (merged_clientes['Variação (%)'].notna()) & 
        ((merged_clientes['Variação (%)'] > threshold_aumento) | (merged_clientes['Variação (%)'] < threshold_reducao))
    ][['Cliente', 'Qtd._Atual', 'Qtd._Anterior', 'Variação (%)']]

    # Alertas para Artigo
    totais_artigo_atual = df_atual.groupby('Artigo')['Qtd.'].sum().reset_index()
    totais_artigo_anterior = df_anterior.groupby('Artigo')['Qtd.'].sum().reset_index()
    merged_artigos = totais_artigo_atual.merge(totais_artigo_anterior, on='Artigo', how='outer', suffixes=('_Atual', '_Anterior'))
    merged_artigos.fillna({'Qtd._Atual': 0, 'Qtd._Anterior': 0}, inplace=True)
    merged_artigos['Variação (%)'] = ((merged_artigos['Qtd._Atual'] - merged_artigos['Qtd._Anterior']) / merged_artigos['Qtd._Anterior'].replace(0, np.nan) * 100).round(2)
    alertas_artigos = merged_artigos[
        (merged_artigos['Variação (%)'].notna()) & 
        ((merged_artigos['Variação (%)'] > threshold_aumento) | (merged_artigos['Variação (%)'] < threshold_reducao))
    ][['Artigo', 'Qtd._Atual', 'Qtd._Anterior', 'Variação (%)']]

    return alertas_clientes, alertas_artigos

# Configurar estilo dos gráficos
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'Inter',
    'text.color': '#1E293B',
    'axes.labelcolor': '#1E293B',
    'xtick.color': '#1E293B',
    'ytick.color': '#1E293B',
    'axes.edgecolor': '#1E293B',
    'axes.titleweight': 'bold',
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10
})

# Opção de comparação 2024 vs 2025
st.subheader("Comparação de Dados")
compare_years = st.checkbox("Comparar mesmo mês entre 2024 e 2025")

if compare_years:
    meses_disponiveis = sorted(df[df['Ano'].isin([2024, 2025])]['Mês'].unique())
    nomes_meses = [meses_pt.get(m, f"Mês {m}") for m in meses_disponiveis]
    if nomes_meses:
        mes_label = st.selectbox("Selecionar Mês para Comparação", nomes_meses)
        mes_num = obter_numero_mes(mes_label)
        if mes_num is None:
            st.error(f"❌ Mês '{mes_label}' não reconhecido.")
            st.stop()
    else:
        st.warning("⚠️ Nenhum mês disponível para os anos 2024 e 2025.")
        st.stop()

    # Dados para 2024 e 2025
    df_2024 = df[(df['Mês'] == mes_num) & (df['Ano'] == 2024)]
    df_2025 = df[(df['Mês'] == mes_num) & (df['Ano'] == 2025)]

    # Filtros adicionais
    st.subheader("Filtros Adicionais")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        clientes = st.multiselect("Filtrar por Cliente", sorted(df[df['Mês'] == mes_num]['Cliente'].unique()))
    with col2:
        artigos = st.multiselect("Filtrar por Artigo", sorted(df[df['Mês'] == mes_num]['Artigo'].unique()))
    with col3:
        categorias = st.multiselect("Filtrar por Categoria", sorted(df[df['Mês'] == mes_num]['Categoria'].unique())) if 'Categoria' in df.columns else []
    with col4:
        comerciais = st.multiselect("Filtrar por Comercial", sorted(df[df['Mês'] == mes_num]['Comercial'].unique())) if 'Comercial' in df.columns else []

    # Aplicar filtros
    if clientes:
        df_2024 = df_2024[df_2024['Cliente'].isin(clientes)]
        df_2025 = df_2025[df_2025['Cliente'].isin(clientes)]
    if artigos:
        df_2024 = df_2024[df_2024['Artigo'].isin(artigos)]
        df_2025 = df_2025[df_2025['Artigo'].isin(artigos)]
    if categorias:
        df_2024 = df_2024[df_2024['Categoria'].isin(categorias)]
        df_2025 = df_2025[df_2025['Categoria'].isin(categorias)]
    if comerciais:
        df_2024 = df_2024[df_2024['Comercial'].isin(comerciais)]
        df_2025 = df_2025[df_2025['Comercial'].isin(comerciais)]

    # KPIs para Clientes
    totais_cliente_2024 = df_2024.groupby('Cliente').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False)
    totais_cliente_2025 = df_2025.groupby('Cliente').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False)
    totais_categoria_2024 = df_2024.groupby('Categoria').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False) if 'Categoria' in df_2024.columns else pd.DataFrame()
    totais_categoria_2025 = df_2025.groupby('Categoria').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False) if 'Categoria' in df_2025.columns else pd.DataFrame()

    # Calcular KPIs
    kpi_2024 = {
        'Total Qtd.': totais_cliente_2024['Qtd.'].sum(),
        'Top Cliente': totais_cliente_2024.iloc[0]['Cliente'] if not totais_cliente_2024.empty else 'N/A',
        'Top Qtd.': totais_cliente_2024.iloc[0]['Qtd.'] if not totais_cliente_2024.empty else 0,
        'Atividade (%)': (len(totais_cliente_2024[totais_cliente_2024['Qtd.'] > 0]) / len(totais_cliente_2024) * 100) if not totais_cliente_2024.empty else 0,
        'Média Qtd.': totais_cliente_2024['Qtd.'].mean() if not totais_cliente_2024.empty else 0
    }
    kpi_2025 = {
        'Total Qtd.': totais_cliente_2025['Qtd.'].sum(),
        'Top Cliente': totais_cliente_2025.iloc[0]['Cliente'] if not totais_cliente_2025.empty else 'N/A',
        'Top Qtd.': totais_cliente_2025.iloc[0]['Qtd.'] if not totais_cliente_2025.empty else 0,
        'Atividade (%)': (len(totais_cliente_2025[totais_cliente_2025['Qtd.'] > 0]) / len(totais_cliente_2025) * 100) if not totais_cliente_2025.empty else 0,
        'Média Qtd.': totais_cliente_2025['Qtd.'].mean() if not totais_cliente_2025.empty else 0
    }
    merged_clientes = totais_cliente_2024.merge(totais_cliente_2025, on='Cliente', how='outer', suffixes=('_2024', '_2025'))
    merged_clientes.fillna({'Qtd._2024': 0, 'Qtd._2025': 0}, inplace=True)
    merged_clientes['Crescimento Qtd. (%)'] = ((merged_clientes['Qtd._2025'] - merged_clientes['Qtd._2024']) / merged_clientes['Qtd._2024'].replace(0, np.nan) * 100).round(2)
    kpi_df = merged_clientes[['Cliente', 'Qtd._2024', 'Qtd._2025', 'Crescimento Qtd. (%)']].fillna({'Qtd._2024': 0, 'Qtd._2025': 0})

    # Calcular alertas para 2025
    alertas_clientes, alertas_artigos = calcular_alertas(df, mes_num, 2025)

    st.subheader(f"🚨 Alertas de Quantidade: {mes_label} 2025 vs Mês Anterior")
    if not alertas_clientes.empty:
        st.markdown("**Clientes com variações significativas**")
        for _, row in alertas_clientes.iterrows():
            if row['Variação (%)'] > 50:
                st.markdown(f"<div class='alert-success'>✔ {row['Cliente']}: Aumento de {row['Variação (%)']:.1f}% (Atual: {row['Qtd._Atual']:.0f}, Anterior: {row['Qtd._Anterior']:.0f})</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='alert-error'>❌ {row['Cliente']}: Redução de {row['Variação (%)']:.1f}% (Atual: {row['Qtd._Atual']:.0f}, Anterior: {row['Qtd._Anterior']:.0f})</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum alerta para clientes.")
    if not alertas_artigos.empty:
        st.markdown("**Artigos com variações significativas**")
        for _, row in alertas_artigos.iterrows():
            if row['Variação (%)'] > 50:
                st.markdown(f"<div class='alert-success'>✔ {row['Artigo']}: Aumento de {row['Variação (%)']:.1f}% (Atual: {row['Qtd._Atual']:.0f}, Anterior: {row['Qtd._Anterior']:.0f})</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='alert-error'>❌ {row['Artigo']}: Redução de {row['Variação (%)']:.1f}% (Atual: {row['Qtd._Atual']:.0f}, Anterior: {row['Qtd._Anterior']:.0f})</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum alerta para artigos.")
    with st.expander("Detalhes dos Alertas"):
        if not alertas_clientes.empty:
            st.markdown("**Alertas por Cliente**")
            st.dataframe(alertas_clientes, use_container_width=True)
        if not alertas_artigos.empty:
            st.markdown("**Alertas por Artigo**")
            st.dataframe(alertas_artigos, use_container_width=True)

    st.subheader(f"📊 KPIs por Cliente: {mes_label} 2024 vs 2025")
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.metric("Total Qtd. 2024", f"{kpi_2024['Total Qtd.']:.0f}")
        st.metric("Total Qtd. 2025", f"{kpi_2025['Total Qtd.']:.0f}")
    with col_kpi2:
        st.metric("Top Cliente 2024", f"{kpi_2024['Top Cliente']} ({kpi_2024['Top Qtd.']:.0f})")
        st.metric("Top Cliente 2025", f"{kpi_2025['Top Cliente']} ({kpi_2025['Top Qtd.']:.0f})")
    with col_kpi3:
        st.metric("Atividade 2024 (%)", f"{kpi_2024['Atividade (%)']:.1f}%")
        st.metric("Atividade 2025 (%)", f"{kpi_2025['Atividade (%)']:.1f}%")
    with st.expander("Detalhes dos KPIs"):
        st.dataframe(kpi_df, use_container_width=True)

    # Exibir dados filtrados
    st.subheader(f"📋 Dados Filtrados: {mes_label} 2024")
    st.dataframe(df_2024[['Código', 'Cliente', 'Artigo', 'Qtd.', 'V. Líquido', 'PM', 'UN', 'Categoria', 'Comercial', 'Mês', 'Ano']], use_container_width=True)
    st.subheader(f"📋 Dados Filtrados: {mes_label} 2025")
    st.dataframe(df_2025[['Código', 'Cliente', 'Artigo', 'Qtd.', 'V. Líquido', 'PM', 'UN', 'Categoria', 'Comercial', 'Mês', 'Ano']], use_container_width=True)

    # Visualizações comparativas
    st.subheader("📈 Comparação 2024 vs 2025")
    col5, col6 = st.columns(2)

    with col5:
        if not totais_cliente_2024.empty or not totais_cliente_2025.empty:
            st.markdown(f"**Quantidade por Cliente: {mes_label}**")
            fig1, ax1 = plt.subplots(figsize=(8, 4))
            width = 0.35
            clientes = pd.concat([totais_cliente_2024['Cliente'], totais_cliente_2025['Cliente']]).unique()[:10]
            x = np.arange(len(clientes))
            qtd_2024 = [totais_cliente_2024[totais_cliente_2024['Cliente'] == c]['Qtd.'].sum() for c in clientes]
            qtd_2025 = [totais_cliente_2025[totais_cliente_2025['Cliente'] == c]['Qtd.'].sum() for c in clientes]
            ax1.bar(x - width/2, qtd_2024, width, label='2024', color='#1E3A8A')
            ax1.bar(x + width/2, qtd_2025, width, label='2025', color='#F97316')
            ax1.set_ylabel('Quantidade')
            ax1.set_title(f'Top Clientes por Quantidade - {mes_label}')
            ax1.set_xticks(x)
            ax1.set_xticklabels(clientes, rotation=45, ha='right')
            ax1.legend()
            plt.tight_layout()
            st.pyplot(fig1)

    with col6:
        if not totais_categoria_2024.empty or not totais_categoria_2025.empty:
            st.markdown(f"**Valor Líquido por Categoria: {mes_label}**")
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            categorias = pd.concat([totais_categoria_2024['Categoria'], totais_categoria_2025['Categoria']]).unique()[:8]
            x = np.arange(len(categorias))
            valor_2024 = [totais_categoria_2024[totais_categoria_2024['Categoria'] == c]['V. Líquido'].sum() for c in categorias]
            valor_2025 = [totais_categoria_2025[totais_categoria_2025['Categoria'] == c]['V. Líquido'].sum() for c in categorias]
            ax2.bar(x - width/2, valor_2024, width, label='2024', color='#1E3A8A')
            ax2.bar(x + width/2, valor_2025, width, label='2025', color='#F97316')
            ax2.set_ylabel('Valor Líquido')
            ax2.set_title(f'Top Categorias por Valor Líquido - {mes_label}')
            ax2.set_xticks(x)
            ax2.set_xticklabels(categorias, rotation=45, ha='right')
            ax2.legend()
            plt.tight_layout()
            st.pyplot(fig2)

else:
    # Modo normal (sem comparação)
    col1, col2 = st.columns(2)
    with col1:
        anos_disponiveis = sorted(df['Ano'].unique())
        ano_selecionado = st.selectbox("Selecionar Ano", anos_disponiveis) if len(anos_disponiveis) > 1 else anos_disponiveis[0]

    with col2:
        df_ano = df[df['Ano'] == ano_selecionado]
        meses_disponiveis = sorted(df_ano['Mês'].unique())
        nomes_meses = [meses_pt.get(m, f"Mês {m}") for m in meses_disponiveis]
        if nomes_meses:
            mes_label = st.selectbox("Selecionar Mês", nomes_meses)
            mes_num = obter_numero_mes(mes_label)
            if mes_num is None:
                st.error(f"❌ Mês '{mes_label}' não reconhecido.")
                st.stop()
        else:
            st.warning("⚠️ Nenhum mês disponível nos dados para o ano selecionado.")
            st.stop()

    # Filtros adicionais
    st.subheader("Filtros Adicionais")
    col3, col4, col5, col6 = st.columns(4)
    with col3:
        clientes = st.multiselect("Filtrar por Cliente", sorted(df_ano['Cliente'].unique()))
    with col4:
        artigos = st.multiselect("Filtrar por Artigo", sorted(df_ano['Artigo'].unique()))
    with col5:
        categorias = st.multiselect("Filtrar por Categoria", sorted(df_ano['Categoria'].unique())) if 'Categoria' in df_ano.columns else []
    with col6:
        comerciais = st.multiselect("Filtrar por Comercial", sorted(df_ano['Comercial'].unique())) if 'Comercial' in df_ano.columns else []

    # Aplicar filtros
    df_filtrado = df_ano[df_ano['Mês'] == mes_num]
    if clientes:
        df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes)]
    if artigos:
        df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(artigos)]
    if categorias:
        df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias)]
    if comerciais:
        df_filtrado = df_filtrado[df_filtrado['Comercial'].isin(comerciais)]

    # Calcular alertas
    alertas_clientes, alertas_artigos = calcular_alertas(df, mes_num, ano_selecionado)

    st.subheader(f"🚨 Alertas de Quantidade: {mes_label} {ano_selecionado} vs Mês Anterior")
    if not alertas_clientes.empty:
        st.markdown("**Clientes com variações significativas**")
        for _, row in alertas_clientes.iterrows():
            if row['Variação (%)'] > 50:
                st.markdown(f"<div class='alert-success'>✔ {row['Cliente']}: Aumento de {row['Variação (%)']:.1f}% (Atual: {row['Qtd._Atual']:.0f}, Anterior: {row['Qtd._Anterior']:.0f})</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='alert-error'>❌ {row['Cliente']}: Redução de {row['Variação (%)']:.1f}% (Atual: {row['Qtd._Atual']:.0f}, Anterior: {row['Qtd._Anterior']:.0f})</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum alerta para clientes.")
    if not alertas_artigos.empty:
        st.markdown("**Artigos com variações significativas**")
        for _, row in alertas_artigos.iterrows():
            if row['Variação (%)'] > 50:
                st.markdown(f"<div class='alert-success'>✔ {row['Artigo']}: Aumento de {row['Variação (%)']:.1f}% (Atual: {row['Qtd._Atual']:.0f}, Anterior: {row['Qtd._Anterior']:.0f})</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='alert-error'>❌ {row['Artigo']}: Redução de {row['Variação (%)']:.1f}% (Atual: {row['Qtd._Atual']:.0f}, Anterior: {row['Qtd._Anterior']:.0f})</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum alerta para artigos.")
    with st.expander("Detalhes dos Alertas"):
        if not alertas_clientes.empty:
            st.markdown("**Alertas por Cliente**")
            st.dataframe(alertas_clientes, use_container_width=True)
        if not alertas_artigos.empty:
            st.markdown("**Alertas por Artigo**")
            st.dataframe(alertas_artigos, use_container_width=True)

    # KPIs para Clientes
    totais_cliente = df_filtrado.groupby('Cliente').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False)
    kpi_normal = {
        'Total Qtd.': totais_cliente['Qtd.'].sum(),
        'Top Cliente': totais_cliente.iloc[0]['Cliente'] if not totais_cliente.empty else 'N/A',
        'Top Qtd.': totais_cliente.iloc[0]['Qtd.'] if not totais_cliente.empty else 0,
        'Atividade (%)': (len(totais_cliente[totais_cliente['Qtd.'] > 0]) / len(totais_cliente) * 100) if not totais_cliente.empty else 0,
        'Média Qtd.': totais_cliente['Qtd.'].mean() if not totais_cliente.empty else 0
    }
    kpi_df = totais_cliente[['Cliente', 'Qtd.']].rename(columns={'Qtd.': 'Quantidade Total'})

    st.subheader(f"📊 KPIs por Cliente: {mes_label} {ano_selecionado}")
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.metric("Total Quantidade", f"{kpi_normal['Total Qtd.']:.0f}")
    with col_kpi2:
        st.metric("Top Cliente", f"{kpi_normal['Top Cliente']} ({kpi_normal['Top Qtd.']:.0f})")
    with col_kpi3:
        st.metric("Atividade (%)", f"{kpi_normal['Atividade (%)']:.1f}%")
        st.metric("Média Qtd. por Cliente", f"{kpi_normal['Média Qtd.']:.1f}")
    with st.expander("Detalhes dos KPIs"):
        st.dataframe(kpi_df, use_container_width=True)

    st.subheader("📋 Dados Filtrados")
    st.dataframe(df_filtrado[['Código', 'Cliente', 'Artigo', 'Qtd.', 'V. Líquido', 'PM', 'UN', 'Categoria', 'Comercial', 'Mês', 'Ano']], use_container_width=True)

    # Totais
    totais_artigo = df_filtrado.groupby('Artigo').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False)
    totais_categoria = df_filtrado.groupby('Categoria').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False) if 'Categoria' in df_filtrado.columns else pd.DataFrame()
    totais_comercial = df_filtrado.groupby('Comercial').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False) if 'Comercial' in df_filtrado.columns else pd.DataFrame()

    # Visualizações
    st.subheader("📈 Visualizações")
    col7, col8 = st.columns(2)

    with col7:
        if not totais_cliente.empty:
            st.markdown(f"**Totais por Cliente (Quantidade) - {mes_label} {ano_selecionado}**")
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            top_clientes = totais_cliente.head(10)
            ax1.barh(top_clientes['Cliente'], top_clientes['Qtd.'], color='#1E3A8A')
            ax1.set_xlabel('Quantidade')
            ax1.set_title(f'Top 10 Clientes por Quantidade')
            plt.tight_layout()
            st.pyplot(fig1)

    with col8:
        if not totais_categoria.empty:
            st.markdown(f"**Totais por Categoria (Valor Líquido) - {mes_label} {ano_selecionado}**")
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            top_categorias = totais_categoria.head(8)
            ax2.pie(top_categorias['V. Líquido'], labels=top_categorias['Categoria'], autopct='%1.1f%%', colors=['#1E3A8A', '#F97316', '#EF4444', '#10B981', '#3B82F6', '#F59E0B', '#8B5CF6', '#EC4899'])
            ax2.set_title(f'Top 8 Categorias por Valor Líquido')
            plt.tight_layout()
            st.pyplot(fig2)

def exportar_excel_completo(dados_df, cliente_df, artigo_df, categoria_df, comercial_df, kpi_df, alertas_clientes, alertas_artigos, nome_mes, mes_num, ano, compare_years=False, df_2024=None, df_2025=None, totais_cliente_2024=None, totais_cliente_2025=None, totais_categoria_2024=None, totais_categoria_2025=None):
    output = BytesIO()
    try:
        logo_url = "https://github.com/paulom40/PFonseca.py/raw/main/Bracar.png"
        logo_data = requests.get(logo_url).content
    except:
        logo_data = None
        st.warning("⚠️ Não foi possível carregar o logotipo para o relatório.")

    # Variações por Cliente e Artigo
    variacoes = dados_df.groupby(['Cliente', 'Artigo', 'Mês'])['Qtd.'].sum().reset_index()
    variacoes_pivot = variacoes.pivot_table(index=['Cliente', 'Artigo'], columns='Mês', values='Qtd.', fill_value=0).reset_index()

    # Variações por Comercial
    variacoes_comercial = dados_df.groupby(['Comercial', 'Cliente', 'Mês'])['Qtd.'].sum().reset_index() if 'Comercial' in dados_df.columns else pd.DataFrame()
    variacoes_comercial_pivot = variacoes_comercial.pivot_table(index=['Comercial', 'Cliente'], columns='Mês', values='Qtd.', fill_value=0).reset_index() if not variacoes_comercial.empty else pd.DataFrame({'Aviso': ['Coluna "Comercial" não encontrada.']})

    # Alertas de clientes inativos
    mes_anterior = mes_num - 1 if mes_num > 1 else 12
    ano_anterior = ano if mes_num > 1 else ano - 1
    todos_clientes = sorted(df['Cliente'].unique())
    clientes_ativos = sorted(df[(df['Mês'] == mes_anterior) & (df['Ano'] == ano_anterior)]['Cliente'].unique())
    clientes_inativos = [c for c in todos_clientes if c not in clientes_ativos]
    alertas_inativos_df = pd.DataFrame({'Cliente sem compras': clientes_inativos}) if clientes_inativos else pd.DataFrame({'Todos os clientes compraram': ['✔']})

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        bold = workbook.add_format({'bold': True})
        italic = workbook.add_format({'italic': True})

        # Dados Filtrados
        dados_df.to_excel(writer, index=False, sheet_name='Dados_Filtrados')
        ws1 = writer.sheets['Dados_Filtrados']
        ws1.set_column('A:Z', 20)
        if logo_data:
            ws1.insert_image('A1', '', {'image_data': BytesIO(logo_data), 'x_scale': 0.5, 'y_scale': 0.5})
        ws1.write('C1', f'Relatório Comercial – {nome_mes} {ano}', bold)
        ws1.write('C2', f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', italic)

        # Totais Cliente
        cliente_df.to_excel(writer, index=False, sheet_name='Totais_Cliente')
        ws2 = writer.sheets['Totais_Cliente']
        ws2.set_column('A:Z', 20)
        ws2.write('A1', f'Totais por Cliente – {nome_mes} {ano}', bold)
        ws2.write('A2', f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', italic)

        # Totais Artigo
        artigo_df.to_excel(writer, index=False, sheet_name='Totais_Artigo')
        ws3 = writer.sheets['Totais_Artigo']
        ws3.set_column('A:Z', 20)
        ws3.write('A1', f'Totais por Artigo – {nome_mes} {ano}', bold)
        ws3.write('A2', f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', italic)

        # Totais Categoria
        if not categoria_df.empty:
            categoria_df.to_excel(writer, index=False, sheet_name='Totais_Categoria')
            ws4 = writer.sheets['Totais_Categoria']
            ws4.set_column('A:Z', 20)
            ws4.write('A1', f'Totais por Categoria – {nome_mes} {ano}', bold)
            ws4.write('A2', f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', italic)

        # Totais Comercial
        if not comercial_df.empty:
            comercial_df.to_excel(writer, index=False, sheet_name='Totais_Comercial')
            ws5 = writer.sheets['Totais_Comercial']
            ws5.set_column('A:Z', 20)
            ws5.write('A1', f'Totais por Comercial – {nome_mes} {ano}', bold)
            ws5.write('A2', f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', italic)

        # KPIs Cliente
        kpi_df.to_excel(writer, index=False, sheet_name='KPIs_Cliente')
        ws6 = writer.sheets['KPIs_Cliente']
        ws6.set_column('A:Z', 20)
        ws6.write('A1', f'KPIs por Cliente – {nome_mes} {ano}', bold)
        ws6.write('A2', f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', italic)

        # Alertas Qtd.
        if not alertas_clientes.empty:
            alertas_clientes.to_excel(writer, index=False, sheet_name='Alertas_Qtd_Cliente')
            ws7 = writer.sheets['Alertas_Qtd_Cliente']
            ws7.set_column('A:Z', 20)
            ws7.write('A1', f'Alertas de Quantidade por Cliente – {nome_mes} {ano}', bold)
        if not alertas_artigos.empty:
            alertas_artigos.to_excel(writer, index=False, sheet_name='Alertas_Qtd_Artigo')
            ws8 = writer.sheets['Alertas_Qtd_Artigo']
            ws8.set_column('A:Z', 20)
            ws8.write('A1', f'Alertas de Quantidade por Artigo – {nome_mes} {ano}', bold)

        # Variações Cliente e Artigo
        variacoes_pivot.to_excel(writer, index=False, sheet_name='Variacoes_Cliente_Artigo')
        ws9 = writer.sheets['Variacoes_Cliente_Artigo']
        ws9.set_column('A:Z', 20)
        ws9.write('A1', f'Variações por Cliente e Artigo', bold)

        # Variações Comercial
        variacoes_comercial_pivot.to_excel(writer, index=False, sheet_name='Variacoes_Comercial')
        ws10 = writer.sheets['Variacoes_Comercial']
        ws10.set_column('A:Z', 20)
        ws10.write('A1', f'Variações por Comercial', bold)

        # Alertas de Clientes Inativos
        alertas_inativos_df.to_excel(writer, index=False, sheet_name='Alertas_Clientes_Inativos')
        ws11 = writer.sheets['Alertas_Clientes_Inativos']
        ws11.set_column('A:Z', 20)
        ws11.write('A1', f'Alertas de Clientes Inativos no Mês Anterior', bold)

        # Comparação 2024 vs 2025
        if compare_years:
            if not totais_cliente_2024.empty:
                totais_cliente_2024.to_excel(writer, index=False, sheet_name='Comparacao_Cliente_2024')
                ws12 = writer.sheets['Comparacao_Cliente_2024']
                ws12.set_column('A:Z', 20)
                ws12.write('A1', f'Comparação Clientes – {nome_mes} 2024', bold)
            if not totais_cliente_2025.empty:
                totais_cliente_2025.to_excel(writer, index=False, sheet_name='Comparacao_Cliente_2025')
                ws13 = writer.sheets['Comparacao_Cliente_2025']
                ws13.set_column('A:Z', 20)
                ws13.write('A1', f'Comparação Clientes – {nome_mes} 2025', bold)
            if not totais_categoria_2024.empty:
                totais_categoria_2024.to_excel(writer, index=False, sheet_name='Comparacao_Categoria_2024')
                ws14 = writer.sheets['Comparacao_Categoria_2024']
                ws14.set_column('A:Z', 20)
                ws14.write('A1', f'Comparação Categorias – {nome_mes} 2024', bold)
            if not totais_categoria_2025.empty:
                totais_categoria_2025.to_excel(writer, index=False, sheet_name='Comparacao_Categoria_2025')
                ws15 = writer.sheets['Comparacao_Categoria_2025']
                ws15.set_column('A:Z', 20)
                ws15.write('A1', f'Comparação Categorias – {nome_mes} 2025', bold)

    output.seek(0)
    return output

# Botão de exportação
if st.button("📥 Exportar Relatório para Excel"):
    if compare_years:
        excel_data = exportar_excel_completo(
            df_2025, totais_cliente_2025, totais_artigo, totais_categoria_2025, totais_comercial,
            kpi_df, alertas_clientes, alertas_artigos, mes_label, mes_num, 2025, compare_years=True,
            df_2024=df_2024, df_2025=df_2025,
            totais_cliente_2024=totais_cliente_2024, totais_cliente_2025=totais_cliente_2025,
            totais_categoria_2024=totais_categoria_2024, totais_categoria_2025=totais_categoria_2025
        )
        file_name = f"Relatorio_Comercial_{mes_label}_2024_2025.xlsx"
    else:
        excel_data = exportar_excel_completo(
            df_filtrado, totais_cliente, totais_artigo, totais_categoria, totais_comercial,
            kpi_df, alertas_clientes, alertas_artigos, mes_label, mes_num, ano_selecionado
        )
        file_name = f"Relatorio_Comercial_{mes_label}_{ano_selecionado}.xlsx"
    
    st.download_button(
        label="Baixar Relatório",
        data=excel_data,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
