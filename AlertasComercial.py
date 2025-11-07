import streamlit as st
import pandas as pd

st.title("🚀 TESTE SIMPLES - Filtro de Artigos")

# Carregar dados
@st.cache_data
def load_simple_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
        df = pd.read_excel(url)
        return df
    except:
        return pd.DataFrame()

df = load_simple_data()

if not df.empty:
    st.success(f"✅ Dados carregados: {len(df)} registos")
    
    # Verificar se a coluna Artigo existe
    if 'Artigo' in df.columns:
        st.success("✅ Coluna 'Artigo' encontrada!")
        
        # Mostrar informações sobre a coluna Artigo
        st.write("**Informações da coluna Artigo:**")
        st.write(f"- Tipo: {df['Artigo'].dtype}")
        st.write(f"- Valores únicos: {df['Artigo'].nunique()}")
        st.write(f"- Valores nulos: {df['Artigo'].isna().sum()}")
        
        # Mostrar primeiros 10 artigos
        st.write("**Primeiros 10 artigos:**")
        artigos_amostra = df['Artigo'].dropna().head(10).tolist()
        for i, artigo in enumerate(artigos_amostra, 1):
            st.write(f"{i}. {artigo}")
        
        # FILTRO SIMPLES
        st.header("🎛️ Filtro de Artigos")
        
        artigos_unicos = sorted(df['Artigo'].dropna().astype(str).unique())
        st.write(f"📚 Total de artigos únicos: {len(artigos_unicos)}")
        
        artigo_selecionado = st.selectbox(
            "Selecione um artigo:",
            options=artigos_unicos
        )
        
        if artigo_selecionado:
            df_filtrado = df[df['Artigo'] == artigo_selecionado]
            st.success(f"✅ Filtrado: {len(df_filtrado)} registos para '{artigo_selecionado}'")
            st.dataframe(df_filtrado)
        
    else:
        st.error("❌ Coluna 'Artigo' NÃO encontrada!")
        st.write("Colunas disponíveis:", list(df.columns))
else:
    st.error("❌ Não foi possível carregar os dados")
