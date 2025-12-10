# Find this section in your code (around line 815) and replace it with this:

# Ensure data for the chart exists
if 'Data' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns and len(df_filtrado) > 0:
    try:
        # Prepare data - ensure Data_Dia is string type for plotting
        df_filtrado['Data_Dia'] = df_filtrado['Data'].dt.date.astype(str)
        vendas_diarias = df_filtrado.groupby('Data_Dia').agg({
            'V_Liquido': 'sum',
            'Quantidade': 'sum',
            'Entidade_Nome': 'nunique'
        }).reset_index()
        
        # Create the figure
        fig = go.Figure()
        
        # Add Vendas trace
        fig.add_trace(go.Scatter(
            x=vendas_diarias['Data_Dia'],
            y=vendas_diarias['V_Liquido'],
            mode='lines+markers',
            name='Vendas Líquidas (€)',
            line=dict(color='blue', width=2)
        ))
        
        # Add Quantidade trace on secondary y-axis
        fig.add_trace(go.Bar(
            x=vendas_diarias['Data_Dia'],
            y=vendas_diarias['Quantidade'],
            name='Quantidade Vendida',
            marker_color='lightblue',
            opacity=0.6,
            yaxis='y2'
        ))
        
        # Update layout with SAFE values (convert to string where needed)
        fig.update_layout(
            title=dict(text='📈 Evolução Diária de Vendas'),
            xaxis=dict(title='Data', type='category'),
            yaxis=dict(
                title='Vendas Líquidas (€)',
                titlefont=dict(color='blue'),
                tickfont=dict(color='blue')
            ),
            yaxis2=dict(
                title='Quantidade',
                titlefont=dict(color='lightblue'),
                tickfont=dict(color='lightblue'),
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            height=400,
            legend=dict(
                x=1.05,
                y=1,
                xanchor='left',
                yanchor='top'
            )
        )
        
        # Render the chart
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico de evolução diária: {str(e)}")
        # Show a simple error message and data preview
        st.info("Não foi possível gerar o gráfico. Verificando dados...")
        if 'df_filtrado' in locals():
            st.write("Preview dos dados:", df_filtrado[['Data', 'V_Liquido', 'Quantidade']].head())
else:
    st.warning("Dados insuficientes para gerar gráfico de evolução diária.")
