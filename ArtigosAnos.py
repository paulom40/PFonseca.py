import streamlit as st
import pandas as pd
import io
import altair as alt

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Page configuration
st.set_page_config(layout="wide")
st.image("https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Bracar.png", width=100)

# Define ordered months
ordered_months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

# Cache the data loading function
@st.cache_data
def load_data():
    excel_url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/Artigos_totais_ANOS.xlsx"
    df = pd.read_excel(excel_url, sheet_name="Resumo", engine="openpyxl")
    df.columns = df.columns.str.strip().str.upper()
    df['MES'] = df['MÊS'].str.capitalize().str.strip()
    df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce').astype('Int64')
    df['KGS'] = pd.to_numeric(df['KGS'], errors='coerce')
    df['PM'] = pd.to_numeric(df['PM'], errors='coerce')
    return df

# Load data
df = load_data()

# Validate month names
invalid_months = df[~df['MES'].isin(ordered_months)]['MES'].unique()
if invalid_months.size > 0:
    st.warning(f"⚠️ Meses inválidos encontrados: {invalid_months}")

# Sidebar filters
st.sidebar.header("🔎 Filtros")
produtos = df['PRODUTO'].dropna().unique()
meses = df['MES'].dropna().unique()
anos = sorted(df['ANO'].dropna().unique())
selected_produto = st.sidebar.multiselect("Produto", options=produtos, default=produtos)
selected_mes = st.sidebar.multiselect("Mês", options=meses, default=meses)
selected_ano = st.sidebar.multiselect("Ano", options=anos, default=anos)

# Refresh button
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()  # Clear the cache
    df = load_data()  # Reload the data
    st.sidebar.success("Dados atualizados com sucesso!")

# Filter data
filtered_df = df[
    (df['PRODUTO'].isin(selected_produto)) &
    (df['MES'].isin(selected_mes)) &
    (df['ANO'].isin(selected_ano))
].copy()

# Display filtered data
st.write("### 📋 Dados Filtrados")
st.dataframe(filtered_df, width='stretch')

# Metrics
st.write("### 🔢 Indicadores")
if not filtered_df.empty:
    total_kgs = filtered_df['KGS'].sum()
    st.metric("📦 Quantidade Total (KGS)", f"{total_kgs:,.2f}")
    if 'PM' in filtered_df.columns:
        avg_price = filtered_df['PM'].mean()
        st.metric("💰 Preço Médio", f"€{avg_price:,.2f}")
else:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")

# Download filtered data as Excel
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name='Filtrado')
st.download_button(
    label="📥 Baixar dados filtrados em Excel",
    data=excel_buffer.getvalue(),
    file_name="dados_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Line chart for KGS
chart_df = filtered_df[filtered_df['KGS'].notnull()].copy()
chart_df['MES'] = pd.Categorical(chart_df['MES'], categories=ordered_months, ordered=True)

if not chart_df.empty:
    # Fixed: Added observed=False to suppress the warning
    pivot_data = chart_df.groupby(['MES', 'ANO'], observed=False)['KGS'].sum().reset_index()
    line_chart = alt.Chart(pivot_data).mark_line(point=True).encode(
        x=alt.X('MES:N', title='Mês', sort=ordered_months),
        y=alt.Y('KGS:Q', title='Quantidade (KGS)'),
        color=alt.Color('ANO:N', title='Ano'),
        tooltip=['MES', 'ANO', 'KGS']
    ).properties(
        title='📈 Evolução de Quantidades por Mês (KGS)',
        width=700,
        height=400
    )
    labels = alt.Chart(pivot_data).mark_text(
        align='center',
        baseline='bottom',
        dy=-5,
        fontSize=11,
        font='Arial',
        color='white'
    ).encode(
        x=alt.X('MES:N', sort=ordered_months),
        y='KGS:Q',
        detail='ANO:N',
        text=alt.Text('KGS:Q', format=".0f")
    )
    st.altair_chart(line_chart + labels, use_container_width=True)
else:
    st.info("ℹ️ Não há dados de KGS válidos para gerar o gráfico.")

# Top e Bottom 15 Artigos por Quantidade (KGS) com base nos filtros
st.write("### 📦 Top e Bottom 15 Artigos por Quantidade (KGS) - Filtrado")

if 'KGS' in filtered_df.columns and filtered_df['KGS'].notnull().any():
    kgs_data = filtered_df[filtered_df['KGS'].notnull()].copy()
    
    if not kgs_data.empty:
        # Group by product to get total KGS across all filtered data
        kgs_agg = kgs_data.groupby('PRODUTO')['KGS'].sum().reset_index()
        
        # Calculate average KGS for the filtered data
        avg_kgs_filtered = kgs_agg['KGS'].mean()
        
        # Get top 15 and bottom 15 articles from the filtered data
        top_15 = kgs_agg.nlargest(15, 'KGS')[['PRODUTO', 'KGS']].round(2)
        bottom_15 = kgs_agg.nsmallest(15, 'KGS')[['PRODUTO', 'KGS']].round(2)
        
        # Display metrics and dataframes
        st.metric("📦 Quantidade Média (KGS) nos Filtros Selecionados", f"{avg_kgs_filtered:,.2f}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Top 15 Artigos (Maior KGS)**")
            if not top_15.empty:
                st.dataframe(
                    top_15.rename(columns={'PRODUTO': 'Artigo', 'KGS': 'Quantidade (KGS)'}),
                    width='stretch'
                )
            else:
                st.info("ℹ️ Não há dados suficientes para os top 15 artigos.")
        
        with col2:
            st.write("**Bottom 15 Artigos (Menor KGS)**")
            if not bottom_15.empty:
                st.dataframe(
                    bottom_15.rename(columns={'PRODUTO': 'Artigo', 'KGS': 'Quantidade (KGS)'}),
                    width='stretch'
                )
            else:
                st.info("ℹ️ Não há dados suficientes para os bottom 15 artigos.")
        
        # Show filter summary
        st.write("**Resumo dos Filtros Aplicados:**")
        st.write(f"- **Produtos selecionados:** {len(selected_produto)}")
        st.write(f"- **Meses selecionados:** {len(selected_mes)}")
        st.write(f"- **Anos selecionados:** {len(selected_ano)}")
        st.write(f"- **Total de artigos únicos:** {len(kgs_agg)}")
        
    else:
        st.info("ℹ️ Não há dados de KGS válidos após aplicar os filtros.")
else:
    st.info("ℹ️ Não há dados de KGS válidos para gerar os indicadores.")
