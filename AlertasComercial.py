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
    .alerta-verde {color: green; font-weight: bold;}
    .alerta-vermelho {color: red; font-weight: bold;}
    .alerta-amarelo {color: orange; font-weight: bold;}
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

        # CORREÇÃO 1: Forçar colunas problemáticas como string
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
        filtros_atuais = {k: v for k, v in locals().items() if k in ["clientes", "artigos", "comerciais", "categorias", "meses", "anos"]}
        salvar_preset(nome_preset, filtros_atuais)
        st.success(f"Configuração '{nome_preset}' salva!")

    st.markdown("---")
    st.markdown("### Estatísticas")
    if not df.empty:
        st.write(f"**Registros:** {len(df):,}")
        st.write(f"**Artigos únicos:** {df['Artigo'].nunique():,}")
        st.write(f"**Clientes únicos:** {df['Cliente'].nunique():,}")
        st.write(f"- V. Líquido: {formatar_numero_pt(df['V_Liquido'].sum(), 'EUR ')}")
        st.write(f"- Qtd: {formatar_numero_pt(df['Qtd'].sum())}")

# -------------------------------------------------
# 7. APLICAÇÃO DOS FILTROS
# -------------------------------------------------
df_filtrado = df.copy()
filtros_aplicados = []

if not df.empty:
    if clientes: df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes)]; filtros_aplicados.append(f"Clientes: {len(clientes)}")
    if artigos: df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(artigos)]; filtros_aplicados.append(f"Artigos: {len(artigos)}")
    if comerciais: df_filtrado = df_filtrado[df_filtrado['Comercial'].isin(comerciais)]; filtros_aplicados.append(f"Comerciais: {len(comerciais)}")
    if categorias: df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias)]; filtros_aplicados.append(f"Categorias: {len(categorias)}")
    if meses: df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses)]; filtros_aplicados.append(f"Meses: {len(meses)}")
    if anos: df_filtrado = df_filtrado[df_filtrado['Ano'].isin(anos)]; filtros_aplicados.append(f"Anos: {len(anos)}")

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
        st.metric("Total Vendas", formatar_numero_pt(total_vendas, "EUR "))

    with col2:
        total_qtd = df_filtrado['Qtd'].sum()
        st.metric("Quantidade", formatar_numero_pt(total_qtd))

    with col3:
        st.metric("Clientes", f"{df_filtrado['Cliente'].nunique():,}")

    with col4:
        st.metric("Artigos", f"{df_filtrado['Artigo'].nunique():,}")

    # -------------------------------------------------
    # 10. ALERTAS MENSAIS (por Cliente)
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Alertas Mensais (por Cliente)</div>", unsafe_allow_html=True)

    df_alertas = df_filtrado[['Cliente', 'Mes', 'Ano', 'Qtd']].copy()
    df_alertas['Mes'] = pd.to_numeric(df_alertas['Mes'], errors='coerce').fillna(0).astype(int)
    df_alertas['Ano'] = pd.to_numeric(df_alertas['Ano'], errors='coerce').fillna(0).astype(int)
    df_alertas['AnoMes'] = df_alertas['Ano'] * 100 + df_alertas['Mes']
    df_alertas = df_alertas.groupby(['Cliente', 'AnoMes'])['Qtd'].sum().reset_index()

    if not df_alertas.empty:
        ultimo_ano_mes = df_alertas['AnoMes'].max()
        mes_atual = ultimo_ano_mes % 100
        alertas_list = []

        for cliente in df_alertas['Cliente'].unique():
            dados = df_alertas[df_alertas['Cliente'] == cliente].sort_values('AnoMes')
            if len(dados) < 2: continue
            qtd_atual = dados.iloc[-1]['Qtd']
            qtd_anterior = dados.iloc[-2]['Qtd']
            variacao = (qtd_atual - qtd_anterior) / qtd_anterior * 100 if qtd_anterior > 0 else 0
            status = "Aumento" if variacao > 0 else ("Descida" if variacao < 0 else "Estável")
            variacao_str = f"{variacao:+.1f}%"

            alertas_list.append({
                'Cliente': cliente,
                'Qtd Atual': formatar_numero_pt(qtd_atual),
                'Variação %': variacao_str,
                'Status': status
            })

        df_tabela_alertas = pd.DataFrame(alertas_list).head(20)
        if not df_tabela_alertas.empty:
            def estilo_alerta(row):
                cor = 'green' if 'Aumento' in row['Status'] else 'red' if 'Descida' in row['Status'] else 'orange'
                return [f'color: {cor}; font-weight: bold' for _ in row]
            st.table(df_tabela_alertas.style.apply(estilo_alerta, axis=1))

    # -------------------------------------------------
    # 11. COMPARAÇÃO DE MESES (Qtd Comprada)
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Comparação de Qtd por Mês</div>", unsafe_allow_html=True)

    df_comp = df_filtrado.copy()
    df_comp['Mes'] = pd.to_numeric(df_comp['Mes'], errors='coerce').fillna(0).astype(int)
    df_comp['Ano'] = pd.to_numeric(df_comp['Ano'], errors='coerce').fillna(0).astype(int)
    df_comp['AnoMes'] = df_comp['Ano'].astype(str) + "-" + df_comp['Mes'].astype(str).str.zfill(2)
    meses_disponiveis = sorted(df_comp['AnoMes'].unique())

    if len(meses_disponiveis) >= 2:
        col1, col2 = st.columns(2)
        with col1:
            mes_1 = st.selectbox("Mês 1", options=meses_disponiveis, index=0)
        with col2:
            mes_2 = st.selectbox("Mês 2", options=meses_disponiveis, index=1)

        qtd_mes1 = df_comp[df_comp['AnoMes'] == mes_1]['Qtd'].sum()
        qtd_mes2 = df_comp[df_comp['AnoMes'] == mes_2]['Qtd'].sum()
        variacao = ((qtd_mes2 - qtd_mes1) / qtd_mes1 * 100) if qtd_mes1 > 0 else 0

        icone = "High Increase" if variacao > 10 else "Moderate Increase" if variacao > 0 else "High Decrease" if variacao < -10 else "Moderate Decrease" if variacao < 0 else "Stable"
        cor = "green" if variacao > 10 else "lightgreen" if variacao > 0 else "red" if variacao < -10 else "orange" if variacao < 0 else "gray"

        st.markdown(f"**{icone}** <span style='color:{cor}'>Variação: {variacao:+.1f}%</span>", unsafe_allow_html=True)
        dados_comp = pd.DataFrame({
            'Mês': [mes_1, mes_2],
            'Qtd': [formatar_numero_pt(qtd_mes1), formatar_numero_pt(qtd_mes2)],
           一个小节: ['', f"{variacao:+.1f}%"]
        })
        st.table(dados_comp.style.apply(lambda x: ['background: lightyellow' if x.name == 1 else '' for _ in x], axis=1))
    else:
        st.info("Menos de 2 meses disponíveis.")

    # -------------------------------------------------
    # 12. GRÁFICOS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Visualizações</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        top_clientes = df_filtrado.groupby('Cliente')['V_Liquido'].sum().nlargest(10)
        if not top_clientes.empty:
            fig = px.bar(top_clientes.reset_index(), x='V_Liquido', y='Cliente', orientation='h',
                         title='Top 10 Clientes', text=top_clientes.map(lambda x: formatar_numero_pt(x, "EUR ")))
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, width='stretch')  # CORRIGIDO

    with col2:
        top_artigos = df_filtrado.groupby('Artigo')['V_Liquido'].sum().nlargest(10)
        if not top_artigos.empty:
            fig = px.bar(top_artigos.reset_index(), x='V_Liquido', y='Artigo', orientation='h',
                         title='Top 10 Artigos', text=top_artigos.map(lambda x: formatar_numero_pt(x, "EUR ")))
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, width='stretch')  # CORRIGIDO

    # -------------------------------------------------
    # 13. TABELA DE DADOS FILTRADOS (CORRIGIDA)
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Dados Filtrados</div>", unsafe_allow_html=True)
    df_display = df_filtrado.copy()
    # CORREÇÃO 2: Forçar todas as colunas object como string
    for col in df_display.select_dtypes(include=['object']).columns:
        df_display[col] = df_display[col].astype(str)
    st.dataframe(df_display, width='stretch')  # CORRIGIDO

# -------------------------------------------------
# 14. FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#7f8c8d;'>Dashboard • {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)
