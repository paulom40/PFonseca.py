import streamlit as st
import pandas as pd
from io import BytesIO
import requests
from datetime import datetime

# Meses em português
meses_pt = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def obter_numero_mes(nome_mes):
    if not isinstance(nome_mes, str):
        return None
    nome_mes = nome_mes.strip().lower()
    for k, v in meses_pt.items():
        nome_mes_ref = v.lower()
        if nome_mes == nome_mes_ref or nome_mes.startswith(nome_mes_ref[:3]):
            return k
    return None

def validar_colunas(df):
    colunas_esperadas = {
        'Mês': ['mês', 'mes', 'mês de venda', 'month'],
        'Cliente': ['cliente', 'cliente nome', 'nome cliente'],
        'Artigo': ['artigo', 'produto', 'item', 'artigo vendido'],
        'Qtd.': ['qtd.', 'quantidade', 'qtd', 'qtde'],
        'Ano': ['ano', 'year'],
        'Data': ['data', 'data venda', 'data da compra']
    }

    df.columns = df.columns.str.strip().str.lower()
    renomear = {}
    colunas_detectadas = {}

    for padrao, alternativas in colunas_esperadas.items():
        for alt in alternativas:
            if alt.lower() in df.columns:
                renomear[alt.lower()] = padrao
                colunas_detectadas[padrao] = alt
                break

    df = df.rename(columns=renomear)
    faltando = [col for col in colunas_esperadas if col not in df.columns and col != 'Data']
    return df, colunas_detectadas, faltando

@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    response = requests.get(url)
    xls = pd.ExcelFile(BytesIO(response.content))
    df_raw = pd.read_excel(xls, sheet_name=0)

    df, colunas_detectadas, faltando = validar_colunas(df_raw)

    st.markdown("### ✅ Validação de Estrutura do Ficheiro")
    for padrao, original in colunas_detectadas.items():
        st.success(f"✔ Coluna '{padrao}' detectada como '{original}'")

    if faltando:
        for col in faltando:
            st.error(f"❌ Coluna obrigatória ausente: '{col}'")
        st.stop()

    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df = df.dropna(subset=['Mês'])
    df['Mês'] = df['Mês'].astype(int)

    if 'Data' not in df.columns:
        df['Data'] = pd.to_datetime(dict(year=df['Ano'], month=df['Mês'], day=1), errors='coerce')

    df = df.dropna(subset=['Data', 'Qtd.', 'Cliente', 'Artigo'])
    return df

df = load_data()

st.title("📊 Dashboard Comercial")

meses_disponiveis = sorted(df['Mês'].dropna().unique())
nomes_meses = [meses_pt.get(int(m), f"Mês {m}") for m in meses_disponiveis]

mes_label = st.selectbox("Selecionar Mês", nomes_meses)
mes_num = obter_numero_mes(mes_label)
if mes_num is None:
    st.error(f"❌ Mês '{mes_label}' não reconhecido.")
    st.stop()

clientes = st.multiselect("Filtrar por Cliente", sorted(df['Cliente'].unique()))
artigos = st.multiselect("Filtrar por Artigo", sorted(df['Artigo'].unique()))

df_filtrado = df[df['Mês'] == mes_num]
if clientes:
    df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes)]
if artigos:
    df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(artigos)]

st.dataframe(df_filtrado[['Data', 'Cliente', 'Artigo', 'Qtd.']], use_container_width=True)

totais_cliente = df_filtrado.groupby('Cliente')['Qtd.'].sum().reset_index()
totais_artigo = df_filtrado.groupby('Artigo')['Qtd.'].sum().reset_index()

def exportar_excel_completo(dados_df, cliente_df, artigo_df, nome_mes, mes_num):
    output = BytesIO()
    logo_url = "https://github.com/paulom40/PFonseca.py/raw/main/Bracar.png"
    logo_data = requests.get(logo_url).content

    variacoes = dados_df.groupby(['Cliente', 'Artigo', 'Mês'])['Qtd.'].sum().reset_index()
    variacoes_pivot = variacoes.pivot_table(index=['Cliente', 'Artigo'], columns='Mês', values='Qtd.', fill_value=0).reset_index()

    if 'Comercial' in dados_df.columns:
        variacoes_comercial = dados_df.groupby(['Comercial', 'Cliente', 'Mês'])['Qtd.'].sum().reset_index()
        variacoes_comercial_pivot = variacoes_comercial.pivot_table(index=['Comercial', 'Cliente'], columns='Mês', values='Qtd.', fill_value=0).reset_index()
    else:
        variacoes_comercial_pivot = pd.DataFrame({'Aviso': ['Coluna "Comercial" não encontrada nos dados.']})

    mes_anterior = mes_num - 1 if mes_num > 1 else 12
    todos_clientes = sorted(df['Cliente'].unique())
    clientes_ativos = sorted(df[df['Mês'] == mes_anterior]['Cliente'].unique())
    clientes_inativos = [c for c in todos_clientes if c not in clientes_ativos]
    alertas_df = pd.DataFrame({'Cliente sem compras': clientes_inativos}) if clientes_inativos else pd.DataFrame({'Todos os clientes compraram': ['✔']})

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        bold = workbook.add_format({'bold': True})
        italic = workbook.add_format({'italic': True})

        dados_df.to_excel(writer, index=False, sheet_name='Dados_Filtrados')
        ws1 = writer.sheets['Dados_Filtrados']
        ws1.set_column('A:D', 20)
        ws1.insert_image('A1', 'logo.png', {'image_data': BytesIO(logo_data), 'x_scale': 0.5, 'y_scale': 0.5})
        ws1.write('C1', f'Relatório Comercial – {nome_mes}', bold)
        ws1.write('C2', f'Gerado em: {datetime.today().strftime("%d/%m/%Y %H:%M")}', italic)

        cliente_df.to_excel(writer, index=False, sheet_name='Totais_Cliente')
        ws2 = writer.sheets['Totais_Cliente']
        ws2.set_column('A:B', 20)
        ws2.write('A1', f'Totais por Cliente – {nome_mes}', bold)
        ws2.write('A2', f'Gerado em: {datetime.today().strftime("%d/%m/%Y %H:%M")}', italic)

        artigo_df.to_excel(writer, index=False, sheet_name='Totais_Artigo')
        ws3 = writer.sheets['Totais_Artigo']
        ws3.set_column('A:B', 20)
        ws3.write('A1', f'Totais por Artigo – {nome_mes}', bold)
        ws3.write('A2', f'Gerado em: {datetime.today().strftime("%d/%m/%Y %H:%M")}', italic)

        variacoes_pivot.to_excel(writer, index=False, sheet_name='Variações_Produto_Cliente')
        ws4 = writer.sheets['Variações_Produto_Cliente']
        ws4.set_column(0, len(variacoes_pivot.columns)-1, 18)
        ws4.write('A1', f'Variações por Produto e Cliente – {nome_mes}', bold)
        ws4.write('A2', f'Gerado em: {datetime.today().strftime("%d/%m/%Y %H:%M")}', italic)

        variacoes_comercial_pivot.to_excel(writer, index=False, sheet_name='Variações_Comercial_Cliente')
        ws5 = writer.sheets['Variações_Comercial_Cliente']
        ws5.set_column(0, len(variacoes_comercial_pivot.columns)-1, 18)
        ws5.write('A1', f'Variações por Comercial e Cliente – {nome_mes}', bold)
        ws5.write('A2', f'Gerado em: {datetime.today().strftime("%d/%m/%Y %H:%M")}', italic)

