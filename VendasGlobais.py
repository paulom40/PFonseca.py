import streamlit as st
import pandas as pd
from io import BytesIO
import requests
from datetime import datetime
import numpy as np

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
        df['Cliente'] = df['Cliente'].astype(str)
        df['Artigo'] = df['Artigo'].astype(str)
        df['Código'] = df['Código'].astype(str)
        df['Categoria'] = df['Categoria'].astype(str) if 'Categoria' in df.columns else ''
        df['Comercial'] = df['Comercial'].astype(str) if 'Comercial' in df.columns else ''
        df['Qtd.'] = pd.to_numeric(df['Qtd.'], errors='coerce')
        df['V. Líquido'] = pd.to_numeric(df['V. Líquido'], errors='coerce') if 'V. Líquido' in df.columns else 0
        df['PM'] = pd.to_numeric(df['PM'], errors='coerce') if 'PM' in df.columns else 0
        df['UN'] = df['UN'].astype(str) if 'UN' in df.columns else ''

        df = df.dropna(subset=['Código', 'Cliente', 'Qtd.', 'Artigo', 'Mês', 'Ano'])

        # Debug: Show processed data
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

# Filtros
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
        st.warning("⚠️ Nenhum mês disponível nos dados.")
        st.stop()

# Filtros adicionais
clientes = st.multiselect("Filtrar por Cliente", sorted(df_ano['Cliente'].unique()))
artigos = st.multiselect("Filtrar por Artigo", sorted(df_ano['Artigo'].unique()))
categorias = st.multiselect("Filtrar por Categoria", sorted(df_ano['Categoria'].unique())) if 'Categoria' in df_ano.columns else []
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

st.subheader("📋 Dados Filtrados")
st.dataframe(df_filtrado[['Código', 'Cliente', 'Artigo', 'Qtd.', 'V. Líquido', 'Categoria', 'Comercial', 'Data']], use_container_width=True)

# Totais
totais_cliente = df_filtrado.groupby('Cliente').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False)
totais_artigo = df_filtrado.groupby('Artigo').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False)
totais_categoria = df_filtrado.groupby('Categoria').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False) if 'Categoria' in df_filtrado.columns else pd.DataFrame()

# Visualizações com Chart.js
st.subheader("📈 Visualizações")

# Chart: Quantidade por Cliente
st.markdown("**Totais por Cliente (Quantidade)**")
if not totais_cliente.empty:
    ```chartjs
    {
        "type": "bar",
        "data": {
            "labels": [row["Cliente"] for row in totais_cliente.head(10).to_dict("records")],
            "datasets": [{
                "label": "Quantidade",
                "data": [row["Qtd."] for row in totais_cliente.head(10).to_dict("records")],
                "backgroundColor": "#4e79a7",
                "borderColor": "#2e4977",
                "borderWidth": 1
            }]
        },
        "options": {
            "indexAxis": "y",
            "scales": {
                "x": {"title": {"display": true, "text": "Quantidade"}}
            },
            "plugins": {"title": {"display": true, "text": "Top 10 Clientes por Quantidade"}}
        }
    }
