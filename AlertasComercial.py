import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import re
from datetime import datetime

# -------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------------------------
st.set_page_config(
    page_title="Tabela Geral de Clientes",
    page_icon="📊",
    layout="wide"
)

# -------------------------------------------------
# CSS (mantém o mesmo estilo)
# -------------------------------------------------
st.markdown("""
<style>
    .main-header {font-size:2.5rem;color:#1f77b4;text-align:center;margin-bottom:2rem;font-weight:700;}
    .section-header {font-size:1.5rem;color:#2c3e50;margin:2rem 0 1rem 0;padding-bottom:0.5rem;border-bottom:3px solid #3498db;font-weight:600;}
    .logo-container {
        position: fixed;
        top: 10px;
        left: 10px;
        z-index: 1000;
        background: white;
        padding: 5px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .logo-container img {
        height: 70px;
        width: auto;
    }
</style>
""", unsafe_allow_html=True)

# LOGO
st.markdown(f"""
<div class="logo-container">
    <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" alt="Bracar Logo">
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# FUNÇÕES ESPECÍFICAS PARA ESTA PÁGINA
# -------------------------------------------------
def formatar_numero_pt(valor, simbolo="", sinal_forcado=False):
    if pd.isna(valor):
        return "N/D"
    valor = float(valor)
    sinal = "+" if sinal_forcado and valor >= 0 else ("-" if valor < 0 else "")
    valor_abs = abs(valor)
    if valor_abs == int(valor_abs):
        return f"{sinal}{simbolo}{valor_abs:,.0f}".replace(",", " ")
    else:
        return f"{sinal}{simbolo}{valor_abs:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def to_excel(df, sheet_name="Dados"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

def processar_datas_mes_ano(df):
    """Processa colunas Mes e Ano para criar períodos consistentes"""
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

def criar_tabela_geral_clientes(df):
    """Cria tabela geral com Qtd mensal por cliente e alertas de variação"""
    
    df_processado = processar_datas_mes_ano(df)
    
    if df_processado.empty:
        return pd.DataFrame()
    
    df_agrupado = df_processado.groupby(['Cliente', 'Periodo', 'Periodo_Label']).agg({
        'Qtd': 'sum'
    }).reset_index()
    
    periodos_ordenados = sorted(df_agrupado['Periodo'].unique())
    
    if len(periodos_ordenados) < 2:
        return pd.DataFrame()
    
    df_pivot = df_agrupado.pivot_table(
        index='Cliente',
        columns='Periodo_Label',
        values='Qtd',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    colunas_ordenadas = ['Cliente'] + sorted(df_pivot.columns[1:], reverse=True)
    df_pivot = df_pivot[colunas_ordenadas]
    
    if len(df_pivot.columns) >= 3:
        coluna_atual = df_pivot.columns[1]
        coluna_anterior = df_pivot.columns[2]
        
        df_pivot['Qtd_Atual'] = df_pivot[coluna_atual]
        df_pivot['Qtd_Anterior'] = df_pivot[coluna_anterior]
        
        df_pivot['Variacao_%'] = ((df_pivot['Qtd_Atual'] - df_pivot['Qtd_Anterior']) / 
                                 df_pivot['Qtd_Anterior'].replace(0, 1)) * 100
        
        def classificar_alerta(variacao, qtd_anterior, qtd_atual):
            if qtd_anterior == 0 and qtd_atual > 0:
                return "🟢 Novo Cliente"
            elif qtd_anterior > 0 and qtd_atual == 0:
                return "🔴 Parou de Comprar"
            elif variacao > 50:
                return "🟢 Subida Forte"
            elif variacao > 20:
                return "🟡 Subida Moderada"
            elif variacao < -50:
                return "🔴 Descida Forte"
            elif variacao < -20:
                return "🟠 Descida Moderada"
            elif variacao > 0:
                return "🔵 Subida Leve"
            elif variacao < 0:
                return "⚫ Descida Leve"
            else:
                return "⚪ Estável"
        
        df_pivot['Alerta'] = df_pivot.apply(
            lambda x: classificar_alerta(x['Variacao_%'], x['Qtd_Anterior'], x['Qtd_Atual']), 
            axis=1
        )
        
        for col in df_pivot.columns:
            if col not in ['Cliente', 'Alerta', 'Variacao_%'] and df_pivot[col].dtype in [np.int64, np.float64]:
                df_pivot[col] = df_pivot[col].apply(lambda x: formatar_numero_pt(x) if pd.notna(x) else '0')
        
        df_pivot['Variacao_Formatada'] = df_pivot['Variacao_%'].apply(
            lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/D"
        )
        
        colunas_finais = ['Cliente', 'Alerta', 'Variacao_Formatada'] + colunas_ordenadas[1:]
        df_final = df_pivot[colunas_finais].rename(columns={'Variacao_Formatada': 'Variação %'})
        
        return df_final
    
    return pd.DataFrame()

# -------------------------------------------------
# INTERFACE DA PÁGINA
# -------------------------------------------------
st.markdown("<h1 class='main-header'>📊 Tabela Geral de Clientes</h1>", unsafe_allow_html=True)

# Botão para voltar à página principal
if st.button("← Voltar ao Dashboard Principal"):
    st.switch_page("Dashboard_Principal.py")

# Acessa os dados filtrados da sessão (se disponível) ou carrega novamente
if 'df_filtrado' in st.session_state:
    df_filtrado = st.session_state.df_filtrado
else:
    # Se não estiver na sessão, carrega os dados (simplificado)
    import requests
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/VendasGeraisTranf.xlsx"
        df = pd.read_excel(url, thousands=None, decimal=',')
        # Aplica filtros básicos se necessário
        df_filtrado = df
    except:
        st.error("Erro ao carregar dados")
        st.stop()

if df_filtrado.empty:
    st.warning("Nenhum dado disponível para análise.")
else:
    st.success(f"**{len(df_filtrado):,}** registos analisados")

    # Criar tabela geral
    df_tabela_geral = criar_tabela_geral_clientes(df_filtrado)
    
    if not df_tabela_geral.empty:
        # Estatísticas rápidas
        st.markdown("<div class='section-header'>📈 Estatísticas Gerais</div>", unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_clientes = len(df_tabela_geral)
        clientes_subida = len(df_tabela_geral[df_tabela_geral['Alerta'].str.contains('Subida')])
        clientes_descida = len(df_tabela_geral[df_tabela_geral['Alerta'].str.contains('Descida')])
        clientes_novos = len(df_tabela_geral[df_tabela_geral['Alerta'] == '🟢 Novo Cliente'])
        clientes_inativos = len(df_tabela_geral[df_tabela_geral['Alerta'] == '🔴 Parou de Comprar'])
        
        with col1:
            st.metric("Total Clientes", total_clientes)
        with col2:
            st.metric("Em Subida", clientes_subida)
        with col3:
            st.metric("Em Descida", clientes_descida)
        with col4:
            st.metric("Novos", clientes_novos)
        with col5:
            st.metric("Inativos", clientes_inativos)

        # Filtros
        st.markdown("<div class='section-header'>🔍 Filtros e Configurações</div>", unsafe_allow_html=True)
        
        col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
        
        with col_filtro1:
            filtro_alerta = st.multiselect(
                "Filtrar por Alerta:",
                options=sorted(df_tabela_geral['Alerta'].unique()),
                default=sorted(df_tabela_geral['Alerta'].unique())
            )
        
        with col_filtro2:
            ordenacao = st.selectbox(
                "Ordenar por:",
                options=["Cliente", "Maior Subida", "Maior Descida", "Maior Qtd Atual"]
            )
        
        with col_filtro3:
            # Opção para mostrar/ocultar colunas antigas
            mostrar_todos_meses = st.checkbox("Mostrar todos os meses", value=False)
        
        # Aplicar filtros
        df_filtrado_tabela = df_tabela_geral[df_tabela_geral['Alerta'].isin(filtro_alerta)].copy()
        
        # Aplicar ordenação
        if ordenacao == "Maior Subida":
            df_filtrado_tabela['Var_Num'] = df_filtrado_tabela['Variação %'].str.replace('%', '').str.replace('+', '').astype(float)
            df_filtrado_tabela = df_filtrado_tabela.sort_values('Var_Num', ascending=False)
        elif ordenacao == "Maior Descida":
            df_filtrado_tabela['Var_Num'] = df_filtrado_tabela['Variação %'].str.replace('%', '').str.replace('+', '').astype(float)
            df_filtrado_tabela = df_filtrado_tabela.sort_values('Var_Num', ascending=True)
        elif ordenacao == "Maior Qtd Atual":
            if 'Qtd_Atual' in df_filtrado_tabela.columns:
                df_filtrado_tabela['Qtd_Num'] = df_filtrado_tabela['Qtd_Atual'].str.replace(' ', '').astype(float)
                df_filtrado_tabela = df_filtrado_tabela.sort_values('Qtd_Num', ascending=False)
            else:
                df_filtrado_tabela = df_filtrado_tabela.sort_values('Cliente')
        else:
            df_filtrado_tabela = df_filtrado_tabela.sort_values('Cliente')
        
        # Limitar colunas se não quiser mostrar todos os meses
        if not mostrar_todos_meses and len(df_filtrado_tabela.columns) > 8:
            colunas_principais = ['Cliente', 'Alerta', 'Variação %'] + list(df_filtrado_tabela.columns[3:6])
            df_filtrado_tabela = df_filtrado_tabela[colunas_principais]
        
        # Exibir tabela
        st.markdown("<div class='section-header'>📋 Tabela Geral de Clientes</div>", unsafe_allow_html=True)
        st.write(f"**{len(df_filtrado_tabela)} clientes encontrados**")
        
        # Função para colorir as células
        def colorir_linhas(row):
            alerta = row['Alerta']
            if '🔴' in alerta or 'Parou' in alerta:
                return ['background-color: #ffe6e6'] * len(row)
            elif '🟢' in alerta or 'Novo' in alerta:
                return ['background-color: #e8f5e8'] * len(row)
            elif '🟡' in alerta:
                return ['background-color: #fff3e0'] * len(row)
            elif '🟠' in alerta:
                return ['background-color: #fbe9e7'] * len(row)
            else:
                return [''] * len(row)
        
        styled_df = df_filtrado_tabela.style.apply(colorir_linhas, axis=1)
        st.dataframe(styled_df, width='stretch', height=600)
        
        # Botão de exportação
        st.download_button(
            "📥 Exportar Tabela para Excel",
            to_excel(df_filtrado_tabela),
            "tabela_geral_clientes.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    else:
        st.warning("Não foi possível gerar a tabela geral. Verifique se há dados suficientes para análise.")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#7f8c8d;'>Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)
