import streamlit as st
import pandas as pd
import io
import altair as alt

st.set_page_config(layout="wide")
st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=100)

# 📂 Load and clean data
excel_url = 'https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx'
df = pd.read_excel(excel_url, sheet_name='Resumo', engine='openpyxl')

# 🔧 Normalize columns
df.columns = df.columns.str.strip().str.upper()
df['ANO'] = pd.to_numeric(df['ANO'].astype(str).str.strip(), errors='coerce').astype('Int64')
df['KGS'] = pd.to_numeric(df['KGS'], errors='coerce')
df['PLACEHOLDER'] = False  # mark original data

# 🔍 Detect quantity column
quantity_candidates = ['QUANTIDADE', 'QTD', 'TOTAL', 'VALOR', 'KGS']
quantity_col = next((col for col in df.columns if col in quantity_candidates), None)

if quantity_col:
    # 🎛️ Sidebar filters
    st.sidebar.header("🔎 Filtros")
    selected_produto = st.sidebar.multiselect(
        "Produto", options=df['PRODUTO'].dropna().unique(),
        default=df['PRODUTO'].dropna().unique()
    )
    selected_mes = st.sidebar.multiselect(
        "Mês", options=df['MÊS'].dropna().unique(),
        default=df['MÊS'].dropna().unique()
    )

    # Combine existing years + future years, then remove duplicates
    anos_disponiveis = sorted(df['ANO'].dropna().unique().tolist())
    future_years = [2023, 2024, 2025]
    all_years = sorted(set(anos_disponiveis + future_years))

    selected_ano = st.sidebar.multiselect(
        "Ano (Comparar)",
        options=all_years,
        default=all_years
    )

    # 🔍 Filter real data
    filtered_df = df[
        (df['PRODUTO'].isin(selected_produto)) &
        (df['MÊS'].isin(selected_mes)) &
        (df['ANO'].isin(selected_ano))
    ].copy()

    # ➕ Add placeholders for missing (ANO, PRODUTO, MÊS)
    existing_keys = filtered_df[['ANO', 'PRODUTO', 'MÊS']].drop_duplicates()
    placeholders = []

    for ano in selected_ano:
        for produto in selected_produto:
            for mes in selected_mes:
                if not ((existing_keys['ANO'] == ano) &
                        (existing_keys['PRODUTO'] == produto) &
                        (existing_keys['MÊS'] == mes)).any():
                    placeholders.append({
                        'ANO': ano,
                        'PRODUTO': produto,
                        'MÊS': mes,
                        quantity_col: 0,
                        'PM': 0 if 'PM' in df.columns else None,
                        'PLACEHOLDER': True
                    })

    if placeholders:
        filtered_df = pd.concat([filtered_df, pd.DataFrame(placeholders)], ignore_index=True)

    # 🚨 Warn if selected years were fully missing
    missing_years = set(selected_ano) - set(df['ANO'].dropna().unique())
    if missing_years:
        st.warning(f"⚠️ Os anos {', '.join(map(str, missing_years))} não existem nos dados originais. Linhas com 0 foram adicionadas.")

    # 📋 Show filtered data
    st.write("### 📋 Dados Filtrados")
    st.dataframe(filtered_df)

    # 🔢 Summary metrics
    st.write("### 🔢 Indicadores")
    total_qty = filtered_df[quantity_col].sum()
    st.metric("📦 Quantidade Total", f"{total_qty:,.2f}")

    if 'PM' in filtered_df.columns:
        avg_price = filtered_df['PM'].mean()
        st.metric("💰 Preço Médio", f"€{avg_price:,.2f}")
    else:
        st.info("ℹ️ Coluna 'PM' ausente — indicador de preço médio não disponível.")

    # 📥 Excel download
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Filtrado')

    st.download_button(
        label="📥 Baixar dados filtrados em Excel",
        data=excel_buffer.getvalue(),
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 📈 Line chart of quantity
    ordered_months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    chart_df = filtered_df.copy()
    chart_df['MÊS'] = pd.Categorical(chart_df['MÊS'], categories=ordered_months, ordered=True)

    real_data = chart_df[chart_df['PLACEHOLDER'] == False].copy()

    if real_data.empty:
        st.warning("⚠️ Nenhum dado real encontrado. Apenas placeholders foram gerados.")
    else:
        pivot_data = real_data.groupby(['MÊS', 'ANO'])[quantity_col].sum().reset_index()

        line_chart = alt.Chart(pivot_data).mark_line(point=True).encode(
            x=alt.X('MÊS:N', title='Mês', sort=ordered_months),
            y=alt.Y(f'{quantity_col}:Q', title='Quantidade'),
            color=alt.Color('ANO:N', title='Ano'),
            tooltip=['MÊS', 'ANO', quantity_col]
        ).properties(
            title='📈 Evolução de Quantidades por Mês',
            width=700,
            height=400
        )

        labels = alt.Chart(pivot_data).mark_text(
            align='center', baseline='bottom', dy=-5, fontSize=11, font='Arial'
        ).encode(
            x='MÊS:N', y=alt.Y(f'{quantity_col}:Q'), detail='ANO:N',
            text=alt.Text(f'{quantity_col}:Q', format=".0f")
        )

        st.altair_chart(line_chart + labels, use_container_width=True)

    # 💸 Bar chart for PM (if available)
    if 'PM' in filtered_df.columns:
        pm_df = chart_df[chart_df['PLACEHOLDER'] == False].copy()
        pm_df['MÊS'] = pd.Categorical(pm_df['MÊS'], categories=ordered_months, ordered=True)

        pm_data = pm_df.groupby(['MÊS', 'ANO'])['PM'].mean().reset_index()

        bar_chart = alt.Chart(pm_data).mark_bar().encode(
            x=alt.X('MÊS:N', title='Mês', sort=ordered_months),
            y=alt.Y('PM:Q', title='Preço Médio'),
            color=alt.Color('ANO:N', title='Ano'),
            tooltip=['ANO', 'MÊS', 'PM']
        ).properties(
            title='💸 Evolução do Preço Médio por Mês',
            width=700,
            height=400
        )

        pm_labels = alt.Chart(pm_data).mark_text(
            align='center', baseline='bottom', dy=-3, fontSize=12, font='Arial'
        ).encode(
            x='MÊS:N', y='PM:Q', detail='ANO:N', text=alt.Text('PM:Q', format=".2f")
        )

        st.altair_chart(bar_chart + pm_labels, use_container_width=True)

else:
    st.warning("🛑 Nenhuma coluna de quantidade foi encontrada no arquivo.")
