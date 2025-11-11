import streamlit as st
import pandas as pd
import json
from pathlib import Path
import numpy as np
import plotly.express as px
from datetime import datetime
from io import BytesIO
import re

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas - BI",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS + Logo
st.markdown("""
<style>
    .main-header {font-size:2.5rem;color:#1f77b4;text-align:center;margin-bottom:2rem;font-weight:700;}
    .metric-card {background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:1.5rem;border-radius:15px;color:white;box-shadow:0 4px 6px rgba(0,0,0,0.1);}
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

# Logo
st.markdown(f"""
<div class="logo-container">
    <img src="https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png" alt="Bracar Logo">
</div>
""", unsafe_allow_html=True)

# Formatação PT-PT
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

# Exportação para Excel
def to_excel(df, sheet_name="Dados"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

# Carregamento dos dados (aba "Dados" do GitHub)
@st.cache_data
def load_all_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/VendasGeraisTranf.xlsx"
        df = pd.read_excel(url, sheet_name="Dados", thousands=None, decimal=',')
        
        # Mapeamento de colunas (dict correto)
        mapeamento = {
            'Código': 'Codigo',
            'Cliente': 'Cliente',
            'Qtd.': 'Qtd',
            'UN': 'UN',
            'PM': 'PM',
            'V. Líquido': 'V_Liquido',
            'Artigo': 'Artigo',
            'Comercial': 'Comercial',
            'Categoria': 'Categoria',
            'Mês': 'Mes',
            'Ano': 'Ano'
        }
        df = df.rename(columns={k: v for k, v in mapeamento.items() if k in df.columns})
        
        # Tratamento de strings
        colunas_string = ['UN', 'Artigo', 'Cliente', 'Comercial', 'Categoria', 'Mes', 'Ano']
        for col in colunas_string:
            if col in df.columns:
                df[col] = df[col].astype(str).replace({'nan': 'N/D', 'None': 'N/D', '<NA>': 'N/D'})
        
        # Conversão numérica
        for col in ['V_Liquido', 'Qtd', 'PM']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a aba 'Dados': {e}")
        return pd.DataFrame()

df = load_all_data()

# Presets
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

# Sidebar
with st.sidebar:
    st.markdown("<div class='metric-card'>Painel de Controle</div>", unsafe_allow_html=True)
    presets = carregar_presets()
    preset_selecionado = st.selectbox("Configuração", [""] + list(presets.keys()))
    filtros = presets.get(preset_selecionado, {}) if preset_selecionado else {}
    st.markdown("---")
    st.markdown("### Filtros")
    
    def criar_filtro(label, coluna, default=None):
        if coluna not in df.columns or df.empty: 
            return []
        opcoes = sorted(df[coluna].dropna().astype(str).unique())
        return st.multiselect(label, opcoes, default=default or [])
    
    clientes = criar_filtro("Clientes", "Cliente", filtros.get("Cliente"))
    artigos = criar_filtro("Artigos", "Artigo", filtros.get("Artigo"))
    comerciais = criar_filtro("Comerciais", "Comercial", filtros.get("Comercial"))
    categorias = criar_filtro("Categorias", "Categoria", filtros.get("Categoria"))
    meses = criar_filtro("Meses", "Mes", filtros.get("Mes"))
    anos = criar_filtro("Anos", "Ano", filtros.get("Ano"))
    
    st.markdown("---")
    nome_preset = st.text_input("Nome da configuração")
    if st.button("Salvar") and nome_preset:
        salvar_preset(nome_preset, {
            "Cliente": clientes, "Artigo": artigos, "Comercial": comerciais,
            "Categoria": categorias, "Mes": meses, "Ano": anos
        })
        st.success(f"Salvo: {nome_preset}")

# Aplicar filtros
df_filtrado = df.copy()
if clientes: df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes)]
if artigos: df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(artigos)]
if comerciais: df_filtrado = df_filtrado[df_filtrado['Comercial'].isin(comerciais)]
if categorias: df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias)]
if meses: df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses)]
if anos: df_filtrado = df_filtrado[df_filtrado['Ano'].isin(anos)]

# Processar datas com Periodo_Date
def processar_datas_mes_ano(df):
    df_processed = df.copy()
    meses_map = {
        'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05', 'jun': '06',
        'jul': '07', 'ago': '08', 'set': '09', 'out': '10', 'nov': '11', 'dez': '12',
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04', 'maio': '05', 'junho': '06',
        'julho': '07', 'agosto': '08', 'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12',
        '1': '01', '2': '02', '3': '03', '4': '04', '5': '05', '6': '06',
        '7': '07', '8': '08', '9': '09', '10': '10', '11': '11', '12': '12',
        '01': '01', '02': '02', '03': '03', '04': '04', '05': '05', '06': '06',
        '07': '07', '08': '08', '09': '09', '10': '10', '11': '11', '12': '12'
    }

    def padronizar_mes(mes_str):
        if pd.isna(mes_str) or str(mes_str).strip() in ['nan', 'None', 'NULL', '', ' ']:
            return None
        mes_str = re.sub(r'[^a-z0-9]', '', str(mes_str).lower())
        return next((v for k, v in meses_map.items() if k in mes_str), None)

    def padronizar_ano(ano_str):
        if pd.isna(ano_str) or str(ano_str).strip() in ['nan', 'None', 'NULL', '', ' ']:
            return None
        ano_numeros = re.sub(r'[^\d]', '', str(ano_str))
        if len(ano_numeros) == 4:
            return ano_numeros
        elif len(ano_numeros) == 2:
            ano = int(ano_numeros)
            return f"20{ano:02d}" if ano < 50 else f"19{ano:02d}"
        return str(datetime.now().year)

    df_processed['Mes_Padronizado'] = df_processed['Mes'].apply(padronizar_mes)
    df_processed['Ano_Padronizado'] = df_processed['Ano'].apply(padronizar_ano)
    df_valido = df_processed.dropna(subset=['Mes_Padronizado', 'Ano_Padronizado']).copy()

    if not df_valido.empty:
        df_valido['Periodo'] = df_valido['Ano_Padronizado'] + '-' + df_valido['Mes_Padronizado']
        df_valido['Periodo_Date'] = pd.to_datetime(df_valido['Periodo'], format='%Y-%m')
        meses_nome = {'01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', '05': 'Mai', '06': 'Jun',
                      '07': 'Jul', '08': 'Ago', '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'}
        df_valido['Mes_Nome'] = df_valido['Mes_Padronizado'].map(meses_nome)
        df_valido['Periodo_Label'] = df_valido['Mes_Nome'] + ' ' + df_valido['Ano_Padronizado']
    return df_valido

# Tabela Geral de Clientes (ORDENADA POR DATA)
def criar_tabela_geral_clientes(df):
    df_processado = processar_datas_mes_ano(df)
    if df_processado.empty:
        return pd.DataFrame()

    df_agrupado = df_processado.groupby(['Cliente', 'Periodo_Label', 'Periodo_Date']).agg({
        'Qtd': 'sum', 'V_Liquido': 'sum'
    }).reset_index()

    # Ordenar períodos por data (mais recente à esquerda)
    periodos_ordenados = df_agrupado['Periodo_Date'].drop_duplicates().sort_values(ascending=False)
    if len(periodos_ordenados) < 2:
        return pd.DataFrame()

    # Pivot com colunas em ordem cronológica reversa
    df_pivot = df_agrupado.pivot_table(
        index='Cliente',
        columns='Periodo_Label',
        values='Qtd',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    # Mapear Periodo_Label → Periodo_Date
    label_to_date = dict(zip(df_agrupado['Periodo_Label'], df_agrupado['Periodo_Date']))
    colunas_existentes = [col for col in df_pivot.columns if col in label_to_date]
    
    # Ordenar colunas por data (mais recente primeiro)
    colunas_ordenadas = ['Cliente'] + sorted(
        colunas_existentes[1:],
        key=lambda x: label_to_date[x],
        reverse=True
    )
    df_pivot = df_pivot[colunas_ordenadas]

    # Cálculo de variação
    if len(df_pivot.columns) >= 3:
        coluna_atual = df_pivot.columns[1]
        coluna_anterior = df_pivot.columns[2]
        df_pivot['Qtd_Atual'] = df_pivot[coluna_atual]
        df_pivot['Qtd_Anterior'] = df_pivot[coluna_anterior]
        df_pivot['Variacao_%'] = ((df_pivot['Qtd_Atual'] - df_pivot['Qtd_Anterior']) /
                                 df_pivot['Qtd_Anterior'].replace(0, 1)) * 100

        def classificar_alerta(variacao, qtd_anterior, qtd_atual):
            if qtd_anterior == 0 and qtd_atual > 0:
                return "Novo Cliente"
            elif qtd_anterior > 0 and qtd_atual == 0:
                return "Parou de Comprar"
            elif variacao > 50:
                return "Subida Forte"
            elif variacao > 20:
                return "Subida Moderada"
            elif variacao < -50:
                return "Descida Forte"
            elif variacao < -20:
                return "Descida Moderada"
            elif variacao > 0:
                return "Subida Leve"
            elif variacao < 0:
                return "Descida Leve"
            else:
                return "Estável"

        df_pivot['Alerta'] = df_pivot.apply(
            lambda x: classificar_alerta(x['Variacao_%'], x['Qtd_Anterior'], x['Qtd_Atual']), axis=1
        )

        # Formatação PT-PT
        for col in df_pivot.columns:
            if col not in ['Cliente', 'Alerta', 'Variacao_%', 'Qtd_Atual', 'Qtd_Anterior'] and df_pivot[col].dtype in [np.int64, np.float64]:
                df_pivot[col] = df_pivot[col].apply(lambda x: formatar_numero_pt(x) if pd.notna(x) else '0')

        df_pivot['Variação %'] = df_pivot['Variacao_%'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/D")
        colunas_finais = ['Cliente', 'Alerta', 'Variação %'] + colunas_ordenadas[1:]
        return df_pivot[colunas_finais]

    return pd.DataFrame()

# Tabela Qtd por Artigo/Cliente/Mês
def criar_tabela_qtd_artigo_cliente_mes(df):
    df_processado = processar_datas_mes_ano(df)
    if df_processado.empty or 'Artigo' not in df_processado.columns:
        return pd.DataFrame()

    df_agrupado = df_processado.groupby(['Cliente', 'Artigo', 'Periodo_Label', 'Periodo_Date']).agg({'Qtd': 'sum'}).reset_index()
    df_pivot = df_agrupado.pivot_table(
        index=['Cliente', 'Artigo'], columns='Periodo_Label', values='Qtd', aggfunc='sum', fill_value=0
    ).reset_index()

    colunas_periodo = sorted(
        [col for col in df_pivot.columns if col not in ['Cliente', 'Artigo']],
        key=lambda x: df_agrupado[df_agrupado['Periodo_Label'] == x]['Periodo_Date'].iloc[0],
        reverse=True
    )
    return df_pivot[['Cliente', 'Artigo'] + colunas_periodo]

# Interface Principal
st.markdown("<h1 class='main-header'>Dashboard de Vendas</h1>", unsafe_allow_html=True)

if df.empty:
    st.error("Erro ao carregar a aba 'Dados' do GitHub.")
elif df_filtrado.empty:
    st.warning("Nenhum dado com os filtros aplicados.")
else:
    st.success(f"**{len(df_filtrado):,}** registos carregados")

    # Métricas
    st.markdown("<div class='section-header'>Métricas Gerais</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Vendas Totais", formatar_numero_pt(df_filtrado['V_Liquido'].sum(), "EUR "))
    with col2: st.metric("Quantidade Total", formatar_numero_pt(df_filtrado['Qtd'].sum()))
    with col3: st.metric("Clientes Únicos", f"{df_filtrado['Cliente'].nunique():,}")
    with col4: st.metric("Artigos Únicos", f"{df_filtrado['Artigo'].nunique():,}")

    # TABELA GERAL DE CLIENTES - VARIAÇÃO MENSAL CONSECUTIVA
def criar_tabela_geral_clientes(df):
    df_processado = processar_datas_mes_ano(df)
    if df_processado.empty:
        return pd.DataFrame()

    # Agrupar por Cliente e Período
    df_agrupado = df_processado.groupby(['Cliente', 'Periodo_Label', 'Periodo_Date']).agg({
        'Qtd': 'sum'
    }).reset_index()

    # Ordenar períodos cronologicamente (antigo → recente)
    periodos_ordenados = df_agrupado['Periodo_Date'].drop_duplicates().sort_values(ascending=True)
    if len(periodos_ordenados) < 2:
        return pd.DataFrame()

    # Pivot: Cliente x Mês
    df_pivot = df_agrupado.pivot_table(
        index='Cliente',
        columns='Periodo_Label',
        values='Qtd',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    # Mapear Label → Date
    label_to_date = dict(zip(df_agrupado['Periodo_Label'], df_agrupado['Periodo_Date']))
    colunas_mes = [col for col in df_pivot.columns if col in label_to_date]

    # Ordenar colunas por data (antigo → recente)
    colunas_mes = sorted(colunas_mes, key=lambda x: label_to_date[x])

    # Reordenar pivot: mais antigo à esquerda → mais recente à direita
    df_pivot = df_pivot[['Cliente'] + colunas_mes]

    # === CALCULAR VARIAÇÃO ENTRE MESES CONSECUTIVOS ===
    variacao_cols = []
    for i in range(1, len(colunas_mes)):
        mes_atual = colunas_mes[i]
        mes_anterior = colunas_mes[i-1]
        col_variacao = f"Var.% {mes_atual}"
        df_pivot[col_variacao] = ((df_pivot[mes_atual] - df_pivot[mes_anterior]) /
                                  df_pivot[mes_anterior].replace(0, 1)) * 100
        variacao_cols.append(col_variacao)

    # === ALERTA BASEADO NA ÚLTIMA VARIAÇÃO ===
    ultima_variacao = variacao_cols[-1] if variacao_cols else None
    if ultima_variacao:
        df_pivot['Variacao_%'] = df_pivot[ultima_variacao]

        def classificar_alerta(variacao, qtd_anterior, qtd_atual):
            if qtd_anterior == 0 and qtd_atual > 0:
                return "Novo Cliente"
            elif qtd_anterior > 0 and qtd_atual == 0:
                return "Parou de Comprar"
            elif variacao > 50:
                return "Subida Forte"
            elif variacao > 20:
                return "Subida Moderada"
            elif variacao < -50:
                return "Descida Forte"
            elif variacao < -20:
                return "Descida Moderada"
            elif variacao > 0:
                return "Subida Leve"
            elif variacao < 0:
                return "Descida Leve"
            else:
                return "Estável"

        df_pivot['Alerta'] = df_pivot.apply(
            lambda x: classificar_alerta(
                x['Variacao_%'],
                x[colunas_mes[-2]] if len(colunas_mes) > 1 else 0,
                x[colunas_mes[-1]]
            ), axis=1
        )
    else:
        df_pivot['Alerta'] = "Estável"
        df_pivot['Variacao_%'] = 0

    # === FORMATAR COLUNAS ===
    # Meses: formato PT-PT
    for col in colunas_mes:
        df_pivot[col] = df_pivot[col].apply(lambda x: formatar_numero_pt(x) if pd.notna(x) else '0')

    # Variações: +XX.X%
    for col in variacao_cols:
        df_pivot[col] = df_pivot[col].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/D")

    # === COLUNAS FINAIS (mais recente à esquerda) ===
    colunas_mes_invertidas = colunas_mes[::-1]
    variacao_invertidas = [f"Var.% {m}" for m in colunas_mes_invertidas]

    colunas_finais = (
        ['Cliente', 'Alerta'] +
        [item for pair in zip(variacao_invertidas, colunas_mes_invertidas) for item in pair]
    )
    # Remover excesso se houver menos variações
    colunas_finais = [c for c in colunas_finais if c in df_pivot.columns]

    return df_pivot[colunas_finais]

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#7f8c8d;'>Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)
