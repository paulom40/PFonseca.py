import streamlit as st
import pandas as pd
import altair as alt
import io
import base64

# 🎨 Configuração visual
st.set_page_config(
    layout="wide",
    page_title="Dashboard da Frota",
    page_icon="🚘",
    initial_sidebar_state="expanded"
)



# 📂 Carregar dados
url = "https://github.com/paulom40/PFonseca.py/raw/main/frota.xlsx"
try:
    df = pd.read_excel(url, sheet_name="Dados")
    df.columns = df.columns.str.strip()

    # 🔄 Converter colunas numéricas
    for col in ['Consumo', 'Portagem', 'Reparação', 'Pneus']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 🗓️ Corrigir ordem dos meses
    ordem_meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    df["Mês"] = pd.Categorical(df["Mês"], categories=ordem_meses, ordered=True)

    st.success("✅ Dados da frota carregados com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {e}")
    st.stop()

# 🔧 Função reutilizável para métricas seguras
def mostrar_metrica_segura(label, serie, unidade=""):
    valor = pd.to_numeric(serie, errors='coerce').mean()
    if pd.isna(valor):
        st.metric(label, "—")
    else:
        st.metric(label, f"{valor:.2f} {unidade}")

# 🎛️ Filtros
st.sidebar.header("🔍 Filtros")
marcas = sorted(df['Marca'].dropna().unique())
selected_marca = st.sidebar.selectbox("Marca", ["Todas"] + marcas)

matriculas = sorted(df['Matricula'].dropna().unique())
selected_matricula = st.sidebar.selectbox("Matrícula", ["Todas"] + matriculas)

anos = sorted(df['Ano'].dropna().unique())
selected_ano = st.sidebar.selectbox("Ano", ["Todos"] + list(map(str, anos)))

df_filtrado = df.copy()
if selected_marca != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Marca'] == selected_marca]
if selected_matricula != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Matricula'] == selected_matricula]
if selected_ano != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Ano'] == int(selected_ano)]

df_filtrado["Mês"] = pd.Categorical(df_filtrado["Mês"], categories=ordem_meses, ordered=True)

# 🧭 Abas temáticas
aba_combustivel, aba_portagem, aba_reparacao, aba_manutencao, aba_pneus = st.tabs([
    "⛽ Combustível", "🚧 Portagem", "🔧 Reparação", "🛠️ Manutenção", "🛞 Pneus"
])

# ⛽ Combustível
with aba_combustivel:
    st.header("⛽ Indicadores de Combustível")
    mostrar_metrica_segura("Consumo Médio", df_filtrado['Consumo'], "L/100km")

    consumo_mes = df_filtrado.groupby("Mês")["Consumo"].sum().reset_index()
    chart = alt.Chart(consumo_mes).mark_bar(color="#59a14f").encode(
        x=alt.X("Mês", sort=ordem_meses), y="Consumo", tooltip=["Mês", "Consumo"]
    ).properties(title="Consumo Total por Mês")
    st.altair_chart(chart, use_container_width=True)

# 🚧 Portagem
with aba_portagem:
    st.header("🚧 Indicadores de Portagem")
    mostrar_metrica_segura("Custo Médio de Portagem", df_filtrado['Portagem'], "€")

    portagem_mes = df_filtrado.groupby("Mês")["Portagem"].sum().reset_index()
    chart = alt.Chart(portagem_mes).mark_line(point=True, color="#f28e2b").encode(
        x=alt.X("Mês", sort=ordem_meses), y="Portagem", tooltip=["Mês", "Portagem"]
    ).properties(title="Portagem Total por Mês")
    st.altair_chart(chart, use_container_width=True)

# 🔧 Reparação
with aba_reparacao:
    st.header("🔧 Indicadores de Reparação")
    mostrar_metrica_segura("Custo Médio de Reparação", df_filtrado['Reparação'], "€")

    reparacao_mes = df_filtrado.groupby("Mês")["Reparação"].sum().reset_index()
    chart = alt.Chart(reparacao_mes).mark_area(color="#e15759").encode(
        x=alt.X("Mês", sort=ordem_meses), y="Reparação", tooltip=["Mês", "Reparação"]
    ).properties(title="Reparações por Mês")
    st.altair_chart(chart, use_container_width=True)

# 🛠️ Manutenção
with aba_manutencao:
    st.header("🛠️ Indicadores de Manutenção")
    pendentes = df_filtrado[df_filtrado['Manutenção'] == 'Pendente'].shape[0]
    st.metric("Manutenções Pendentes", pendentes)

    manutencao_mes = df_filtrado.groupby("Mês")["Manutenção"].apply(lambda x: (x == 'Pendente').sum()).reset_index(name="Pendentes")
    chart = alt.Chart(manutencao_mes).mark_bar(color="#9c755f").encode(
        x=alt.X("Mês", sort=ordem_meses), y="Pendentes", tooltip=["Mês", "Pendentes"]
    ).properties(title="Manutenções Pendentes por Mês")
    st.altair_chart(chart, use_container_width=True)

# 🛞 Pneus
with aba_pneus:
    st.header("🛞 Indicadores de Pneus")
    mostrar_metrica_segura("Custo Médio com Pneus", df_filtrado['Pneus'], "€")

    pneus_mes = df_filtrado.groupby("Mês")["Pneus"].sum().reset_index()
    chart = alt.Chart(pneus_mes).mark_bar(color="#76b7b2").encode(
        x=alt.X("Mês", sort=ordem_meses), y="Pneus", tooltip=["Mês", "Pneus"]
    ).properties(title="Despesas com Pneus por Mês")
    st.altair_chart(chart, use_container_width=True)

# 📥 Exportação para Excel
st.subheader("📥 Exportar dados da frota para Excel")

output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_filtrado.to_excel(writer, sheet_name='Frota Filtrada', index=False)
output.seek(0)

b64 = base64.b64encode(output.read()).decode()
href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="Frota_Filtrada.xlsx">📥 Baixar Excel</a>'
st.markdown(href, unsafe_allow_html=True)
