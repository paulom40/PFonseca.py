# 📊 Desvios
with aba_desvios:
    st.header("📊 Análise de Desvios e Comparações")
    
    # Seleção de métrica para análise
    metricas_opcoes = {
        "Consumo": "Consumo",
        "Portagem": "Portagem", 
        "Reparação": "Reparação",
        "Pneus": "Pneus"
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
                y=alt.Y(f"{metrica_coluna}:Q", title=f"{selected_metrica}"),
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
                y=alt.Y('Total:Q', title=f'{selected_metrica} Total'),
                tooltip=['Mês', 'Total']
            )
            
            media_line = base.mark_rule(color='red', strokeWidth=2, strokeDash=[5,5]).encode(
                y=alt.Y('mean(Total):Q', title='Média'),
                tooltip=[alt.Tooltip('mean(Total)', format='.2f', title='Média')]
            )
            
            chart_totais = (bars + media_line).properties(
                title=f'Totais Mensais vs Média ({media_geral:.2f})',
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
                value=f"{valor_atual:.1f}",
                delta=f"{desvio_atual:+.1f} ({percentual_atual:+.1f}%)"
            )
        
        with col_kpi2:
            max_desvio_positivo = desvios.max()
            mes_max_positivo = desvios.idxmax()
            st.metric(
                label="Maior Desvio Positivo",
                value=f"{max_desvio_positivo:+.1f}",
                delta=f"{mes_max_positivo}"
            )
        
        with col_kpi3:
            max_desvio_negativo = desvios.min()
            mes_max_negativo = desvios.idxmin()
            st.metric(
                label="Maior Desvio Negativo", 
                value=f"{max_desvio_negativo:+.1f}",
                delta=f"{mes_max_negativo}"
            )
        
        with col_kpi4:
            variacao = (totais_mensais.max() - totais_mensais.min()) / totais_mensais.min() * 100
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
                    f"Total {selected_metrica}",
                    format="%.2f"
                ),
                "Desvio_Absoluto": st.column_config.NumberColumn(
                    "Desvio Absoluto",
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

    # Função original de KPI desvio (mantida para compatibilidade)
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

    # KPIs rápidos originais
    st.subheader("🚀 KPIs Rápidos - Todas as Métricas")
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
