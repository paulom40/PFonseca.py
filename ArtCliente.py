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
    .seta-subida { color: #2e7d32; font-weight: bold; }
    .seta-descida { color: #d32f2f; font-weight: bold; }
    .seta-neutra { color: #666666; font-weight: bold; }
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
# 9. FUNÇÃO PARA PROCESSAR DATAS (VERSÃO MAIS ROBUSTA)
# -------------------------------------------------
def processar_datas_mes_ano(df):
    """Processa colunas Mes e Ano para criar períodos consistentes - versão mais robusta"""
    df_processed = df.copy()
    
    meses_map = {
        'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05', 'jun': '06',
        'jul': '07', 'ago': '08', 'set': '09', 'out': '10', 'nov': '11', 'dez': '12',
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04', 'maio': '05', 'junho': '06',
        'julho': '07', 'agosto': '08', 'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12',
        'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 'june': '06',
        'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12',
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
        if mes_str in meses_map:
            return meses_map[mes_str]
        for key, value in meses_map.items():
            if key in mes_str:
                return value
        return None
    
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
        elif len(ano_numeros) == 1:
            ano_atual = datetime.now().year
            return str(ano_atual)
        return None
    
    df_processed['Mes_Padronizado'] = df_processed['Mes'].apply(padronizar_mes)
    df_processed['Ano_Padronizado'] = df_processed['Ano'].apply(padronizar_ano)
    
    df_valido = df_processed.dropna(subset=['Mes_Padronizado', 'Ano_Padronizado']).copy()
    
    if not df_valido.empty:
        df_valido['Periodo'] = df_valido['Ano_Padronizado'] + '-' + df_valido['Mes_Padronizado']
        meses_nome = {
            '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', '05': 'Mai', '06': 'Jun',
            '07': 'Jul', '08': 'Ago', '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
        }
        df_valido['Mes_Nome'] = df_valido['Mes_Padronizado'].map(meses_nome)
        df_valido['Periodo_Label'] = df_valido['Mes_Nome'] + ' ' + df_valido['Ano_Padronizado']
        
    return df_valido

# -------------------------------------------------
# 10. FUNÇÃO PARA CRIAR TABELA GERAL DE CLIENTES
# -------------------------------------------------
def criar_tabela_geral_clientes(df):
    """Cria tabela geral com Qtd mensal por cliente e alertas de variação"""
    
    df_processado = processar_datas_mes_ano(df)
    
    if df_processado.empty:
        return pd.DataFrame()
    
    df_agrupado = df_processado.groupby(['Cliente', 'Periodo', 'Periodo_Label']).agg({
        'Qtd': 'sum',
        'V_Liquido': 'sum'
    }).reset_index()
    
    periodos_ordenados = sorted(df_agrupado['Periodo'].unique())
    
    if len(periodos_ordenados) < 2:
        return pd.DataFrame()
    
    periodo_atual = periodos_ordenados[-1]
    periodo_anterior = periodos_ordenados[-2]
    
    df_pivot = df_agrupado.pivot_table(
        index='Cliente',
        columns='Periodo_Label',
        values='Qtd',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    colunas_ordenadas = ['Cliente'] + sorted(df_pivot.columns[1:], reverse=True)
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
                return "🟢 Novo Cliente"
            elif qtd_anterior > 0 and qtd_atual == 0:
                return "🔴 Parou de Comprar"
            elif variacao > 50:
                return "🟢 Subida Forte"
            elif variacao > 20:
                return "🟡 Subida Moderada"
            elif variacao < -50:
                return "🔴 Descida Forte"
            elif variacao < -20:
                return "🟠 Descida Moderada"
            elif variacao > 0:
                return "🔵 Subida Leve"
            elif variacao < 0:
                return "⚫ Descida Leve"
            else:
                return "⚪ Estável"
        
        df_pivot['Alerta'] = df_pivot.apply(
            lambda x: classificar_alerta(x['Variacao_%'], x['Qtd_Anterior'], x['Qtd_Atual']), 
            axis=1
        )
        
        for col in df_pivot.columns:
            if col not in ['Cliente', 'Alerta', 'Variacao_%'] and df_pivot[col].dtype in [np.int64, np.float64]:
                df_pivot[col] = df_pivot[col].apply(lambda x: formatar_numero_pt(x) if pd.notna(x) else '0')
        
        df_pivot['Variacao_Formatada'] = df_pivot['Variacao_%'].apply(
            lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/D"
        )
        
        colunas_finais = ['Cliente', 'Alerta', 'Variacao_Formatada'] + colunas_ordenadas[1:]
        df_final = df_pivot[colunas_finais].rename(columns={'Variacao_Formatada': 'Variação %'})
        
        return df_final
    
    return pd.DataFrame()

# -------------------------------------------------
# 11. NOVA FUNÇÃO: TABELA DE QTD POR ARTIGO, CLIENTE E MÊS
# -------------------------------------------------
def criar_tabela_qtd_artigo_cliente_mes(df):
    """Agrupa os dados por Cliente, Artigo e Mês, somando as quantidades."""
    df_processado = processar_datas_mes_ano(df)
    if df_processado.empty or 'Artigo' not in df_processado.columns:
        return pd.DataFrame()
    
    df_agrupado = df_processado.groupby(['Cliente', 'Artigo', 'Periodo', 'Periodo_Label']).agg({
        'Qtd': 'sum'
    }).reset_index()
    
    df_pivot = df_agrupado.pivot_table(
        index=['Cliente', 'Artigo'],
        columns='Periodo_Label',
        values='Qtd',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    colunas_periodo = sorted(df_pivot.columns[2:], reverse=True)
    df_pivot = df_pivot[['Cliente', 'Artigo'] + colunas_periodo]
    
    return df_pivot

# -------------------------------------------------
# 12. INTERFACE
# -------------------------------------------------
st.markdown("<h1 class='main-header'>Dashboard de Vendas</h1>", unsafe_allow_html=True)

if df.empty:
    st.error("Erro ao carregar dados.")
elif df_filtrado.empty:
    st.warning("Nenhum dado com os filtros.")
else:
    st.success(f"**{len(df_filtrado):,}** registos")

    # -------------------------------------------------
    # 13. MÉTRICAS
    # -------------------------------------------------
    st.markdown("<div class='section-header'>Métricas</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Vendas", formatar_numero_pt(df_filtrado['V_Liquido'].sum(), "EUR "))
    with col2: st.metric("Qtd", formatar_numero_pt(df_filtrado['Qtd'].sum()))
    with col3: st.metric("Clientes", f"{df_filtrado['Cliente'].nunique():,}")
    with col4: st.metric("Artigos", f"{df_filtrado['Artigo'].nunique():,}")

    # -------------------------------------------------
    # 14. TABELA GERAL DE CLIENTES - VISÃO MENSAL
    # -------------------------------------------------
    st.markdown("<div class='section-header'>📊 Tabela Geral de Clientes - Visão Mensal</div>", unsafe_allow_html=True)
    
    df_tabela_geral = criar_tabela_geral_clientes(df_filtrado)
    
    if not df_tabela_geral.empty:
        col1, col2, col3 = st.columns(3)
        
        total_clientes = len(df_tabela_geral)
        clientes_subida = len(df_tabela_geral[df_tabela_geral['Alerta'].str.contains('Subida')])
        clientes_descida = len(df_tabela_geral[df_tabela_geral['Alerta'].str.contains('Descida')])
        clientes_novos = len(df_tabela_geral[df_tabela_geral['Alerta'] == '🟢 Novo Cliente'])
        clientes_inativos = len(df_tabela_geral[df_tabela_geral['Alerta'] == '🔴 Parou de Comprar'])
        
        with col1:
            st.metric("Total Clientes", total_clientes)
        with col2:
            st.metric("Clientes em Subida", clientes_subida)
        with col3:
            st.metric("Clientes em Descida", clientes_descida)
        
        st.subheader("Filtros da Tabela")
        filtro_alerta = st.multiselect(
            "Filtrar por Alerta:",
            options=sorted(df_tabela_geral['Alerta'].unique()),
            default=sorted(df_tabela_geral['Alerta'].unique())
        )
        
        df_filtrado_tabela = df_tabela_geral[df_tabela_geral['Alerta'].isin(filtro_alerta)]
        
        def colorir_linhas(row):
            alerta = row['Alerta']
            if '🔴' in alerta or 'Parou' in alerta:
                return ['background-color: #ffe6e6'] * len(row)
            elif '🟢' in alerta or 'Novo' in alerta:
                return ['background-color: #e8f5e8'] * len(row)
            elif '🟡' in alerta:
                return ['background-color: #fff3e0'] * len(row)
            elif '🟠' in alerta:
                return ['background-color: #fbe9e7'] * len(row)
            else:
                return [''] * len(row)
        
        styled_df = df_filtrado_tabela.style.apply(colorir_linhas, axis=1)
        st.dataframe(styled_df, width='stretch', height=600)
        
        st.download_button(
            "📥 Exportar Tabela Geral",
            to_excel(df_filtrado_tabela),
            "tabela_geral_clientes.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    else:
        st.warning("Não foi possível gerar a tabela geral. Verifique se há dados suficientes para análise.")

    # -------------------------------------------------
    # 15. NOVA SEÇÃO: QUANTIDADE DE ARTIGOS POR CLIENTE MENSALMENTE
    # -------------------------------------------------
    st.markdown("<div class='section-header'>📦 Quantidade de Artigos por Cliente Mensalmente</div>", unsafe_allow_html=True)
    
    df_qtd_artigo = criar_tabela_qtd_artigo_cliente_mes(df_filtrado)
    
    if not df_qtd_artigo.empty:
        clientes_unicos = sorted(df_qtd_artigo['Cliente'].unique())
        cliente_selecionado = st.selectbox("Selecione o Cliente:", ["Todos"] + clientes_unicos, key="cliente_artigo")
        
        if cliente_selecionado != "Todos":
            df_display = df_qtd_artigo[df_qtd_artigo['Cliente'] == cliente_selecionado]
        else:
            df_display = df_qtd_artigo
        
        st.subheader(f"Quantidade de Artigos Vendidos por Mês" if cliente_selecionado == "Todos" else f"Quantidade de Artigos para {cliente_selecionado}")
        st.dataframe(df_display, width='stretch', height=600)
        
        st.download_button(
            "📥 Exportar Detalhes de Artigos",
            to_excel(df_display),
            "detalhes_artigos_clientes.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # -------------------------------------------------
        # 16. GRÁFICO DE TENDÊNCIA POR ARTIGO E CLIENTE
        # -------------------------------------------------
        st.markdown("<div class='section-header'>📈 Tendência de Vendas por Artigo</div>", unsafe_allow_html=True)
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            artigo_selecionado = st.selectbox("Selecione o Artigo:", ["Todos"] + sorted(df_qtd_artigo['Artigo'].unique()), key="artigo_grafico")
        
        with col_g2:
            if cliente_selecionado == "Todos":
                opcoes_cliente_grafico = ["Todos"] + sorted(df_qtd_artigo['Cliente'].unique())
            else:
                opcoes_cliente_grafico = [cliente_selecionado]
            cliente_grafico = st.selectbox("Selecione o Cliente:", opcoes_cliente_grafico, key="cliente_grafico")
        
        df_grafico = df_qtd_artigo.copy()
        if artigo_selecionado != "Todos":
            df_grafico = df_grafico[df_grafico['Artigo'] == artigo_selecionado]
        if cliente_grafico != "Todos":
            df_grafico = df_grafico[df_grafico['Cliente'] == cliente_grafico]
        
        colunas_periodo = [col for col in df_grafico.columns if col not in ['Cliente', 'Artigo']]
        df_melt = df_grafico.melt(id_vars=['Cliente', 'Artigo'], value_vars=colunas_periodo, 
                                  var_name='Mês', value_name='Qtd')
        
        if not df_melt.empty:
            fig = px.line(df_melt, x="Mês", y="Qtd", color='Artigo' if artigo_selecionado == "Todos" else None,
                          title=f"Quantidade Vendida", line_group='Cliente' if cliente_grafico == "Todos" else None,
                          labels={'Qtd': 'Quantidade', 'Mês': 'Mês'}, markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhum dado para o gráfico com os filtros selecionados.")
        
    else:
        st.warning("Nenhum dado disponível para a visualização de artigos por cliente mensalmente.")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#7f8c8d;'>Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)
```

### Principais Correções e Alterações:

1. **Remoção de texto explicativo fora de strings**:  
   O erro `SyntaxError: invalid syntax` ocorria porque havia texto em português (como "**quantidade**") diretamente no arquivo Python, fora de qualquer string ou comentário. Isso foi removido.

2. **Adição da função `criar_tabela_qtd_artigo_cliente_mes`**:
   - Agrupa os dados por `Cliente`, `Artigo` e `Mês`.
   - Cria uma tabela pivotada com a quantidade vendida de cada artigo por cliente em cada mês.

3. **Nova Seção no Dashboard**:
   - **Tabela de Quantidades por Artigo por Cliente**: Permite visualizar e filtrar os dados por cliente.
   - **Botão de Exportação**: Exporta os dados para Excel.
   - **Gráfico Interativo com Plotly**: Mostra a tendência de vendas de um artigo específico por cliente ao longo dos meses.

4. **Melhor organização do código**:
   - As funções e seções estão devidamente comentadas e ordenadas para facilitar a manutenção.

Agora o código está **funcional e pronto para executar no Streamlit**, exibindo a quantidade vendida de artigos por cliente mensalmente, tanto em tabela quanto em gráfico.
