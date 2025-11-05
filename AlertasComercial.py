import streamlit as st
import pandas as pd
import altair as alt
import io

st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

@st.cache_data
def load_data():
    url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"
    df = pd.read_excel(url)
    df.columns = df.columns.str.strip().str.upper()
    df = df.rename(columns={
        "CLIENTE": "Cliente",
        "QTD": "Qtd",
        "ARTIGO": "Artigo",
        "V. LÍQUIDO": "V_Liquido",
        "COMERCIAL": "Comercial",
        "CATEGORIA": "Categoria",
        "MÊS": "Mes",
        "ANO": "Ano"
    })
    return df

df = load_data()

# Filtros
st.sidebar.header("Filtros")
clientes = st.sidebar.multiselect("Cliente", df["Cliente"].unique())
artigos = st.sidebar.multiselect("Artigo", df["Artigo"].unique())
comerciais = st.sidebar.multiselect("Comercial", df["Comercial"].unique())
categorias = st.sidebar.multiselect("Categoria", df["Categoria"].unique())
meses = st.sidebar.multiselect("Mês", sorted(df["Mes"].dropna().unique()))
anos = st.sidebar.multiselect("Ano", sorted(df["Ano"].dropna().unique()))

df_filtrado = df.copy()
if clientes: df_filtrado = df_filtrado[df_filtrado["Cliente"].isin(clientes)]
if artigos: df_filtrado = df_filtrado[df_filtrado["Artigo"].isin(artigos)]
if comerciais: df_filtrado = df_filtrado[df_filtrado["Comercial"].isin(comerciais)]
if categorias: df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categorias)]
if meses: df_filtrado = df_filtrado[df_filtrado["Mes"].isin(meses)]
if anos: df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos)]

# Validação de colunas
colunas_esperadas = ["Qtd", "V_Liquido"]
colunas_faltantes = [col for col in colunas_esperadas if col not in df_filtrado.columns]
if colunas_faltantes:
    st.error(f"❌ As seguintes colunas estão ausentes: {', '.join(colunas_faltantes)}")
    st.stop()

# Conversão segura
df_filtrado["V_Liquido"] = (
    df_filtrado["V_Liquido"]
    .astype(str)
    .str.replace(",", ".")
    .str.replace("€", "")
    .str.strip()
)
df_filtrado["V_Liquido"] = pd.to_numeric(df_filtrado["V_Liquido"], errors="coerce")
df_filtrado["Qtd"] = pd.to_numeric(df_filtrado["Qtd"], errors="coerce")

# Validação de dados
if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# KPIs
total_vendas = df_filtrado["V_Liquido"].sum()
total_qtd = df_filtrado["Qtd"].sum()
ticket_medio = total_vendas / total_qtd if total_qtd else 0

col1, col2, col3 = st.columns(3)
col1.metric("💰 Valor Líquido Total", f"€ {total_vendas:,.2f}")
col2.metric("📦 Quantidade Total", f"{total_qtd:,.0f}")
col3.metric("🎯 Ticket Médio", f"€ {ticket_medio:,.2f}")

# Evolução
st.subheader("📈 Evolução de Vendas por Mês e Ano")
evolucao = df_filtrado.groupby(["Ano", "Mes"]).agg({"V_Liquido": "sum"}).reset_index()
chart = alt.Chart(evolucao).mark_line(point=True).encode(
    x=alt.X("Mes:O", title="Mês"),
    y=alt.Y("V_Liquido:Q", title="Valor Líquido (€)"),
    color="Ano:N"
).properties(width=700)
st.altair_chart(chart)

# Alertas de inatividade
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

# Variação percentual
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
# Exportação para Excel
st.subheader("📤 Exportar relatório completo para Excel")
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_filtrado.to_excel(writer, index=False, sheet_name='Vendas Filtradas')
    pd.DataFrame({
        "Indicador": ["Valor Líquido Total", "Quantidade Total", "Ticket Médio"],
        "Valor": [total_vendas, total_qtd, ticket_medio]
    }).to_excel(writer, index=False, sheet_name='KPIs')
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

    # Segmentações
    for nome, grupo, tipo in [
        ("Por Categoria", "Categoria", "column"),
        ("Por Comercial", "Comercial", "bar"),
        ("Top 10 Clientes", "Cliente", "column"),
        ("Top 10 Artigos", "Artigo", "column")
    ]:
        df_seg = df_filtrado.groupby(grupo).agg({"Qtd": "sum", "V_Liquido": "sum"}).reset_index()
        if "Top" in nome:
            df_seg = df_seg.sort_values("V_Liquido", ascending=False).head(10)
        df_seg.to_excel(writer, index=False, sheet_name=nome)
        chart = workbook.add_chart({'type': tipo})
        chart.add_series({
            'name': 'Valor Líquido',
            'categories': [nome, 1, 0, len(df_seg), 0],
            'values': [nome, 1, 2, len(df_seg), 2],
        })
        chart.set_title({'name': f'{nome} por Vendas'})
        writer.sheets[nome].insert_chart('E5', chart)

    # Resumo mensal
    mesano_df = df_filtrado.groupby(["Ano", "Mes"]).agg({"Qtd": "sum", "V_Liquido": "sum"}).reset_index()
    mesano_df.to_excel(writer, index=False, sheet_name='Resumo Mensal')

    # Crescimento anual
    crescimento_df = df_filtrado.groupby("Ano").agg({"V_Liquido": "sum"}).reset_index()
    crescimento_df["Crescimento (%)"] = crescimento_df["V_Liquido"].pct_change() * 100
    crescimento_df.to_excel(writer, index=False, sheet_name='Crescimento Anual')

    # Alertas e quedas
    variacoes_df.to_excel(writer, index=False, sheet_name='Alertas Variação Mensal')
    cliente_mes["Queda"] = cliente_mes["Variação (%)"].apply(lambda x: x < 0 if pd.notna(x) else False)
    cliente_mes["Queda Seq"] = cliente_mes.groupby("Cliente")["Queda"].cumsum()
    cliente_mes["Queda Flag"] = cliente_mes.groupby("Cliente")["Queda"].rolling(3).sum().reset_index(level=0, drop=True) >= 3
    quedas_df = cliente_mes[cliente_mes["Queda Flag"]].copy()
    quedas_df = quedas_df[["Cliente", "Ano", "Mes", "V_Liquido", "Variação (%)"]]
    quedas_df.to_excel(writer, index=False, sheet_name='Quedas Consecutivas')

    # Dispersão do Ticket Médio
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
