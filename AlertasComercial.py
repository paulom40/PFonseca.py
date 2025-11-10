import streamlit as st
import pandas as pd
import json
from pathlib import Path
import numpy as np
import plotly.express as px
from datetime import datetime
from io import BytesIO
import re

# -------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# -------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Vendas - BI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# 2. CSS + LOGO NO CANTO SUPERIOR ESQUERDO
# -------------------------------------------------
st.markdown("""
<style>
    .main-header {font-size:2.5rem;color:#1f77b4;text-align:center;margin-bottom:2rem;font-weight:700;}
    .metric-card {background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:1.5rem;border-radius:15px;color:white;box-shadow:0 4px 6px rgba(0,0,0,0.1);}
    .section-header {font-size:1.5rem;color:#2c3e50;margin:2rem 0 1rem 0;padding-bottom:0.5rem;border-bottom:3px solid #3498db;font-weight:600;}
    .alerta-critico {color: #8B0000; font-weight: bold; background-color: #ffe6e6; padding: 2px 6px; border-radius: 4px;}
    .alerta-alto {color: #d32f2f; font-weight: bold;}
    .alerta-moderado {color: #f57c00; font-weight: bold;}
    .alerta-positivo {color: #2e7d32; font-weight: bold; background-color: #e8f5e8; padding: 2px 6px; border-radius: 4px;}
    .alerta-negativo {color: #8B0000; font-weight: bold; background-color: #ffe6e6; padding: 2px 6px; border-radius: 4px;}
    .alerta-neutro {color: #666666; font-weight: bold; background-color: #f5f5f5; padding: 2px 6px; border-radius: 4px;}
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
    .card-alerta {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .card-subida { border-left-color: #2e7d32; }
    .card-descida { border-left-color: #d32f2f; }
    .card-inativo { border-left-color: #666666; }
</style>
""", unsafe_allow_html=True)

# LOGO
st.markdown(f"""
<div class="logo-container">
    <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" alt="Bracar Logo">
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 3. FORMATAÇÃO PT-PT
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

# -------------------------------------------------
# 4. EXPORTAÇÃO PARA EXCEL
# -------------------------------------------------
def to_excel(df, sheet_name="Dados"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

# -------------------------------------------------
# 5. CARREGAMENTO DOS DADOS
# -------------------------------------------------
@st.cache_data
def load_all_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/VendasGeraisTranf.xlsx"
        df = pd.read_excel(url, thousands=None, decimal=',')
        mapeamento = {
            'Código': 'Codigo', 'Cliente': 'Cliente', 'Qtd.': 'Qtd', 'UN': 'UN',
            'PM': 'PM', 'V. Líquido': 'V_Liquido', 'Artigo': 'Artigo',
            'Comercial': 'Comercial', 'Categoria': 'Categoria',
            'Mês': 'Mes', 'Ano': 'Ano'
        }
        df = df.rename(columns={k: v for k, v in mapeamento.items() if k in df.columns})
        colunas_string = ['UN', 'Artigo', 'Cliente', 'Comercial', 'Categoria', 'Mes', 'Ano']
        for col in colunas_string:
            if col in df.columns:
                df[col] = df[col].astype(str).replace({'nan': 'N/D', 'None': 'N/D'})
        for col in ['V_Liquido', 'Qtd', 'PM']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_all_data()

# -------------------------------------------------
# 6. PRESETS
# -------------------------------------------------
preset_path = Path("diagnosticos/presets_filtros.json")
preset_path.parent.mkdir(exist_ok=True)

def carregar_presets():
    if preset_path.exists():
        with open(preset_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_preset(nome, filtros):
    presets = carregar_presets()
    presets[nome] = filtros
    with open(preset_path, "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=2)

# -------------------------------------------------
# 7. SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown("<div class='metric-card'>Painel de Controle</div>", unsafe_allow_html=True)
    presets = carregar_presets()
    preset_selecionado = st.selectbox("Configuração", [""] + list(presets.keys()))
    filtros = presets.get(preset_selecionado, {}) if preset_selecionado else {}

    st.markdown("---")
    st.markdown("### Filtros")
    def criar_filtro(label, coluna, default=None):
        if coluna not in df.columns or df.empty: return []
        opcoes = sorted(df[coluna].dropna().astype(str).unique())
        return st.multiselect(label, opcoes, default=default or [])
    clientes   = criar_filtro("Clientes", "Cliente", filtros.get("Cliente"))
    artigos    = criar_filtro("Artigos", "Artigo", filtros.get("Artigo"))
    comerciais = criar_filtro("Comerciais", "Comercial", filtros.get("Comercial"))
    categorias = criar_filtro("Categorias", "Categoria", filtros.get("Categoria"))
    meses      = criar_filtro("Meses", "Mes", filtros.get("Mes"))
    anos       = criar_filtro("Anos", "Ano", filtros.get("Ano"))

    st.markdown("---")
    nome_preset = st.text_input("Nome da configuração")
    if st.button("Salvar") and nome_preset:
        salvar_preset(nome_preset, {"Cliente": clientes, "Artigo": artigos, "Comercial": comerciais,
                                   "Categoria": categorias, "Mes": meses, "Ano": anos})
        st.success(f"Salvo: {nome_preset}")

# -------------------------------------------------
# 8. FILTROS PRINCIPAIS
# -------------------------------------------------
df_filtrado = df.copy()
if clientes: df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes)]
if artigos: df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(artigos)]
if comerciais: df_filtrado = df_filtrado[df_filtrado['Comercial'].isin(comerciais)]
if categorias: df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias)]
if meses: df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses)]
if anos: df_filtrado = df_filtrado[df_filtrado['Ano'].isin(anos)]

# -------------------------------------------------
# 9. FUNÇÃO PARA ANÁLISE DE ALERTAS
# -------------------------------------------------
def analisar_alertas_clientes(df):
    """Analisa subidas, descidas e clientes inativos baseado na quantidade"""
    
    # Processar datas
    df_processed = df.copy()
    
    # Mapeamento de meses
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
    
    # Aplicar padronização
    df_processed['Mes_Padronizado'] = df_processed['Mes'].apply(padronizar_mes)
    df_processed['Ano_Padronizado'] = df_processed['Ano'].apply(padronizar_ano)
    
    # Filtrar dados válidos
    df_valido = df_processed.dropna(subset=['Mes_Padronizado', 'Ano_Padronizado']).copy()
    
    if df_valido.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    # Criar período ordenável
    df_valido['Periodo'] = df_valido['Ano_Padronizado'] + '-' + df_valido['Mes_Padronizado']
    
    # Agrupar por cliente e período
    df_agrupado = df_valido.groupby(['Cliente', 'Periodo'])['Qtd'].sum().reset_index()
    
    # Ordenar períodos
    periodos_ordenados = sorted(df_agrupado['Periodo'].unique())
    
    if len(periodos_ordenados) < 2:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    # Período atual e anterior
    periodo_atual = periodos_ordenados[-1]
    periodo_anterior = periodos_ordenados[-2]
    
    # Dados do período atual
    dados_atual = df_agrupado[df_agrupado['Periodo'] == periodo_atual][['Cliente', 'Qtd']].rename(
        columns={'Qtd': 'Qtd_Atual'})
    
    # Dados do período anterior
    dados_anterior = df_agrupado[df_agrupado['Periodo'] == periodo_anterior][['Cliente', 'Qtd']].rename(
        columns={'Qtd': 'Qtd_Anterior'})
    
    # Combinar dados para comparação
    comparacao = pd.merge(dados_atual, dados_anterior, on='Cliente', how='outer').fillna(0)
    
    # Calcular variações
    comparacao['Variacao_Qtd'] = comparacao['Qtd_Atual'] - comparacao['Qtd_Anterior']
    comparacao['Variacao_Percentual'] = (comparacao['Variacao_Qtd'] / comparacao['Qtd_Anterior'].replace(0, 1)) * 100
    
    # Classificar alertas
    alertas_subida = []
    alertas_descida = []
    alertas_inativos = []
    
    for _, row in comparacao.iterrows():
        cliente = row['Cliente']
        qtd_atual = row['Qtd_Atual']
        qtd_anterior = row['Qtd_Anterior']
        variacao_perc = row['Variacao_Percentual']
        
        # Clientes que deixaram de comprar (estavam ativos e agora são zero)
        if qtd_anterior > 0 and qtd_atual == 0:
            alertas_inativos.append({
                'Cliente': cliente,
                'Qtd_Anterior': qtd_anterior,
                'Qtd_Atual': qtd_atual,
                'Variacao_Percentual': -100,
                'Tipo': 'Parou de Comprar'
            })
        
        # Subidas significativas (> 20%)
        elif variacao_perc > 20 and qtd_anterior > 0:
            alertas_subida.append({
                'Cliente': cliente,
                'Qtd_Anterior': qtd_anterior,
                'Qtd_Atual': qtd_atual,
                'Variacao_Percentual': variacao_perc,
                'Tipo': 'Subida Significativa'
            })
        
        # Descidas significativas (< -20%)
        elif variacao_perc < -20 and qtd_anterior > 0:
            alertas_descida.append({
                'Cliente': cliente,
                'Qtd_Anterior': qtd_anterior,
                'Qtd_Atual': qtd_atual,
                'Variacao_Percentual': variacao_perc,
                'Tipo': 'Descida Significativa'
            })
    
    # Converter para DataFrames
    df_subidas = pd.DataFrame(alertas_subida)
    df_descidas = pd.DataFrame(alertas_descida)
    df_inativos = pd.DataFrame(alertas_inativos)
    
    # Ordenar por magnitude da variação
    if not df_subidas.empty:
        df_subidas = df_subidas.sort_values('Variacao_Percentual', ascending=False)
    if not df_descidas.empty:
        df_descidas = df_descidas.sort_values('Variacao_Percentual', ascending=True)
    if not df_inativos.empty:
        df_inativos = df_inativos.sort_values('Qtd_Anterior', ascending=False)
    
    return df_subidas, df_descidas, df_inativos

# -------------------------------------------------
# 10. INTERFACE
# -------------------------------------------------
st.markdown("<h1 class='main-header'>Dashboard de Vendas</h1>", unsafe_allow_html=True)

if df.empty:
    st.error("Erro ao carregar dados.")
elif df_filtrado.empty:
    st.warning("Nenhum dado com os filtros.")
else:
    st.success(f"**{len(df_filtrado):,}** registos")

    # -------------------------------------------------
    # 11. MÉTRICAS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Métricas</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Vendas", formatar_numero_pt(df_filtrado['V_Liquido'].sum(), "EUR "))
    with col2: st.metric("Qtd", formatar_numero_pt(df_filtrado['Qtd'].sum()))
    with col3: st.metric("Clientes", f"{df_filtrado['Cliente'].nunique():,}")
    with col4: st.metric("Artigos", f"{df_filtrado['Artigo'].nunique():,}")

    # -------------------------------------------------
    # 12. ALERTAS DE COMPRAS - SUBIDAS, DESCIDAS E INATIVOS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>🚨 Alertas de Compras - Análise de Tendências</div>", unsafe_allow_html=True)
    
    # Analisar alertas
    df_subidas, df_descidas, df_inativos = analisar_alertas_clientes(df_filtrado)
    
    # Criar abas para os diferentes tipos de alerta
    tab1, tab2, tab3 = st.tabs([
        f"📈 Subidas Significativas ({len(df_subidas)})",
        f"📉 Descidas Significativas ({len(df_descidas)})", 
        f"⏸️ Clientes Inativos ({len(df_inativos)})"
    ])
    
    with tab1:
        st.subheader("📈 Clientes com Subidas Significativas (> 20%)")
        
        if not df_subidas.empty:
            # Métricas resumo
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Clientes", len(df_subidas))
            with col2:
                maior_subida = df_subidas['Variacao_Percentual'].max()
                st.metric("Maior Subida", f"{maior_subida:.1f}%")
            with col3:
                media_subidas = df_subidas['Variacao_Percentual'].mean()
                st.metric("Média de Subidas", f"{media_subidas:.1f}%")
            
            # Tabela de alertas
            st.write("**Detalhes das Subidas:**")
            
            # Preparar dados para exibição
            df_display = df_subidas.copy()
            df_display['Qtd_Anterior_Formatada'] = df_display['Qtd_Anterior'].apply(formatar_numero_pt)
            df_display['Qtd_Atual_Formatada'] = df_display['Qtd_Atual'].apply(formatar_numero_pt)
            df_display['Variacao_Formatada'] = df_display['Variacao_Percentual'].apply(lambda x: f"+{x:.1f}%")
            
            # Adicionar classificação de intensidade
            def classificar_subida(variacao):
                if variacao > 100:
                    return "🟢 Subida Muito Forte"
                elif variacao > 50:
                    return "🟡 Subida Forte"
                else:
                    return "🔵 Subida Moderada"
            
            df_display['Intensidade'] = df_display['Variacao_Percentual'].apply(classificar_subida)
            
            # Exibir tabela
            st.dataframe(
                df_display[['Cliente', 'Qtd_Anterior_Formatada', 'Qtd_Atual_Formatada', 'Variacao_Formatada', 'Intensidade']].rename(
                    columns={
                        'Qtd_Anterior_Formatada': 'Qtd Anterior',
                        'Qtd_Atual_Formatada': 'Qtd Atual',
                        'Variacao_Formatada': 'Variação %',
                        'Intensidade': 'Intensidade'
                    }
                ),
                width='stretch'
            )
            
            # Botão de exportação
            st.download_button(
                "📥 Exportar Subidas",
                to_excel(df_subidas),
                "clientes_subidas.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Gráfico das maiores subidas
            st.subheader("📊 Top 10 Maiores Subidas")
            top_subidas = df_subidas.head(10)
            fig_subidas = px.bar(
                top_subidas,
                x='Variacao_Percentual',
                y='Cliente',
                orientation='h',
                text='Variacao_Formatada',
                title="Top 10 Clientes com Maiores Subidas",
                color='Variacao_Percentual',
                color_continuous_scale='Viridis'
            )
            fig_subidas.update_traces(textposition='outside')
            st.plotly_chart(fig_subidas, width='stretch')
            
        else:
            st.success("🎉 Nenhum cliente com subida significativa identificada!")
    
    with tab2:
        st.subheader("📉 Clientes com Descidas Significativas (> 20%)")
        
        if not df_descidas.empty:
            # Métricas resumo
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Clientes", len(df_descidas))
            with col2:
                maior_descida = df_descidas['Variacao_Percentual'].min()
                st.metric("Maior Descida", f"{maior_descida:.1f}%")
            with col3:
                media_descidas = df_descidas['Variacao_Percentual'].mean()
                st.metric("Média de Descidas", f"{media_descidas:.1f}%")
            
            # Tabela de alertas
            st.write("**Detalhes das Descidas:**")
            
            # Preparar dados para exibição
            df_display = df_descidas.copy()
            df_display['Qtd_Anterior_Formatada'] = df_display['Qtd_Anterior'].apply(formatar_numero_pt)
            df_display['Qtd_Atual_Formatada'] = df_display['Qtd_Atual'].apply(formatar_numero_pt)
            df_display['Variacao_Formatada'] = df_display['Variacao_Percentual'].apply(lambda x: f"{x:.1f}%")
            
            # Adicionar classificação de intensidade
            def classificar_descida(variacao):
                if variacao < -50:
                    return "🔴 Descida Crítica"
                elif variacao < -30:
                    return "🟠 Descida Severa"
                else:
                    return "🟡 Descida Moderada"
            
            df_display['Intensidade'] = df_display['Variacao_Percentual'].apply(classificar_descida)
            
            # Exibir tabela
            st.dataframe(
                df_display[['Cliente', 'Qtd_Anterior_Formatada', 'Qtd_Atual_Formatada', 'Variacao_Formatada', 'Intensidade']].rename(
                    columns={
                        'Qtd_Anterior_Formatada': 'Qtd Anterior',
                        'Qtd_Atual_Formatada': 'Qtd Atual',
                        'Variacao_Formatada': 'Variação %',
                        'Intensidade': 'Intensidade'
                    }
                ),
                width='stretch'
            )
            
            # Botão de exportação
            st.download_button(
                "📥 Exportar Descidas",
                to_excel(df_descidas),
                "clientes_descidas.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Gráfico das maiores descidas
            st.subheader("📊 Top 10 Maiores Descidas")
            top_descidas = df_descidas.head(10)
            fig_descidas = px.bar(
                top_descidas,
                x='Variacao_Percentual',
                y='Cliente',
                orientation='h',
                text='Variacao_Formatada',
                title="Top 10 Clientes com Maiores Descidas",
                color='Variacao_Percentual',
                color_continuous_scale='Reds_r'
            )
            fig_descidas.update_traces(textposition='outside')
            st.plotly_chart(fig_descidas, width='stretch')
            
        else:
            st.success("✅ Nenhum cliente com descida significativa identificada!")
    
    with tab3:
        st.subheader("⏸️ Clientes que Pararam de Comprar")
        
        if not df_inativos.empty:
            # Métricas resumo
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Clientes", len(df_inativos))
            with col2:
                maior_compra_anterior = df_inativos['Qtd_Anterior'].max()
                st.metric("Maior Compra Anterior", formatar_numero_pt(maior_compra_anterior))
            with col3:
                media_compras_anteriores = df_inativos['Qtd_Anterior'].mean()
                st.metric("Média Compras Anteriores", formatar_numero_pt(media_compras_anteriores))
            
            # Tabela de alertas
            st.write("**Detalhes dos Clientes Inativos:**")
            
            # Preparar dados para exibição
            df_display = df_inativos.copy()
            df_display['Qtd_Anterior_Formatada'] = df_display['Qtd_Anterior'].apply(formatar_numero_pt)
            df_display['Qtd_Atual_Formatada'] = df_display['Qtd_Atual'].apply(formatar_numero_pt)
            df_display['Perda_Formatada'] = df_display['Qtd_Anterior'].apply(lambda x: formatar_numero_pt(x))
            
            # Adicionar classificação por volume anterior
            def classificar_volume(qtd):
                if qtd > 1000:
                    return "🔴 Perda Crítica"
                elif qtd > 500:
                    return "🟠 Perda Significativa"
                else:
                    return "🟡 Perda Moderada"
            
            df_display['Impacto'] = df_display['Qtd_Anterior'].apply(classificar_volume)
            
            # Exibir tabela
            st.dataframe(
                df_display[['Cliente', 'Qtd_Anterior_Formatada', 'Perda_Formatada', 'Impacto']].rename(
                    columns={
                        'Qtd_Anterior_Formatada': 'Última Compra (Qtd)',
                        'Perda_Formatada': 'Volume Perdido',
                        'Impacto': 'Impacto da Perda'
                    }
                ),
                width='stretch'
            )
            
            # Botão de exportação
            st.download_button(
                "📥 Exportar Clientes Inativos",
                to_excel(df_inativos),
                "clientes_inativos.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Gráfico dos clientes com maior volume perdido
            st.subheader("📊 Top 10 Clientes com Maior Volume Perdido")
            top_inativos = df_inativos.head(10)
            fig_inativos = px.bar(
                top_inativos,
                x='Qtd_Anterior',
                y='Cliente',
                orientation='h',
                text='Perda_Formatada',
                title="Top 10 Clientes com Maior Volume Perdido",
                color='Qtd_Anterior',
                color_continuous_scale='Blues'
            )
            fig_inativos.update_traces(textposition='outside')
            st.plotly_chart(fig_inativos, width='stretch')
            
        else:
            st.success("✅ Nenhum cliente inativo identificado!")

    # -------------------------------------------------
    # 13. RESUMO EXECUTIVO DOS ALERTAS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>📋 Resumo Executivo dos Alertas</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Clientes com Subida",
            len(df_subidas),
            delta=f"+{len(df_subidas)}",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Clientes com Descida", 
            len(df_descidas),
            delta=f"-{len(df_descidas)}",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "Clientes Inativos",
            len(df_inativos),
            delta=f"-{len(df_inativos)}",
            delta_color="off"
        )

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#7f8c8d;'>Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)
