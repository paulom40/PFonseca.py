import streamlit as st
import pandas as pd
import altair as alt
import io

st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    df = pd.read_excel(url)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Renomear colunas
df = df.rename(columns={
    df.columns[1]: "Cliente",
    df.columns[2]: "Qtd",
    df.columns[4]: "V_Liquido",
    df.columns[7]: "Comercial",
    df.columns[8]: "Categoria",
    df.columns[9]: "Mes",
    df.columns[10]: "Ano",
    df.columns[3]: "Artigo"
})

# Filtros
st.sidebar.header("Filtros")
clientes = st.sidebar.multiselect("Cliente", df["Cliente"].unique())
artigos = st.sidebar.multiselect("Artigo", df["Artigo"].unique())
comerciais = st.sidebar.multiselect("Comercial", df["Comercial"].unique())
categorias = st.sidebar.multiselect("Categoria", df["Categoria"].unique())
meses = st.sidebar.multiselect("Mês", sorted(df["Mes"].dropna().unique()))
anos = st.sidebar.multiselect("Ano", sorted(df["Ano"].dropna().unique()))

df_filtrado = df.copy()
if clientes:
    df_filtrado = df_filtrado[df_filtrado["Cliente"].isin(clientes)]
if artigos:
    df_filtrado = df_filtrado[df_filtrado["Artigo"].isin(artigos)]
if comerciais:
    df_filtrado = df_filtrado[df_filtrado["Comercial"].isin(comerciais)]
if categorias:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categorias)]
if meses:
    df_filtrado = df_filtrado[df_filtrado["Mes"].isin(meses)]
if anos:
    df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos)]
# KPIs
total_vendas = df_filtrado["V_Liquido"].sum()
total_qtd = df_filtrado["Qtd"].sum()
ticket_medio = total_vendas / total_qtd if total_qtd else 0

col1, col2, col3 = st.columns(3)
col1.metric("💰 Valor Líquido Total", f"€ {total_vendas:,.2f}")
col2.metric("📦 Quantidade Total", f"{total_qtd:,.0f}")
col3.metric("🎯 Ticket Médio", f"€ {ticket_medio:,.2f}")

# Gráfico de evolução por mês e ano
st.subheader("📈 Evolução de Vendas por Mês e Ano")
evolucao = df_filtrado.groupby(["Ano", "Mes"]).agg({"V_Liquido": "sum"}).reset_index()
chart = alt.Chart(evolucao).mark_line(point=True).encode(
    x=alt.X("Mes:O", title="Mês"),
    y=alt.Y("V_Liquido:Q", title="Valor Líquido (€)"),
    color="Ano:N"
).properties(width=700)
st.altair_chart(chart)

# Alertas de clientes que não compram todos os meses
st.subheader("🚨 Clientes com meses sem compra")
todos_meses = sorted(df_filtrado["Mes"].dropna().unique())
presenca = df_filtrado.groupby(["Cliente", "Mes"]).size().unstack(fill_value=0)
alertas = []
for cliente in presenca.index:
    meses_compras = presenca.loc[cliente]
    meses_faltantes = [mes for mes in todos_meses if meses_compras.get(mes, 0) == 0]
    if meses_faltantes:
        alertas.append({
            "Cliente": cliente,
            "Meses sem compra": ", ".join(map(str, meses_faltantes)),
            "Total de meses ausentes": len(meses_faltantes)
        })
alertas_df = pd.DataFrame(alertas)
st.dataframe(alertas_df)
# Variação percentual de compras por cliente
st.subheader("📉 Variação Percentual de Compras por Cliente")

cliente_mes = df_filtrado.groupby(["Cliente", "Ano", "Mes"]).agg({"V_Liquido": "sum"}).reset_index()
cliente_mes = cliente_mes.sort_values(["Cliente", "Ano", "Mes"])
cliente_mes["Variação (%)"] = cliente_mes.groupby("Cliente")["V_Liquido"].pct_change() * 100

variacoes = []
for _, row in cliente_mes.iterrows():
    if pd.isna(row["Variação (%)"]) or row["Variação (%)"] < 0:
        variacoes.append({
            "Cliente": row["Cliente"],
            "Ano": row["Ano"],
            "Mês": row["Mes"],
            "Vendas (€)": row["V_Liquido"],
            "Variação (%)": f"{row['Variação (%)']:.2f}" if pd.notna(row["Variação (%)"]) else "Sem histórico",
            "Alerta": "Queda ou ausência"
        })

variacoes_df = pd.DataFrame(variacoes)
st.dataframe(variacoes_df)

# Início da exportação para Excel
st.subheader("📤 Exportar relatório completo para Excel")

output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    # Aba 1: Dados filtrados
    df_filtrado.to_excel(writer, index=False, sheet_name='Vendas Filtradas')

    # Aba 2: KPIs
    kpi_df = pd.DataFrame({
        "Indicador": ["Valor Líquido Total", "Quantidade Total", "Ticket Médio"],
        "Valor": [total_vendas, total_qtd, ticket_medio]
    })
    kpi_df.to_excel(writer, index=False, sheet_name='KPIs')

    # Aba 3: Evolução
    evolucao.to_excel(writer, index=False, sheet_name='Evolução')
    workbook = writer.book
    worksheet = writer.sheets['Evolução']
    chart = workbook.add_chart({'type': 'line'})
    chart.add_series({
        'name': 'Valor Líquido',
        'categories': ['Evolução', 1, 1, len(evolucao), 1],
        'values': ['Evolução', 1, 2, len(evolucao), 2],
    })
    chart.set_title({'name': 'Evolução de Vendas por Mês'})
    worksheet.insert_chart('E5', chart)
    # Aba 4: Por Categoria
    cat_df = df_filtrado.groupby("Categoria").agg({"Qtd": "sum", "V_Liquido": "sum"}).reset_index()
    cat_df.to_excel(writer, index=False, sheet_name='Por Categoria')
    cat_chart = workbook.add_chart({'type': 'column'})
    cat_chart.add_series({
        'name': 'Valor Líquido',
        'categories': ['Por Categoria', 1, 0, len(cat_df), 0],
        'values': ['Por Categoria', 1, 2, len(cat_df), 2],
    })
    cat_chart.set_title({'name': 'Vendas por Categoria'})
    writer.sheets['Por Categoria'].insert_chart('E5', cat_chart)

    # Aba 5: Por Comercial
    com_df = df_filtrado.groupby("Comercial").agg({"Qtd": "sum", "V_Liquido": "sum"}).reset_index()
    com_df.to_excel(writer, index=False, sheet_name='Por Comercial')
    com_chart = workbook.add_chart({'type': 'bar'})
    com_chart.add_series({
        'name': 'Valor Líquido',
        'categories': ['Por Comercial', 1, 0, len(com_df), 0],
        'values': ['Por Comercial', 1, 2, len(com_df), 2],
    })
    com_chart.set_title({'name': 'Vendas por Comercial'})
    writer.sheets['Por Comercial'].insert_chart('E5', com_chart)

    # Aba 6: Top 10 Clientes
    cli_df = df_filtrado.groupby("Cliente").agg({"Qtd": "sum", "V_Liquido": "sum"}).reset_index()
    top10_cli = cli_df.sort_values("V_Liquido", ascending=False).head(10)
    top10_cli.to_excel(writer, index=False, sheet_name='Top 10 Clientes')
    cli_chart = workbook.add_chart({'type': 'column'})
    cli_chart.add_series({
        'name': 'Top 10 Valor Líquido',
        'categories': ['Top 10 Clientes', 1, 0, len(top10_cli), 0],
        'values': ['Top 10 Clientes', 1, 2, len(top10_cli), 2],
    })
    cli_chart.set_title({'name': 'Top 10 Clientes por Vendas'})
    writer.sheets['Top 10 Clientes'].insert_chart('E5', cli_chart)

    # Aba 7: Top 10 Artigos
    art_df = df_filtrado.groupby("Artigo").agg({"Qtd": "sum", "V_Liquido": "sum"}).reset_index()
    top10_art = art_df.sort_values("V_Liquido", ascending=False).head(10)
    top10_art.to_excel(writer, index=False, sheet_name='Top 10 Artigos')
    art_chart = workbook.add_chart({'type': 'column'})
    art_chart.add_series({
        'name': 'Top 10 Valor Líquido',
        'categories': ['Top 10 Artigos', 1, 0, len(top10_art), 0],
        'values': ['Top 10 Artigos', 1, 2, len(top10_art), 2],
    })
    art_chart.set_title({'name': 'Top 10 Artigos por Vendas'})
    writer.sheets['Top 10 Artigos'].insert_chart('E5', art_chart)

    # Aba 8: Resumo por Mês/Ano
    mesano_df = df_filtrado.groupby(["Ano", "Mes"]).agg({"Qtd": "sum", "V_Liquido": "sum"}).reset_index()
    mesano_df.to_excel(writer, index=False, sheet_name='Resumo Mensal')
    mesano_chart = workbook.add_chart({'type': 'bar'})
    mesano_chart.add_series({
        'name': 'Valor Líquido',
        'categories': ['Resumo Mensal', 1, 1, len(mesano_df), 1],
        'values': ['Resumo Mensal', 1, 2, len(mesano_df), 2],
    })
    mesano_chart.set_title({'name': 'Resumo por Mês e Ano'})
    writer.sheets['Resumo Mensal'].insert_chart('E5', mesano_chart)
    # Aba 9: Crescimento Percentual por Ano
    crescimento_df = df_filtrado.groupby("Ano").agg({"V_Liquido": "sum"}).reset_index()
    crescimento_df["Crescimento (%)"] = crescimento_df["V_Liquido"].pct_change() * 100
    crescimento_df.to_excel(writer, index=False, sheet_name='Crescimento Anual')
    crescimento_chart = workbook.add_chart({'type': 'line'})
    crescimento_chart.add_series({
        'name': 'Crescimento (%)',
        'categories': ['Crescimento Anual', 1, 0, len(crescimento_df), 0],
        'values': ['Crescimento Anual', 1, 2, len(crescimento_df), 2],
    })
    crescimento_chart.set_title({'name': 'Crescimento Percentual por Ano'})
    writer.sheets['Crescimento Anual'].insert_chart('E5', crescimento_chart)

    # Aba 10: Alertas de Variação Mensal
    variacoes_df.to_excel(writer, index=False, sheet_name='Alertas Variação Mensal')

    # Aba 11: Quedas Consecutivas
    cliente_mes["Queda"] = cliente_mes["Variação (%)"].apply(lambda x: x < 0 if pd.notna(x) else False)
    cliente_mes["Queda Seq"] = cliente_mes.groupby("Cliente")["Queda"].cumsum()
    cliente_mes["Queda Flag"] = cliente_mes.groupby("Cliente")["Queda"].rolling(3).sum().reset_index(level=0, drop=True) >= 3
    quedas_df = cliente_mes[cliente_mes["Queda Flag"]].copy()
    quedas_df = quedas_df[["Cliente", "Ano", "Mes", "V_Liquido", "Variação (%)"]]
    quedas_df.to_excel(writer, index=False, sheet_name='Quedas Consecutivas')

    # Aba 12: Dispersão Ticket Médio por Cliente
    ticket_df = df_filtrado.groupby("Cliente").agg({"V_Liquido": "sum", "Qtd": "sum"}).reset_index()
    ticket_df["Ticket Médio"] = ticket_df["V_Liquido"] / ticket_df["Qtd"]
    ticket_df.to_excel(writer, index=False, sheet_name='Ticket Médio Cliente')
    scatter_chart = workbook.add_chart({'type': 'scatter'})
    scatter_chart.add_series({
        'name': 'Ticket Médio',
        'categories': ['Ticket Médio Cliente', 1, 1, len(ticket_df), 1],
        'values': ['Ticket Médio Cliente', 1, 3, len(ticket_df), 3],
    })
    scatter_chart.set_title({'name': 'Dispersão Ticket Médio por Cliente'})
    scatter_chart.set_x_axis({'name': 'Quantidade'})
    scatter_chart.set_y_axis({'name': 'Ticket Médio (€)'})
    writer.sheets['Ticket Médio Cliente'].insert_chart('E5', scatter_chart)

    writer.save()
    processed_data = output.getvalue()

# Botão final de download
st.download_button(
    label="📥 Baixar Excel completo com análises",
    data=processed_data,
    file_name="relatorio_vendas_completo.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
