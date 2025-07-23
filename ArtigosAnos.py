import streamlit as st
import pandas as pd
import altair as alt
import io

st.set_page_config(layout="wide")
st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=100)

# 📂 Carregar e limpar dados
url = 'https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx'
df = pd.read_excel(url, sheet_name='Resumo', engine='openpyxl')
df.columns = df.columns.str.strip().str.upper()
df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce').astype('Int64')
df['KGS'] = pd.to_numeric(df['KGS'], errors='coerce')

# 🔎 Identificar coluna de quantidade
quantity_candidates = ['QUANTIDADE', 'QTD', 'TOTAL', 'VALOR', 'KGS']
quantity_col = next((col for col in df.columns if col in quantity_candidates), None)

if not quantity_col:
    st.warning("🛑 Nenhuma coluna de quantidade encontrada.")
    st.stop()

# 🎛️ Filtros
st.sidebar.header("🔎 Filtros")
selected_produto = st.sidebar.multiselect("Produto", options=df['PRODUTO'].dropna().unique(),
                                          default=df['PRODUTO'].dropna().unique())
selected_mes = st.sidebar.multiselect("Mês", options=df['MÊS'].dropna().unique(),
                                      default=df['MÊS'].dropna().unique())
anos_disponiveis = sorted(df['ANO'].dropna().unique())
selected_ano = st.sidebar.multiselect("Ano (Comparar)", options=anos_disponiveis,
                                      default=anos_disponiveis)

# 🔍 Aplicar filtros
filtered_df = df[
    df['PRODUTO'].isin(selected_produto) &
    df['MÊS'].isin(selected_mes) &
    df['ANO'].isin(selected_ano)
]

# ➕ Adicionar placeholders para anos faltantes
for ano in selected_ano:
    if ano not in filtered_df['ANO'].unique():
        placeholder = {
            'ANO': ano,
            'PRODUTO': selected_produto[0] if selected_produto else None,
            'MÊS': selected_mes[0] if selected_mes else None,
            quantity_col: 0,
            'PM': 0 if 'PM' in df.columns else None
        }
        filtered_df = pd.concat([filtered_df, pd.DataFrame([placeholder])], ignore_index=True)

# 🚨 Aviso sobre anos ausentes
missing_years = set(selected_ano) - set(df['ANO'].dropna().unique())
if missing_years:
    st.warning(f"⚠️ Os dados originais não contêm os anos: {', '.join(map(str, missing_years))}. Foram adicionados como placeholders.")

# 📋 Mostrar dados
st.write("### 📋 Dados Filtrados")
st.dataframe(filtered_df)

# 🔢 Indicadores
st.write("### 🔢 Indicadores")
st.metric("📦 Quantidade Total", f"{filtered_df[quantity_col].sum():,.2f} kg")

if 'PM' in filtered_df.columns and not filtered_df['PM'].isna().all():
    st.metric("💰 Preço Médio", f"€{filtered_df['PM'].mean():,.2f}")
else:
    st.info("ℹ️ Coluna 'PM' ausente ou inválida.")

# 📥 Exportar para Excel
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name='Filtrado')

st.download_button(
    label="📥 Baixar dados filtrados em Excel",
    data=excel_buffer.getvalue(),
    file_name="dados_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 📈 Gráfico de linhas (quantidade por mês)
ordered_months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
chart_df = filtered_df.copy()
chart_df['MÊS'] = pd.Categorical(chart_df['MÊS'], categories=ordered_months, ordered=True)

pivot_data = chart_df.groupby(['ANO', 'MÊS'])[quantity_col].sum().reset_index()
pivot_data['MÊS'] = pd.Categorical(pivot_data['MÊS'], categories=ordered_months, ordered=True)
pivot_data['LABEL_QTD'] = pivot_data[quantity_col].apply(lambda x: f"{x:,.0f} kg")

line_chart = alt.Chart(pivot_data).mark_line(point=True).encode(
    x='MÊS:N',
    y=alt.Y(f'{quantity_col}:Q', title='Quantidade'),
    color='ANO:N',
    tooltip=['ANO', 'MÊS', quantity_col]
).properties(
    title='📈 Evolução de Quantidades por Mês',
    width=700, height=400
)

labels = alt.Chart(pivot_data).mark_text(
    align='center', baseline='bottom', dy=-5,
    fontSize=11, font='Arial', color='white'
).encode(
    x='MÊS:N',
    y=alt.Y(f'{quantity_col}:Q'),
    detail='ANO:N',
    text='LABEL_QTD:N'
)

st.altair_chart(line_chart + labels, use_container_width=True)

# 🚨 Alertas visuais
media_geral = pivot_data[quantity_col].mean()
pivot_data['ALERTA'] = pivot_data[quantity_col].apply(
    lambda x: "📉 Queda acentuada" if x < media_geral * 0.6 else
              ("📈 Aumento acentuado" if x > media_geral * 1.4 else "✅ Estável")
)

st.write("### 🚨 Alertas por Mês")
st.dataframe(pivot_data[['MÊS', 'ANO', quantity_col, 'ALERTA']])

# 💸 Gráfico de barras (PM)
if 'PM' in filtered_df.columns:
    pm_data = filtered_df.groupby(['ANO', 'MÊS'])['PM'].mean().reset_index()
    pm_data['MÊS'] = pd.Categorical(pm_data['MÊS'], categories=ordered_months, ordered=True)
    pm_data['LABEL_PM'] = pm_data['PM'].apply(lambda x: f"€{x:,.2f}")

    bar_chart = alt.Chart(pm_data).mark_bar().encode(
        x='MÊS:N',
        y=alt.Y('PM:Q', title='Preço Médio'),
        color='ANO:N',
        tooltip=['ANO', 'MÊS', 'PM']
    ).properties(
        title='💸 Evolução do Preço Médio por Mês',
        width=700, height=400
    )

    pm_labels = alt.Chart(pm_data).mark_text(
        align='center', baseline='bottom', dy=-3,
        fontSize=12, font='Arial'
    ).encode(
        x='MÊS:N',
        y='PM:Q',
        detail='ANO:N',
        text='LABEL_PM:N'
    )

    st.altair_chart(bar_chart + pm_labels, use_container_width=True)
