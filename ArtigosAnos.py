import streamlit as st
import pandas as pd
import io
import altair as alt

# 🖼️ Logo
st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=100)

# 📂 Load Excel data from GitHub
excel_url = 'https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx'
df = pd.read_excel(excel_url, sheet_name='Resumo', engine='openpyxl')

# 🧼 Clean column names
df.columns = df.columns.str.strip().str.upper()

# 🔧 Ensure 'ANO' is numeric
df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce').astype('Int64')

# 🔍 Detect quantity column
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

    anos_target = [2023, 2024, 2025]
    anos_disponiveis = df['ANO'].dropna().unique().tolist()
    anos_filtrados = [ano for ano in anos_target if ano in anos_disponiveis]

    selected_ano = st.sidebar.multiselect(
        "Ano (Comparar)",
        options=anos_filtrados,
        default=anos_filtrados
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

    # 📥 Download button for filtered data
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Filtrado')

    st.download_button(
        label="📥 Baixar dados filtrados em Excel",
        data=excel_buffer.getvalue(),
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 📈 Prepare chart
    chart_df = filtered_df[filtered_df['ANO'].isin(selected_ano)]
    pivot_data = chart_df.groupby(['MÊS', 'ANO'])[quantity_col].sum().reset_index()
    pivot_table = pivot_data.pivot(index='MÊS', columns='ANO', values=quantity_col).fillna(0)

    # 📊 Render chart
    st.write("### 📈 Comparação de Quantidades: 2023 vs 2024 vs 2025")
    st.line_chart(pivot_table)

else:
    st.warning("🛑 Nenhuma coluna de quantidade foi encontrada.")



# ✅ Lista de meses ordenados
ordered_months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

# 📊 Calcular Preço Médio por mês e ano
pm_data = filtered_df.groupby(['MÊS', 'ANO'])['PM'].mean().reset_index()

# 🔄 Garantir a ordem dos meses
pm_data['MÊS'] = pd.Categorical(pm_data['MÊS'], categories=ordered_months, ordered=True)

# 🎨 Criar gráfico de barras com Altair
bar_chart = alt.Chart(pm_data).mark_bar().encode(
    x=alt.X('MÊS:N', title='Mês'),
    y=alt.Y('PM:Q', title='Preço Médio'),
    color=alt.Color('ANO:N', title='Ano'),
    tooltip=['ANO', 'MÊS', 'PM']
).properties(
    title='💸 Evolução do Preço Médio por Mês: 2023 vs 2024 vs 2025',
    width=700,
    height=400
)

# ✏️ Adicionar valores acima de cada barra
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

# 🔗 Combinar os gráficos
final_chart = bar_chart + text_labels
final_chart
