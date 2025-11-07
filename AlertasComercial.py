import streamlit as st
import pandas as pd

st.title("🔄 ABORDAGEM RADICAL - Debug Completo")

@st.cache_data
def load_raw_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
        
        # Tentar carregar sem conversões
        df = pd.read_excel(url)
        
        # DEBUG: Mostrar TUDO sobre a coluna Artigo
        st.header("🔍 DEBUG COMPLETO - Coluna Artigo")
        
        if 'Artigo' in df.columns:
            st.write("**1. Informações básicas:**")
            st.write(f"- Tipo: {df['Artigo'].dtype}")
            st.write(f"- Valores únicos: {df['Artigo'].nunique()}")
            st.write(f"- Nulos: {df['Artigo'].isna().sum()}")
            
            st.write("**2. Primeiros 30 valores CRUS:**")
            for i in range(min(30, len(df))):
                valor = df.iloc[i]['Artigo']
                st.write(f"Linha {i}: '{valor}' (tipo: {type(valor).__name__})")
            
            st.write("**3. Conversão forçada para texto:**")
            df['Artigo_Texto'] = df['Artigo'].astype(str)
            
            st.write("**4. Valores únicos como texto:**")
            artigos_texto = sorted(df['Artigo_Texto'].dropna().unique())
            for i, artigo in enumerate(artigos_texto[:30]):
                st.write(f"{i+1}. '{artigo}'")
            
            return df
        else:
            st.error("Coluna Artigo não existe!")
            st.write("Colunas disponíveis:", list(df.columns))
            return df
            
    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame()

df = load_raw_data()

# Filtro usando a coluna convertida
if not df.empty and 'Artigo_Texto' in df.columns:
    st.header("🎛️ FILTRO - Usando coluna convertida")
    
    artigos_unicos = sorted(df['Artigo_Texto'].dropna().unique())
    
    artigo_selecionado = st.selectbox(
        "Selecione:",
        options=artigos_unicos
    )
    
    if artigo_selecionado:
        resultado = df[df['Artigo_Texto'] == artigo_selecionado]
        st.success(f"✅ Encontrados: {len(resultado)} registos")
        st.dataframe(resultado.head())
