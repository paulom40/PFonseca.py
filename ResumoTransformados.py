import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas - ResumoTR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar dados
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('ResumoTR.xlsx')
        
        # Garantir que as colunas de data sejam datetime
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'])
            df['Ano'] = df['Data'].dt.year
            df['Mês'] = df['Data'].dt.month
            df['Mês_Nome'] = df['Data'].dt.strftime('%B')
        
        # Converter colunas numéricas
        numeric_cols = ['Quantidade', 'V Líquido', 'PM']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

# Função principal
def main():
    # Título e descrição
    st.title("📊 Dashboard de Análise de Vendas")
    st.markdown("---")
    
    # Carregar dados
    df = load_data()
    
    if df is None:
        st.error("Não foi possível carregar os dados. Verifique o arquivo.")
        return
    
    # Sidebar - Filtros
    with st.sidebar:
        st.header("⚙️ Filtros")
        
        # Filtro de Ano (dinâmico)
        anos = sorted(df['Ano'].unique()) if 'Ano' in df.columns else []
        ano_selecionado = st.selectbox(
            "Ano",
            options=["Todos"] + list(anos),
            index=0
        )
        
        # Filtro de Mês (dinâmico)
        meses_disponiveis = sorted(df['Mês_Nome'].unique()) if 'Mês_Nome' in df.columns else []
        mes_selecionado = st.selectbox(
            "Mês",
            options=["Todos"] + list(meses_disponiveis),
            index=0
        )
        
        # Filtro de Comercial (dinâmico)
        comerciais = sorted(df['Comercial'].dropna().unique()) if 'Comercial' in df.columns else []
        comercial_selecionado = st.selectbox(
            "Comercial",
            options=["Todos"] + list(comerciais),
            index=0
        )
        
        # Filtro de Entidade (pesquisável)
        entidades = sorted(df['Nome'].dropna().unique()) if 'Nome' in df.columns else []
        entidade_selecionada = st.selectbox(
            "Entidade",
            options=["Todas"] + list(entidades),
            index=0
        )
        
        # Filtro de Artigo (dinâmico)
        artigos = sorted(df['Artigo'].dropna().unique()) if 'Artigo' in df.columns else []
        artigo_selecionado = st.selectbox(
            "Artigo",
            options=["Todos"] + list(artigos),
            index=0
        )
        
        # Botão para resetar filtros
        if st.button("🔄 Resetar Filtros"):
            st.rerun()
        
        st.markdown("---")
        st.markdown("**ℹ️ Dados carregados:**")
        st.info(f"{len(df)} registros carregados")
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if ano_selecionado != "Todos" and 'Ano' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Ano'] == ano_selecionado]
    
    if mes_selecionado != "Todos" and 'Mês_Nome' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Mês_Nome'] == mes_selecionado]
    
    if comercial_selecionado != "Todos" and 'Comercial' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Comercial'] == comercial_selecionado]
    
    if entidade_selecionada != "Todas" and 'Nome' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Nome'] == entidade_selecionada]
    
    if artigo_selecionado != "Todos" and 'Artigo' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Artigo'] == artigo_selecionado]
    
    # Seção de KPIs
    st.header("📈 KPIs Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_vendas = df_filtrado['V Líquido'].sum() if 'V Líquido' in df_filtrado.columns else 0
        st.metric(
            label="💰 Total Vendas Líquidas",
            value=f"€{total_vendas:,.2f}",
            delta=None
        )
    
    with col2:
        total_quantidade = df_filtrado['Quantidade'].sum() if 'Quantidade' in df_filtrado.columns else 0
        st.metric(
            label="📦 Quantidade Total",
            value=f"{total_quantidade:,.0f}",
            delta=None
        )
    
    with col3:
        num_entidades = df_filtrado['Nome'].nunique() if 'Nome' in df_filtrado.columns else 0
        ticket_medio = total_vendas / num_entidades if num_entidades > 0 else 0
        st.metric(
            label="👥 Ticket Médio por Entidade",
            value=f"€{ticket_medio:,.2f}",
            delta=None
        )
    
    with col4:
        num_comerciais = df_filtrado['Comercial'].nunique() if 'Comercial' in df_filtrado.columns else 0
        st.metric(
            label="👨‍💼 Comerciais Ativos",
            value=num_comerciais,
            delta=None
        )
    
    st.markdown("---")
    
    # Gráficos e Análises
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "👥 Por Entidade", "🛒 Por Artigo", "📈 Tendências"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Vendas por Comercial
            if 'Comercial' in df_filtrado.columns and 'V Líquido' in df_filtrado.columns:
                vendas_por_comercial = df_filtrado.groupby('Comercial')['V Líquido'].sum().reset_index()
                vendas_por_comercial = vendas_por_comercial.sort_values('V Líquido', ascending=False).head(10)
                
                fig = px.bar(
                    vendas_por_comercial,
                    x='Comercial',
                    y='V Líquido',
                    title='Top 10 Comerciais por Vendas',
                    color='V Líquido',
                    color_continuous_scale='Blues',
                    text_auto='.2s'
                )
                fig.update_layout(
                    xaxis_title="Comercial",
                    yaxis_title="Vendas Líquidas (€)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distribuição por Mês
            if 'Mês_Nome' in df_filtrado.columns and 'V Líquido' in df_filtrado.columns:
                vendas_por_mes = df_filtrado.groupby('Mês_Nome')['V Líquido'].sum().reset_index()
                
                # Ordenar por mês cronológico
                meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June', 
                              'July', 'August', 'September', 'October', 'November', 'December']
                vendas_por_mes['Mês_Nome'] = pd.Categorical(vendas_por_mes['Mês_Nome'], categories=meses_ordem, ordered=True)
                vendas_por_mes = vendas_por_mes.sort_values('Mês_Nome')
                
                fig = px.line(
                    vendas_por_mes,
                    x='Mês_Nome',
                    y='V Líquido',
                    title='Vendas por Mês',
                    markers=True
                )
                fig.update_layout(
                    xaxis_title="Mês",
                    yaxis_title="Vendas Líquidas (€)"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 Entidades por Compras
            if 'Nome' in df_filtrado.columns and 'V Líquido' in df_filtrado.columns:
                top_entidades = df_filtrado.groupby('Nome').agg({
                    'V Líquido': 'sum',
                    'Quantidade': 'sum',
                    'Entidade': 'count'
                }).reset_index()
                top_entidades = top_entidades.sort_values('V Líquido', ascending=False).head(10)
                top_entidades.columns = ['Entidade', 'Total Vendas (€)', 'Quantidade Total', 'Nº Compras']
                
                st.subheader("🏆 Top 10 Entidades")
                st.dataframe(
                    top_entidades.style.format({
                        'Total Vendas (€)': '€{:,.2f}',
                        'Quantidade Total': '{:,.0f}',
                        'Nº Compras': '{:,.0f}'
                    }),
                    use_container_width=True
                )
        
        with col2:
            # Distribuição geográfica (se houver dados de localização)
            if 'Nome' in df_filtrado.columns:
                compras_por_entidade = df_filtrado['Nome'].value_counts().reset_index()
                compras_por_entidade.columns = ['Entidade', 'Nº Compras']
                compras_por_entidade = compras_por_entidade.head(10)
                
                fig = px.pie(
                    compras_por_entidade,
                    values='Nº Compras',
                    names='Entidade',
                    title='Top 10 Entidades por Nº de Compras',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 Artigos mais vendidos
            if 'Artigo' in df_filtrado.columns and 'Quantidade' in df_filtrado.columns:
                top_artigos = df_filtrado.groupby('Artigo').agg({
                    'Quantidade': 'sum',
                    'V Líquido': 'sum'
                }).reset_index()
                top_artigos = top_artigos.sort_values('Quantidade', ascending=False).head(10)
                
                fig = px.bar(
                    top_artigos,
                    x='Artigo',
                    y='Quantidade',
                    title='Top 10 Artigos por Quantidade Vendida',
                    color='V Líquido',
                    color_continuous_scale='Viridis',
                    hover_data=['V Líquido']
                )
                fig.update_layout(
                    xaxis_title="Artigo",
                    yaxis_title="Quantidade Vendida",
                    xaxis_tickangle=45
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Preço Médio por Artigo
            if 'Artigo' in df_filtrado.columns and 'PM' in df_filtrado.columns:
                preco_medio_artigo = df_filtrado.groupby('Artigo')['PM'].mean().reset_index()
                preco_medio_artigo = preco_medio_artigo.sort_values('PM', ascending=False).head(10)
                
                fig = px.bar(
                    preco_medio_artigo,
                    x='Artigo',
                    y='PM',
                    title='Top 10 Artigos por Preço Médio',
                    color='PM',
                    color_continuous_scale='Reds',
                    text_auto='.2f'
                )
                fig.update_layout(
                    xaxis_title="Artigo",
                    yaxis_title="Preço Médio (€)",
                    xaxis_tickangle=45
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Análise temporal
        if 'Data' in df_filtrado.columns and 'V Líquido' in df_filtrado.columns:
            # Vendas por dia
            df_filtrado['Data_Dia'] = df_filtrado['Data'].dt.date
            vendas_diarias = df_filtrado.groupby('Data_Dia').agg({
                'V Líquido': 'sum',
                'Quantidade': 'sum'
            }).reset_index()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=vendas_diarias['Data_Dia'],
                y=vendas_diarias['V Líquido'],
                mode='lines+markers',
                name='Vendas Líquidas',
                yaxis='y',
                line=dict(color='blue', width=2)
            ))
            
            fig.add_trace(go.Bar(
                x=vendas_diarias['Data_Dia'],
                y=vendas_diarias['Quantidade'],
                name='Quantidade',
                yaxis='y2',
                marker_color='lightblue',
                opacity=0.6
            ))
            
            fig.update_layout(
                title='Evolução Diária de Vendas',
                xaxis=dict(title='Data'),
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
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Seção de Dados Detalhados
    st.markdown("---")
    st.header("📋 Dados Detalhados")
    
    # Opções de visualização
    view_option = st.radio(
        "Visualização:",
        ["Visão Resumida", "Dados Completos"],
        horizontal=True
    )
    
    if view_option == "Visão Resumida":
        # Colunas mais importantes para visualização
        colunas_importantes = ['Data', 'Nome', 'Artigo', 'Quantidade', 'V Líquido', 'PM', 'Comercial']
        colunas_disponiveis = [col for col in colunas_importantes if col in df_filtrado.columns]
        
        st.dataframe(
            df_filtrado[colunas_disponiveis].sort_values('Data', ascending=False).head(50),
            use_container_width=True
        )
    else:
        # Todos os dados
        st.dataframe(
            df_filtrado.sort_values('Data', ascending=False),
            use_container_width=True
        )
    
    # Estatísticas descritivas
    with st.expander("📊 Estatísticas Descritivas"):
        if 'V Líquido' in df_filtrado.columns:
            stats = df_filtrado['V Líquido'].describe()
            st.write("**Vendas Líquidas:**")
            st.write(stats)
        
        if 'Quantidade' in df_filtrado.columns:
            stats_qtd = df_filtrado['Quantidade'].describe()
            st.write("**Quantidade:**")
            st.write(stats_qtd)
    
    # Download dos dados filtrados
    st.markdown("---")
    st.download_button(
        label="📥 Baixar Dados Filtrados (CSV)",
        data=df_filtrado.to_csv(index=False).encode('utf-8'),
        file_name=f"dados_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# Rodar o aplicativo
if __name__ == "__main__":
    main()
