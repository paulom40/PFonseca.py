import streamlit as st
import pandas as pd

st.title("🎯 FILTRO DE ARTIGOS - SOLUÇÃO DEFINITIVA")

@st.cache_data
def load_and_clean_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
        df = pd.read_excel(url)
        
        if 'Artigo' in df.columns:
            # Converter para string
            df['Artigo'] = df['Artigo'].astype(str)
            
            # FILTRAR APENAS ARTIGOS "REAIS" (não valores numéricos)
            # Criar uma coluna auxiliar para identificar artigos reais
            def is_real_article(artigo):
                artigo_str = str(artigo).strip()
                # Se começa com '-' e depois tem apenas números, é um ajuste numérico
                if artigo_str.startswith('-') and artigo_str[1:].replace('.', '', 1).isdigit():
                    return False
                # Se é apenas números (positivos ou negativos)
                if artigo_str.replace('-', '', 1).replace('.', '', 1).isdigit():
                    return False
                # Se é vazio ou nan
                if artigo_str in ['', 'nan', 'None']:
                    return False
                return True
            
            df['is_real_article'] = df['Artigo'].apply(is_real_article)
            df_reais = df[df['is_real_article'] == True]
            
            st.sidebar.success(f"✅ Artigos reais: {len(df_reais)} de {len(df)} registos")
            st.sidebar.info(f"📦 Artigos únicos reais: {df_reais['Artigo'].nunique()}")
            
            return df_reais
        else:
            st.error("Coluna Artigo não encontrada!")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame()

# Carregar dados limpos
df_clean = load_and_clean_data()

if not df_clean.empty:
    # OBTER ARTIGOS REAIS
    artigos_reais = sorted(df_clean['Artigo'].dropna().unique())
    
    st.header("🎛️ FILTRO DE ARTIGOS REAIS")
    st.write(f"**📚 {len(artigos_reais)} artigos disponíveis**")
    
    # Mostrar alguns exemplos
    st.write("**📋 Exemplos de artigos disponíveis:**")
    for i, artigo in enumerate(artigos_reais[:20]):
        st.write(f"{i+1:2d}. {artigo}")
    
    # FILTRO PRINCIPAL
    artigo_selecionado = st.selectbox(
        "Selecione o artigo:",
        options=artigos_reais,
        index=0,  # Seleciona o primeiro por padrão
        placeholder="Escolha um artigo..."
    )
    
    if artigo_selecionado:
        resultado = df_clean[df_clean['Artigo'] == artigo_selecionado]
        
        st.success(f"✅ **{len(resultado)} registos encontrados para:** {artigo_selecionado}")
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'V. Líquido' in resultado.columns:
                total = resultado['V. Líquido'].sum()
                st.metric("💰 Total Vendas", f"€ {total:,.2f}")
        with col2:
            if 'Qtd.' in resultado.columns:
                qtd = resultado['Qtd.'].sum()
                st.metric("📦 Quantidade", f"{qtd:,.0f}")
        with col3:
            if 'Cliente' in resultado.columns:
                clientes = resultado['Cliente'].nunique()
                st.metric("👥 Clientes", f"{clientes}")
        
        # Dados
        st.dataframe(resultado, width='stretch')

else:
    st.error("❌ Não foi possível carregar os dados")

# 🎯 VERSÃO ALTERNATIVA - MULTISELECT
st.header("🎪 FILTRO MÚLTIPLO")

if not df_clean.empty:
    artigos_multiselect = st.multiselect(
        "Selecione vários artigos:",
        options=artigos_reais,
        placeholder="Escolha um ou mais artigos..."
    )
    
    if artigos_multiselect:
        resultado_mult = df_clean[df_clean['Artigo'].isin(artigos_multiselect)]
        st.success(f"✅ {len(resultado_mult)} registos para {len(artigos_multiselect)} artigo(s)")
        st.dataframe(resultado_mult, width='stretch')
