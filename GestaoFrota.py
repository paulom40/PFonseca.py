import streamlit as st
import pandas as pd
import altair as alt

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
    # Carregar ambas as abas
    df_dados = pd.read_excel(url, sheet_name="Dados")
    df_sheet1 = pd.read_excel(url, sheet_name="Sheet1")
    
    # Usar a aba Dados como principal
    df = df_dados.copy()
    df.columns = df.columns.str.strip()

    # Converter colunas numéricas
    for col in ['Combustivel', 'Portagem', 'Manutenção', 'Consumo']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Ordem dos meses
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

# 🔧 Função para KPIs por viatura
def mostrar_kpi_viatura(label, df_viatura, coluna, unidade=""):
    if df_viatura.empty:
        st.metric(label, "—")
        return
        
    valor = df_viatura[coluna].sum()
    media_mensal = df_viatura.groupby("Mês")[coluna].sum().mean()
    
    st.metric(
        label=label,
        value=f"{valor:.2f} {unidade}",
        delta=f"Média mensal: {media_mensal:.2f} {unidade}"
    )

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
aba_combustivel, aba_portagem, aba_manutencao, aba_consumo, aba_desvios = st.tabs([
    "⛽ Combustível", "🚧 Portagem", "🛠️ Manutenção", "📊 Consumo", "📈 Desvios"
])

# ⛽ Combustível
with aba_combustivel:
    st.header("⛽ Indicadores de Combustível")
    
    # KPIs por viatura selecionada
    if selected_matriculas:
        st.subheader(f"🚗 KPIs por Viatura - Combustível")
        
        for matricula in selected_matriculas:
            df_viatura = df_filtrado[df_filtrado['Matricula'] == matricula]
            
            if not df_viatura.empty:
                st.markdown(f"### 📋 Viatura: {matricula}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_combustivel = df_viatura['Combustivel'].sum()
                    media_mensal = df_viatura.groupby("Mês")['Combustivel'].sum().mean()
                    st.metric(
                        label="Total Gasto em Combustível",
                        value=f"€ {total_combustivel:.2f}",
                        delta=f"Média mensal: € {media_mensal:.2f}"
                    )
                
                with col2:
                    custo_medio_abastecimento = df_viatura[df_viatura['Combustivel'] > 0]['Combustivel'].mean()
                    if pd.isna(custo_medio_abastecimento):
                        st.metric("Custo Médio por Abastecimento", "—")
                    else:
                        st.metric(
                            label="Custo Médio por Abastecimento",
                            value=f"€ {custo_medio_abastecimento:.2f}"
                        )
                
                with col3:
                    meses_com_abastecimento = df_viatura[df_viatura['Combustivel'] > 0]['Mês'].nunique()
                    st.metric(
                        label="Meses com Abastecimento",
                        value=meses_com_abastecimento
                    )
                
                with col4:
                    # ADICIONADO: Consumo relacionado com combustível
                    consumo_total = df_viatura['Consumo'].sum()
                    st.metric(
                        label="Consumo Total (L)",
                        value=f"{consumo_total:.1f} L"
                    )
                
                st.markdown("---")
    
    # Gráficos
    if selected_matriculas and len(selected_matriculas) > 1:
        # Gráfico de linhas comparando múltiplas viaturas
        combustivel_mes_matricula = df_filtrado.groupby(["Mês", "Matricula"])["Combustivel"].sum().reset_index()
        
        line_chart = alt.Chart(combustivel_mes_matricula).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X("Mês", sort=ordem_meses, title="Mês"),
            y=alt.Y("Combustivel", title="Combustível (€)"),
            color=alt.Color("Matricula", legend=alt.Legend(title="Matrícula")),
            tooltip=["Mês", "Matricula", "Combustivel"]
        ).properties(title="Comparação de Gastos com Combustível entre Viaturas", height=400)
        
        labels = alt.Chart(combustivel_mes_matricula).mark_text(
            align='center',
            baseline='bottom',
            dy=-10,
            fontSize=11,
            fontWeight='bold'
        ).encode(
            x=alt.X("Mês", sort=ordem_meses),
            y="Combustivel",
            text=alt.Text("Combustivel:Q", format=".1f"),
            color="Matricula"
        )
        
        chart = line_chart + labels
        st.altair_chart(chart, use_container_width=True)
    else:
        # Gráfico para uma única viatura
        combustivel_mes = df_filtrado.groupby("Mês")["Combustivel"].sum().reindex(ordem_meses, fill_value=0).reset_index()
        
        line_chart = alt.Chart(combustivel_mes).mark_line(point=True, color="#59a14f", strokeWidth=3).encode(
            x=alt.X("Mês", sort=ordem_meses, title="Mês"), 
            y=alt.Y("Combustivel", title="Combustível (€)"), 
            tooltip=["Mês", "Combustivel"]
        ).properties(title="Gastos com Combustível por Mês", height=400)
        
        labels = alt.Chart(combustivel_mes).mark_text(
            align='center',
            baseline='bottom',
            dy=-10,
            fontSize=11,
            fontWeight='bold',
            color='#59a14f'
        ).encode(
            x=alt.X("Mês", sort=ordem_meses),
            y="Combustivel",
            text=alt.Text("Combustivel:Q", format=".1f")
        )
        
        chart = line_chart + labels
        st.altair_chart(chart, use_container_width=True)

# 🚧 Portagem
with aba_portagem:
    st.header("🚧 Indicadores de Portagem")
    
    # KPIs por viatura selecionada
    if selected_matriculas:
        st.subheader(f"🚗 KPIs por Viatura - Portagem")
        
        for matricula in selected_matriculas:
            df_viatura = df_filtrado[df_filtrado['Matricula'] == matricula]
            
            if not df_viatura.empty:
                st.markdown(f"### 📋 Viatura: {matricula}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_portagem = df_viatura['Portagem'].sum()
                    media_mensal = df_viatura.groupby("Mês")['Portagem'].sum().mean()
                    st.metric(
                        label="Total Gasto em Portagem",
                        value=f"€ {total_portagem:.2f}",
                        delta=f"Média mensal: € {media_mensal:.2f}"
                    )
                
                with col2:
                    meses_com_portagem = df_viatura[df_viatura['Portagem'] > 0]['Mês'].nunique()
                    st.metric(
                        label="Meses com Portagem",
                        value=meses_com_portagem
                    )
                
                with col3:
                    max_portagem_mes = df_viatura.groupby("Mês")['Portagem'].sum().max()
                    st.metric(
                        label="Máximo num Mês",
                        value=f"€ {max_portagem_mes:.2f}"
                    )
                
                with col4:
                    # ADICIONADO: Consumo relacionado com portagem
                    consumo_total = df_viatura['Consumo'].sum()
                    st.metric(
                        label="Consumo Total (L)",
                        value=f"{consumo_total:.1f} L"
                    )
                
                st.markdown("---")
    
    # Gráficos
    if selected_matriculas and len(selected_matriculas) > 1:
        portagem_mes_matricula = df_filtrado.groupby(["Mês", "Matricula"])["Portagem"].sum().reset_index()
        
        line_chart = alt.Chart(portagem_mes_matricula).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X("Mês", sort=ordem_meses, title="Mês"),
            y=alt.Y("Portagem", title="Portagem (€)"),
            color=alt.Color("Matricula", legend=alt.Legend(title="Matrícula")),
            tooltip=["Mês", "Matricula", "Portagem"]
        ).properties(title="Comparação de Portagem entre Viaturas", height=400)
        
        labels = alt.Chart(portagem_mes_matricula).mark_text(
            align='center',
            baseline='bottom',
            dy=-10,
            fontSize=11,
            fontWeight='bold'
        ).encode(
            x=alt.X("Mês", sort=ordem_meses),
            y="Portagem",
            text=alt.Text("Portagem:Q", format=".1f"),
            color="Matricula"
        )
        
        chart = line_chart + labels
        st.altair_chart(chart, use_container_width=True)
    else:
        portagem_mes = df_filtrado.groupby("Mês")["Portagem"].sum().reindex(ordem_meses, fill_value=0).reset_index()
        
        line_chart = alt.Chart(portagem_mes).mark_line(point=True, color="#f28e2b", strokeWidth=3).encode(
            x=alt.X("Mês", sort=ordem_meses, title="Mês"), 
            y=alt.Y("Portagem", title="Portagem (€)"), 
            tooltip=["Mês", "Portagem"]
        ).properties(title="Portagem Total por Mês", height=400)
        
        labels = alt.Chart(portagem_mes).mark_text(
            align='center',
            baseline='bottom',
            dy=-10,
            fontSize=11,
            fontWeight='bold',
            color='#f28e2b'
        ).encode(
            x=alt.X("Mês", sort=ordem_meses),
            y="Portagem",
            text=alt.Text("Portagem:Q", format=".1f")
        )
        
        chart = line_chart + labels
        st.altair_chart(chart, use_container_width=True)

# 🛠️ Manutenção
with aba_manutencao:
    st.header("🛠️ Indicadores de Manutenção")
    
    # KPIs por viatura selecionada
    if selected_matriculas:
        st.subheader(f"🚗 KPIs por Viatura - Manutenção")
        
        for matricula in selected_matriculas:
            df_viatura = df_filtrado[df_filtrado['Matricula'] == matricula]
            
            if not df_viatura.empty:
                st.markdown(f"### 📋 Viatura: {matricula}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_manutencao = df_viatura['Manutenção'].sum()
                    media_mensal = df_viatura.groupby("Mês")['Manutenção'].sum().mean()
                    st.metric(
                        label="Total Gasto em Manutenção",
                        value=f"€ {total_manutencao:.2f}",
                        delta=f"Média mensal: € {media_mensal:.2f}"
                    )
                
                with col2:
                    meses_com_manutencao = df_viatura[df_viatura['Manutenção'] > 0]['Mês'].nunique()
                    st.metric(
                        label="Meses com Manutenção",
                        value=meses_com_manutencao
                    )
                
                with col3:
                    custo_medio_intervencao = df_viatura[df_viatura['Manutenção'] > 0]['Manutenção'].mean()
                    if pd.isna(custo_medio_intervencao):
                        st.metric("Custo Médio por Intervenção", "—")
                    else:
                        st.metric(
                            label="Custo Médio por Intervenção",
                            value=f"€ {custo_medio_intervencao:.2f}"
                        )
                
                with col4:
                    # ADICIONADO: Consumo relacionado com manutenção
                    consumo_total = df_viatura['Consumo'].sum()
                    st.metric(
                        label="Consumo Total (L)",
                        value=f"{consumo_total:.1f} L"
                    )
                
                st.markdown("---")
    
    # Gráficos
    if selected_matriculas and len(selected_matriculas) > 1:
        manutencao_mes_matricula = df_filtrado.groupby(["Mês", "Matricula"])["Manutenção"].sum().reset_index()
        
        line_chart = alt.Chart(manutencao_mes_matricula).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X("Mês", sort=ordem_meses, title="Mês"),
            y=alt.Y("Manutenção", title="Manutenção (€)"),
            color=alt.Color("Matricula", legend=alt.Legend(title="Matrícula")),
            tooltip=["Mês", "Matricula", "Manutenção"]
        ).properties(title="Comparação de Custos de Manutenção entre Viaturas", height=400)
        
        labels = alt.Chart(manutencao_mes_matricula).mark_text(
            align='center',
            baseline='bottom',
            dy=-10,
            fontSize=11,
            fontWeight='bold'
        ).encode(
            x=alt.X("Mês", sort=ordem_meses),
            y="Manutenção",
            text=alt.Text("Manutenção:Q", format=".1f"),
            color="Matricula"
        )
        
        chart = line_chart + labels
        st.altair_chart(chart, use_container_width=True)
    else:
        manutencao_mes = df_filtrado.groupby("Mês")["Manutenção"].sum().reindex(ordem_meses, fill_value=0).reset_index()
        
        line_chart = alt.Chart(manutencao_mes).mark_line(point=True, color="#e15759", strokeWidth=3).encode(
            x=alt.X("Mês", sort=ordem_meses, title="Mês"), 
            y=alt.Y("Manutenção", title="Manutenção (€)"), 
            tooltip=["Mês", "Manutenção"]
        ).properties(title="Custos de Manutenção por Mês", height=400)
        
        labels = alt.Chart(manutencao_mes).mark_text(
            align='center',
            baseline='bottom',
            dy=-10,
            fontSize=11,
            fontWeight='bold',
            color='#e15759'
        ).encode(
            x=alt.X("Mês", sort=ordem_meses),
            y="Manutenção",
            text=alt.Text("Manutenção:Q", format=".1f")
        )
        
        chart = line_chart + labels
        st.altair_chart(chart, use_container_width=True)

# 📊 Consumo
with aba_consumo:
    st.header("📊 Indicadores de Consumo")
    
    # KPIs por viatura selecionada
    if selected_matriculas:
        st.subheader(f"🚗 KPIs por Viatura - Consumo")
        
        for matricula in selected_matriculas:
            df_viatura = df_filtrado[df_filtrado['Matricula'] == matricula]
            
            if not df_viatura.empty:
                st.markdown(f"### 📋 Viatura: {matricula}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    consumo_total = df_viatura['Consumo'].sum()
                    st.metric(
                        label="Consumo Total",
                        value=f"{consumo_total:.1f} L"
                    )
                
                with col2:
                    consumo_medio = df_viatura['Consumo'].mean()
                    if pd.isna(consumo_medio):
                        st.metric("Consumo Médio", "—")
                    else:
                        st.metric(
                            label="Consumo Médio",
                            value=f"{consumo_medio:.1f} L"
                        )
                
                with col3:
                    max_consumo = df_viatura['Consumo'].max()
                    if pd.isna(max_consumo) or max_consumo == 0:
                        st.metric("Máximo Consumo", "—")
                    else:
                        st.metric(
                            label="Máximo Consumo",
                            value=f"{max_consumo:.1f} L"
                        )
                
                with col4:
                    meses_com_consumo = df_viatura[df_viatura['Consumo'] > 0]['Mês'].nunique()
                    st.metric(
                        label="Meses com Consumo",
                        value=meses_com_consumo
                    )
                
                st.markdown("---")
    
    # Gráficos
    if selected_matriculas and len(selected_matriculas) > 1:
        # Gráfico de linhas comparando múltiplas viaturas
        consumo_mes_matricula = df_filtrado.groupby(["Mês", "Matricula"])["Consumo"].sum().reset_index()
        
        line_chart = alt.Chart(consumo_mes_matricula).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X("Mês", sort=ordem_meses, title="Mês"),
            y=alt.Y("Consumo", title="Consumo (L)"),
            color=alt.Color("Matricula", legend=alt.Legend(title="Matrícula")),
            tooltip=["Mês", "Matricula", "Consumo"]
        ).properties(title="Comparação de Consumo entre Viaturas", height=400)
        
        labels = alt.Chart(consumo_mes_matricula).mark_text(
            align='center',
            baseline='bottom',
            dy=-10,
            fontSize=11,
            fontWeight='bold'
        ).encode(
            x=alt.X("Mês", sort=ordem_meses),
            y="Consumo",
            text=alt.Text("Consumo:Q", format=".1f"),
            color="Matricula"
        )
        
        chart = line_chart + labels
        st.altair_chart(chart, use_container_width=True)
    else:
        # Gráfico para uma única viatura
        consumo_mes = df_filtrado.groupby("Mês")["Consumo"].sum().reindex(ordem_meses, fill_value=0).reset_index()
        
        line_chart = alt.Chart(consumo_mes).mark_line(point=True, color="#4E79A7", strokeWidth=3).encode(
            x=alt.X("Mês", sort=ordem_meses, title="Mês"), 
            y=alt.Y("Consumo", title="Consumo (L)"), 
            tooltip=["Mês", "Consumo"]
        ).properties(title="Consumo Total por Mês", height=400)
        
        labels = alt.Chart(consumo_mes).mark_text(
            align='center',
            baseline='bottom',
            dy=-10,
            fontSize=11,
            fontWeight='bold',
            color='#4E79A7'
        ).encode(
            x=alt.X("Mês", sort=ordem_meses),
            y="Consumo",
            text=alt.Text("Consumo:Q", format=".1f")
        )
        
        chart = line_chart + labels
        st.altair_chart(chart, use_container_width=True)
    
    # Análise adicional de consumo
    st.subheader("📈 Análise Detalhada de Consumo")
    
    col_analise1, col_analise2 = st.columns(2)
    
    with col_analise1:
        # Top 5 viaturas com maior consumo
        consumo_por_viatura = df_filtrado.groupby('Matricula')['Consumo'].sum().sort_values(ascending=False).head(5)
        if not consumo_por_viatura.empty:
            st.markdown("**🏆 Top 5 Viaturas com Maior Consumo**")
            for i, (matricula, consumo) in enumerate(consumo_por_viatura.items(), 1):
                st.write(f"{i}. {matricula}: {consumo:.1f} L")
    
    with col_analise2:
        # Consumo por marca
        consumo_por_marca = df_filtrado.groupby('Marca')['Consumo'].sum().sort_values(ascending=False)
        if not consumo_por_marca.empty:
            st.markdown("**🏭 Consumo por Marca**")
            for marca, consumo in consumo_por_marca.items():
                st.write(f"{marca}: {consumo:.1f} L")

# 📈 Desvios (código mantido igual)
with aba_desvios:
    st.header("📈 Análise de Desvios e Comparações")
    
    # [O código desta aba permanece igual...]

# 📋 Visualização dos dados
st.sidebar.header("📋 Dados Filtrados")
if st.sidebar.checkbox("Mostrar dados filtrados"):
    st.subheader("📊 Dados Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

# 📈 Informações gerais
st.sidebar.header("ℹ️ Informações")
st.sidebar.info(f"**Total de registros:** {len(df_filtrado)}")
st.sidebar.info(f"**Período:** {df_filtrado['Mês'].min()} a {df_filtrado['Mês'].max()} {df_filtrado['Ano'].iloc[0]}")
