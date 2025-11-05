import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import requests
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Business Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="Business Intelligence"
)

# --- MODERN COLOR SCHEME ---
primary_color = "#6366f1"    # Indigo
secondary_color = "#10b981"  # Emerald
accent_color = "#f59e0b"     # Amber
warning_color = "#ef4444"    # Red
success_color = "#22c55e"    # Green
info_color = "#3b82f6"       # Blue

# --- CLEAN WHITE STYLING ---
st.markdown(f"""
    <style>
    .main {{
        background: #ffffff;
        color: #1e293b;
    }}
    .stApp {{ background: #ffffff; }}
    h1 {{
        color: {primary_color};
        font-weight: 800;
        font-size: 2.8em;
        margin-bottom: 20px;
        font-family: 'Inter', sans-serif;
        border-bottom: 3px solid {primary_color};
        padding-bottom: 10px;
    }}
    h2 {{
        color: #1e293b;
        font-weight: 700;
        font-size: 2em;
        margin-top: 30px;
        margin-bottom: 20px;
        font-family: 'Inter', sans-serif;
    }}
    h3 {{
        color: #475569;
        font-weight: 600;
        font-size: 1.4em;
        font-family: 'Inter', sans-serif;
    }}
    [data-testid="metric-container"] {{
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }}
    [data-testid="metric-container"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        border-color: {primary_color};
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {primary_color} 0%, #4f46e5 100%);
        border-right: none;
    }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] div,
    .stSelectbox [data-baseweb="select"] input,
    .stSelectbox [data-baseweb="select"] span {{
        background-color: white !important;
        color: #1e293b !important;
    }}
    .stRadio [role="radiogroup"] {{
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }}
    .stRadio [role="radiogroup"] label {{
        color: white !important;
        background: transparent !important;
        padding: 10px 15px !important;
        margin: 5px 0 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        border: 1px solid transparent !important;
    }}
    .stRadio [role="radiogroup"] label:hover {{
        background: rgba(255, 255, 255, 0.2) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }}
    .stRadio [role="radiogroup"] label:has(input:checked) {{
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
        font-weight: 600 !important;
    }}
    .stDownloadButton button {{
        background: linear-gradient(135deg, {primary_color}, {secondary_color});
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 12px 25px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }}
    .stDownloadButton button:hover {{
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }}
    [data-testid="metric-value"] {{
        font-size: 2em !important;
        font-weight: 800 !important;
        color: #1e293b !important;
    }}
    [data-testid="metric-label"] {{
        font-size: 1.1em !important;
        font-weight: 600 !important;
        color: {primary_color} !important;
    }}
    hr {{
        border: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 30px 0;
    }}
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: #f1f5f9; }}
    ::-webkit-scrollbar-thumb {{ background: {primary_color}; border-radius: 3px; }}
    .streamlit-expanderHeader {{
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        font-weight: 600;
    }}
    .dataframe {{ border-radius: 10px; border: 1px solid #e2e8f0; }}
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
month_names_to_number = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
    'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6,
    'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
}

@st.cache_data(ttl=3600)
def carregar_dados():
    try:
        url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Vendas_Globais.xlsx"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            st.error(f"Erro ao carregar dados: Status {response.status_code}")
            return pd.DataFrame()

        df = pd.read_excel(BytesIO(response.content))

        # Padronizar colunas
        col_mappings = {
            'Mês': 'mes', 'mes': 'mes', 'MÊS': 'mes',
            'Qtd.': 'qtd', 'Qtd': 'qtd', 'qtd': 'qtd', 'QTD': 'qtd', 'Quantidade': 'qtd',
            'Ano': 'ano', 'ano': 'ano', 'ANO': 'ano',
            'Cliente': 'cliente', 'cliente': 'cliente', 'CLIENTE': 'cliente',
            'Comercial': 'comercial', 'comercial': 'comercial', 'COMERCIAL': 'comercial',
            'V. Líquido': 'v_liquido', 'V_Liquido': 'v_liquido', 'V Liquido': 'v_liquido',
            'V. LÍQUIDO': 'v_liquido', 'PM': 'pm', 'Preço Médio': 'pm',
            'Categoria': 'categoria', 'categoria': 'categoria', 'CATEGORIA': 'categoria'
        }
        df = df.rename(columns=col_mappings)

        # Verificar colunas críticas
        critical_cols = ['mes', 'qtd', 'ano', 'cliente', 'comercial']
        missing_cols = [col for col in critical_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Colunas em falta: {missing_cols}")
            return pd.DataFrame()

        # Converter mês
        if df['mes'].dtype == 'object':
            df['mes'] = df['mes'].apply(lambda x: month_names_to_number.get(str(x).strip().lower(), np.nan))
        df['mes'] = pd.to_numeric(df['mes'], errors='coerce')

        # Converter numéricos
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        df['qtd'] = pd.to_numeric(df['qtd'], errors='coerce')

        # Tratar V. Líquido (europeu)
        if 'v_liquido' in df.columns:
            df['v_liquido'] = df['v_liquido'].astype(str).str.strip()
            df['v_liquido'] = df['v_liquido'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df['v_liquido'] = pd.to_numeric(df['v_liquido'], errors='coerce')

        # Limpeza final
        df = df.dropna(subset=critical_cols)
        df = df[(df['mes'] >= 1) & (df['mes'] <= 12)]
        return df

    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

df = carregar_dados()
if df.empty:
    st.error("Não foi possível carregar os dados. Verifique a conexão e o URL.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 30px 0;">
        <div style="font-size: 2.5em; margin-bottom: 10px;">Chart</div>
        <h1 style="color: white; margin: 0; font-size: 1.8em; font-weight: 700;">Business Intelligence</h1>
        <p style="color: rgba(255, 255, 255, 0.8); margin: 5px 0 0 0; font-size: 0.9em;">Dashboard Analítico</p>
    </div>
""", unsafe_allow_html=True)
st.sidebar.markdown("<div style='height: 2px; background: rgba(255,255,255,0.3); margin: 20px 0;'></div>", unsafe_allow_html=True)

# Navegação
st.sidebar.markdown('<div class="navigation-radio">', unsafe_allow_html=True)
pagina = st.sidebar.radio(
    "**NAVEGAÇÃO**",
    [
        "VISÃO GERAL",
        "KPIS PERSONALIZADOS",
        "TENDÊNCIAS",
        "ALERTAS",
        "ANÁLISE DE CLIENTES",
        "VISTA COMPARATIVA"
    ],
    key="navigation"
)
st.sidebar.markdown('</div>', unsafe_allow_html=True)
st.sidebar.markdown("<div style='height: 2px; background: rgba(255,255,255,0.3); margin: 20px 0;'></div>", unsafe_allow_html=True)

# Filtros
st.sidebar.markdown("### FILTROS")
st.sidebar.markdown("<p style='color: rgba(255,255,255,0.7); font-size: 0.9em;'>Selecione os filtros desejados</p>", unsafe_allow_html=True)

def get_filtro_opcoes(dados, ano, comercial, cliente):
    temp = dados.copy()
    if ano != "Todos": temp = temp[temp['ano'] == int(ano)]
    if comercial != "Todos": temp = temp[temp['comercial'].astype(str).str.strip() == str(comercial).strip()]
    if cliente != "Todos": temp = temp[temp['cliente'].astype(str).str.strip() == str(cliente).strip()]
    anos = sorted([int(x) for x in temp['ano'].dropna().unique()])
    comerciais = sorted(temp['comercial'].dropna().unique().tolist())
    clientes = sorted(temp['cliente'].dropna().unique().tolist())
    categorias = sorted(temp['categoria'].dropna().unique().tolist()) if 'categoria' in temp.columns else []
    return anos, comerciais, clientes, categorias

def aplicar_filtros(dados, ano, comercial, cliente, categoria):
    res = dados.copy()
    if ano != "Todos": res = res[res['ano'] == int(ano)]
    if comercial != "Todos": res = res[res['comercial'].astype(str).str.strip() == str(comercial).strip()]
    if cliente != "Todos": res = res[res['cliente'].astype(str).str.strip() == str(cliente).strip()]
    if categoria != "Todas" and 'categoria' in res.columns:
        res = res[res['categoria'].astype(str).str.strip() == str(categoria).strip()]
    return res

anos_disponiveis, _, _, _ = get_filtro_opcoes(df, "Todos", "Todos", "Todos")
ano = st.sidebar.selectbox("**ANO**", ["Todos"] + anos_disponiveis, key="ano_select")

_, comerciais_for_year, _, _ = get_filtro_opcoes(df, ano, "Todos", "Todos")
comercial = st.sidebar.selectbox("**COMERCIAL**", ["Todos"] + comerciais_for_year, key="comercial_select")

_, _, clientes_for_filters, _ = get_filtro_opcoes(df, ano, comercial, "Todos")
cliente = st.sidebar.selectbox("**CLIENTE**", ["Todos"] + clientes_for_filters, key="cliente_select")

_, _, _, categorias_for_filters = get_filtro_opcoes(df, ano, comercial, cliente)
categoria = st.sidebar.selectbox("**CATEGORIA**", ["Todas"] + categorias_for_filters, key="categoria_select")

dados_filtrados = aplicar_filtros(df, ano, comercial, cliente, categoria)

# Exportar
def gerar_excel(dados):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dados.to_excel(writer, index=False, sheet_name='Dados')
    return output.getvalue()

# Formatação
def formatar_euros(valor):
    if pd.isna(valor) or valor == 0: return "€ 0"
    return f"€ {valor:,.2f}"

def formatar_euros_simples(valor):
    if pd.isna(valor) or valor == 0: return "€ 0"
    return f"€ {valor:,.0f}" if valor >= 1000 else f"€ {valor:,.2f}"

def formatar_kg(valor):
    if pd.isna(valor) or valor == 0: return "0 kg"
    return f"{valor:,.0f} kg" if valor >= 1000 else f"{valor:,.2f} kg"

month_names_pt = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
                  7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}

# --- PÁGINAS ---
if pagina == "VISÃO GERAL":
    st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <h1>DASHBOARD ANALÍTICO</h1>
            <p style="font-size: 1.2em; color: #64748b; font-weight: 500;">Visão Geral de Performance Comercial</p>
        </div>
    """, unsafe_allow_html=True)

    # Métricas principais
    total_qty = dados_filtrados['qtd'].sum()
    total_value = dados_filtrados['v_liquido'].sum() if 'v_liquido' in dados_filtrados.columns else 0
    num_customers = dados_filtrados['cliente'].nunique()
    num_commercials = dados_filtrados['comercial'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("QUANTIDADE TOTAL (KG)", formatar_kg(total_qty))
    with col2:
        st.metric("VALOR TOTAL (€)", formatar_euros(total_value))
    with col3:
        st.metric("Nº CLIENTES", f"{num_customers}")
    with col4:
        st.metric("Nº COMERCIAIS", f"{num_commercials}")

    st.markdown("---")

    # Top 10 Clientes
    st.markdown("### TOP 10 CLIENTES (QUANTIDADE EM KG)")
    top_qtd = dados_filtrados.groupby('cliente')[['qtd', 'v_liquido']].sum().sort_values('qtd', ascending=False).head(10)
    fig_qtd = px.bar(top_qtd.reset_index(), x='cliente', y='qtd', color='v_liquido',
                     labels={'qtd': 'Quantidade (kg)', 'cliente': 'Cliente'},
                     color_continuous_scale='Viridis', text='qtd')
    fig_qtd.update_traces(texttemplate='%{text:,.0f} kg', textposition='outside')
    fig_qtd.update_layout(plot_bgcolor='white', paper_bgcolor='white', xaxis_tickangle=-45, showlegend=False, height=500)
    st.plotly_chart(fig_qtd, use_container_width=True)

    st.markdown("### TOP 10 CLIENTES (VALOR EM €)")
    top_valor = dados_filtrados.groupby('cliente')[['v_liquido']].sum().sort_values('v_liquido', ascending=False).head(10)
    fig_valor = px.bar(top_valor.reset_index(), x='cliente', y='v_liquido', color='v_liquido',
                       labels={'v_liquido': 'Valor (€)'}, color_continuous_scale='Plasma', text='v_liquido')
    fig_valor.update_traces(texttemplate='€ %{text:,.0f}', textposition='outside')
    fig_valor.update_layout(plot_bgcolor='white', paper_bgcolor='white', xaxis_tickangle=-45, showlegend=False, height=500)
    st.plotly_chart(fig_valor, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### PERFORMANCE COMERCIAL")
        kpi_com = dados_filtrados.groupby('comercial')['v_liquido'].sum().sort_values(ascending=False).head(8)
        fig_com = px.bar(kpi_com.reset_index(), x='comercial', y='v_liquido', color='v_liquido',
                         color_continuous_scale='Blues', text='v_liquido')
        fig_com.update_traces(texttemplate='€ %{text:,.0f}', textposition='outside')
        fig_com.update_layout(plot_bgcolor='white', paper_bgcolor='white', showlegend=False, height=400)
        st.plotly_chart(fig_com, use_container_width=True)

    with col2:
        if 'categoria' in dados_filtrados.columns and not dados_filtrados['categoria'].isna().all():
            st.markdown("### PERFORMANCE POR CATEGORIA")
            kpi_cat = dados_filtrados.groupby('categoria')['v_liquido'].sum().sort_values(ascending=False).head(6)
            fig_cat = px.pie(kpi_cat.reset_index(), values='v_liquido', names='categoria',
                             color_discrete_sequence=px.colors.qualitative.Bold)
            fig_cat.update_traces(texttemplate='%{label}<br>€ %{value:,.0f}', textposition='inside')
            fig_cat.update_layout(plot_bgcolor='white', paper_bgcolor='white', legend=dict(x=1.1))
            st.plotly_chart(fig_cat, use_container_width=True)

    if st.button("Exportar Dados Filtrados"):
        st.download_button("Baixar Excel", gerar_excel(dados_filtrados), "vendas_filtradas.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Outras páginas podem ser expandidas conforme necessário
elif pagina == "KPIS PERSONALIZADOS":
    st.info("KPIs personalizados em desenvolvimento...")
elif pagina == "TENDÊNCIAS":
    st.info("Análise de tendências em desenvolvimento...")
elif pagina == "ALERTAS":
    st.info("Alertas em desenvolvimento...")
elif pagina == "ANÁLISE DE CLIENTES":
    st.info("Análise detalhada de clientes em desenvolvimento...")
elif pagina == "VISTA COMPARATIVA":
    st.info("Comparação entre períodos em desenvolvimento...")
