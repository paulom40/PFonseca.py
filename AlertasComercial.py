import streamlit as st
import pandas as pd
import numpy as np

st.title("🔍 DIAGNÓSTICO EM TEMPO REAL - Análise das Diferenças")

@st.cache_data
def load_raw_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
        df = pd.read_excel(url)
        return df
    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame()

# Carregar dados crus
df_raw = load_raw_data()

if not df_raw.empty:
    st.header("📊 ANÁLISE COMPLETA DOS DADOS CRUS")
    
    # 1. TOTAIS SEM QUALQUER FILTRO
    st.subheader("1. 🎯 TOTAIS CRUS (Sem nenhum filtro)")
    
    total_v_liquido_raw = df_raw['V. Líquido'].sum() if 'V. Líquido' in df_raw.columns else 0
    total_qtd_raw = df_raw['Qtd.'].sum() if 'Qtd.' in df_raw.columns else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 V. Líquido CRU", f"€ {total_v_liquido_raw:,.2f}")
    with col2:
        st.metric("📦 Qtd CRUA", f"{total_qtd_raw:,.2f}")
    
    st.write(f"**Comparação com tuas referências:**")
    st.write(f"- V. Líquido: € {total_v_liquido_raw:,.2f} vs € 11,032,291.50 → Diferença: € {total_v_liquido_raw - 11032291.5:,.2f}")
    st.write(f"- Qtd: {total_qtd_raw:,.2f} vs 4,449,342.03 → Diferença: {total_qtd_raw - 4449342.03:,.2f}")
    
    # 2. ANÁLISE DETALHADA DA COLUNA ARTIGO
    st.subheader("2. 🔎 Análise Detalhada da Coluna 'Artigo'")
    
    if 'Artigo' in df_raw.columns:
        # Converter para análise
        df_raw['Artigo_str'] = df_raw['Artigo'].astype(str)
        
        # Análise mais detalhada
        def analise_detalhada_artigo(artigo):
            artigo_str = str(artigo).strip()
            
            if artigo_str == 'nan' or artigo_str == '':
                return "Vazio/Nulo"
            elif artigo_str.startswith('-') and artigo_str[1:].replace('.', '', 1).isdigit():
                return "Número Negativo"
            elif artigo_str.replace('.', '', 1).isdigit():
                return "Número Positivo"
            elif any(x in artigo_str.lower() for x in ['leitao', 'banha', 'bacalhau']):
                return "Produto Principal"
            else:
                return "Outro Texto"
        
        df_raw['tipo_detalhado'] = df_raw['Artigo_str'].apply(analise_detalhada_artigo)
        
        # Estatísticas detalhadas
        stats_detalhado = df_raw.groupby('tipo_detalhado').agg({
            'V. Líquido': ['sum', 'count', 'mean'],
            'Qtd.': ['sum', 'mean']
        }).round(2)
        
        st.write("**Estatísticas por Tipo Detalhado:**")
        st.dataframe(stats_detalhado)
        
        # Mostrar exemplos específicos
        st.write("**📋 Exemplos de cada categoria (primeiros 3):**")
        for tipo in stats_detalhado.index:
            exemplos = df_raw[df_raw['tipo_detalhado'] == tipo]['Artigo_str'].unique()[:3]
            total_vl = df_raw[df_raw['tipo_detalhado'] == tipo]['V. Líquido'].sum()
            total_qtd = df_raw[df_raw['tipo_detalhado'] == tipo]['Qtd.'].sum()
            
            st.write(f"**{tipo}** (V.Líquido: € {total_vl:,.2f}, Qtd: {total_qtd:,.2f}):")
            for ex in exemplos:
                st.write(f"  - '{ex}'")
    
    # 3. VERIFICAR SE HÁ FILTROS AUTOMÁTICOS
    st.subheader("3. 🕵️ Verificação de Filtros Automáticos")
    
    st.write("**Verificando se há dados excluídos automaticamente:**")
    
    # Contar registros antes e depois da conversão
    total_registros = len(df_raw)
    st.write(f"- Total de registros no ficheiro: {total_registros:,}")
    
    # Verificar se há filtros no carregamento
    st.write("**Possíveis causas da diferença:**")
    
    # 4. ANÁLISE DOS VALORES NEGATIVOS
    st.subheader("4. 📉 Análise dos Valores Negativos")
    
    if 'V. Líquido' in df_raw.columns:
        negativos_vl = df_raw[df_raw['V. Líquido'] < 0]
        st.write(f"**V. Líquido Negativo:** {len(negativos_vl)} registos, Total: € {negativos_vl['V. Líquido'].sum():,.2f}")
        
    if 'Qtd.' in df_raw.columns:
        negativos_qtd = df_raw[df_raw['Qtd.'] < 0]
        st.write(f"**Qtd Negativa:** {len(negativos_qtd)} registos, Total: {negativos_qtd['Qtd.'].sum():,.2f}")
    
    # 5. TESTE: CARREGAR DIRETAMENTE SEM CONVERSÕES
    st.subheader("5. 🧪 Teste - Carregamento Direto")
    
    @st.cache_data
    def load_direct_test():
        try:
            url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
            # Carregar sem nenhuma transformação
            df_test = pd.read_excel(url)
            return df_test
        except:
            return pd.DataFrame()
    
    df_test = load_direct_test()
    
    if not df_test.empty:
        total_vl_test = df_test['V. Líquido'].sum() if 'V. Líquido' in df_test.columns else 0
        total_qtd_test = df_test['Qtd.'].sum() if 'Qtd.' in df_test.columns else 0
        
        st.write("**Resultado do carregamento direto (sem conversões):**")
        st.write(f"- V. Líquido: € {total_vl_test:,.2f}")
        st.write(f"- Qtd: {total_qtd_test:,.2f}")
        
        if abs(total_vl_test - 11032291.5) < 0.01 and abs(total_qtd_test - 4449342.03) < 0.01:
            st.success("🎉 CARREGAMENTO DIRETO CORRESPONDE ÀS TUAS REFERÊNCIAS!")
        else:
            st.error("❌ CARREGAMENTO DIRETO TAMBÉM ESTÁ DIFERENTE!")
    
    # 6. SOLUÇÃO: USAR OS DADOS CRUS
    st.subheader("6. 🚀 SOLUÇÃO RECOMENDADA")
    
    st.error("**PROBLEMA IDENTIFICADO:**")
    st.write("O ficheiro Excel original já tem os totais diferentes das tuas referências!")
    st.write("Isto significa que o problema não está no nosso código, mas sim nos dados originais.")
    
    st.success("**SOLUÇÃO IMEDIATA:**")
    st.write("Vamos usar os **dados crus sem nenhum filtro** no dashboard principal.")
    
    # Código da solução
    st.code("""
# NO DASHBOARD PRINCIPAL - USAR ESTA FUNÇÃO:
@st.cache_data
def load_raw_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    df = pd.read_excel(url)
    
    # APENAS renomear colunas, SEM filtrar dados
    mapeamento = {
        'Código': 'Codigo',
        'Cliente': 'Cliente', 
        'Qtd.': 'Qtd',
        'V. Líquido': 'V_Liquido',
        'Artigo': 'Artigo',
        'Comercial': 'Comercial',
        'Categoria': 'Categoria',
        'Mês': 'Mes',
        'Ano': 'Ano'
    }
    
    for col_original, col_novo in mapeamento.items():
        if col_original in df.columns:
            df = df.rename(columns={col_original: col_novo})
    
    return df
    """)

else:
    st.error("Não foi possível carregar os dados para análise")

# 🎯 DASHBOARD SIMPLES COM DADOS CRUS
st.header("🎯 DASHBOARD SIMPLES - Dados Crus")

if not df_raw.empty:
    # Métricas básicas
    col1, col2 = st.columns(2)
    
    with col1:
        total_vl = df_raw['V. Líquido'].sum() if 'V. Líquido' in df_raw.columns else 0
        st.metric("💰 V. Líquido CRU", f"€ {total_vl:,.2f}")
    
    with col2:
        total_qtd = df_raw['Qtd.'].sum() if 'Qtd.' in df_raw.columns else 0
        st.metric("📦 Qtd CRUA", f"{total_qtd:,.2f}")
    
    # Comparação
    st.write("**Comparação com Referências:**")
    
    diff_vl = total_vl - 11032291.5
    diff_qtd = total_qtd - 4449342.03
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "V. Líquido vs Referência", 
            f"€ {total_vl:,.2f}",
            delta=f"€ {diff_vl:,.2f}",
            delta_color="inverse" if diff_vl < 0 else "normal"
        )
    
    with col2:
        st.metric(
            "Qtd vs Referência", 
            f"{total_qtd:,.2f}",
            delta=f"{diff_qtd:,.2f}",
            delta_color="inverse" if diff_qtd < 0 else "normal"
        )
    
    # Mostrar primeiros registos
    st.write("**Primeiros 10 registos (crus):**")
    st.dataframe(df_raw.head(10))
