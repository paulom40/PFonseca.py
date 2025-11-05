elif pagina == "TENDÊNCIAS":
    st.markdown("<h1>Tendências & Previsão</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        metrica = st.selectbox("Métrica", ["Quantidade (kg)", "Valor (€)"])
    with col2:
        janela = st.slider("Média Móvel", 1, 6, 3)
    
    # --- Preparar dados ---
    temp = dados.copy()
    temp['data'] = pd.to_datetime(temp['ano'].astype(str) + '-' + temp['mes'].astype(str).str.zfill(2) + '-01')
    temp = temp.sort_values('data')
    
    if "kg" in metrica:
        serie = temp.groupby('data')['qtd'].sum()
        y_label = "Quantidade (kg)"
        fmt_func = fmt_kg
    else:
        serie = temp.groupby('data')['v_liquido'].sum()
        y_label = "Valor (€)"
        fmt_func = fmt_euro

    if serie.empty:
        st.warning("Nenhum dado para exibir.")
        st.stop()

    # --- Média Móvel ---
    ma = serie.rolling(window=janela, center=True).mean()

    # --- Modelo de Previsão (ARIMA) ---
    from statsmodels.tsa.arima.model import ARIMA
    import warnings
    warnings.filterwarnings("ignore")

    try:
        # Ajustar ARIMA (p=5, d=1, q=0) - bom para vendas mensais
        model = ARIMA(serie, order=(5,1,0))
        model_fit = model.fit()

        # Prever próximos 6 meses
        forecast_steps = 6
        forecast_result = model_fit.get_forecast(steps=forecast_steps)
        forecast = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int()

        # Criar índice futuro
        last_date = serie.index[-1]
        future_dates = pd.date_range(last_date + pd.DateOffset(months=1), periods=forecast_steps, freq='MS')

        # --- Gráfico com Previsão ---
        fig = go.Figure()

        # Dados reais
        fig.add_trace(go.Scatter(
            x=serie.index, y=serie, mode='lines+markers', name='Real',
            line=dict(color="#4f46e5", width=3)
        ))

        # Média móvel
        fig.add_trace(go.Scatter(
            x=ma.index, y=ma, mode='lines', name=f'Média Móvel {janela}m',
            line=dict(color="#7c3aed", dash='dash', width=2)
        ))

        # Previsão
        fig.add_trace(go.Scatter(
            x=future_dates, y=forecast, mode='lines+markers', name='Previsão',
            line=dict(color="#10b981", width=3)
        ))

        # Intervalo de confiança
        fig.add_trace(go.Scatter(
            x=list(future_dates) + list(future_dates)[::-1],
            y=list(conf_int.iloc[:, 1]) + list(conf_int.iloc[:, 0])[::-1],
            fill='toself', fillcolor='rgba(16,185,129,0.2)',
            line=dict(color='rgba(255,255,255,0)'), name='95% Confiança',
            showlegend=True
        ))

        fig.update_layout(
            title=f"Previsão: {y_label}",
            xaxis_title="Data",
            yaxis_title=y_label,
            height=600,
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)', bordercolor='gray', borderwidth=1),
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

        # --- Exibir Previsão em Tabela ---
        st.markdown("### Previsão para os Próximos 6 Meses")
        forecast_df = pd.DataFrame({
            'Mês': future_dates.strftime('%b/%Y'),
            'Previsão': forecast,
            'Mínimo (95%)': conf_int.iloc[:, 0],
            'Máximo (95%)': conf_int.iloc[:, 1]
        })
        forecast_df['Previsão'] = forecast_df['Previsão'].apply(fmt_func)
        forecast_df['Mínimo (95%)'] = forecast_df['Mínimo (95%)'].apply(fmt_func)
        forecast_df['Máximo (95%)'] = forecast_df['Máximo (95%)'].apply(fmt_func)
        st.dataframe(forecast_df, use_container_width=True)

    except Exception as e:
        st.error(f"Previsão não disponível: {str(e)}")
        # Gráfico sem previsão
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=serie.index, y=serie, mode='lines+markers', name='Real', line=dict(color="#4f46e5")))
        fig.add_trace(go.Scatter(x=ma.index, y=ma, mode='lines', name=f'Média {janela}m', line=dict(color="#7c3aed", dash='dash')))
        fig.update_layout(title=f"Tendência: {y_label}", height=500)
        st.plotly_chart(fig, use_container_width=True)
