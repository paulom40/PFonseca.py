import streamlit as st
import pandas as pd
import json
from pathlib import Path
import numpy as np
import plotly.express as px
from datetime import datetime

# -------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# -------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Vendas - Business Intelligence",
    page_icon="Chart",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# 2. CSS PERSONALIZADO
# -------------------------------------------------
st.markdown("""
<style>
    .main-header {font-size:2.5rem;color:#1f77b4;text-align:center;margin-bottom:2rem;font-weight:700;}
    .metric-card {background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:1.5rem;border-radius:15px;color:white;box-shadow:0 4px 6px rgba(0,0,0,0.1);}
    .section-header {font-size:1.5rem;color:#2c3e50;margin:2rem 0 1rem 0;padding-bottom:0.5rem;border-bottom:3px solid #3498db;font-weight:600;}
    .alert-table td {font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 3. FUNÇÃO DE FORMATAÇÃO PT-PT
# -------------------------------------------------
def formatar_numero_pt(valor, simbolo="", sinal_forcado=False):
    if pd.isna(valor):
        return "N/D"
    valor = float(valor)
    sinal = "+" if sinal_forcado and valor >= 0 else ("-" if valor < 0 else "")
    valor_abs = abs(valor)
    if valor_abs == int(valor_abs):
        formato = f"{sinal}{simbolo}{valor_abs:,.0f}".replace(",", " ")
    else:
        formato = f"{sinal}{simbolo}{valor_abs:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return formato

# -------------------------------------------------
# 4. CARREGAMENTO DOS DADOS (sem logs)
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
        mapeamento_final = {k: v for k, v in mapeamento.items() if k in df.columns}
        df = df.rename(columns=mapeamento_final)

        # Conversões silenciosas
        for col in ['V_Liquido', 'Qtd', 'PM']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        for col in ['Artigo', 'Cliente', 'Comercial', 'Categoria', 'Mes', 'Ano', 'UN']:
            if col in df.columns:
                df[col] = df[col].astype(str)

        return df

    except Exception as e:
        st.error(f"Erro no carregamento dos dados.")
        return pd.DataFrame()

df = load_all_data()

# -------------------------------------------------
# 5. PRESETS DE FILTROS
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
# 6. SIDEBAR – CONTROLES
# -------------------------------------------------
with st.sidebar:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("### Painel de Controle")
    st.markdown("</div>", unsafe_allow_html=True)

    presets = carregar_presets()
    preset_selecionado = st.selectbox("Carregar Configuração", [""] + list(presets.keys()))
    filtros = presets.get(preset_selecionado, {}) if preset_selecionado else {}

    st.markdown("---")
    st.markdown("### Filtros")

    def criar_filtro(label, coluna, default=None):
        if coluna not in df.columns or df.empty:
            return []
        opcoes = sorted(df[coluna].dropna().astype(str).unique())
        return st.multiselect(label, opcoes, default=default or [])

    clientes   = criar_filtro("Clientes", "Cliente", filtros.get("Cliente"))
    artigos    = criar_filtro("Artigos", "Artigo", filtros.get("Artigo"))
    comerciais = criar_filtro("Comerciais", "Comercial", filtros.get("Comercial"))
    categorias = criar_filtro("Categorias", "Categoria", filtros.get("Categoria"))
    meses      = criar_filtro("Meses", "Mes", filtros.get("Mes"))
    anos       = criar_filtro("Anos", "Ano", filtros.get("Ano"))

    st.markdown("---")
    st.markdown("### Configurações")
    nome_preset = st.text_input("Nome da configuração")
    if st.button("Salvar Configuração") and nome_preset:
        filtros_atuais = {
            "Cliente": clientes, "Artigo": artigos, "Comercial": comerciais,
            "Categoria": categorias, "Mes": meses, "Ano": anos
        }
        salvar_preset(nome_preset, filtros_atuais)
        st.success(f"Configuração '{nome_preset}' salva!")

    st.markdown("---")
    st.markdown("### Estatísticas")
    if not df.empty:
        st.write(f"**Registros:** {len(df):,}")
        if 'Artigo' in df.columns:
            st.write(f"**Artigos únicos:** {df['Artigo'].nunique():,}")
        if 'Cliente' in df.columns:
            st.write(f"**Clientes únicos:** {df['Cliente'].nunique():,}")

        if 'V_Liquido' in df.columns and 'Qtd' in df.columns:
            st.write("**Totais do ficheiro:**")
            st.write(f"- V. Líquido: {formatar_numero_pt(df['V_Liquido'].sum(), 'EUR ')}")
            st.write(f"- Qtd: {formatar_numero_pt(df['Qtd'].sum())}")

# -------------------------------------------------
# 7. APLICAÇÃO DOS FILTROS
# -------------------------------------------------
df_filtrado = df.copy()
filtros_aplicados = []

if not df.empty:
    if clientes:
        df_filtrado = df_filtrado[df_filtrado['Cliente'].astype(str).isin(clientes)]
        filtros_aplicados.append(f"Clientes: {len(clientes)}")
    if artigos:
        df_filtrado = df_filtrado[df_filtrado['Artigo'].astype(str).isin(artigos)]
        filtros_aplicados.append(f"Artigos: {len(artigos)}")
    if comerciais:
        df_filtrado = df_filtrado[df_filtrado['Comercial'].astype(str).isin(comerciais)]
        filtros_aplicados.append(f"Comerciais: {len(comerciais)}")
    if categorias:
        df_filtrado = df_filtrado[df_filtrado['Categoria'].astype(str).isin(categorias)]
        filtros_aplicados.append(f"Categorias: {len(categorias)}")
    if meses:
        df_filtrado = df_filtrado[df_filtrado['Mes'].astype(str).isin(meses)]
        filtros_aplicados.append(f"Meses: {len(meses)}")
    if anos:
        df_filtrado = df_filtrado[df_filtrado['Ano'].astype(str).isin(anos)]
        filtros_aplicados.append(f"Anos: {len(anos)}")

# -------------------------------------------------
# 8. INTERFACE PRINCIPAL
# -------------------------------------------------
st.markdown("<h1 class='main-header'>Dashboard de Vendas</h1>", unsafe_allow_html=True)

if df.empty:
    st.error("Não foi possível carregar os dados.")
elif df_filtrado.empty:
    st.warning("Nenhum dado encontrado com os filtros aplicados.")
else:
    st.success(f"**{len(df_filtrado):,}** registos encontrados")
    if filtros_aplicados:
        st.info("**Filtros aplicados:** " + " | ".join(filtros_aplicados))

    # -------------------------------------------------
    # 9. MÉTRICAS PRINCIPAIS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Métricas Principais</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_vendas = df_filtrado['V_Liquido'].sum()
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Total Vendas", formatar_numero_pt(total_vendas, "EUR "))
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        total_qtd = df_filtrado['Qtd'].sum()
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Quantidade", formatar_numero_pt(total_qtd))
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        clientes_unicos = df_filtrado['Cliente'].nunique()
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Clientes", f"{clientes_unicos:,}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        artigos_unicos = df_filtrado['Artigo'].nunique()
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Artigos", f"{artigos_unicos:,}")
        st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # 10. ALERTAS MENSAIS (por Cliente)
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Alertas Mensais (por Cliente)</div>", unsafe_allow_html=True)

    df_alertas = df_filtrado[['Cliente', 'Mes', 'Ano', 'Qtd']].copy()
    df_alertas['Mes'] = df_alertas['Mes'].astype(int)
    df_alertas['Ano'] = df_alertas['Ano'].astype(int)
    df_alertas['AnoMes'] = df_alertas['Ano'] * 100 + df_alertas['Mes']
    df_alertas = df_alertas.groupby(['Cliente', 'AnoMes'])['Qtd'].sum().reset_index()
    df_alertas = df_alertas.sort_values(['Cliente', 'AnoMes'])

    ultimo_ano_mes = df_alertas['AnoMes'].max()
    mes_atual = ultimo_ano_mes % 100
    ano_atual = ultimo_ano_mes // 100

    alertas_list = []
    for cliente in df_alertas['Cliente'].unique():
        dados = df_alertas[df_alertas['Cliente'] == cliente].sort_values('AnoMes')
        if dados.empty:
            continue

        qtd_atual = dados.iloc[-1]['Qtd']
        mes_cliente = dados.iloc[-1]['AnoMes'] % 100

        if len(dados) >= 2:
            qtd_anterior = dados.iloc[-2]['Qtd']
            variacao = (qtd_atual - qtd_anterior) / qtd_anterior * 100 if qtd_anterior > 0 else 0
            status = "Aumento" if variacao > 0 else ("Descida" if variacao < 0 else "Estável")
            variacao_str = f"{variacao:+.1f}%"
        else:
            status = "Novo Cliente"
            variacao_str = "N/A"

        comprou_atual = "Sim" if mes_cliente == mes_atual else "Não"
        tempo_sem = "Atual" if mes_cliente == mes_atual else f"{mes_atual - mes_cliente} meses"

        alertas_list.append({
            'Cliente': cliente,
            'Qtd Atual': formatar_numero_pt(qtd_atual),
            'Variação %': variacao_str,
            'Status': status,
            'Comprou Atual?': comprou_atual,
            'Tempo sem Compra': tempo_sem
        })

    df_tabela_alertas = pd.DataFrame(alertas_list)
    if not df_tabela_alertas.empty:
        df_tabela_alertas['Qtd_Num'] = df_tabela_alertas['Qtd Atual'].str.replace(' ', '').str.replace(',', '.').astype(float)
        df_tabela_alertas = df_tabela_alertas.sort_values('Qtd_Num', ascending=False).drop('Qtd_Num', axis=1).head(20)
        st.table(df_tabela_alertas.style.apply(lambda x: ['color: green' if 'Aumento' in v else 'color: red' if 'Descida' in v else '' for v in x], subset=['Status']))

        descidas = len(df_tabela_alertas[df_tabela_alertas['Status'] == 'Descida'])
        st.info(f"Resumo: {len(df_tabela_alertas)} clientes monitorizados | {descidas} em descida")
    else:
        st.warning("Nenhum cliente com histórico suficiente para alertas.")

    # -------------------------------------------------
    # 11. COMPARAÇÃO 2024 vs 2025 (mesmos meses)
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Comparação 2024 vs 2025 (mesmos meses)</div>", unsafe_allow_html=True)

    df_comp = df_filtrado.copy()
    df_comp['Mes'] = df_comp['Mes'].astype(int)
    df_comp['Ano'] = df_comp['Ano'].astype(int)
    df_comp = df_comp.groupby(['Ano', 'Mes']).agg({
        'Qtd': 'sum',
        'V_Liquido': 'sum'
    }).reset_index()

    # Pivot para 2024 e 2025
    df_2024 = df_comp[df_comp['Ano'] == 2024][['Mes', 'Qtd', 'V_Liquido']].rename(columns={'Qtd': 'Qtd_2024', 'V_Liquido': 'V_Liquido_2024'})
    df_2025 = df_comp[df_comp['Ano'] == 2025][['Mes', 'Qtd', 'V_Liquido']].rename(columns={'Qtd': 'Qtd_2025', 'V_Liquido': 'V_Liquido_2025'})

    df_comparacao = pd.merge(df_2024, df_2025, on='Mes', how='inner')
    df_comparacao['Var_Qtd_%'] = ((df_comparacao['Qtd_2025'] - df_comparacao['Qtd_2024']) / df_comparacao['Qtd_2024'] * 100).round(1)
    df_comparacao['Var_VL_%'] = ((df_comparacao['V_Liquido_2025'] - df_comparacao['V_Liquido_2024']) / df_comparacao['V_Liquido_2024'] * 100).round(1)

    # Nome do mês
    meses_nome = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
                  7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
    df_comparacao['Mês'] = df_comparacao['Mes'].map(meses_nome)

    df_comparacao = df_comparacao[['Mês', 'Qtd_2024', 'Qtd_2025', 'Var_Qtd_%', 'V_Liquido_2024', 'V_Liquido_2025', 'Var_VL_%']]
    df_comparacao = df_comparacao.sort_values('Mes')

    # Formatação
    df_display_comp = df_comparacao.copy()
    df_display_comp['Qtd_2024'] = df_display_comp['Qtd_2024'].apply(lambda x: formatar_numero_pt(x))
    df_display_comp['Qtd_2025'] = df_display_comp['Qtd_2025'].apply(lambda x: formatar_numero_pt(x))
    df_display_comp['V_Liquido_2024'] = df_display_comp['V_Liquido_2024'].apply(lambda x: formatar_numero_pt(x, 'EUR '))
    df_display_comp['V_Liquido_2025'] = df_display_comp['V_Liquido_2025'].apply(lambda x: formatar_numero_pt(x, 'EUR '))
    df_display_comp['Var_Qtd_%'] = df_display_comp['Var_Qtd_%'].apply(lambda x: f"{x:+.1f}%")
    df_display_comp['Var_VL_%'] = df_display_comp['Var_VL_%'].apply(lambda x: f"{x:+.1f}%")

    if not df_display_comp.empty:
        st.table(df_display_comp)
    else:
        st.info("Nenhum mês comum entre 2024 e 2025 nos dados filtrados.")

    # -------------------------------------------------
    # 12. GRÁFICOS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Visualizações</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if 'V_Liquido' in df_filtrado.columns and 'Cliente' in df_filtrado.columns:
            top_clientes = df_filtrado.groupby('Cliente')['V_Liquido'].sum().nlargest(10)
            if not top_clientes.empty:
                fig = px.bar(
                    top_clientes.reset_index(),
                    x='V_Liquido', y='Cliente',
                    orientation='h',
                    title='Top 10 Clientes',
                    labels={'V_Liquido': 'Vendas (EUR)', 'Cliente': ''},
                    text=top_clientes.map(lambda x: formatar_numero_pt(x, "EUR "))
                )
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        if 'V_Liquido' in df_filtrado.columns and 'Artigo' in df_filtrado.columns:
            top_artigos = df_filtrado.groupby('Artigo')['V_Liquido'].sum().nlargest(10)
            if not top_artigos.empty:
                fig = px.bar(
                    top_artigos.reset_index(),
                    x='V_Liquido', y='Artigo',
                    orientation='h',
                    title='Top 10 Artigos',
                    labels={'V_Liquido': 'Vendas (EUR)', 'Artigo': ''},
                    text=top_artigos.map(lambda x: formatar_numero_pt(x, "EUR "))
                )
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # 13. TABELA DE DADOS FILTRADOS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Dados Filtrados</div>", unsafe_allow_html=True)
    df_display = df_filtrado.copy()
    for col in df_display.columns:
        if df_display[col].dtype == 'object':
            df_display[col] = df_display[col].astype(str)
    st.dataframe(df_display, use_container_width=True)

# -------------------------------------------------
# 14. FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#7f8c8d;'>"
    f"Dashboard • {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    f"</div>",
    unsafe_allow_html=True
)
