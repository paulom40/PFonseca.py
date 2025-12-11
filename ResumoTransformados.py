import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Análise", layout="wide")
st.title("📊 Dashboard de Análise de Compras")

# URL do ficheiro
RAW_URL = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/ResumoTR.xlsx"

# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_excel(RAW_URL)
    return df

with st.spinner("A carregar dados..."):
    df_raw = load_data()

# === PASSO 1: VISUALIZAR ESTRUTURA DOS DADOS ===
st.header("🔍 Passo 1: Estrutura dos Dados")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total de linhas", f"{len(df_raw):,}")
with col2:
    st.metric("Total de colunas", len(df_raw.columns))

st.subheader("Primeiras 10 linhas do ficheiro:")
st.dataframe(df_raw.head(10), use_container_width=True)

st.subheader("Informação das colunas:")
col_info = pd.DataFrame({
    'Índice': range(len(df_raw.columns)),
    'Nome da Coluna': df_raw.columns,
    'Tipo': df_raw.dtypes.values,
    'Valores Únicos': [df_raw[col].nunique() for col in df_raw.columns],
    'Nulos': [df_raw[col].isnull().sum() for col in df_raw.columns]
})
st.dataframe(col_info, use_container_width=True)

# === PASSO 2: IDENTIFICAR AS COLUNAS ===
st.header("📋 Passo 2: Identificar as Colunas Importantes")

st.markdown("""
**Por favor, confirme quais são as colunas:**

Baseado nos códigos anteriores, parece ser:
- **Coluna A (índice 0)**: Data
- **Coluna B (índice 1)**: Nome do Cliente
- **Coluna C (índice 2)**: Artigo/Produto
- **Coluna D (índice 3)**: Quantidade
- **Coluna I (índice 8)**: Comercial

**Está correto? Quer mostrar algumas amostras de cada coluna?**
""")

# Mostrar amostras das colunas principais
if st.checkbox("Mostrar amostras das colunas identificadas"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Coluna 0 - Data:**")
        st.write(df_raw.iloc[:, 0].head(10))
    
    with col2:
        st.markdown("**Coluna 1 - Cliente:**")
        st.write(df_raw.iloc[:, 1].head(10))
    
    with col3:
        st.markdown("**Coluna 2 - Artigo:**")
        st.write(df_raw.iloc[:, 2].head(10))
    
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown("**Coluna 3 - Quantidade:**")
        st.write(df_raw.iloc[:, 3].head(10))
    
    with col5:
        st.markdown("**Coluna 8 - Comercial:**")
        st.write(df_raw.iloc[:, 8].head(10))

# === PASSO 3: VALIDAR MAPEAMENTO ===
st.header("✅ Passo 3: Validar Mapeamento")

st.markdown("""
**Se o mapeamento estiver correto, vou criar o dashboard com:**

1. ✅ Filtros interativos (Comercial, Cliente, Artigo, Período)
2. ✅ Comparação Year-over-Year
3. ✅ KPIs principais (Total por cliente, distribuição de artigos, evolução mensal)
4. ✅ Gráficos e tabelas
5. ✅ Exportação para Excel

**As colunas estão corretas ou precisa ajustar alguma?**
""")

# Opção para ajustar índices
if st.checkbox("Preciso ajustar os índices das colunas"):
    st.markdown("### Configurar Índices das Colunas")
    
    col1, col2 = st.columns(2)
    with col1:
        idx_data = st.number_input("Índice da coluna Data", min_value=0, max_value=len(df_raw.columns)-1, value=0)
        idx_cliente = st.number_input("Índice da coluna Cliente", min_value=0, max_value=len(df_raw.columns)-1, value=1)
        idx_artigo = st.number_input("Índice da coluna Artigo", min_value=0, max_value=len(df_raw.columns)-1, value=2)
    
    with col2:
        idx_quantidade = st.number_input("Índice da coluna Quantidade", min_value=0, max_value=len(df_raw.columns)-1, value=3)
        idx_comercial = st.number_input("Índice da coluna Comercial", min_value=0, max_value=len(df_raw.columns)-1, value=8)
    
    if st.button("Confirmar e Criar Dashboard"):
        st.success(f"""
        ✅ Configuração guardada:
        - Data: Coluna {idx_data}
        - Cliente: Coluna {idx_cliente}
        - Artigo: Coluna {idx_artigo}
        - Quantidade: Coluna {idx_quantidade}
        - Comercial: Coluna {idx_comercial}
        
        **Pronto para criar o dashboard completo!**
        """)

st.divider()

st.info("""
💡 **Próximos Passos:**
1. Confirme se as colunas estão corretas acima
2. Diga-me quais KPIs são mais importantes para si
3. Vou criar o dashboard final completo e funcional
""")
