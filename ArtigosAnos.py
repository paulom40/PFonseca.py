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

# Filter data for main display and charts
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
    # FIXED: Replaced use_container_width with width='stretch'
    st.altair_chart(line_chart + labels, width='stretch')
else:
    st.info("ℹ️ Não há dados de KGS válidos para gerar o gráfico.")

# Top e Bottom 15 Artigos por Quantidade (KGS) - Relatórios Anuais
st.write("### 📦 Top e Bottom 15 Artigos por Quantidade (KGS) - Relatórios Anuais")

# Define the years we want to analyze
target_years = [2023, 2024, 2025]

for year in target_years:
    # Filter data for the specific year, but keep product and month filters
    year_filtered_df = df[
        (df['PRODUTO'].isin(selected_produto)) &
        (df['MES'].isin(selected_mes)) &
        (df['ANO'] == year)
    ].copy()
    
    if 'KGS' in year_filtered_df.columns and year_filtered_df['KGS'].notnull().any():
        kgs_data = year_filtered_df[year_filtered_df['KGS'].notnull()].copy()
        
        if not kgs_data.empty:
            # Group by product to get total KGS for the year
            kgs_agg = kgs_data.groupby('PRODUTO')['KGS'].sum().reset_index()
            
            # Calculate average KGS for the year
            avg_kgs_year = kgs_agg['KGS'].mean()
            
            # Get top 15 and bottom 15 articles for the year
            top_15 = kgs_agg.nlargest(15, 'KGS')[['PRODUTO', 'KGS']].round(2)
            bottom_15 = kgs_agg.nsmallest(15, 'KGS')[['PRODUTO', 'KGS']].round(2)
            
            # Display year section in an expander
            with st.expander(f"📊 Ano {year}", expanded=True):
                st.metric(f"📦 Quantidade Média (KGS) {year}", f"{avg_kgs_year:,.2f}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Top 15 Artigos {year} (Maior KGS)**")
                    if not top_15.empty:
                        st.dataframe(
                            top_15.rename(columns={'PRODUTO': 'Artigo', 'KGS': 'Quantidade (KGS)'}),
                            width='stretch'
                        )
                    else:
                        st.info("ℹ️ Não há dados suficientes para os top 15 artigos.")
                
                with col2:
                    st.write(f"**Bottom 15 Artigos {year} (Menor KGS)**")
                    if not bottom_15.empty:
                        st.dataframe(
                            bottom_15.rename(columns={'PRODUTO': 'Artigo', 'KGS': 'Quantidade (KGS)'}),
                            width='stretch'
                        )
                    else:
                        st.info("ℹ️ Não há dados suficientes para os bottom 15 artigos.")
                
                # Create Excel download for this year's data
                year_excel_buffer = io.BytesIO()
                with pd.ExcelWriter(year_excel_buffer, engine='openpyxl') as writer:
                    # Create sheets for top and bottom data
                    top_15.to_excel(writer, sheet_name=f'Top15_{year}', index=False)
                    bottom_15.to_excel(writer, sheet_name=f'Bottom15_{year}', index=False)
                    kgs_agg.to_excel(writer, sheet_name=f'Todos_Artigos_{year}', index=False)
                
                # Download button for this year
                st.download_button(
                    label=f"📥 Baixar Relatório {year} em Excel",
                    data=year_excel_buffer.getvalue(),
                    file_name=f"relatorio_artigos_{year}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"download_{year}"  # Unique key for each button
                )
                
                # Show year summary
                st.write("**Resumo do Ano:**")
                st.write(f"- **Total de artigos únicos:** {len(kgs_agg)}")
                st.write(f"- **Total KGS do ano:** {kgs_agg['KGS'].sum():,.2f}")
                st.write(f"- **Meses com dados:** {len(kgs_data['MES'].unique())}")
                
        else:
            st.info(f"ℹ️ Não há dados de KGS válidos para o ano {year} com os filtros aplicados.")
    else:
        st.info(f"ℹ️ Não há dados de KGS válidos para o ano {year}.")

# Overall summary across all target years with download button
st.write("### 📊 Resumo Geral dos Anos 2023-2025")

# Create a summary dataframe for all target years with filter information
summary_data = []
for year in target_years:
    year_data = df[
        (df['PRODUTO'].isin(selected_produto)) &
        (df['MES'].isin(selected_mes)) &
        (df['ANO'] == year)
    ]
    if not year_data.empty and 'KGS' in year_data.columns:
        total_kgs_year = year_data['KGS'].sum()
        unique_products = year_data['PRODUTO'].nunique()
        avg_kgs_year = year_data['KGS'].mean()
        months_with_data = year_data['MES'].nunique()
        
        # Get product and month names for display
        produtos_str = ", ".join(selected_produto) if selected_produto else "Todos os Produtos"
        meses_str = ", ".join(selected_mes) if selected_mes else "Todos os Meses"
        
        summary_data.append({
            'Ano': year,
            'Produtos': produtos_str,
            'Meses': meses_str,
            'Total KGS': total_kgs_year,
            'Artigos Únicos': unique_products,
            'Média KGS': avg_kgs_year,
            'Meses com Dados': months_with_data
        })

if summary_data:
    summary_df = pd.DataFrame(summary_data)
    
    # Format the numbers for better display
    display_df = summary_df.copy()
    display_df['Total KGS'] = display_df['Total KGS'].apply(lambda x: f"{x:,.2f}")
    display_df['Média KGS'] = display_df['Média KGS'].apply(lambda x: f"{x:,.2f}")
    
    st.dataframe(display_df, width='stretch')
    
    # Download button for overall summary
    summary_excel_buffer = io.BytesIO()
    with pd.ExcelWriter(summary_excel_buffer, engine='openpyxl') as writer:
        # Summary sheet with all columns
        summary_df.to_excel(writer, sheet_name='Resumo_Geral', index=False)
        
        # Also include detailed data for each year in separate sheets
        for year in target_years:
            year_data = df[
                (df['PRODUTO'].isin(selected_produto)) &
                (df['MES'].isin(selected_mes)) &
                (df['ANO'] == year)
            ]
            if not year_data.empty:
                year_data.to_excel(writer, sheet_name=f'Detalhes_{year}', index=False)
    
    st.download_button(
        label="📥 Baixar Resumo Geral em Excel",
        data=summary_excel_buffer.getvalue(),
        file_name="resumo_geral_2023_2025.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("ℹ️ Não há dados para gerar o resumo geral.")
