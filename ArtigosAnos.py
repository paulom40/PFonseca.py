import streamlit as st
import pandas as pd
import altair as alt
import io
import unidecode

# 🎨 Layout and branding
st.set_page_config(layout="wide")
st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=100)

# 📥 Load and clean data
excel_url = 'https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx'
df = pd.read_excel(excel_url, sheet_name='Resumo', engine='openpyxl')

# 🧹 Normalize column names (uppercase, no accents)
df.columns = [unidecode.unidecode(col).upper() for col in df.columns]

# 🧽 Clean values
df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce').astype('Int64')
df['KGS'] = pd.to_numeric(df['KGS'], errors='coerce')

# Convert PM using comma to dot if needed
if 'PM' in df.columns:
    df['PM'] = df['PM'].astype(str).str.replace(',', '.').str.replace(' ', '')
    df['PM'] = pd.to_numeric(df['PM'], errors='coerce')

# Normalize month names
df['MES'] = df['MES'].astype(str).str.strip().str.capitalize()

# 🧠 Detect quantity column
quantity_candidates = ['QUANTIDADE', 'QTD', 'TOTAL', 'VALOR', 'KGS']
quantity_col = next((col for col in df.columns if col in quantity_candidates), None)

if quantity_col:

    # 🎛 Sidebar filters
    st.sidebar.header("🔎 Filtros")
    selected_produto = st.sidebar.multiselect("Produto", options=df['PRODUTO'].dropna().unique(),
                                              default=df['PRODUTO'].dropna().unique())
    selected_mes = st.sidebar.multiselect("Mês", options=df['MES'].dropna().unique(),
                                          default=df['MES'].dropna().unique())
    anos_disponiveis = sorted(df['ANO'].dropna().unique())
    selected_ano = st.sidebar.multiselect("Ano (Comparar)", options=anos_disponiveis,
                                          default=anos_disponiveis)

    # ✅ Filtered data
    filtered_df = df[
        (df['PRODUTO'].isin(selected_produto)) &
        (df['MES'].isin(selected_mes)) &
        (df['ANO'].isin(selected_ano))
    ].copy()
    filtered_df['PLACEHOLDER'] = False

    # ➕ Add placeholders for missing years
    for ano in selected_ano:
        if ano not in filtered_df['ANO'].unique():
            placeholder = {
                'ANO': ano,
                'PRODUTO': selected_produto[0] if selected_produto else None,
                'MES': selected_mes[0] if selected_mes else None,
                quantity_col: 0,
                'PM': 0 if 'PM' in df.columns else None,
                'PLACEHOLDER': True
            }
            filtered_df = pd.concat([filtered_df, pd.DataFrame([placeholder])], ignore_index=True)

    # 🚨 Warn if only placeholder rows are being shown
    real_data = filtered_df[filtered_df['PLACEHOLDER'] == False]
    if real_data.empty:
        st.warning("⚠️ Os dados selecionados são apenas placeholders (valores 0) — não há dados reais disponíveis.")

    # 📋 Show data
    st.write("### 📋 Dados Filtrados")
    st.dataframe(filtered_df)

    # 📊 Indicadores
    st.write("### 🔢 Indicadores")
    metrics_df = filtered_df[filtered_df['PLACEHOLDER'] == False]
    total_qty = metrics_df[quantity_col].sum()
    st.metric("📦 Quantidade Total", f"{total_qty:,.2f}")

    if 'PM' in metrics_df.columns:
        avg_price = metrics_df['PM'].mean()
        st.metric("💰 Preço Médio", f"€{avg_price:,.2f}")
    else:
        st.info("ℹ️ Coluna 'PM' ausente — indicador de preço médio não disponível.")

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

    # 📈 Line chart
    ordered_months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    chart_df = filtered_df[filtered_df['PLACEHOLDER'] == False].copy()
    chart_df['MES'] = pd.Categorical(chart_df['MES'], categories=ordered_months, ordered=True)

    pivot_data = chart_df.groupby(['MES', 'ANO'])[quantity_col].sum().reset_index()

    line_chart = alt.Chart(pivot_data).mark_line(point=True).encode(
        x=alt.X('MES:N', title='Mês', sort=ordered_months),
        y=alt.Y(f'{quantity_col}:Q', title='Quantidade'),
        color=alt.Color('ANO:N', title='Ano'),
        tooltip=['MES', 'ANO', quantity_col]
    ).properties(
        title='📈 Evolução de Quantidades por Mês',
        width=700,
        height=400
    )

    labels = alt.Chart(pivot_data).mark_text(
        align='center', baseline='bottom', dy=-5, fontSize=11, font='Arial'
    ).encode(
        x='MES:N', y=alt.Y(f'{quantity_col}:Q'), detail='ANO:N',
        text=alt.Text(f'{quantity_col}:Q', format=".0f")
    )

    st.altair_chart(line_chart + labels, use_container_width=True)

    # 💸 Bar chart for PM
    if 'PM' in chart_df.columns:
        pm_data = chart_df.groupby(['MES', 'ANO'])['PM'].mean().reset_index()
        pm_data['MES'] = pd.Categorical(pm_data['MES'], categories=ordered_months, ordered=True)

        bar_chart = alt.Chart(pm_data).mark_bar().encode(
            x=alt.X('MES:N', title='Mês', sort=ordered_months),
            y=alt.Y('PM:Q', title='Preço Médio'),
            color=alt.Color('ANO:N', title='Ano'),
            tooltip=['ANO', 'MES', 'PM']
        ).properties(
            title='💸 Evolução do Preço Médio por Mês',
            width=700,
            height=400
        )

        pm_labels = alt.Chart(pm_data).mark_text(
            align='center', baseline='bottom', dy=-3, fontSize=12, font='Arial'
        ).encode(
            x='MES:N', y='PM:Q', detail='ANO:N', text=alt.Text('PM:Q', format=".2f")
        )

        st.altair_chart(bar_chart + pm_labels, use_container_width=True)

else:
    st.warning("🛑 Nenhuma coluna de quantidade foi encontrada no arquivo.")
