import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import re

st.set_page_config(page_title="Alertas de Compras", page_icon="🚨", layout="wide")

# CSS
st.markdown("""
<style>
    .main-header {font-size:2.5rem;color:#1f77b4;text-align:center;margin-bottom:2rem;font-weight:700;}
    .section-header {font-size:1.5rem;color:#2c3e50;margin:2rem 0 1rem 0;padding-bottom:0.5rem;border-bottom:3px solid #3498db;font-weight:600;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🚨 Alertas de Compras</h1>", unsafe_allow_html=True)

# Botão voltar
if st.button("← Voltar ao Dashboard Principal"):
    st.switch_page("Dashboard_Principal.py")

# Acessar dados da sessão
if 'df_filtrado' not in st.session_state:
    st.error("Por favor, volte à página principal para carregar os dados primeiro.")
    st.stop()

df_filtrado = st.session_state.df_filtrado

# Funções específicas para alertas
def processar_datas_mes_ano(df):
    if 'Mes' not in df.columns or 'Ano' not in df.columns:
        return pd.DataFrame()
    
    df_processed = df.copy()
    
    meses_map = {
        'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05', 'jun': '06',
        'jul': '07', 'ago': '08', 'set': '09', 'out': '10', 'nov': '11', 'dez': '12',
        '1': '01', '2': '02', '3': '03', '4': '04', '5': '05', '6': '06',
        '7': '07', '8': '08', '9': '09', '10': '10', '11': '11', '12': '12',
        '01': '01', '02': '02', '03': '03', '04': '04', '05': '05', '06': '06',
        '07': '07', '08': '08', '09': '09', '10': '10', '11': '11', '12': '12'
    }
    
    def padronizar_mes(mes_str):
        if pd.isna(mes_str) or mes_str in ['nan', 'None', 'NULL', '', ' ']:
            return None
        mes_str = str(mes_str).lower().strip()
        mes_str = re.sub(r'[^a-z0-9]', '', mes_str)
        return meses_map.get(mes_str, None)
    
    def padronizar_ano(ano_str):
        if pd.isna(ano_str) or ano_str in ['nan', 'None', 'NULL', '', ' ']:
            return None
        ano_str = str(ano_str).strip()
        ano_numeros = re.sub(r'[^\d]', '', ano_str)
        if len(ano_numeros) == 4:
            return ano_numeros
        elif len(ano_numeros) == 2:
            ano = int(ano_numeros)
            return f"20{ano:02d}" if ano < 50 else f"19{ano:02d}"
        return None
    
    df_processed['Mes_Padronizado'] = df_processed['Mes'].apply(padronizar_mes)
    df_processed['Ano_Padronizado'] = df_processed['Ano'].apply(padronizar_ano)
    
    df_valido = df_processed.dropna(subset=['Mes_Padronizado', 'Ano_Padronizado']).copy()
    
    if not df_valido.empty:
        df_valido['Periodo'] = df_valido['Ano_Padronizado'] + '-' + df_valido['Mes_Padronizado']
        meses_nome = {
            '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', '05': 'Mai', '06': 'Jun',
            '07': 'Jul', '08': 'Ago', '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
        }
        df_valido['Mes_Nome'] = df_valido['Mes_Padronizado'].map(meses_nome)
        df_valido['Periodo_Label'] = df_valido['Mes_Nome'] + ' ' + df_valido['Ano_Padronizado']
        
    return df_valido

def analisar_alertas_clientes(df):
    df_processed = df.copy()
    
    if 'Mes' not in df_processed.columns or 'Ano' not in df_processed.columns:
        st.warning("Dados de mês/ano não disponíveis para análise de alertas")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    df_processado = processar_datas_mes_ano(df_processed)
    
    if df_processado.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    df_agrupado = df_processado.groupby(['Cliente', 'Periodo'])['Qtd'].sum().reset_index()
    periodos_ordenados = sorted(df_agrupado['Periodo'].unique())
    
    if len(periodos_ordenados) < 2:
        st.warning("São necessários pelo menos 2 períodos para análise de alertas")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    periodo_atual = periodos_ordenados[-1]
    periodo_anterior = periodos_ordenados[-2]
    
    dados_atual = df_agrupado[df_agrupado['Periodo'] == periodo_atual][['Cliente', 'Qtd']].rename(columns={'Qtd': 'Qtd_Atual'})
    dados_anterior = df_agrupado[df_agrupado['Periodo'] == periodo_anterior][['Cliente', 'Qtd']].rename(columns={'Qtd': 'Qtd_Anterior'})
    
    comparacao = pd.merge(dados_atual, dados_anterior, on='Cliente', how='outer').fillna(0)
    comparacao['Variacao_Qtd'] = comparacao['Qtd_Atual'] - comparacao['Qtd_Anterior']
    comparacao['Variacao_Percentual'] = (comparacao['Variacao_Qtd'] / comparacao['Qtd_Anterior'].replace(0, 1)) * 100
    
    alertas_subida = []
    alertas_descida = []
    alertas_inativos = []
    
    for _, row in comparacao.iterrows():
        cliente = row['Cliente']
        qtd_atual = row['Qtd_Atual']
        qtd_anterior = row['Qtd_Anterior']
        variacao_perc = row['Variacao_Percentual']
        
        if qtd_anterior > 0 and qtd_atual == 0:
            alertas_inativos.append({
                'Cliente': cliente,
                'Qtd_Anterior': qtd_anterior,
                'Qtd_Atual': qtd_atual,
                'Variacao_Percentual': -100,
                'Tipo': 'Parou de Comprar'
            })
        elif variacao_perc > 20 and qtd_anterior > 0:
            alertas_subida.append({
                'Cliente': cliente,
                'Qtd_Anterior': qtd_anterior,
                'Qtd_Atual': qtd_atual,
                'Variacao_Percentual': variacao_perc,
                'Tipo': 'Subida Significativa'
            })
        elif variacao_perc < -20 and qtd_anterior > 0:
            alertas_descida.append({
                'Cliente': cliente,
                'Qtd_Anterior': qtd_anterior,
                'Qtd_Atual': qtd_atual,
                'Variacao_Percentual': variacao_perc,
                'Tipo': 'Descida Significativa'
            })
    
    df_subidas = pd.DataFrame(alertas_subida)
    df_descidas = pd.DataFrame(alertas_descida)
    df_inativos = pd.DataFrame(alertas_inativos)
    
    if not df_subidas.empty:
        df_subidas = df_subidas.sort_values('Variacao_Percentual', ascending=False)
    if not df_descidas.empty:
        df_descidas = df_descidas.sort_values('Variacao_Percentual', ascending=True)
    if not df_inativos.empty:
        df_inativos = df_inativos.sort_values('Qtd_Anterior', ascending=False)
    
    return df_subidas, df_descidas, df_inativos

# Interface dos Alertas
st.markdown("<div class='section-header'>📊 Análise de Tendências por Cliente</div>", unsafe_allow_html=True)

df_subidas, df_descidas, df_inativos = analisar_alertas_clientes(df_filtrado)

# Métricas de resumo
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Clientes em Subida", len(df_subidas))
with col2:
    st.metric("Clientes em Descida", len(df_descidas))
with col3:
    st.metric("Clientes Inativos", len(df_inativos))

# Abas para cada tipo de alerta
tab1, tab2, tab3 = st.tabs([
    f"📈 Subidas Significativas ({len(df_subidas)})",
    f"📉 Descidas Significativas ({len(df_descidas)})", 
    f"⏸️ Clientes Inativos ({len(df_inativos)})"
])

with tab1:
    if not df_subidas.empty:
        st.dataframe(df_subidas, use_container_width=True)
        
        # Gráfico das maiores subidas
        top_subidas = df_subidas.head(10)
        fig_subidas = px.bar(
            top_subidas,
            x='Variacao_Percentual',
            y='Cliente',
            orientation='h',
            title="Top 10 Maiores Subidas",
            color='Variacao_Percentual'
        )
        st.plotly_chart(fig_subidas, use_container_width=True)
    else:
        st.success("🎉 Nenhum cliente com subida significativa!")

with tab2:
    if not df_descidas.empty:
        st.dataframe(df_descidas, use_container_width=True)
        
        # Gráfico das maiores descidas
        top_descidas = df_descidas.head(10)
        fig_descidas = px.bar(
            top_descidas,
            x='Variacao_Percentual',
            y='Cliente',
            orientation='h',
            title="Top 10 Maiores Descidas",
            color='Variacao_Percentual'
        )
        st.plotly_chart(fig_descidas, use_container_width=True)
    else:
        st.success("✅ Nenhum cliente com descida significativa!")

with tab3:
    if not df_inativos.empty:
        st.dataframe(df_inativos, use_container_width=True)
        
        # Gráfico dos maiores volumes perdidos
        top_inativos = df_inativos.head(10)
        fig_inativos = px.bar(
            top_inativos,
            x='Qtd_Anterior',
            y='Cliente',
            orientation='h',
            title="Top 10 Maiores Volumes Perdidos",
            color='Qtd_Anterior'
        )
        st.plotly_chart(fig_inativos, use_container_width=True)
    else:
        st.success("✅ Nenhum cliente inativo identificado!")

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#7f8c8d;'>Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)
