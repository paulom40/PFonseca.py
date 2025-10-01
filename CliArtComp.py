import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import numpy as np
import re

# Custom CSS for modern, colorful UI
custom_css = """
<style>
:root {
    --primary: #4F46E5; /* Indigo */
    --secondary: #EC4899; /* Pink */
    --accent: #FBBF24; /* Amber */
    --success: #10B981; /* Green */
    --error: #EF4444; /* Red */
    --bg: #F9FAFB; /* Light gray */
    --text: #1F2937; /* Dark gray */
    --card-bg: #FFFFFF;
}

@media (prefers-color-scheme: dark) {
    :root {
        --bg: #111827;
        --card-bg: #1F2937;
        --text: #F9FAFB;
    }
}

body {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

.stApp {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

h1 {
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.stButton > button {
    background: linear-gradient(90deg, var(--primary), --secondary);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    transition: transform 0.2s;
}

.stButton > button:hover {
    transform: scale(1.05);
}

.stDataFrame, .stMetric {
    background: var(--card-bg);
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    padding: 1rem;
    margin-bottom: 1rem;
}

.alert-success {
    background: var(--success);
    color: white;
    padding: 0.75rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}

.alert-error {
    background: var(--error);
    color: white;
    padding: 0.75rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Meses em português
meses_pt = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def obter_numero_mes(nome_mes):
    if not isinstance(nome_mes, str):
        return nome_mes if isinstance(nome_mes, (int, float)) and 1 <= nome_mes <= 12 else None
    nome_mes = nome_mes.strip().lower()
    for k, v in meses_pt.items():
        if nome_mes == v.lower() or nome_mes.startswith(v.lower()[:3]):
            return k
    try:
        # Try converting string to number if it's numeric
        num = float(nome_mes)
        if 1 <= num <= 12:
            return int(num)
    except ValueError:
        pass
    return None

def validar_colunas(df):
    colunas_esperadas = {
        'Cliente': ['cliente', 'cliente nome', 'nome cliente'],
        'Qtd.': ['qtd.', 'quantidade', 'qtd', 'qtde'],
        'Artigo': ['artigo', 'produto', 'item', 'artigo vendido'],
        'Mês': ['mês', 'mes', 'mês de venda', 'month'],
        'Ano': ['ano', 'year'],
        'Categoria': ['categoria', 'tipo']
    }
    df.columns = df.columns.str.strip().str.lower()
    renomear = {alt.lower(): padrao for padrao, alternativas in colunas_esperadas.items() 
                for alt in alternativas if alt.lower() in df.columns}
    df = df.rename(columns=renomear)
    faltando = [col for col in ['Cliente', 'Qtd.', 'Artigo', 'Mês', 'Ano'] if col not in df.columns]
    return df, faltando

@st.cache_data
def load_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        xls = pd.ExcelFile(BytesIO(response.content))
        df = pd.read_excel(xls, sheet_name=0)
        df, faltando = validar_colunas(df)
        
        # Debug: Show unique month values before processing
        st.write("Valores únicos na coluna 'Mês' (antes do processamento):", df['Mês'].unique())
        
        if df['Mês'].dtype == 'object':
            df['Mês'] = df['Mês'].apply(obter_numero_mes)
        df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce').astype('Int64')
        df = df.dropna(subset=['Mês'])
        df = df[df['Mês'].between(1, 12)]
        
        # Debug: Show unique month values after processing
        st.write("Valores únicos na coluna 'Mês' (após conversão para numérico):", df['Mês'].unique())
        
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').astype('Int64')
        df = df.dropna(subset=['Ano'])
        
        df['Qtd.'] = pd.to_numeric(df['Qtd.'], errors='coerce')
        df = df.dropna(subset=['Cliente', 'Artigo', 'Qtd.', 'Mês', 'Ano'])
        
        if 'Categoria' in df.columns:
            df['Categoria'] = df['Categoria'].astype(str).replace('nan', '')
        
        return df, faltando
    except Exception as e:
        return None, [f"Erro ao carregar dados: {str(e)}"]

# Input for GitHub Excel file URL (hidden by default)
if 'show_url_input' not in st.session_state:
    st.session_state['show_url_input'] = False

if st.button("Link do Excel"):
    st.session_state['show_url_input'] = not st.session_state['show_url_input']

if st.session_state['show_url_input']:
    st.subheader("🔗 Atualizar Link do Arquivo Excel")
    excel_url = st.text_input("Insira o link do arquivo Excel no GitHub", 
                             value="https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx", 
                             type="password")
    if st.button("Atualizar"):
        st.session_state['excel_url'] = excel_url
        st.cache_data.clear()  # Clear cache to reload data with new URL
        st.success("Link atualizado com sucesso! Recarregando dados...")

# Load data
url = st.session_state.get('excel_url', "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx")
df, faltando = load_data(url)
if df is None:
    for erro in faltando:
        st.error(erro)
    st.stop()

st.title("📊 Comparador de Vendas: Cliente/Artigo por Mês")

# Seleção de anos e meses
col1, col2 = st.columns(2)
with col1:
    anos_disponiveis = sorted(df['Ano'].unique())
    anos_selecionados = st.multiselect("Selecionar Anos", anos_disponiveis, default=[2024] if 2024 in anos_disponiveis else anos_disponiveis[:1])

with col2:
    df_anos = df[df['Ano'].isin(anos_selecionados)]
    meses_disponiveis = sorted(df_anos['Mês'].dropna().astype(int).unique())
    nomes_meses = [meses_pt.get(m, f"Mês {m}") for m in meses_disponiveis]
    st.write("Meses disponíveis no conjunto de dados:", nomes_meses)  # Debug info
    selected_meses = st.multiselect("Selecionar Meses para Comparação", nomes_meses, default=nomes_meses[:3] if nomes_meses else [])

if not anos_selecionados:
    st.warning("Selecione pelo menos um ano para prosseguir.")
    st.stop()

if not selected_meses:
    st.warning("Selecione pelo menos um mês para prosseguir.")
    st.stop()

meses_nums = [obter_numero_mes(m) for m in selected_meses if obter_numero_mes(m) is not None]
df_filtrado = df_anos[df_anos['Mês'].isin(meses_nums)]

# Filtros opcionais
st.subheader("Filtros Opcionais")
col3, col4, col5 = st.columns(3)
with col3:
    clientes = st.multiselect("Filtrar por Cliente", sorted(df_filtrado['Cliente'].unique()))
with col4:
    artigos = st.multiselect("Filtrar por Artigo", sorted(df_filtrado['Artigo'].unique()))
with col5:
    categorias = st.multiselect("Filtrar por Categoria", sorted(df_filtrado['Categoria'].unique()) if 'Categoria' in df_filtrado.columns else []) if 'Categoria' in df_filtrado.columns else []

if clientes:
    df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes)]
if artigos:
    df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(artigos)]
if categorias and 'Categoria' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias)]

# Cálculo da matriz com variações
st.subheader("Matriz de Quantidades por Cliente/Artigo")
with st.spinner("Calculando..."):
    pivot = df_filtrado.pivot_table(
        index=['Cliente', 'Artigo'],
        columns=['Ano', 'Mês'],
        values='Qtd.',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    new_columns = ['Cliente', 'Artigo']
    for (ano, mes) in pivot.columns[2:]:
        new_columns.append(f"{meses_pt.get(int(mes), f'Mês {mes}')} {ano}")
    pivot.columns = new_columns
    
    month_cols = []
    for ano in sorted(anos_selecionados):
        for mes in sorted(meses_nums):
            col_name = f"{meses_pt.get(mes, f'Mês {mes}')} {ano}"
            if col_name in pivot.columns:
                month_cols.append(col_name)
    pivot = pivot[['Cliente', 'Artigo'] + month_cols]
    
    if len(month_cols) > 1:
        pivot['Total'] = pivot[month_cols].sum(axis=1)
        for i in range(1, len(month_cols)):
            prev = month_cols[i-1]
            curr = month_cols[i]
            var_col = f"Variação {curr} vs {prev} (%)"
            pivot[var_col] = ((pivot[curr] - pivot[prev]) / pivot[prev].replace(0, np.nan) * 100).round(2).fillna(0)
    
    # Format numeric columns to display with two decimal places
    for col in pivot.columns:
        if col not in ['Cliente', 'Artigo']:
            pivot[col] = pivot[col].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
    
    pivot = pivot.sort_values('Total' if 'Total' in pivot.columns else month_cols[-1], ascending=False)
    
    st.dataframe(pivot, use_container_width=True)

# Alertas de variações significativas
if len(month_cols) > 1:
    st.subheader("🚨 Alertas de Variações")
    threshold_aumento = 50
    threshold_reducao = -50
    alertas = []
    for i in range(1, len(month_cols)):
        prev = month_cols[i-1]
        curr = month_cols[i]
        var_col = f"Variação {curr} vs {prev} (%)"
        significant = pivot[(pivot[var_col].astype(float) > threshold_aumento) | (pivot[var_col].astype(float) < threshold_reducao)]
        for _, row in significant.iterrows():
            var = float(row[var_col])
            if var > threshold_aumento:
                alertas.append(f"<div class='alert-success'>↑ Aumento: {row['Cliente']} / {row['Artigo']} - {var:.1f}% em {curr}</div>")
            elif var < threshold_reducao:
                alertas.append(f"<div class='alert-error'>↓ Redução: {row['Cliente']} / {row['Artigo']} - {var:.1f}% em {curr}</div>")
    
    if alertas:
        for alerta in alertas:
            st.markdown(alerta, unsafe_allow_html=True)
    else:
        st.info("Nenhuma variação significativa detectada.")

# Exportação de Alertas
def export_alerts_to_excel(alertas):
    if not alertas:
        return None
    # Parse alerts into a DataFrame
    alert_data = []
    for alerta in alertas:
        # Extract information from the alert HTML string
        match = re.search(r'(↑ Aumento|↓ Redução): (.*?) / (.*?) - ([\-\d\.]+)% em (.*?)<', alerta)
        if match:
            tipo, cliente, artigo, variacao, periodo = match.groups()
            alert_data.append({
                'Tipo': 'Aumento' if tipo == '↑ Aumento' else 'Redução',
                'Cliente': cliente,
                'Artigo': artigo,
                'Variação (%)': float(variacao),
                'Período': periodo
            })
    df_alertas = pd.DataFrame(alert_data)
    
    # Export to Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_alertas.to_excel(writer, index=False, sheet_name='Alertas_Variacoes')
        workbook = writer.book
        worksheet = writer.sheets['Alertas_Variacoes']
        worksheet.set_column('A:E', 20)
    output.seek(0)
    return output

# Add export button for alerts
st.subheader("📥 Exportar Alertas")
if alertas:
    if st.button("Gerar Excel com Alertas"):
        with st.spinner("Gerando relatório de alertas..."):
            excel_alerts_data = export_alerts_to_excel(alertas)
            if excel_alerts_data:
                st.download_button(
                    label="Baixar Alertas em Excel",
                    data=excel_alerts_data,
                    file_name=f"Alertas_Variacoes_{'_'.join(str(a) for a in anos_selecionados)}_{'_'.join(selected_meses)}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
else:
    st.info("Nenhum alerta disponível para exportação.")

# KPIs resumidos
st.subheader("📈 KPIs Resumidos")
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
total_qtd = df_filtrado['Qtd.'].sum()
num_clientes = df_filtrado['Cliente'].nunique()
num_artigos = df_filtrado['Artigo'].nunique()

with col_kpi1:
    st.metric("Quantidade Total", f"{total_qtd:.0f}")
with col_kpi2:
    st.metric("Clientes Únicos", num_clientes)
with col_kpi3:
    st.metric("Artigos Únicos", num_artigos)

# Exportação da Matriz
def export_to_excel(pivot_df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pivot_df.to_excel(writer, index=False, sheet_name='Matriz_Cliente_Artigo')
        workbook = writer.book
        worksheet = writer.sheets['Matriz_Cliente_Artigo']
        worksheet.set_column('A:Z', 20)
    output.seek(0)
    return output

st.subheader("📥 Exportar Relatório")
if st.button("Gerar Excel"):
    with st.spinner("Gerando relatório..."):
        excel_data = export_to_excel(pivot)
        st.download_button(
            label="Baixar Matriz em Excel",
            data=excel_data,
            file_name=f"Comparacao_Cliente_Artigo_{'_'.join(str(a) for a in anos_selecionados)}_{'_'.join(selected_meses)}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
