import streamlit as st
import pandas as pd
import io
import altair as alt

# 🖼️ Logo
st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=100)

# 📂 Load Excel data
excel_url = 'https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx'
df = pd.read_excel(excel_url, sheet_name='Resumo', engine='openpyxl')

# 🧼 Clean column names
df.columns = df.columns.str.strip().str.upper()

# 🧼 Clean and convert 'ANO' column
df['ANO'] = df['ANO'].astype(str).str.strip()
df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce').astype('Int64')
df['KGS'] = pd.to_numeric(df['KGS'], errors='coerce')


# 🧮 Detect quantity column (includes 'KGS')
quantity_candidates = ['QUANTIDADE', 'QTD', 'TOTAL', 'VALOR', 'KGS']
quantity_col = next((col for col in df.columns if col in quantity_candidates), None)

if quantity_col:

    # 🎛️ Sidebar filters
    st.sidebar.header("🔎 Filtros")

    selected_produto = st.sidebar.multiselect(
        "Produto",
        options=df['PRODUTO'].dropna().unique(),
        default=df['PRODUTO'].dropna().unique()
    )

    selected_mes = st.sidebar.multiselect(
        "Mês",
        options=df['MÊS'].dropna().unique(),
        default=df['MÊS'].dropna().unique()
    )

    anos_disponiveis = sorted(df['ANO'].dropna().unique().tolist())
    selected_ano = st.sidebar.multiselect(
        "Ano (Comparar)",
        options=anos_disponiveis,
        default=anos_disponiveis
    )

    # 🔍 Apply filters
    filtered_df = df[
        (df['PRODUTO'].isin(selected_produto)) &
        (df['MÊS'].isin(selected_mes)) &
        (df['ANO'].isin(selected_ano))
    ]

    # 📋 Show filtered data
    st.write("### 📋 Dados Filtrados")
    st.dataframe(filtered_df)

    # 📥 Download button
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Filtrado')

    st.download_button(
        label="📥 Baixar dados filtrados em Excel",
        data=excel_buffer.getvalue(),
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 🗓️ Month order
    ordered_months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    # 📈 Line chart for quantity comparison
    chart_df = filtered_df.copy()
    chart_df['MÊS'] = pd.Categorical(chart_df['MÊS'], categories=ordered_months, ordered=True)

    pivot_data = chart_df.groupby(['MÊS', 'ANO'])[quantity_col].sum().reset_index()

    line_chart = alt.Chart(pivot_data).mark_line(point=True).encode(
        x=alt.X('MÊS:N', title='Mês'),
        y=alt.Y(f'{quantity_col}:Q', title='Quantidade'),
        color=alt.Color('ANO:N', title='Ano'),
        tooltip=['MÊS', 'ANO', quantity_col]
    ).properties(
        title='📈 Evolução de Quantidades por Mês',
        width=700,
        height=400
    )

    st.altair_chart(line_chart, use_container_width=True)

    # 💸 Bar chart for Preço Médio
    pm_data = filtered_df.groupby(['MÊS', 'ANO'])['PM'].mean().reset_index()
    pm_data['MÊS'] = pd.Categorical(pm_data['MÊS'], categories=ordered_months, ordered=True)

    bar_chart = alt.Chart(pm_data).mark_bar().encode(
        x=alt.X('MÊS:N', title='Mês'),
        y=alt.Y('PM:Q', title='Preço Médio'),
        color=alt.Color('ANO:N', title='Ano'),
        tooltip=['ANO', 'MÊS', 'PM']
    ).properties(
        title='💸 Evolução do Preço Médio por Mês',
        width=700,
        height=400
    )

    text_labels = alt.Chart(pm_data).mark_text(
        align='center',
        baseline='bottom',
        dy=-3,
        fontSize=12,
        font='Arial'
    ).encode(
        x='MÊS:N',
        y='PM:Q',
        detail='ANO:N',
        text=alt.Text('PM:Q', format=".2f")
    )

    st.altair_chart(bar_chart + text_labels, use_container_width=True)

else:
    st.warning("🛑 Nenhuma coluna de quantidade foi encontrada no arquivo.")
