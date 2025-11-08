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
    page_icon="Chart",
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
# 9. INTERFACE
# -------------------------------------------------
st.markdown("<h1 class='main-header'>Dashboard de Vendas</h1>", unsafe_allow_html=True)

if df.empty:
    st.error("Erro ao carregar dados.")
elif df_filtrado.empty:
    st.warning("Nenhum dado com os filtros.")
else:
    st.success(f"**{len(df_filtrado):,}** registos")

    # -------------------------------------------------
    # 10. MÉTRICAS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Métricas</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Vendas", formatar_numero_pt(df_filtrado['V_Liquido'].sum(), "EUR "))
    with col2: st.metric("Qtd", formatar_numero_pt(df_filtrado['Qtd'].sum()))
    with col3: st.metric("Clientes", f"{df_filtrado['Cliente'].nunique():,}")
    with col4: st.metric("Artigos", f"{df_filtrado['Artigo'].nunique():,}")

    # -------------------------------------------------
    # 11. TOP 20 DESCIDAS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Top 20 Clientes em Descida (Qtd)</div>", unsafe_allow_html=True)
    df_alertas = df_filtrado[['Cliente', 'Mes', 'Ano', 'Qtd']].copy()
    df_alertas['Mes_Raw'] = df_alertas['Mes'].astype(str).str.strip().str.lower()
    df_alertas['Ano_Raw'] = df_alertas['Ano'].astype(str).str.strip()

    meses_map = {
        'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05', 'jun': '06',
        'jul': '07', 'ago': '08', 'set': '09', 'out': '10', 'nov': '11', 'dez': '12',
        'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 'june': '06',
        'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }

    def padronizar_mes(m):
        m = str(m).lower().strip()
        if m in meses_map: return meses_map[m]
        if m.isdigit() and 1 <= int(m) <= 12: return f"{int(m):02d}"
        return None

    def extrair_ano(a):
        a = str(a).strip()
        match = re.search(r'\d{4}', a)
        return match.group(0) if match else None

    df_alertas['Mes_Pad'] = df_alertas['Mes_Raw'].apply(padronizar_mes)
    df_alertas['Ano_Pad'] = df_alertas['Ano_Raw'].apply(extrair_ano)
    df_alertas = df_alertas.dropna(subset=['Mes_Pad', 'Ano_Pad'])
    df_alertas['AnoMes'] = df_alertas['Ano_Pad'] + df_alertas['Mes_Pad']
    df_alertas = df_alertas.groupby(['Cliente', 'AnoMes'])['Qtd'].sum().reset_index()

    if df_alertas['AnoMes'].nunique() >= 2:
        ultimo = df_alertas['AnoMes'].max()
        penultimo = df_alertas[df_alertas['AnoMes'] < ultimo]['AnoMes'].max()
        atual = df_alertas[df_alertas['AnoMes'] == ultimo][['Cliente', 'Qtd']].rename(columns={'Qtd': 'Qtd_Atual'})
        anterior = df_alertas[df_alertas['AnoMes'] == penultimo][['Cliente', 'Qtd']].rename(columns={'Qtd': 'Qtd_Anterior'})
        comp = pd.merge(atual, anterior, on='Cliente')
        comp['Variacao'] = (comp['Qtd_Atual'] - comp['Qtd_Anterior']) / comp['Qtd_Anterior'] * 100
        descidas = comp[comp['Variacao'] < 0].copy()
        descidas['Variacao_Abs'] = descidas['Variacao'].abs()
        descidas = descidas.sort_values('Variacao_Abs', ascending=False).head(20)

        if not descidas.empty:
            descidas['Qtd_Atual_Str'] = descidas['Qtd_Atual'].apply(formatar_numero_pt)
            descidas['Qtd_Anterior_Str'] = descidas['Qtd_Anterior'].apply(formatar_numero_pt)
            def alerta(row):
                v = row['Variacao']
                if v <= -30: return f"<span class='alerta-critico'>Down Arrow {v:+.1f}%</span>"
                elif v <= -10: return f"<span class='alerta-alto'>Down Arrow {v:+.1f}%</span>"
                else: return f"<span class='alerta-moderado'>Down Arrow {v:+.1f}%</span>"
            descidas['Alerta'] = descidas.apply(alerta, axis=1)
            tabela = descidas[['Cliente', 'Qtd_Anterior_Str', 'Qtd_Atual_Str', 'Alerta']].rename(columns={
                'Qtd_Anterior_Str': 'Qtd Anterior', 'Qtd_Atual_Str': 'Qtd Atual'
            })
            st.markdown(tabela.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.download_button("Exportar Top 20", to_excel(tabela), "top20_descidas.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.success("Nenhum cliente em descida.")
    else:
        st.info("Dados insuficientes.")

    # -------------------------------------------------
    # 12. COMPARAÇÃO DE QTD POR MÊS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Comparação de Qtd por Mês</div>", unsafe_allow_html=True)
    df_comp = df.copy()
    if clientes: df_comp = df_comp[df_comp['Cliente'].isin(clientes)]
    if artigos: df_comp = df_comp[df_comp['Artigo'].isin(artigos)]
    if comerciais: df_comp = df_comp[df_comp['Comercial'].isin(comerciais)]
    if categorias: df_comp = df_comp[df_comp['Categoria'].isin(categorias)]

    df_comp['Mes_Raw'] = df_comp['Mes'].astype(str).str.strip().str.lower()
    df_comp['Ano_Raw'] = df_comp['Ano'].astype(str).str.strip()
    df_comp['Mes_Pad'] = df_comp['Mes_Raw'].apply(padronizar_mes)
    df_comp['Ano_Pad'] = df_comp['Ano_Raw'].apply(extrair_ano)
    df_valido = df_comp.dropna(subset=['Mes_Pad', 'Ano_Pad', 'Qtd']).copy()
    df_valido['AnoMes'] = df_valido['Ano_Pad'] + "-" + df_valido['Mes_Pad']

    if df_valido.empty:
        st.warning("Nenhum mês válido encontrado.")
    else:
        meses_nome = {'01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', '05': 'Mai', '06': 'Jun',
                      '07': 'Jul', '08': 'Ago', '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'}
        df_valido['Mes_Nome'] = df_valido['Mes_Pad'].map(meses_nome)
        df_valido['Label'] = df_valido['Mes_Nome'] + " " + df_valido['Ano_Pad']
        meses_disponiveis = sorted(df_valido['Label'].unique())

        if len(meses_disponiveis) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                mes_label_1 = st.selectbox("Mês 1", options=meses_disponiveis, index=0, key="comp_mes1")
            with col2:
                mes_label_2 = st.selectbox("Mês 2", options=meses_disponiveis, index=1, key="comp_mes2")

            mes_1 = df_valido[df_valido['Label'] == mes_label_1]['AnoMes'].iloc[0]
            mes_2 = df_valido[df_valido['Label'] == mes_label_2]['AnoMes'].iloc[0]
            qtd1 = df_valido[df_valido['AnoMes'] == mes_1]['Qtd'].sum()
            qtd2 = df_valido[df_valido['AnoMes'] == mes_2]['Qtd'].sum()
            var = (qtd2 - qtd1) / qtd1 * 100 if qtd1 > 0 else 0
            cor = "green" if var >= 10 else "lightgreen" if var > 0 else "red" if var <= -10 else "orange" if var < 0 else "gray"
            st.markdown(f"<span style='color:{cor};font-weight:bold'>Variação: {var:+.1f}%</span>", unsafe_allow_html=True)

            dados_comp = pd.DataFrame({
                'Mês': [mes_label_1, mes_label_2],
                'Qtd': [formatar_numero_pt(qtd1), formatar_numero_pt(qtd2)],
                'Variação': ['', f"{var:+.1f}%"]
            })
            st.table(dados_comp.style.apply(lambda x: ['background: lightyellow' if x.name == 1 else '' for _ in x], axis=1))
            st.download_button("Exportar Comparação", to_excel(dados_comp), "comparacao_meses.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info(f"Apenas {len(meses_disponiveis)} mês disponível.")

    # -------------------------------------------------
    # 13. COMPARAÇÃO DE VENDAS POR ANO (CORRIGIDA)
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Comparação de Vendas por Ano</div>", unsafe_allow_html=True)
    df_ano = df.copy()
    if clientes: df_ano = df_ano[df_ano['Cliente'].isin(clientes)]
    if artigos: df_ano = df_ano[df_ano['Artigo'].isin(artigos)]
    if comerciais: df_ano = df_ano[df_ano['Comercial'].isin(comerciais)]
    if categorias: df_ano = df_ano[df_ano['Categoria'].isin(categorias)]

    df_ano['Ano_Str'] = df_ano['Ano'].astype(str).str.strip()
    df_ano = df_ano[df_ano['Ano_Str'].str.match(r'^\d{4}$')]

    if df_ano.empty:
        st.warning("Nenhum ano válido encontrado.")
    else:
        df_resumo = df_ano.groupby('Ano_Str').agg({
            'V_Liquido': 'sum',
            'Qtd': 'sum'
        }).reset_index()
        df_resumo = df_resumo.sort_values('Ano_Str')
        df_resumo['Vendas_Str'] = df_resumo['V_Liquido'].apply(lambda x: formatar_numero_pt(x, "EUR "))
        df_resumo['Qtd_Str'] = df_resumo['Qtd'].apply(formatar_numero_pt)
        df_resumo['Var_Vendas_%'] = df_resumo['V_Liquido'].pct_change() * 100
        df_resumo['Var_Vendas_Str'] = df_resumo['Var_Vendas_%'].apply(
            lambda x: f"{x:+.1f}%" if pd.notna(x) else ""
        )

        tabela_ano = df_resumo[['Ano_Str', 'Qtd_Str', 'Vendas_Str', 'Var_Vendas_Str']].rename(columns={
            'Ano_Str': 'Ano', 'Qtd_Str': 'Qtd', 'Vendas_Str': 'Vendas', 'Var_Vendas_Str': 'Variação %'
        })

        # ESTILO SEGURO
        def highlight_variacao(val):
            try:
                if pd.isna(val) or val == "":
                    return ""
                num = float(val.replace('%', '').replace('+', '').replace('−', '-'))
                if num > 0:
                    return "background-color: lightgreen"
                elif num < 0:
                    return "background-color: lightcoral"
            except:
                pass
            return ""

        styled_table = tabela_ano.style.applymap(
            highlight_variacao,
            subset=['Variação %']
        )

        st.table(styled_table)

        # Gráfico
        fig = px.bar(df_resumo, x='Ano_Str', y='V_Liquido',
                     text='Vendas_Str', title="Vendas por Ano (EUR)")
        fig.update_traces(textposition='outside')
        fig.update_layout(yaxis_visible=False, yaxis_showticklabels=False)
        st.plotly_chart(fig, use_container_width=True)

        # Exportação
        st.download_button(
            "Exportar Vendas por Ano",
            to_excel(tabela_ano),
            "vendas_por_ano.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # -------------------------------------------------
    # 14. GRÁFICOS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Visualizações</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        top_c = df_filtrado.groupby('Cliente')['V_Liquido'].sum().nlargest(10)
        if not top_c.empty:
            fig = px.bar(top_c.reset_index(), x='V_Liquido', y='Cliente', orientation='h',
                         text=top_c.map(lambda x: formatar_numero_pt(x, "EUR ")))
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        top_a = df_filtrado.groupby('Artigo')['V_Liquido'].sum().nlargest(10)
        if not top_a.empty:
            fig = px.bar(top_a.reset_index(), x='V_Liquido', y='Artigo', orientation='h',
                         text=top_a.map(lambda x: formatar_numero_pt(x, "EUR ")))
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # 15. TABELA FINAL
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Dados Filtrados</div>", unsafe_allow_html=True)
    df_display = df_filtrado.copy()
    for col in df_display.select_dtypes(include=['object']).columns:
        df_display[col] = df_display[col].astype(str)
    st.dataframe(df_display, use_container_width=True)
    st.download_button("Exportar Todos os Dados", to_excel(df_display), "dados_completos.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# -------------------------------------------------
# 16. FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#7f8c8d;'>Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)
