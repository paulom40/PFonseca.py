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
# 9. FUNÇÃO PARA PROCESSAR DATAS
# -------------------------------------------------
def processar_datas_mes_ano(df):
    """Processa colunas Mes e Ano para criar períodos consistentes"""
    df_processed = df.copy()
    
    # Mapeamento completo de meses
    meses_map = {
        'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05', 'jun': '06',
        'jul': '07', 'ago': '08', 'set': '09', 'out': '10', 'nov': '11', 'dez': '12',
        'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 
        'june': '06', 'july': '07', 'august': '08', 'september': '09', 'october': '10', 
        'november': '11', 'december': '12',
        '1': '01', '2': '02', '3': '03', '4': '04', '5': '05', '6': '06',
        '7': '07', '8': '08', '9': '09', '10': '10', '11': '11', '12': '12'
    }
    
    def padronizar_mes(mes_str):
        if pd.isna(mes_str):
            return None
        mes_str = str(mes_str).lower().strip()
        # Remove pontos e espaços extras
        mes_str = re.sub(r'[.\s]', '', mes_str)
        return meses_map.get(mes_str, None)
    
    def padronizar_ano(ano_str):
        if pd.isna(ano_str):
            return None
        ano_str = str(ano_str).strip()
        # Extrai apenas números
        match = re.search(r'\d{4}', ano_str)
        if match:
            return match.group(0)
        return None
    
    # Aplicar padronização
    df_processed['Mes_Padronizado'] = df_processed['Mes'].apply(padronizar_mes)
    df_processed['Ano_Padronizado'] = df_processed['Ano'].apply(padronizar_ano)
    
    # Filtrar apenas registros com dados válidos
    df_valido = df_processed.dropna(subset=['Mes_Padronizado', 'Ano_Padronizado']).copy()
    
    if not df_valido.empty:
        # Criar período no formato YYYY-MM
        df_valido['Periodo'] = df_valido['Ano_Padronizado'] + '-' + df_valido['Mes_Padronizado']
        
        # Mapear nomes dos meses para exibição
        meses_nome = {
            '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', '05': 'Mai', '06': 'Jun',
            '07': 'Jul', '08': 'Ago', '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
        }
        df_valido['Mes_Nome'] = df_valido['Mes_Padronizado'].map(meses_nome)
        df_valido['Periodo_Label'] = df_valido['Mes_Nome'] + ' ' + df_valido['Ano_Padronizado']
    
    return df_valido

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
    # 12. TOP 20 DESCIDAS (CORRIGIDO)
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Top 20 Clientes em Descida (Qtd)</div>", unsafe_allow_html=True)
    
    # Processar datas para análise de descidas
    df_alertas = processar_datas_mes_ano(df_filtrado[['Cliente', 'Mes', 'Ano', 'Qtd']])
    
    if not df_alertas.empty:
        # Agrupar por cliente e período
        df_agrupado = df_alertas.groupby(['Cliente', 'Periodo'])['Qtd'].sum().reset_index()
        
        # Verificar se temos pelo menos 2 períodos
        periodos_unicos = sorted(df_agrupado['Periodo'].unique())
        
        if len(periodos_unicos) >= 2:
            ultimo_periodo = periodos_unicos[-1]
            penultimo_periodo = periodos_unicos[-2]
            
            # Dados do último período
            dados_atuais = df_agrupado[df_agrupado['Periodo'] == ultimo_periodo][['Cliente', 'Qtd']].rename(columns={'Qtd': 'Qtd_Atual'})
            
            # Dados do penúltimo período
            dados_anteriores = df_agrupado[df_agrupado['Periodo'] == penultimo_periodo][['Cliente', 'Qtd']].rename(columns={'Qtd': 'Qtd_Anterior'})
            
            # Combinar dados
            comparacao = pd.merge(dados_atuais, dados_anteriores, on='Cliente', how='inner')
            
            if not comparacao.empty:
                # Calcular variação
                comparacao['Variacao'] = (comparacao['Qtd_Atual'] - comparacao['Qtd_Anterior']) / comparacao['Qtd_Anterior'] * 100
                
                # Filtrar apenas descidas
                descidas = comparacao[comparacao['Variacao'] < 0].copy()
                descidas['Variacao_Abs'] = descidas['Variacao'].abs()
                descidas = descidas.sort_values('Variacao_Abs', ascending=False).head(20)
                
                if not descidas.empty:
                    # Formatar para exibição
                    descidas['Qtd_Atual_Str'] = descidas['Qtd_Atual'].apply(formatar_numero_pt)
                    descidas['Qtd_Anterior_Str'] = descidas['Qtd_Anterior'].apply(formatar_numero_pt)
                    
                    def classificar_alerta(variacao):
                        if variacao <= -30:
                            return f"<span class='alerta-critico'>▼ {variacao:+.1f}%</span>"
                        elif variacao <= -10:
                            return f"<span class='alerta-alto'>▼ {variacao:+.1f}%</span>"
                        else:
                            return f"<span class='alerta-moderado'>▼ {variacao:+.1f}%</span>"
                    
                    descidas['Alerta'] = descidas['Variacao'].apply(classificar_alerta)
                    
                    # Criar tabela para exibição
                    tabela_descidas = descidas[['Cliente', 'Qtd_Anterior_Str', 'Qtd_Atual_Str', 'Alerta']].rename(columns={
                        'Qtd_Anterior_Str': 'Qtd Anterior', 
                        'Qtd_Atual_Str': 'Qtd Atual'
                    })
                    
                    st.markdown(tabela_descidas.to_html(escape=False, index=False), unsafe_allow_html=True)
                    st.download_button(
                        "Exportar Top 20 Descidas", 
                        to_excel(descidas), 
                        "top20_descidas.xlsx", 
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.success("🎉 Nenhum cliente em descida significativa!")
            else:
                st.info("⚠️ Não há dados suficientes para comparação entre os períodos.")
        else:
            st.info(f"ℹ️ São necessários pelo menos 2 períodos para análise. Períodos encontrados: {len(periodos_unicos)}")
    else:
        st.warning("⚠️ Não foi possível processar os dados de data para análise de descidas.")

    # -------------------------------------------------
    # 13. COMPARAÇÃO DE QTD POR MÊS (CORRIGIDO)
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Comparação de Qtd por Mês</div>", unsafe_allow_html=True)
    
    # Processar dados para comparação
    df_comparacao = processar_datas_mes_ano(df_filtrado)
    
    if not df_comparacao.empty:
        # Obter períodos disponíveis
        periodos_disponiveis = sorted(df_comparacao['Periodo_Label'].unique())
        
        st.write(f"**Períodos disponíveis:** {len(periodos_disponiveis)}")
        
        if len(periodos_disponiveis) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                periodo_1 = st.selectbox(
                    "Selecione o primeiro período:",
                    options=periodos_disponiveis,
                    index=len(periodos_disponiveis)-2,
                    key="periodo_1"
                )
            with col2:
                periodo_2 = st.selectbox(
                    "Selecione o segundo período:",
                    options=periodos_disponiveis,
                    index=len(periodos_disponiveis)-1,
                    key="periodo_2"
                )
            
            if periodo_1 != periodo_2:
                # Obter códigos dos períodos selecionados
                periodo_1_codigo = df_comparacao[df_comparacao['Periodo_Label'] == periodo_1]['Periodo'].iloc[0]
                periodo_2_codigo = df_comparacao[df_comparacao['Periodo_Label'] == periodo_2]['Periodo'].iloc[0]
                
                # Calcular totais
                qtd_periodo_1 = df_comparacao[df_comparacao['Periodo'] == periodo_1_codigo]['Qtd'].sum()
                qtd_periodo_2 = df_comparacao[df_comparacao['Periodo'] == periodo_2_codigo]['Qtd'].sum()
                
                # Calcular variação
                if qtd_periodo_1 > 0:
                    variacao = ((qtd_periodo_2 - qtd_periodo_1) / qtd_periodo_1) * 100
                else:
                    variacao = 0
                
                # Exibir métricas
                col_met1, col_met2, col_met3 = st.columns(3)
                with col_met1:
                    st.metric(f"Qtd {periodo_1}", formatar_numero_pt(qtd_periodo_1))
                with col_met2:
                    st.metric(f"Qtd {periodo_2}", formatar_numero_pt(qtd_periodo_2), f"{variacao:+.1f}%")
                with col_met3:
                    cor = "green" if variacao >= 10 else "lightgreen" if variacao > 0 else "red" if variacao <= -10 else "orange" if variacao < 0 else "gray"
                    st.markdown(f"**Variação:** <span style='color:{cor};font-weight:bold'>{variacao:+.1f}%</span>", unsafe_allow_html=True)
                
                # Criar abas para análise detalhada
                tab1, tab2 = st.tabs([f"🔍 Análise Detalhada", "📊 Dados Comparativos"])
                
                with tab1:
                    st.subheader(f"Comparação Detalhada: {periodo_1} vs {periodo_2}")
                    
                    # Dados do período 1
                    dados_periodo_1 = df_comparacao[df_comparacao['Periodo'] == periodo_1_codigo].groupby('Cliente').agg({
                        'Qtd': 'sum',
                        'V_Liquido': 'sum'
                    }).reset_index()
                    dados_periodo_1 = dados_periodo_1.rename(columns={
                        'Qtd': f'Qtd_{periodo_1}', 
                        'V_Liquido': f'Vendas_{periodo_1}'
                    })
                    
                    # Dados do período 2
                    dados_periodo_2 = df_comparacao[df_comparacao['Periodo'] == periodo_2_codigo].groupby('Cliente').agg({
                        'Qtd': 'sum',
                        'V_Liquido': 'sum'
                    }).reset_index()
                    dados_periodo_2 = dados_periodo_2.rename(columns={
                        'Qtd': f'Qtd_{periodo_2}', 
                        'V_Liquido': f'Vendas_{periodo_2}'
                    })
                    
                    # Combinar dados
                    comparacao_detalhada = pd.merge(dados_periodo_1, dados_periodo_2, on='Cliente', how='outer').fillna(0)
                    
                    # Calcular variações
                    comparacao_detalhada['Var_Qtd_%'] = ((comparacao_detalhada[f'Qtd_{periodo_2}'] - comparacao_detalhada[f'Qtd_{periodo_1}']) / 
                                                        comparacao_detalhada[f'Qtd_{periodo_1}'].replace(0, 1)) * 100
                    comparacao_detalhada['Var_Vendas_%'] = ((comparacao_detalhada[f'Vendas_{periodo_2}'] - comparacao_detalhada[f'Vendas_{periodo_1}']) / 
                                                           comparacao_detalhada[f'Vendas_{periodo_1}'].replace(0, 1)) * 100
                    
                    # Formatar para exibição
                    comparacao_display = comparacao_detalhada.copy()
                    for col in [f'Qtd_{periodo_1}', f'Qtd_{periodo_2}', f'Vendas_{periodo_1}', f'Vendas_{periodo_2}']:
                        if 'Vendas' in col:
                            comparacao_display[col] = comparacao_display[col].apply(lambda x: formatar_numero_pt(x, "EUR "))
                        else:
                            comparacao_display[col] = comparacao_display[col].apply(formatar_numero_pt)
                    
                    comparacao_display['Var_Qtd'] = comparacao_detalhada['Var_Qtd_%'].apply(lambda x: f"{x:+.1f}%")
                    comparacao_display['Var_Vendas'] = comparacao_detalhada['Var_Vendas_%'].apply(lambda x: f"{x:+.1f}%")
                    
                    st.dataframe(comparacao_display, width='stretch')
                    
                with tab2:
                    st.subheader("Visão Consolidada")
                    
                    dados_consolidados = pd.DataFrame({
                        'Período': [periodo_1, periodo_2],
                        'Quantidade': [formatar_numero_pt(qtd_periodo_1), formatar_numero_pt(qtd_periodo_2)],
                        'Vendas': [
                            formatar_numero_pt(df_comparacao[df_comparacao['Periodo'] == periodo_1_codigo]['V_Liquido'].sum(), "EUR "),
                            formatar_numero_pt(df_comparacao[df_comparacao['Periodo'] == periodo_2_codigo]['V_Liquido'].sum(), "EUR ")
                        ],
                        'Variação': ['-', f"{variacao:+.1f}%"]
                    })
                    
                    st.table(dados_consolidados)
                    
                    # Gráfico comparativo
                    fig = px.bar(
                        x=[periodo_1, periodo_2],
                        y=[qtd_periodo_1, qtd_periodo_2],
                        text=[formatar_numero_pt(qtd_periodo_1), formatar_numero_pt(qtd_periodo_2)],
                        title=f"Comparação de Quantidades: {periodo_1} vs {periodo_2}",
                        labels={'x': 'Período', 'y': 'Quantidade'}
                    )
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(fig, width='stretch')
                
                # Botão de exportação
                st.download_button(
                    "📥 Exportar Comparação Completa", 
                    to_excel(comparacao_detalhada), 
                    f"comparacao_{periodo_1}_{periodo_2}.xlsx".replace(" ", "_"),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("⚠️ Selecione períodos diferentes para comparação.")
        else:
            st.info(f"ℹ️ São necessários pelo menos 2 períodos para comparação. Períodos encontrados: {len(periodos_disponiveis)}")
    else:
        st.warning("⚠️ Não foi possível processar os dados para comparação entre períodos.")

    # -------------------------------------------------
    # RESTANTE DO CÓDIGO (gráficos, tabela final, etc.)
    # -------------------------------------------------
    # ... (o restante do código permanece igual)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#7f8c8d;'>Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)
