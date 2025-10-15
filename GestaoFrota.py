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

    for col in ['Consumo', 'Portagem', 'Reparação', 'Pneus']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    ordem_meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    df["Mês"] = pd.Categorical(df["Mês"], categories=ordem_meses, ordered=True)

    st.success("✅ Dados da frota carregados com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {e}")
    st.stop()

# 🔧 Função para métricas seguras
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
selected_matriculas = st.sidebar.multiselect("Selecione as Matrículas para Comparar", matriculas, default=matriculas[:2] if len(matriculas) >= 2 else matriculas)

anos = sorted(df['Ano'].dropna().unique())
selected_ano = st.sidebar.selectbox("Ano", ["Todos"] + list(map(str, anos)))

meses_disponiveis = df['Mês'].dropna().unique().tolist()
meses_ordenados = [mes for mes in ordem_meses if mes in meses_disponiveis]
selected_mes = st.sidebar.selectbox("Mês", ["Todos"] + meses_ordenados)

df_filtrado = df.copy()
if selected_marca != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Marca'] == selected_marca]
if selected_matriculas:
    df_filtrado = df_filtrado[df_filtrado['Matricula'].isin(selected_matriculas)]
if selected_ano != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Ano'] == int(selected_ano)]
if selected_mes != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Mês'] == selected_mes]

df_filtrado["Mês"] = pd.Categorical(df_filtrado["Mês"], categories=ordem_meses, ordered=True)

# 🧭 Abas temáticas
aba_combustivel, aba_portagem, aba_reparacao, aba_manutencao, aba_pneus, aba_desvios = st.tabs([
    "⛽ Combustível", "🚧 Portagem", "🔧 Reparação", "🛠️ Manutenção", "🛞 Pneus", "📊 Desvios"
])

# ⛽ Combustível
with aba_combustivel:
    st.header("⛽ Indicadores de Combustível")
    mostrar_metrica_segura("Consumo Médio", df_filtrado['Consumo'], "L/100km")

    if selected_matriculas and len(selected_matriculas) > 1:
        # Gráfico de linhas comparando múltiplas viaturas
        consumo_mes_matricula = df_filtrado.groupby(["Mês", "Matricula"])["Consumo"].sum().reset_index()
        chart = alt.Chart(consumo_mes_matricula).mark_line(point=True).encode(
            x=alt.X("Mês", sort=ordem_meses),
            y="Consumo",
            color="Matricula",
            tooltip=["Mês", "Matricula", "Consumo"]
        ).properties(title="Comparação de Consumo entre Viaturas", height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        # Gráfico original para uma única viatura
        consumo_mes = df_filtrado.groupby("Mês")["Consumo"].sum().reindex(ordem_meses, fill_value=0).reset_index()
        chart = alt.Chart(consumo_mes).mark_line(point=True, color="#59a14f").encode(
            x=alt.X("Mês", sort=ordem_meses), 
            y="Consumo", 
            tooltip=["Mês", "Consumo"]
        ).properties(title="Consumo Total por Mês", height=400)
        st.altair_chart(chart, use_container_width=True)

# 🚧 Portagem
with aba_portagem:
    st.header("🚧 Indicadores de Portagem")
    mostrar_metrica_segura("Custo Médio de Portagem", df_filtrado['Portagem'], "€")

    if selected_matriculas and len(selected_matriculas) > 1:
        portagem_mes_matricula = df_filtrado.groupby(["Mês", "Matricula"])["Portagem"].sum().reset_index()
        chart = alt.Chart(portagem_mes_matricula).mark_line(point=True).encode(
            x=alt.X("Mês", sort=ordem_meses),
            y="Portagem",
            color="Matricula",
            tooltip=["Mês", "Matricula", "Portagem"]
        ).properties(title="Comparação de Portagem entre Viaturas", height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        portagem_mes = df_filtrado.groupby("Mês")["Portagem"].sum().reindex(ordem_meses, fill_value=0).reset_index()
        chart = alt.Chart(portagem_mes).mark_line(point=True, color="#f28e2b").encode(
            x=alt.X("Mês", sort=ordem_meses), 
            y="Portagem", 
            tooltip=["Mês", "Portagem"]
        ).properties(title="Portagem Total por Mês", height=400)
        st.altair_chart(chart, use_container_width=True)

# 🔧 Reparação
with aba_reparacao:
    st.header("🔧 Indicadores de Reparação")
    mostrar_metrica_segura("Custo Médio de Reparação", df_filtrado['Reparação'], "€")

    if selected_matriculas and len(selected_matriculas) > 1:
        reparacao_mes_matricula = df_filtrado.groupby(["Mês", "Matricula"])["Reparação"].sum().reset_index()
        chart = alt.Chart(reparacao_mes_matricula).mark_line(point=True).encode(
            x=alt.X("Mês", sort=ordem_meses),
            y="Reparação",
            color="Matricula",
            tooltip=["Mês", "Matricula", "Reparação"]
        ).properties(title="Comparação de Reparações entre Viaturas", height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        reparacao_mes = df_filtrado.groupby("Mês")["Reparação"].sum().reindex(ordem_meses, fill_value=0).reset_index()
        chart = alt.Chart(reparacao_mes).mark_area(color="#e15759").encode(
            x=alt.X("Mês", sort=ordem_meses), 
            y="Reparação", 
            tooltip=["Mês", "Reparação"]
        ).properties(title="Reparações por Mês", height=400)
        st.altair_chart(chart, use_container_width=True)

# 🛠️ Manutenção
with aba_manutencao:
    st.header("🛠️ Indicadores de Manutenção")
    pendentes = df_filtrado[df_filtrado['Manutenção'] == 'Pendente'].shape[0]
    st.metric("Manutenções Pendentes", pendentes)

    if selected_matriculas and len(selected_matriculas) > 1:
        manutencao_mes_matricula = df_filtrado.groupby(["Mês", "Matricula"])["Manutenção"].apply(lambda x: (x == 'Pendente').sum()).reset_index(name="Pendentes")
        chart = alt.Chart(manutencao_mes_matricula).mark_line(point=True).encode(
            x=alt.X("Mês", sort=ordem_meses),
            y="Pendentes",
            color="Matricula",
            tooltip=["Mês", "Matricula", "Pendentes"]
        ).properties(title="Comparação de Manutenções Pendentes entre Viaturas", height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        manutencao_mes = df_filtrado.groupby("Mês")["Manutenção"].apply(lambda x: (x == 'Pendente').sum()).reindex(ordem_meses, fill_value=0).reset_index(name="Pendentes")
        chart = alt.Chart(manutencao_mes).mark_line(point=True, color="#9c755f").encode(
            x=alt.X("Mês", sort=ordem_meses), 
            y="Pendentes", 
            tooltip=["Mês", "Pendentes"]
        ).properties(title="Manutenções Pendentes por Mês", height=400)
        st.altair_chart(chart, use_container_width=True)

# 🛞 Pneus
with aba_pneus:
    st.header("🛞 Indicadores de Pneus")
    mostrar_metrica_segura("Custo Médio com Pneus", df_filtrado['Pneus'], "€")

    if selected_matriculas and len(selected_matriculas) > 1:
        pneus_mes_matricula = df_filtrado.groupby(["Mês", "Matricula"])["Pneus"].sum().reset_index()
        chart = alt.Chart(pneus_mes_matricula).mark_line(point=True).encode(
            x=alt.X("Mês", sort=ordem_meses),
            y="Pneus",
            color="Matricula",
            tooltip=["Mês", "Matricula", "Pneus"]
        ).properties(title="Comparação de Despesas com Pneus entre Viaturas", height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        pneus_mes = df_filtrado.groupby("Mês")["Pneus"].sum().reindex(ordem_meses, fill_value=0).reset_index()
        chart = alt.Chart(pneus_mes).mark_line(point=True, color="#76b7b2").encode(
            x=alt.X("Mês", sort=ordem_meses), 
            y="Pneus", 
            tooltip=["Mês", "Pneus"]
        ).properties(title="Despesas com Pneus por Mês", height=400)
        st.altair_chart(chart, use_container_width=True)

# 📊 Desvios
with aba_desvios:
    st.header("📊 Indicadores de Desvio Mensal")

    def kpi_desvio(label, serie, unidade=""):
        serie = pd.to_numeric(serie, errors='coerce')
        if serie.empty or serie.isna().all():
            st.metric(label, "—")
            return

        media = serie.mean()
        mes_filtro = selected_mes if selected_mes != "Todos" else ordem_meses[-1]
        valor_mes = serie.get(mes_filtro, 0)
        desvio = valor_mes - media
        delta = f"{'🔺' if desvio > 0 else '🔻'} {desvio:.2f} {unidade}"
        cor = "#fdd835" if desvio > 0 else "#66bb6a"

        st.markdown(f"<div style='background-color:{cor};padding:10px;border-radius:8px;text-align:center'>", unsafe_allow_html=True)
        st.metric(label, f"{valor_mes:.2f} {unidade}", delta=delta)
        st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        consumo_mes = df_filtrado.groupby("Mês")["Consumo"].sum().reindex(ordem_meses, fill_value=0)
        kpi_desvio("Consumo Total", consumo_mes, "L")

    with col2:
        portagem_mes = df_filtrado.groupby("Mês")["Portagem"].sum().reindex(ordem_meses, fill_value=0)
        kpi_desvio("Portagem Total", portagem_mes, "€")

    with col3:
        reparacao_mes = df_filtrado.groupby("Mês")["Reparação"].sum().reindex(ordem_meses, fill_value=0)
        kpi_desvio("Reparação Total", reparacao_mes, "€")

    with col4:
        pneus_mes = df_filtrado.groupby("Mês")["Pneus"].sum().reindex(ordem_meses, fill_value=0)
        kpi_desvio("Pneus Total", pneus_mes, "€")
