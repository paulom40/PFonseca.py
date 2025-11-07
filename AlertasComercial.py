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
    page_title="Dashboard de Vendas - BI",
    page_icon="Chart",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# 2. CSS PERSONALIZADO (com alertas visuais)
# -------------------------------------------------
st.markdown("""
<style>
    .main-header {font-size:2.5rem;color:#1f77b4;text-align:center;margin-bottom:2rem;font-weight:700;}
    .metric-card {background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:1.5rem;border-radius:15px;color:white;box-shadow:0 4px 6px rgba(0,0,0,0.1);}
    .section-header {font-size:1.5rem;color:#2c3e50;margin:2rem 0 1rem 0;padding-bottom:0.5rem;border-bottom:3px solid #3498db;font-weight:600;}
    .alerta-critico {color: #8B0000; font-weight: bold; background-color: #ffe6e6; padding: 2px 6px; border-radius: 4px;}
    .alerta-alto {color: #d32f2f; font-weight: bold;}
    .alerta-moderado {color: #f57c00; font-weight: bold;}
    .seta-baixo {color: red; font-weight: bold;}
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
# 4. CARREGAMENTO DOS DADOS (CORRIGIDO)
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

        # Forçar colunas como string
        colunas_string = ['UN', 'Artigo', 'Cliente', 'Comercial', 'Categoria', 'Mes', 'Ano']
        for col in colunas_string:
            if col in df.columns:
                df[col] = df[col].astype(str).replace({'nan': 'N/D', 'None': 'N/D'})

        # Números
        for col in ['V_Liquido', 'Qtd', 'PM']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
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
# 6. SIDEBAR
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
# 7. FILTROS
# -------------------------------------------------
df_filtrado = df.copy()
if clientes: df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes)]
if artigos: df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(artigos)]
if comerciais: df_filtrado = df_filtrado[df_filtrado['Comercial'].isin(comerciais)]
if categorias: df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias)]
if meses: df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses)]
if anos: df_filtrado = df_filtrado[df_filtrado['Ano'].isin(anos)]

# -------------------------------------------------
# 8. INTERFACE
# -------------------------------------------------
st.markdown("<h1 class='main-header'>Dashboard de Vendas</h1>", unsafe_allow_html=True)

if df.empty:
    st.error("Erro ao carregar dados.")
elif df_filtrado.empty:
    st.warning("Nenhum dado com os filtros.")
else:
    st.success(f"**{len(df_filtrado):,}** registos")

    # -------------------------------------------------
    # 9. MÉTRICAS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Métricas</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Vendas", formatar_numero_pt(df_filtrado['V_Liquido'].sum(), "EUR "))
    with col2: st.metric("Qtd", formatar_numero_pt(df_filtrado['Qtd'].sum()))
    with col3: st.metric("Clientes", f"{df_filtrado['Cliente'].nunique():,}")
    with col4: st.metric("Artigos", f"{df_filtrado['Artigo'].nunique():,}")

    # -------------------------------------------------
    # 10. ALERTAS: TOP 20 CLIENTES EM DESCIDA
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Top 20 Clientes em Descida (Qtd)</div>", unsafe_allow_html=True)

    df_alertas = df_filtrado[['Cliente', 'Mes', 'Ano', 'Qtd']].copy()
    df_alertas['Mes'] = pd.to_numeric(df_alertas['Mes'], errors='coerce').fillna(0).astype(int)
    df_alertas['Ano'] = pd.to_numeric(df_alertas['Ano'], errors='coerce').fillna(0).astype(int)
    df_alertas['AnoMes'] = df_alertas['Ano'] * 100 + df_alertas['Mes']
    df_alertas = df_alertas.groupby(['Cliente', 'AnoMes'])['Qtd'].sum().reset_index()

    if not df_alertas.empty and df_alertas['AnoMes'].nunique() >= 2:
        ultimo_mes = df_alertas['AnoMes'].max()
        penultimo_mes = df_alertas[df_alertas['AnoMes'] < ultimo_mes]['AnoMes'].max()

        atual = df_alertas[df_alertas['AnoMes'] == ultimo_mes][['Cliente', 'Qtd']].rename(columns={'Qtd': 'Qtd_Atual'})
        anterior = df_alertas[df_alertas['AnoMes'] == penultimo_mes][['Cliente', 'Qtd']].rename(columns={'Qtd': 'Qtd_Anterior'})

        comparacao = pd.merge(atual, anterior, on='Cliente', how='inner')
        comparacao['Variacao'] = (comparacao['Qtd_Atual'] - comparacao['Qtd_Anterior']) / comparacao['Qtd_Anterior'] * 100
        descidas = comparacao[comparacao['Variacao'] < 0].copy()
        descidas['Variacao_Abs'] = descidas['Variacao'].abs()
        descidas = descidas.sort_values('Variacao_Abs', ascending=False).head(20)

        if not descidas.empty:
            descidas['Qtd_Atual_Str'] = descidas['Qtd_Atual'].apply(formatar_numero_pt)
            descidas['Qtd_Anterior_Str'] = descidas['Qtd_Anterior'].apply(formatar_numero_pt)
            descidas['Variacao_Str'] = descidas['Variacao'].apply(lambda x: f"{x:+.1f}%")

            # ALERTAS VISUAIS
            def alerta_visual(row):
                var = row['Variacao']
                if var <= -30:
                    return f"<span class='alerta-critico'>Down Arrow {var:+.1f}%</span>"
                elif var <= -10:
                    return f"<span class='alerta-alto'>Down Arrow {var:+.1f}%</span>"
                else:
                    return f"<span class='alerta-moderado'>Down Arrow {var:+.1f}%</span>"

            descidas['Alerta'] = descidas.apply(alerta_visual, axis=1)

            tabela = descidas[['Cliente', 'Qtd_Anterior_Str', 'Qtd_Atual_Str', 'Alerta']].rename(columns={
                'Qtd_Anterior_Str': 'Qtd Anterior',
                'Qtd_Atual_Str': 'Qtd Atual'
            })

            st.markdown(tabela.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.info(f"**{len(descidas)} clientes em descida** | Maior queda: {descidas.iloc[0]['Variacao']:+.1f}%")
        else:
            st.success("Nenhum cliente em descida.")
    else:
        st.info("Dados insuficientes para comparar meses.")

    # -------------------------------------------------
    # 11. COMPARAÇÃO DE MESES
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Comparação de Qtd por Mês</div>", unsafe_allow_html=True)
    df_comp = df_filtrado.copy()
    df_comp['Mes'] = pd.to_numeric(df_comp['Mes'], errors='coerce').fillna(0).astype(int)
    df_comp['Ano'] = pd.to_numeric(df_comp['Ano'], errors='coerce').fillna(0).astype(int)
    df_comp['AnoMes'] = df_comp['Ano'].astype(str) + "-" + df_comp['Mes'].astype(str).str.zfill(2)
    meses_disponiveis = sorted(df_comp['AnoMes'].unique())

    if len(meses_disponiveis) >= 2:
        col1, col2 = st.columns(2)
        with col1: mes_1 = st.selectbox("Mês 1", meses_disponiveis, index=0)
        with col2: mes_2 = st.selectbox("Mês 2", meses_disponiveis, index=1)

        qtd1 = df_comp[df_comp['AnoMes'] == mes_1]['Qtd'].sum()
        qtd2 = df_comp[df_comp['AnoMes'] == mes_2]['Qtd'].sum()
        var = (qtd2 - qtd1) / qtd1 * 100 if qtd1 > 0 else 0

        cor = "green" if var > 10 else "lightgreen" if var > 0 else "red" if var < -10 else "orange" if var < 0 else "gray"
        st.markdown(f"<span style='color:{cor}'>Variação: {var:+.1f}%</span>", unsafe_allow_html=True)

        dados = pd.DataFrame({
            'Mês': [mes_1, mes_2],
            'Qtd': [formatar_numero_pt(qtd1), formatar_numero_pt(qtd2)],
            'Variação': ['', f"{var:+.1f}%"]
        })
        st.table(dados.style.apply(lambda x: ['background: lightyellow' if x.name == 1 else '' for _ in x], axis=1))
    else:
        st.info("Menos de 2 meses.")

    # -------------------------------------------------
    # 12. GRÁFICOS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Visualizações</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        top_c = df_filtrado.groupby('Cliente')['V_Liquido'].sum().nlargest(10)
        if not top_c.empty:
            fig = px.bar(top_c.reset_index(), x='V_Liquido', y='Cliente', orientation='h',
                         text=top_c.map(lambda x: formatar_numero_pt(x, "EUR ")))
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, width='stretch')
    with col2:
        top_a = df_filtrado.groupby('Artigo')['V_Liquido'].sum().nlargest(10)
        if not top_a.empty:
            fig = px.bar(top_a.reset_index(), x='V_Liquido', y='Artigo', orientation='h',
                         text=top_a.map(lambda x: formatar_numero_pt(x, "EUR ")))
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, width='stretch')

    # -------------------------------------------------
    # 13. TABELA FINAL
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Dados Filtrados</div>", unsafe_allow_html=True)
    df_display = df_filtrado.copy()
    for col in df_display.select_dtypes(include=['object']).columns:
        df_display[col] = df_display[col].astype(str)
    st.dataframe(df_display, width='stretch')

# -------------------------------------------------
# 14. FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#7f8c8d;'>Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)
