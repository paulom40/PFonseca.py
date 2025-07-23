import streamlit as st
import altair as alt
import pandas as pd
import io

def render(df, filtered_df, quantity_col, selected_ano):
    st.title("📊 Tendências Mensais")

    # 🚨 Avisar sobre anos em falta
    missing_years = set(selected_ano) - set(df['ANO'].dropna().unique())
    if missing_years:
        st.warning(f"⚠️ Os dados originais não contêm os anos: {', '.join(map(str, missing_years))}. Adicionados como placeholders.")

    # 📋 Tabela
    st.write("### 📋 Dados Filtrados")
    st.dataframe(filtered_df)

    # 🔢 Indicadores (excluindo anos irrelevantes)
    st.write("### 🔢 Indicadores")
    excluded_years = [2023, 2024, 2025]
    indicator_df = filtered_df[~filtered_df['ANO'].isin(excluded_years)]

    st.metric("📦 Quantidade Total", f"{indicator_df[quantity_col].sum():,.2f}")

    if 'PM' in indicator_df.columns and not indicator_df['PM'].isna().all():
        st.metric("💰 Preço Médio", f"€{indicator_df['PM'].mean():,.2f}")
    else:
        st.info("ℹ️ Coluna 'PM' ausente ou sem dados válidos.")

    # 📥 Download Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Filtrado')

    st.download_button(
        label="📥 Baixar dados filtrados em Excel",
        data=excel_buffer.getvalue(),
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 📈 Gráfico de linhas de quantidade
    ordered_months = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
                      'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    chart_df = filtered_df.copy()
    chart_df['MÊS'] = pd.Categorical(chart_df['MÊS'], categories=ordered_months, ordered=True)

    pivot_data = chart_df.groupby(['MÊS', 'ANO'])[quantity_col].sum().reset_index()

    line_chart = alt.Chart(pivot_data).mark_line(point=True).encode(
        x='MÊS:N', y=f'{quantity_col}:Q',
        color='ANO:N',
        tooltip=['MÊS', 'ANO', quantity_col]
    ).properties(title='📈 Evolução de Quantidades por Mês', width=700, height=400)

    st.altair_chart(line_chart, use_container_width=True)

    # 💸 Gráfico de barras do preço médio
    if 'PM' in filtered_df.columns:
        pm_data = filtered_df.groupby(['MÊS', 'ANO'])['PM'].mean().reset_index()
        pm_data['MÊS'] = pd.Categorical(pm_data['MÊS'], categories=ordered_months, ordered=True)

        bar_chart = alt.Chart(pm_data).mark_bar().encode(
            x='MÊS:N', y='PM:Q',
            color='ANO:N',
            tooltip=['ANO', 'MÊS', 'PM']
        ).properties(title='💸 Evolução do Preço Médio por Mês', width=700, height=400)

        st.altair_chart(bar_chart, use_container_width=True)
