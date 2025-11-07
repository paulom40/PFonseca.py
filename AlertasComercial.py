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
# 4. CARREGAMENTO DOS DADOS
# -------------------------------------------------
@st.cache_data
def load_all_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/VendasGeraisTranf.xlsx"
        df = pd.read_excel(url, thousands=None, decimal=',')
        st.sidebar.success(f"Ficheiro carregado: {len(df)} registos")

        mapeamento = {
            'Código': 'Codigo', 'Cliente': 'Cliente', 'Qtd.': 'Qtd', 'UN': 'UN',
            'PM': 'PM', 'V. Líquido': 'V_Liquido', 'Artigo': 'Artigo',
            'Comercial': 'Comercial', 'Categoria': 'Categoria',
            'Mês': 'Mes', 'Ano': 'Ano'
        }
        mapeamento_final = {k: v for k, v in mapeamento.items() if k in df.columns}
        df = df.rename(columns=mapeamento_final)

        for col in ['V_Liquido', 'Qtd', 'PM']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                st.sidebar.info(f"{col} → numérico")

        for col in ['Artigo', 'Cliente', 'Comercial', 'Categoria', 'Mes', 'Ano', 'UN']:
            if col in df.columns:
                df[col] = df[col].astype(str)
                st.sidebar.info(f"{col} → texto")

        return df

    except Exception as e:
        st.error(f"Erro no carregamento: {str(e)}")
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
            st.warning(f"Coluna '{coluna}' não disponível")
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

# ----- DEBUG (opcional) -----
with st.expander("Informações Técnicas", expanded=False):
    if not df.empty:
        st.write("**Estrutura dos dados:**")
        for col in df.columns:
            st.write(f"- **{col}**: {df[col].dtype} | Únicos: {df[col].nunique():,}")
        st.write("**Totais (sem filtros):**")
        st.write(f"- V_Liquido: {formatar_numero_pt(df['V_Liquido'].sum(), 'EUR ')}")
        st.write(f"- Qtd: {formatar_numero_pt(df['Qtd'].sum())}")

# ----- MENSAGENS -----
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
    # 10. GRÁFICOS
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
    # 11. TABELA DE DADOS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Dados Filtrados</div>", unsafe_allow_html=True)
    df_display = df_filtrado.copy()
    for col in df_display.columns:
        if df_display[col].dtype == 'object':
            df_display[col] = df_display[col].astype(str)
    st.dataframe(df_display, use_container_width=True)

# -------------------------------------------------
# 12. FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#7f8c8d;'>"
    f"Dashboard • {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    f"</div>",
    unsafe_allow_html=True
)
