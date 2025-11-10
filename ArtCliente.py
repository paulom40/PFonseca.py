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

# Tabela Geral de Clientes
def criar_tabela_geral_clientes(df):
    df_processado = processar_datas_mes_ano(df)
    if df_processado.empty:
        return pd.DataFrame()

    df_agrupado = df_processado.groupby(['Cliente', 'Periodo_Label', 'Periodo_Date']).agg({
        'Qtd': 'sum', 'V_Liquido': 'sum'
    }).reset_index()

    periodos_ordenados = df_agrupado['Periodo_Date'].drop_duplicates().sort_values(ascending=False)
    if len(periodos_ordenados) < 2:
        return pd.DataFrame()

    df_pivot = df_agrupado.pivot_table(
        index='Cliente', columns='Periodo_Label', values='Qtd', aggfunc='sum', fill_value=0
    ).reset_index()

    colunas_ordenadas = ['Cliente'] + [col for col in df_pivot.columns[1:] 
                                      if col in df_agrupado['Periodo_Label'].values]
    colunas_ordenadas = ['Cliente'] + sorted(
        colunas_ordenadas[1:],
        key=lambda x: df_agrupado[df_agrupado['Periodo_Label'] == x]['Periodo_Date'].iloc[0],
        reverse=True
    )
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

        for col in df_pivot.columns:
            if col not in ['Cliente', 'Alerta', 'Variacao_%'] and df_pivot[col].dtype in [np.int64, np.float64]:
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

    # Tabela Geral de Clientes
    st.markdown("<div class='section-header'>Tabela Geral de Clientes - Visão Mensal</div>", unsafe_allow_html=True)
    df_tabela_geral = criar_tabela_geral_clientes(df_filtrado)

    if not df_tabela_geral.empty:
        col1, col2, col3 = st.columns(3)
        total_clientes = len(df_tabela_geral)
        clientes_subida = len(df_tabela_geral[df_tabela_geral['Alerta'].str.contains('Subida|Novo')])
        clientes_descida = len(df_tabela_geral[df_tabela_geral['Alerta'].str.contains('Descida|Parou')])

        with col1: st.metric("Total Clientes", total_clientes)
        with col2: st.metric("Clientes em Subida", clientes_subida)
        with col3: st.metric("Clientes em Descida", clientes_descida)

        st.subheader("Filtros da Tabela")
        filtro_alerta = st.multiselect(
            "Filtrar por Alerta:",
            options=sorted(df_tabela_geral['Alerta'].unique()),
            default=sorted(df_tabela_geral['Alerta'].unique())
        )
        df_filtrado_tabela = df_tabela_geral[df_tabela_geral['Alerta'].isin(filtro_alerta)]

        def colorir_linhas(row):
            alerta = row['Alerta']
            if 'Parou' in alerta or 'Descida Forte' in alerta:
                return ['background-color: #ffe6e6'] * len(row)
            elif 'Novo' in alerta or 'Subida Forte' in alerta:
                return ['background-color: #e8f5e8'] * len(row)
            elif 'Subida Moderada' in alerta:
                return ['background-color: #fff3e0'] * len(row)
            elif 'Descida Moderada' in alerta:
                return ['background-color: #fbe9e7'] * len(row)
            else:
                return [''] * len(row)

        styled_df = df_filtrado_tabela.style.apply(colorir_linhas, axis=1)
        st.dataframe(styled_df, width="stretch", height=600)

        st.download_button(
            "Exportar Tabela Geral",
            to_excel(df_filtrado_tabela),
            "tabela_geral_clientes.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Não foi possível gerar a tabela geral (poucos períodos).")

    # Quantidade por Artigo/Cliente/Mês
    st.markdown("<div class='section-header'>Quantidade de Artigos por Cliente Mensalmente</div>", unsafe_allow_html=True)
    df_qtd_artigo = criar_tabela_qtd_artigo_cliente_mes(df_filtrado)

    if not df_qtd_artigo.empty:
        clientes_unicos = sorted(df_qtd_artigo['Cliente'].unique())
        cliente_selecionado = st.selectbox("Selecione o Cliente:", ["Todos"] + clientes_unicos, key="cliente_artigo")

        df_display = df_qtd_artigo if cliente_selecionado == "Todos" else df_qtd_artigo[df_qtd_artigo['Cliente'] == cliente_selecionado]
        st.dataframe(df_display, width="stretch", height=600)

        st.download_button(
            "Exportar Detalhes de Artigos",
            to_excel(df_display),
            "detalhes_artigos_clientes.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Gráfico de Tendência
        st.markdown("<div class='section-header'>Tendência de Vendas por Artigo</div>", unsafe_allow_html=True)
        artigos_unicos = sorted(df_qtd_artigo['Artigo'].unique())
        artigos_selecionados = st.multiselect("Selecione o(s) Artigo(s):", artigos_unicos, default=[], key="artigos_grafico")

        opcoes_cliente_grafico = ["Todos"] + clientes_unicos if cliente_selecionado == "Todos" else [cliente_selecionado]
        cliente_grafico = st.selectbox("Cliente no Gráfico:", opcoes_cliente_grafico, key="cliente_grafico")

        df_grafico = df_qtd_artigo.copy()
        if artigos_selecionados:
            df_grafico = df_grafico[df_grafico['Artigo'].isin(artigos_selecionados)]
        if cliente_grafico != "Todos":
            df_grafico = df_grafico[df_grafico['Cliente'] == cliente_grafico]

        colunas_periodo = [col for col in df_grafico.columns if col not in ['Cliente', 'Artigo']]

        if df_grafico.empty or len(colunas_periodo) == 0:
            st.warning("Sem dados suficientes para o gráfico.")
        else:
            # RECRIAR df_processado localmente
            df_processado = processar_datas_mes_ano(df_filtrado)
            if df_processado.empty:
                st.warning("Erro ao processar datas para o gráfico.")
            else:
                df_melt = pd.melt(
                    df_grafico,
                    id_vars=['Cliente', 'Artigo'],
                    value_vars=colunas_periodo,
                    var_name='Periodo_Label',
                    value_name='Qtd'
                )
                df_melt = df_melt.merge(
                    df_processado[['Periodo_Label', 'Periodo_Date']].drop_duplicates(),
                    on='Periodo_Label',
                    how='left'
                )
                df_melt = df_melt.dropna(subset=['Periodo_Date']).sort_values('Periodo_Date')

                color_param = 'Artigo' if len(artigos_selecionados) > 0 else None
                title = f"Quantidade Vendida - {', '.join(artigos_selecionados)}" if artigos_selecionados else "Quantidade Vendida"
                line_group_param = 'Cliente' if cliente_grafico == "Todos" and len(df_grafico['Cliente'].unique()) > 1 else None

                fig = px.line(
                    df_melt,
                    x="Periodo_Label",
                    y="Qtd",
                    color=color_param,
                    line_group=line_group_param,
                    title=title,
                    labels={'Qtd': 'Quantidade', 'Periodo_Label': 'Mês'},
                    markers=True
                )
                st.plotly_chart(fig, width="stretch")
    else:
        st.warning("Nenhum dado disponível para artigos por cliente mensalmente.")

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#7f8c8d;'>Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)
