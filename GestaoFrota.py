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
    for col in ['Combustivel', 'Portagem', 'Manutenção']:
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

# 🧭 Abas temáticas - ATUALIZADAS com nova aba de Abastecimentos
aba_combustivel, aba_portagem, aba_manutencao, aba_abastecimentos, aba_desvios = st.tabs([
    "⛽ Combustível", "🚧 Portagem", "🛠️ Manutenção", "🔄 Abastecimentos", "📊 Desvios"
])

# ⛽ Combustível
with aba_combustivel:
    st.header("⛽ Indicadores de Combustível")
    mostrar_metrica_segura("Gasto Médio com Combustível", df_filtrado['Combustivel'], "€")

    if selected_matriculas and len(selected_matriculas) > 1:
        # Gráfico de linhas comparando múltiplas viaturas
        combustivel_mes_matricula = df_filtrado.groupby(["Mês", "Matricula"])["Combustivel"].sum().reset_index()
        
        # Gráfico de linhas
        line_chart = alt.Chart(combustivel_mes_matricula).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X("Mês", sort=ordem_meses, title="Mês"),
            y=alt.Y("Combustivel", title="Combustível (€)"),
            color=alt.Color("Matricula", legend=alt.Legend(title="Matrícula")),
            tooltip=["Mês", "Matricula", "Combustivel"]
        ).properties(title="Comparação de Gastos com Combustível entre Viaturas", height=400)
        
        # Labels nos pontos
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
        # Gráfico original para uma única viatura
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
    mostrar_metrica_segura("Custo Médio de Portagem", df_filtrado['Portagem'], "€")

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
    mostrar_metrica_segura("Custo Médio de Manutenção", df_filtrado['Manutenção'], "€")

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

# 🔄 NOVA ABA: Abastecimentos
with aba_abastecimentos:
    st.header("🔄 Contagem de Abastecimentos por Viatura")
    
    # Calcular contagem de abastecimentos
    # Consideramos um abastecimento quando há valor positivo na coluna Combustivel
    df_abastecimentos = df_filtrado[df_filtrado['Combustivel'] > 0].copy()
    
    # Contagem total por viatura
    contagem_abastecimentos = df_abastecimentos.groupby('Matricula').size().reset_index(name='Total_Abastecimentos')
    
    # Contagem por viatura e mês
    contagem_mensal = df_abastecimentos.groupby(['Matricula', 'Mês']).size().reset_index(name='Abastecimentos')
    
    # KPIs principais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_abastecimentos = contagem_abastecimentos['Total_Abastecimentos'].sum()
        st.metric("Total de Abastecimentos", total_abastecimentos)
    
    with col2:
        media_por_viatura = contagem_abastecimentos['Total_Abastecimentos'].mean()
        st.metric("Média por Viatura", f"{media_por_viatura:.1f}")
    
    with col3:
        viatura_mais_abasteceu = contagem_abastecimentos.loc[contagem_abastecimentos['Total_Abastecimentos'].idxmax()]
        st.metric("Viatura com Mais Abastecimentos", 
                 f"{viatura_mais_abasteceu['Total_Abastecimentos']}",
                 delta=f"{viatura_mais_abasteceu['Matricula']}")
    
    # Gráfico de barras - Top viaturas por abastecimentos
    st.subheader("📊 Ranking de Abastecimentos por Viatura")
    
    # Ordenar por número de abastecimentos
    contagem_ordenada = contagem_abastecimentos.sort_values('Total_Abastecimentos', ascending=True)
    
    chart_barras = alt.Chart(contagem_ordenada).mark_bar(color='#4ECDC4').encode(
        x=alt.X('Total_Abastecimentos:Q', title='Número de Abastecimentos'),
        y=alt.Y('Matricula:N', sort='-x', title='Matrícula'),
        tooltip=['Matricula', 'Total_Abastecimentos']
    ).properties(
        title='Total de Abastecimentos por Viatura',
        height=400
    )
    
    # Adicionar labels nas barras
    text_barras = chart_barras.mark_text(
        align='left',
        baseline='middle',
        dx=3,
        color='black',
        fontWeight='bold'
    ).encode(
        text='Total_Abastecimentos:Q'
    )
    
    st.altair_chart(chart_barras + text_barras, use_container_width=True)
    
    # Evolução mensal dos abastecimentos
    st.subheader("📈 Evolução Mensal dos Abastecimentos")
    
    if selected_matriculas and len(selected_matriculas) > 1:
        # Gráfico de linhas para múltiplas viaturas
        line_chart = alt.Chart(contagem_mensal).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X('Mês', sort=ordem_meses, title='Mês'),
            y=alt.Y('Abastecimentos:Q', title='Número de Abastecimentos'),
            color=alt.Color('Matricula', legend=alt.Legend(title='Matrícula')),
            tooltip=['Mês', 'Matricula', 'Abastecimentos']
        ).properties(height=400)
        
        st.altair_chart(line_chart, use_container_width=True)
    else:
        # Gráfico de área para uma viatura ou total
        abastecimentos_mensais = contagem_mensal.groupby('Mês')['Abastecimentos'].sum().reindex(ordem_meses, fill_value=0).reset_index()
        
        area_chart = alt.Chart(abastecimentos_mensais).mark_area(
            color='lightblue',
            opacity=0.6,
            line={'color': 'darkblue', 'width': 2}
        ).encode(
            x=alt.X('Mês', sort=ordem_meses, title='Mês'),
            y=alt.Y('Abastecimentos:Q', title='Total de Abastecimentos'),
            tooltip=['Mês', 'Abastecimentos']
        ).properties(
            title='Evolução Mensal do Total de Abastecimentos',
            height=400
        )
        
        st.altair_chart(area_chart, use_container_width=True)
    
    # Tabela detalhada
    st.subheader("📋 Detalhamento por Viatura e Mês")
    
    # Criar tabela pivot
    pivot_table = contagem_mensal.pivot_table(
        values='Abastecimentos',
        index='Matricula',
        columns='Mês',
        aggfunc='sum',
        fill_value=0
    ).reindex(columns=ordem_meses, fill_value=0)
    
    # Adicionar total por viatura
    pivot_table['Total'] = pivot_table.sum(axis=1)
    
    # Ordenar por total
    pivot_table = pivot_table.sort_values('Total', ascending=False)
    
    # Formatar a tabela
    styled_table = pivot_table.style.background_gradient(
        cmap='YlGnBu', 
        subset=[col for col in pivot_table.columns if col != 'Total']
    ).format("{:.0f}")
    
    st.dataframe(styled_table, use_container_width=True)
    
    # Estatísticas adicionais
    st.subheader("📊 Estatísticas dos Abastecimentos")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        viaturas_com_abastecimentos = len(contagem_abastecimentos)
        st.metric("Viaturas com Abastecimentos", viaturas_com_abastecimentos)
    
    with col_stat2:
        max_abastecimentos_mes = contagem_mensal['Abastecimentos'].max()
        st.metric("Máx. Abastecimentos/Mês", max_abastecimentos_mes)
    
    with col_stat3:
        meses_com_abastecimentos = contagem_mensal['Mês'].nunique()
        st.metric("Meses com Abastecimentos", meses_com_abastecimentos)
    
    with col_stat4:
        viatura_menos_abasteceu = contagem_abastecimentos.loc[contagem_abastecimentos['Total_Abastecimentos'].idxmin()]
        st.metric("Menos Abastecimentos", 
                 f"{viatura_menos_abasteceu['Total_Abastecimentos']}",
                 delta=f"{viatura_menos_abasteceu['Matricula']}")

# 📊 Desvios (aba original mantida)
with aba_desvios:
    st.header("📊 Análise de Desvios e Comparações")
    
    # Seleção de métrica para análise
    metricas_opcoes = {
        "Combustível": "Combustivel",
        "Portagem": "Portagem", 
        "Manutenção": "Manutenção"
    }
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        selected_metrica = st.selectbox(
            "Selecione a Métrica para Análise",
            options=list(metricas_opcoes.keys()),
            index=0
        )
    
    with col_sel2:
        tipo_analise = st.radio(
            "Tipo de Análise",
            ["Comparação entre Viaturas", "Desvios Mensais"],
            horizontal=True
        )
    
    metrica_coluna = metricas_opcoes[selected_metrica]
    
    if tipo_analise == "Comparação entre Viaturas":
        st.subheader(f"📈 Comparação de {selected_metrica} entre Viaturas")
        
        if selected_matriculas and len(selected_matriculas) > 1:
            # Dados para comparação entre viaturas
            comparacao_mes_matricula = df_filtrado.groupby(["Mês", "Matricula"])[metrica_coluna].sum().reset_index()
            
            # Calcular média por mês para referência
            media_mensal = df_filtrado.groupby("Mês")[metrica_coluna].mean().reset_index()
            media_mensal['Matricula'] = 'Média'
            
            # Gráfico de comparação
            line_chart = alt.Chart(comparacao_mes_matricula).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X("Mês", sort=ordem_meses, title="Mês"),
                y=alt.Y(f"{metrica_coluna}:Q", title=f"{selected_metrica} (€)"),
                color=alt.Color("Matricula", legend=alt.Legend(title="Matrícula")),
                tooltip=["Mês", "Matricula", alt.Tooltip(metrica_coluna, format=".2f")]
            ).properties(title=f"Comparação de {selected_metrica} entre Viaturas", height=400)
            
            # Linha de média
            media_line = alt.Chart(media_mensal).mark_line(
                point=True, 
                strokeWidth=2, 
                strokeDash=[5,5],
                color='gray'
            ).encode(
                x=alt.X("Mês", sort=ordem_meses),
                y=alt.Y(f"{metrica_coluna}:Q"),
                tooltip=["Mês", alt.Tooltip(metrica_coluna, format=".2f", title="Média")]
            )
            
            # Labels para as linhas
            labels = alt.Chart(comparacao_mes_matricula).mark_text(
                align='center',
                baseline='bottom',
                dy=-10,
                fontSize=10,
                fontWeight='bold'
            ).encode(
                x=alt.X("Mês", sort=ordem_meses),
                y=alt.Y(f"{metrica_coluna}:Q"),
                text=alt.Text(f"{metrica_coluna}:Q", format=".1f"),
                color="Matricula"
            )
            
            chart = line_chart + media_line + labels
            st.altair_chart(chart, use_container_width=True)
            
            # Tabela de comparação
            st.subheader("📋 Tabela de Comparação")
            pivot_table = comparacao_mes_matricula.pivot_table(
                values=metrica_coluna,
                index='Mês',
                columns='Matricula',
                aggfunc='sum'
            ).reindex(ordem_meses)
            
            # Adicionar coluna de média
            pivot_table['Média'] = media_mensal[metrica_coluna].values
            
            # Formatar a tabela
            styled_table = pivot_table.style.format("{:.1f}").background_gradient(cmap='Blues')
            st.dataframe(styled_table, use_container_width=True)
            
        else:
            st.info("ℹ️ Selecione pelo menos 2 matrículas para comparação")
    
    else:  # Desvios Mensais
        st.subheader(f"📊 Análise de Desvios Mensais - {selected_metrica}")
        
        # Calcular totais mensais
        totais_mensais = df_filtrado.groupby("Mês")[metrica_coluna].sum().reindex(ordem_meses, fill_value=0)
        media_geral = totais_mensais.mean()
        
        # Calcular desvios
        desvios = totais_mensais - media_geral
        percentual_desvios = (desvios / media_geral) * 100
        
        # Criar DataFrame para análise
        analise_desvios = pd.DataFrame({
            'Mês': totais_mensais.index,
            'Total': totais_mensais.values,
            'Desvio_Absoluto': desvios.values,
            'Desvio_Percentual': percentual_desvios.values
        })
        
        # Gráfico de desvios
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            # Gráfico de totais com linha de média
            base = alt.Chart(analise_desvios).encode(
                x=alt.X('Mês', sort=ordem_meses, title='Mês')
            )
            
            bars = base.mark_bar(color='lightblue').encode(
                y=alt.Y('Total:Q', title=f'{selected_metrica} Total (€)'),
                tooltip=['Mês', 'Total']
            )
            
            media_line = base.mark_rule(color='red', strokeWidth=2, strokeDash=[5,5]).encode(
                y=alt.Y('mean(Total):Q', title='Média'),
                tooltip=[alt.Tooltip('mean(Total)', format='.2f', title='Média')]
            )
            
            chart_totais = (bars + media_line).properties(
                title=f'Totais Mensais vs Média ({media_geral:.2f}€)',
                height=300
            )
            st.altair_chart(chart_totais, use_container_width=True)
        
        with col_graf2:
            # Gráfico de desvios percentuais
            chart_desvios = alt.Chart(analise_desvios).mark_bar().encode(
                x=alt.X('Mês', sort=ordem_meses, title='Mês'),
                y=alt.Y('Desvio_Percentual:Q', title='Desvio Percentual (%)'),
                color=alt.condition(
                    alt.datum.Desvio_Percentual > 0,
                    alt.value('red'),  # Acima da média
                    alt.value('green')  # Abaixo da média
                ),
                tooltip=['Mês', 'Desvio_Percentual']
            ).properties(
                title='Desvio Percentual em Relação à Média',
                height=300
            )
            st.altair_chart(chart_desvios, use_container_width=True)
        
        # KPIs de desvio
        st.subheader("📈 Indicadores de Desvio")
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        
        with col_kpi1:
            mes_atual = selected_mes if selected_mes != "Todos" else ordem_meses[-1]
            valor_atual = totais_mensais.get(mes_atual, 0)
            desvio_atual = desvios.get(mes_atual, 0)
            percentual_atual = percentual_desvios.get(mes_atual, 0)
            
            st.metric(
                label=f"{selected_metrica} - {mes_atual}",
                value=f"{valor_atual:.1f}€",
                delta=f"{desvio_atual:+.1f}€ ({percentual_atual:+.1f}%)"
            )
        
        with col_kpi2:
            max_desvio_positivo = desvios.max()
            mes_max_positivo = desvios.idxmax()
            st.metric(
                label="Maior Desvio Positivo",
                value=f"{max_desvio_positivo:+.1f}€",
                delta=f"{mes_max_positivo}"
            )
        
        with col_kpi3:
            max_desvio_negativo = desvios.min()
            mes_max_negativo = desvios.idxmin()
            st.metric(
                label="Maior Desvio Negativo", 
                value=f"{max_desvio_negativo:+.1f}€",
                delta=f"{mes_max_negativo}"
            )
        
        with col_kpi4:
            variacao = (totais_mensais.max() - totais_mensais.min()) / totais_mensais.min() * 100 if totais_mensais.min() > 0 else 0
            st.metric(
                label="Variação Anual",
                value=f"{variacao:.1f}%"
            )
        
        # Tabela detalhada de desvios
        st.subheader("📋 Detalhamento de Desvios Mensais")
        
        analise_desvios_formatada = analise_desvios.copy()
        analise_desvios_formatada['Total'] = analise_desvios_formatada['Total'].round(2)
        analise_desvios_formatada['Desvio_Absoluto'] = analise_desvios_formatada['Desvio_Absoluto'].round(2)
        analise_desvios_formatada['Desvio_Percentual'] = analise_desvios_formatada['Desvio_Percentual'].round(2)
        
        # Adicionar coluna de status
        analise_desvios_formatada['Status'] = analise_desvios_formatada['Desvio_Percentual'].apply(
            lambda x: '🔴 Acima da Média' if x > 5 else 
                     '🟢 Abaixo da Média' if x < -5 else 
                     '🟡 Na Média'
        )
        
        st.dataframe(
            analise_desvios_formatada,
            column_config={
                "Mês": "Mês",
                "Total": st.column_config.NumberColumn(
                    f"Total {selected_metrica} (€)",
                    format="%.2f"
                ),
                "Desvio_Absoluto": st.column_config.NumberColumn(
                    "Desvio Absoluto (€)",
                    format="%.2f"
                ),
                "Desvio_Percentual": st.column_config.NumberColumn(
                    "Desvio %",
                    format="%.2f%%"
                ),
                "Status": "Status"
            },
            use_container_width=True
        )

    # Função de KPI desvio
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

    # KPIs rápidos
    st.subheader("🚀 KPIs Rápidos - Todas as Métricas")
    col1, col2, col3 = st.columns(3)

    with col1:
        combustivel_mes = df_filtrado.groupby("Mês")["Combustivel"].sum().reindex(ordem_meses, fill_value=0)
        kpi_desvio("Combustível Total", combustivel_mes, "€")

    with col2:
        portagem_mes = df_filtrado.groupby("Mês")["Portagem"].sum().reindex(ordem_meses, fill_value=0)
        kpi_desvio("Portagem Total", portagem_mes, "€")

    with col3:
        manutencao_mes = df_filtrado.groupby("Mês")["Manutenção"].sum().reindex(ordem_meses, fill_value=0)
        kpi_desvio("Manutenção Total", manutencao_mes, "€")

# 📋 Visualização dos dados
st.sidebar.header("📋 Dados Filtrados")
if st.sidebar.checkbox("Mostrar dados filtrados"):
    st.subheader("📊 Dados Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

# 📈 Informações gerais
st.sidebar.header("ℹ️ Informações")
st.sidebar.info(f"**Total de registros:** {len(df_filtrado)}")
st.sidebar.info(f"**Período:** {df_filtrado['Mês'].min()} a {df_filtrado['Mês'].max()} {df_filtrado['Ano'].iloc[0]}")
