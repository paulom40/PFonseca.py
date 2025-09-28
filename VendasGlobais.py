import streamlit as st
import pandas as pd
from io import BytesIO
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

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
        'Código': ['código', 'codigo'],
        'Cliente': ['cliente', 'cliente nome', 'nome cliente'],
        'Qtd.': ['qtd.', 'quantidade', 'qtd', 'qtde'],
        'UN': ['un', 'unidade'],
        'V. Líquido': ['v. líquido', 'valor líquido', 'valor liquido'],
        'PM': ['pm', 'preço médio', 'preco medio'],
        'Artigo': ['artigo', 'produto', 'item', 'artigo vendido'],
        'Comercial': ['comercial', 'vendedor'],
        'Categoria': ['categoria', 'tipo'],
        'Mês': ['mês', 'mes', 'mês de venda', 'month'],
        'Ano': ['ano', 'year']
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
    faltando = [col for col in ['Código', 'Cliente', 'Qtd.', 'Artigo', 'Mês', 'Ano'] if col not in df.columns]
    return df, colunas_detectadas, faltando

@st.cache_data
def load_data():
    try:
        url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
        response = requests.get(url)
        response.raise_for_status()
        xls = pd.ExcelFile(BytesIO(response.content))
        df_raw = pd.read_excel(xls, sheet_name=0)

        # Debug: Show raw data
        if st.checkbox("Mostrar dados brutos para depuração"):
            st.write("**Colunas no arquivo bruto**:")
            st.write(df_raw.columns.tolist())
            for col in df_raw.columns:
                st.write(f"**{col} (valores únicos)**: {df_raw[col].dropna().unique()[:10]}")

        df, colunas_detectadas, faltando = validar_colunas(df_raw)

        st.markdown("### ✅ Validação de Estrutura do Ficheiro")
        for padrao, original in colunas_detectadas.items():
            st.success(f"✔ Coluna '{padrao}' detectada como '{original}'")

        if faltando:
            for col in faltando:
                st.error(f"❌ Coluna obrigatória ausente: '{col}'")
            st.stop()

        # Convert month names to numbers if necessary
        if df['Mês'].dtype == 'object':
            df['Mês'] = df['Mês'].apply(obter_numero_mes)

        df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
        df = df.dropna(subset=['Mês'])
        df = df[df['Mês'].between(1, 12)]
        df['Mês'] = df['Mês'].astype(int)

        # Ensure Ano is numeric
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
        df = df.dropna(subset=['Ano'])
        df['Ano'] = df['Ano'].astype(int)

        # Ensure other columns are properly typed
        df['Código'] = df['Código'].astype(str)
        df['Cliente'] = df['Cliente'].astype(str)
        df['Artigo'] = df['Artigo'].astype(str)
        df['Categoria'] = df['Categoria'].astype(str) if 'Categoria' in df.columns else ''
        df['Comercial'] = df['Comercial'].astype(str) if 'Comercial' in df.columns else ''
        df['Qtd.'] = pd.to_numeric(df['Qtd.'], errors='coerce')
        df['V. Líquido'] = pd.to_numeric(df['V. Líquido'], errors='coerce') if 'V. Líquido' in df.columns else 0
        df['PM'] = pd.to_numeric(df['PM'], errors='coerce') if 'PM' in df.columns else 0
        df['UN'] = df['UN'].astype(str) if 'UN' in df.columns else ''

        df = df.dropna(subset=['Código', 'Cliente', 'Qtd.', 'Artigo', 'Mês', 'Ano'])

        # Debug: Show processed data
        if st.checkbox("Mostrar dados processados para depuração"):
            st.write("**Colunas após processamento**:")
            for col in df.columns:
                st.write(f"**{col} (valores únicos)**: {df[col].dropna().unique()[:10]}")

        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        st.stop()

df = load_data()

st.title("📊 Dashboard Comercial")

# Painel de valores únicos
with st.expander("📋 Ver valores únicos por coluna"):
    for col in ['Mês', 'Ano', 'Cliente', 'Artigo', 'Categoria', 'Comercial']:
        if col in df.columns and df[col].notna().any():
            try:
                valores = sorted([str(val) for val in df[col].dropna().unique() if pd.notna(val)])
                if col == 'Mês':
                    nomes = [meses_pt.get(int(float(val)), str(val)) for val in valores]
                    st.write(f"**{col}**: {', '.join(nomes[:20])} {'...' if len(nomes) > 20 else ''}")
                else:
                    st.write(f"**{col}**: {', '.join(valores[:20])} {'...' if len(valores) > 20 else ''}")
            except Exception as e:
                st.warning(f"⚠️ Não foi possível exibir valores únicos para '{col}': {str(e)}")

# Opção de comparação 2024 vs 2025
st.subheader("Comparação de Dados")
compare_years = st.checkbox("Comparar mesmo mês entre 2024 e 2025")

if compare_years:
    meses_disponiveis = sorted(df[df['Ano'].isin([2024, 2025])]['Mês'].unique())
    nomes_meses = [meses_pt.get(m, f"Mês {m}") for m in meses_disponiveis]
    if nomes_meses:
        mes_label = st.selectbox("Selecionar Mês para Comparação", nomes_meses)
        mes_num = obter_numero_mes(mes_label)
        if mes_num is None:
            st.error(f"❌ Mês '{mes_label}' não reconhecido.")
            st.stop()
    else:
        st.warning("⚠️ Nenhum mês disponível para os anos 2024 e 2025.")
        st.stop()

    # Dados para 2024 e 2025
    df_2024 = df[(df['Mês'] == mes_num) & (df['Ano'] == 2024)]
    df_2025 = df[(df['Mês'] == mes_num) & (df['Ano'] == 2025)]

    # Filtros adicionais
    st.subheader("Filtros Adicionais")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        clientes = st.multiselect("Filtrar por Cliente", sorted(df[df['Mês'] == mes_num]['Cliente'].unique()))
    with col2:
        artigos = st.multiselect("Filtrar por Artigo", sorted(df[df['Mês'] == mes_num]['Artigo'].unique()))
    with col3:
        categorias = st.multiselect("Filtrar por Categoria", sorted(df[df['Mês'] == mes_num]['Categoria'].unique())) if 'Categoria' in df.columns else []
    with col4:
        comerciais = st.multiselect("Filtrar por Comercial", sorted(df[df['Mês'] == mes_num]['Comercial'].unique())) if 'Comercial' in df.columns else []

    # Aplicar filtros
    if clientes:
        df_2024 = df_2024[df_2024['Cliente'].isin(clientes)]
        df_2025 = df_2025[df_2025['Cliente'].isin(clientes)]
    if artigos:
        df_2024 = df_2024[df_2024['Artigo'].isin(artigos)]
        df_2025 = df_2025[df_2025['Artigo'].isin(artigos)]
    if categorias:
        df_2024 = df_2024[df_2024['Categoria'].isin(categorias)]
        df_2025 = df_2025[df_2025['Categoria'].isin(categorias)]
    if comerciais:
        df_2024 = df_2024[df_2024['Comercial'].isin(comerciais)]
        df_2025 = df_2025[df_2025['Comercial'].isin(comerciais)]

    # Totais para comparação
    totais_cliente_2024 = df_2024.groupby('Cliente').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False)
    totais_cliente_2025 = df_2025.groupby('Cliente').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False)
    totais_categoria_2024 = df_2024.groupby('Categoria').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False) if 'Categoria' in df_2024.columns else pd.DataFrame()
    totais_categoria_2025 = df_2025.groupby('Categoria').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False) if 'Categoria' in df_2025.columns else pd.DataFrame()

    # Exibir dados filtrados
    st.subheader(f"📋 Dados Filtrados: {mes_label} 2024")
    st.dataframe(df_2024[['Código', 'Cliente', 'Artigo', 'Qtd.', 'V. Líquido', 'PM', 'UN', 'Categoria', 'Comercial', 'Mês', 'Ano']], use_container_width=True)
    st.subheader(f"📋 Dados Filtrados: {mes_label} 2025")
    st.dataframe(df_2025[['Código', 'Cliente', 'Artigo', 'Qtd.', 'V. Líquido', 'PM', 'UN', 'Categoria', 'Comercial', 'Mês', 'Ano']], use_container_width=True)

    # Visualizações comparativas
    st.subheader("📈 Comparação 2024 vs 2025")
    col5, col6 = st.columns(2)

    with col5:
        if not totais_cliente_2024.empty or not totais_cliente_2025.empty:
            st.markdown(f"**Quantidade por Cliente: {mes_label}**")
            fig1, ax1 = plt.subplots(figsize=(8, 4))
            width = 0.35
            clientes = pd.concat([totais_cliente_2024['Cliente'], totais_cliente_2025['Cliente']]).unique()[:10]
            x = np.arange(len(clientes))
            qtd_2024 = [totais_cliente_2024[totais_cliente_2024['Cliente'] == c]['Qtd.'].sum() for c in clientes]
            qtd_2025 = [totais_cliente_2025[totais_cliente_2025['Cliente'] == c]['Qtd.'].sum() for c in clientes]
            ax1.bar(x - width/2, qtd_2024, width, label='2024', color='#4e79a7')
            ax1.bar(x + width/2, qtd_2025, width, label='2025', color='#f28e2b')
            ax1.set_ylabel('Quantidade')
            ax1.set_title(f'Top Clientes por Quantidade - {mes_label}')
            ax1.set_xticks(x)
            ax1.set_xticklabels(clientes, rotation=45, ha='right')
            ax1.legend()
            plt.tight_layout()
            st.pyplot(fig1)

    with col6:
        if not totais_categoria_2024.empty or not totais_categoria_2025.empty:
            st.markdown(f"**Valor Líquido por Categoria: {mes_label}**")
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            categorias = pd.concat([totais_categoria_2024['Categoria'], totais_categoria_2025['Categoria']]).unique()[:8]
            x = np.arange(len(categorias))
            valor_2024 = [totais_categoria_2024[totais_categoria_2024['Categoria'] == c]['V. Líquido'].sum() for c in categorias]
            valor_2025 = [totais_categoria_2025[totais_categoria_2025['Categoria'] == c]['V. Líquido'].sum() for c in categorias]
            ax2.bar(x - width/2, valor_2024, width, label='2024', color='#4e79a7')
            ax2.bar(x + width/2, valor_2025, width, label='2025', color='#f28e2b')
            ax2.set_ylabel('Valor Líquido')
            ax2.set_title(f'Top Categorias por Valor Líquido - {mes_label}')
            ax2.set_xticks(x)
            ax2.set_xticklabels(categorias, rotation=45, ha='right')
            ax2.legend()
            plt.tight_layout()
            st.pyplot(fig2)

else:
    # Modo normal (sem comparação)
    col1, col2 = st.columns(2)
    with col1:
        anos_disponiveis = sorted(df['Ano'].unique())
        ano_selecionado = st.selectbox("Selecionar Ano", anos_disponiveis) if len(anos_disponiveis) > 1 else anos_disponiveis[0]

    with col2:
        df_ano = df[df['Ano'] == ano_selecionado]
        meses_disponiveis = sorted(df_ano['Mês'].unique())
        nomes_meses = [meses_pt.get(m, f"Mês {m}") for m in meses_disponiveis]
        if nomes_meses:
            mes_label = st.selectbox("Selecionar Mês", nomes_meses)
            mes_num = obter_numero_mes(mes_label)
            if mes_num is None:
                st.error(f"❌ Mês '{mes_label}' não reconhecido.")
                st.stop()
        else:
            st.warning("⚠️ Nenhum mês disponível nos dados para o ano selecionado.")
            st.stop()

    # Filtros adicionais
    st.subheader("Filtros Adicionais")
    col3, col4, col5, col6 = st.columns(4)
    with col3:
        clientes = st.multiselect("Filtrar por Cliente", sorted(df_ano['Cliente'].unique()))
    with col4:
        artigos = st.multiselect("Filtrar por Artigo", sorted(df_ano['Artigo'].unique()))
    with col5:
        categorias = st.multiselect("Filtrar por Categoria", sorted(df_ano['Categoria'].unique())) if 'Categoria' in df_ano.columns else []
    with col6:
        comerciais = st.multiselect("Filtrar por Comercial", sorted(df_ano['Comercial'].unique())) if 'Comercial' in df_ano.columns else []

    # Aplicar filtros
    df_filtrado = df_ano[df_ano['Mês'] == mes_num]
    if clientes:
        df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes)]
    if artigos:
        df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(artigos)]
    if categorias:
        df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias)]
    if comerciais:
        df_filtrado = df_filtrado[df_filtrado['Comercial'].isin(comerciais)]

    st.subheader("📋 Dados Filtrados")
    st.dataframe(df_filtrado[['Código', 'Cliente', 'Artigo', 'Qtd.', 'V. Líquido', 'PM', 'UN', 'Categoria', 'Comercial', 'Mês', 'Ano']], use_container_width=True)

    # Totais
    totais_cliente = df_filtrado.groupby('Cliente').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False)
    totais_artigo = df_filtrado.groupby('Artigo').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False)
    totais_categoria = df_filtrado.groupby('Categoria').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False) if 'Categoria' in df_filtrado.columns else pd.DataFrame()
    totais_comercial = df_filtrado.groupby('Comercial').agg({'Qtd.': 'sum', 'V. Líquido': 'sum'}).reset_index().sort_values('Qtd.', ascending=False) if 'Comercial' in df_filtrado.columns else pd.DataFrame()

    # Visualizações
    st.subheader("📈 Visualizações")
    col7, col8 = st.columns(2)

    with col7:
        if not totais_cliente.empty:
            st.markdown(f"**Totais por Cliente (Quantidade) - {mes_label} {ano_selecionado}**")
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            top_clientes = totais_cliente.head(10)
            ax1.barh(top_clientes['Cliente'], top_clientes['Qtd.'], color='#4e79a7')
            ax1.set_xlabel('Quantidade')
            ax1.set_title(f'Top 10 Clientes por Quantidade')
            plt.tight_layout()
            st.pyplot(fig1)

    with col8:
        if not totais_categoria.empty:
            st.markdown(f"**Totais por Categoria (Valor Líquido) - {mes_label} {ano_selecionado}**")
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            top_categorias = totais_categoria.head(8)
            ax2.pie(top_categorias['V. Líquido'], labels=top_categorias['Categoria'], autopct='%1.1f%%', colors=['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948', '#b07aa1', '#ff9da7'])
            ax2.set_title(f'Top 8 Categorias por Valor Líquido')
            plt.tight_layout()
            st.pyplot(fig2)

def exportar_excel_completo(dados_df, cliente_df, artigo_df, categoria_df, comercial_df, nome_mes, mes_num, ano, compare_years=False, df_2024=None, df_2025=None, totais_cliente_2024=None, totais_cliente_2025=None, totais_categoria_2024=None, totais_categoria_2025=None):
    output = BytesIO()
    try:
        logo_url = "https://github.com/paulom40/PFonseca.py/raw/main/Bracar.png"
        logo_data = requests.get(logo_url).content
    except:
        logo_data = None
        st.warning("⚠️ Não foi possível carregar o logotipo para o relatório.")

    # Variações por Cliente e Artigo
    variacoes = dados_df.groupby(['Cliente', 'Artigo', 'Mês'])['Qtd.'].sum().reset_index()
    variacoes_pivot = variacoes.pivot_table(index=['Cliente', 'Artigo'], columns='Mês', values='Qtd.', fill_value=0).reset_index()

    # Variações por Comercial
    variacoes_comercial = dados_df.groupby(['Comercial', 'Cliente', 'Mês'])['Qtd.'].sum().reset_index() if 'Comercial' in dados_df.columns else pd.DataFrame()
    variacoes_comercial_pivot = variacoes_comercial.pivot_table(index=['Comercial', 'Cliente'], columns='Mês', values='Qtd.', fill_value=0).reset_index() if not variacoes_comercial.empty else pd.DataFrame({'Aviso': ['Coluna "Comercial" não encontrada.']})

    # Alertas de clientes inativos
    mes_anterior = mes_num - 1 if mes_num > 1 else 12
    ano_anterior = ano if mes_num > 1 else ano - 1
    todos_clientes = sorted(df['Cliente'].unique())
    clientes_ativos = sorted(df[(df['Mês'] == mes_anterior) & (df['Ano'] == ano_anterior)]['Cliente'].unique())
    clientes_inativos = [c for c in todos_clientes if c not in clientes_ativos]
    alertas_df = pd.DataFrame({'Cliente sem compras': clientes_inativos}) if clientes_inativos else pd.DataFrame({'Todos os clientes compraram': ['✔']})

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        bold = workbook.add_format({'bold': True})
        italic = workbook.add_format({'italic': True})

        # Dados Filtrados
        dados_df.to_excel(writer, index=False, sheet_name='Dados_Filtrados')
        ws1 = writer.sheets['Dados_Filtrados']
        ws1.set_column('A:Z', 20)
        if logo_data:
            ws1.insert_image('A1', '', {'image_data': BytesIO(logo_data), 'x_scale': 0.5, 'y_scale': 0.5})
        ws1.write('C1', f'Relatório Comercial – {nome_mes} {ano}', bold)
        ws1.write('C2', f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', italic)

        # Totais Cliente
        cliente_df.to_excel(writer, index=False, sheet_name='Totais_Cliente')
        ws2 = writer.sheets['Totais_Cliente']
        ws2.set_column('A:Z', 20)
        ws2.write('A1', f'Totais por Cliente – {nome_mes} {ano}', bold)
        ws2.write('A2', f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', italic)

        # Totais Artigo
        artigo_df.to_excel(writer, index=False, sheet_name='Totais_Artigo')
        ws3 = writer.sheets['Totais_Artigo']
        ws3.set_column('A:Z', 20)
        ws3.write('A1', f'Totais por Artigo – {nome_mes} {ano}', bold)
        ws3.write('A2', f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', italic)

        # Totais Categoria
        if not categoria_df.empty:
            categoria_df.to_excel(writer, index=False, sheet_name='Totais_Categoria')
            ws4 = writer.sheets['Totais_Categoria']
            ws4.set_column('A:Z', 20)
            ws4.write('A1', f'Totais por Categoria – {nome_mes} {ano}', bold)
            ws4.write('A2', f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', italic)

        # Totais Comercial
        if not comercial_df.empty:
            comercial_df.to_excel(writer, index=False, sheet_name='Totais_Comercial')
            ws5 = writer.sheets['Totais_Comercial']
            ws5.set_column('A:Z', 20)
            ws5.write('A1', f'Totais por Comercial – {nome_mes} {ano}', bold)
            ws5.write('A2', f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', italic)

        # Variações Cliente e Artigo
        variacoes_pivot.to_excel(writer, index=False, sheet_name='Variacoes_Cliente_Artigo')
        ws6 = writer.sheets['Variacoes_Cliente_Artigo']
        ws6.set_column('A:Z', 20)
        ws6.write('A1', f'Variações por Cliente e Artigo', bold)

        # Variações Comercial
        variacoes_comercial_pivot.to_excel(writer, index=False, sheet_name='Variacoes_Comercial')
        ws7 = writer.sheets['Variacoes_Comercial']
        ws7.set_column('A:Z', 20)
        ws7.write('A1', f'Variações por Comercial', bold)

        # Alertas
        alertas_df.to_excel(writer, index=False, sheet_name='Alertas_Clientes_Inativos')
        ws8 = writer.sheets['Alertas_Clientes_Inativos']
        ws8.set_column('A:Z', 20)
        ws8.write('A1', f'Alertas de Clientes Inativos no Mês Anterior', bold)

        # Comparação 2024 vs 2025
        if compare_years:
            if not totais_cliente_2024.empty:
                totais_cliente_2024.to_excel(writer, index=False, sheet_name='Comparacao_Cliente_2024')
                ws9 = writer.sheets['Comparacao_Cliente_2024']
                ws9.set_column('A:Z', 20)
                ws9.write('A1', f'Comparação Clientes – {nome_mes} 2024', bold)
            if not totais_cliente_2025.empty:
                totais_cliente_2025.to_excel(writer, index=False, sheet_name='Comparacao_Cliente_2025')
                ws10 = writer.sheets['Comparacao_Cliente_2025']
                ws10.set_column('A:Z', 20)
                ws10.write('A1', f'Comparação Clientes – {nome_mes} 2025', bold)
            if not totais_categoria_2024.empty:
                totais_categoria_2024.to_excel(writer, index=False, sheet_name='Comparacao_Categoria_2024')
                ws11 = writer.sheets['Comparacao_Categoria_2024']
                ws11.set_column('A:Z', 20)
                ws11.write('A1', f'Comparação Categorias – {nome_mes} 2024', bold)
            if not totais_categoria_2025.empty:
                totais_categoria_2025.to_excel(writer, index=False, sheet_name='Comparacao_Categoria_2025')
                ws12 = writer.sheets['Comparacao_Categoria_2025']
                ws12.set_column('A:Z', 20)
                ws12.write('A1', f'Comparação Categorias – {nome_mes} 2025', bold)

    output.seek(0)
    return output

# Botão de exportação
if st.button("📥 Exportar Relatório para Excel"):
    if compare_years:
        excel_data = exportar_excel_completo(
            df_2025, totais_cliente_2025, totais_artigo, totais_categoria_2025, totais_comercial,
            mes_label, mes_num, 2025, compare_years=True,
            df_2024=df_2024, df_2025=df_2025,
            totais_cliente_2024=totais_cliente_2024, totais_cliente_2025=totais_cliente_2025,
            totais_categoria_2024=totais_categoria_2024, totais_categoria_2025=totais_categoria_2025
        )
        file_name = f"Relatorio_Comercial_{mes_label}_2024_2025.xlsx"
    else:
        excel_data = exportar_excel_completo(
            df_filtrado, totais_cliente, totais_artigo, totais_categoria, totais_comercial,
            mes_label, mes_num, ano_selecionado
        )
        file_name = f"Relatorio_Comercial_{mes_label}_{ano_selecionado}.xlsx"
    
    st.download_button(
        label="Baixar Relatório",
        data=excel_data,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
