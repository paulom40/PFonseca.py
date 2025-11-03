import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import BytesIO
import xlsxwriter
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página com layout wide
st.set_page_config(
    page_title="Dashboard de Vendas - Análise Cliente x Comercial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado com gradientes e estilo moderno
st.markdown("""
<style>
    /* Gradiente principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Cards com gradiente */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-warning {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-success {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Botões modernos */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: white;
        border-radius: 10px;
        padding: 0 2rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Header principal com gradiente
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.5rem;">📊 DASHBOARD DE VENDAS - ANÁLISE CLIENTE x COMERCIAL</h1>
    <p style="margin:0; opacity: 0.9; font-size: 1.1rem;">Análise Comparativa de Histórico por Artigo</p>
</div>
""", unsafe_allow_html=True)

# URL do arquivo Excel
url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"

@st.cache_data
def load_data():
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), sheet_name="Sheet1", header=0)
        
        # Processar colunas e dados
        df.columns = [col.strip() for col in df.columns]
        
        # Converter colunas numéricas
        if 'Qtd.' in df.columns:
            df['Qtd.'] = pd.to_numeric(df['Qtd.'], errors='coerce')
        if 'V. Líquido' in df.columns:
            df['V. Líquido'] = pd.to_numeric(df['V. Líquido'], errors='coerce')
        
        # Limpar e padronizar textos
        if 'Cliente' in df.columns:
            df['Cliente'] = df['Cliente'].astype(str).str.strip()
        if 'Comercial' in df.columns:
            df['Comercial'] = df['Comercial'].astype(str).str.strip()
        if 'Artigo' in df.columns:
            df['Artigo'] = df['Artigo'].astype(str).str.strip()
        if 'Categoria' in df.columns:
            df['Categoria'] = df['Categoria'].astype(str).str.strip()
        
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar ficheiro: {e}")
        st.info("💡 Dica: Verifique se o link do GitHub está correto e se o ficheiro está público.")
        return None

# Container principal para controles
with st.container():
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 🔄 Gestão de Dados")
        if st.button("🔄 Atualizar Dados do Excel", use_container_width=True):
            st.cache_data.clear()
            st.session_state.df = load_data()
            st.session_state.last_updated = datetime.now()
            if st.session_state.df is not None:
                st.success("✅ Dados atualizados com sucesso!")
    
    with col2:
        if "last_updated" in st.session_state:
            st.markdown(f"""
            <div class="metric-card-success">
                <h3 style="margin:0; font-size: 0.9rem;">Última Atualização</h3>
                <p style="margin:0; font-size: 1rem; font-weight: bold;">
                    {st.session_state.last_updated.strftime('%d/%m/%Y')}
                </p>
                <p style="margin:0; font-size: 0.8rem;">
                    {st.session_state.last_updated.strftime('%H:%M:%S')}
                </p>
            </div>
            """, unsafe_allow_html=True)

# Carregar dados
df = st.session_state.get("df", load_data())

if df is not None:
    # Sidebar moderna
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🔎 FILTROS E CONTROLES</div>', unsafe_allow_html=True)
        
        st.markdown("### 📊 Filtros Principais")
        
        # Filtro por Comercial
        if 'Comercial' in df.columns:
            comerciais = sorted(df['Comercial'].dropna().unique())
            selected_comercial = st.multiselect(
                "Selecione o(s) Comercial(ais):",
                comerciais,
                default=comerciais[:3] if len(comerciais) > 3 else comerciais
            )
        else:
            st.warning("Coluna 'Comercial' não encontrada")
            selected_comercial = []
        
        # Filtro por Cliente
        if 'Cliente' in df.columns:
            clientes = sorted(df['Cliente'].dropna().unique())
            selected_cliente = st.multiselect(
                "Selecione o(s) Cliente(s):",
                clientes,
                default=clientes[:3] if len(clientes) > 3 else clientes
            )
        else:
            st.warning("Coluna 'Cliente' não encontrada")
            selected_cliente = []
        
        # Filtro por Artigo
        if 'Artigo' in df.columns:
            artigos = sorted(df['Artigo'].dropna().unique())
            selected_artigo = st.multiselect(
                "Selecione o(s) Artigo(s):",
                artigos,
                default=artigos[:5] if len(artigos) > 5 else artigos
            )
        else:
            st.warning("Coluna 'Artigo' não encontrada")
            selected_artigo = []
        
        # Filtro por Categoria
        if 'Categoria' in df.columns:
            categorias = sorted(df['Categoria'].dropna().unique())
            selected_categoria = st.multiselect(
                "Selecione a(s) Categoria(s):",
                categorias,
                default=categorias
            )
        else:
            st.warning("Coluna 'Categoria' não encontrada")
            selected_categoria = []
        
        st.markdown("---")
        st.markdown("### 📈 Métricas")
        
        if len(df) > 0:
            total_vendas = df['V. Líquido'].sum() if 'V. Líquido' in df.columns else 0
            total_clientes = df['Cliente'].nunique() if 'Cliente' in df.columns else 0
            total_comerciais = df['Comercial'].nunique() if 'Comercial' in df.columns else 0
            total_artigos = df['Artigo'].nunique() if 'Artigo' in df.columns else 0
            
            st.metric("💰 Total Vendas", f"€{total_vendas:,.2f}")
            st.metric("👥 Total Clientes", total_clientes)
            st.metric("👨‍💼 Total Comerciais", total_comerciais)
            st.metric("📦 Total Artigos", total_artigos)

    # Layout principal com tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard Principal", "📈 Análise Comparativa", "📋 Detalhes por Artigo", "📁 Exportação"])

    with tab1:
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if selected_comercial:
            df_filtrado = df_filtrado[df_filtrado['Comercial'].isin(selected_comercial)]
        
        if selected_cliente:
            df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(selected_cliente)]
        
        if selected_artigo:
            df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(selected_artigo)]
        
        if selected_categoria:
            df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(selected_categoria)]
        
        if len(df_filtrado) == 0:
            st.warning("❌ Nenhum dado encontrado com os filtros aplicados.")
        else:
            st.success(f"✅ {len(df_filtrado)} registros encontrados")
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_vendas_filtrado = df_filtrado['V. Líquido'].sum()
                st.markdown(f"""
                <div class="metric-card-success">
                    <h3 style="margin:0; font-size: 0.9rem;">Total Vendas Filtrado</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">€{total_vendas_filtrado:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                qtd_total = df_filtrado['Qtd.'].sum() if 'Qtd.' in df_filtrado.columns else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size: 0.9rem;">Quantidade Total</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{qtd_total:,.0f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                clientes_unicos = df_filtrado['Cliente'].nunique()
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size: 0.9rem;">Clientes Únicos</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{clientes_unicos}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                ticket_medio = total_vendas_filtrado / len(df_filtrado) if len(df_filtrado) > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size: 0.9rem;">Ticket Médio</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">€{ticket_medio:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Gráficos
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("### 📈 Vendas por Comercial")
                if 'Comercial' in df_filtrado.columns and 'V. Líquido' in df_filtrado.columns:
                    vendas_comercial = df_filtrado.groupby('Comercial')['V. Líquido'].sum().sort_values(ascending=False)
                    fig1 = px.bar(
                        vendas_comercial, 
                        x=vendas_comercial.index, 
                        y=vendas_comercial.values,
                        title="Vendas Totais por Comercial",
                        color=vendas_comercial.values,
                        color_continuous_scale='viridis'
                    )
                    fig1.update_layout(showlegend=False)
                    st.plotly_chart(fig1, use_container_width=True)
            
            with col_chart2:
                st.markdown("### 📊 Vendas por Categoria")
                if 'Categoria' in df_filtrado.columns and 'V. Líquido' in df_filtrado.columns:
                    vendas_categoria = df_filtrado.groupby('Categoria')['V. Líquido'].sum().sort_values(ascending=False)
                    fig2 = px.pie(
                        vendas_categoria, 
                        values=vendas_categoria.values, 
                        names=vendas_categoria.index,
                        title="Distribuição de Vendas por Categoria"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
            
            # Top clientes e artigos
            col_top1, col_top2 = st.columns(2)
            
            with col_top1:
                st.markdown("### 🏆 Top 10 Clientes")
                if 'Cliente' in df_filtrado.columns and 'V. Líquido' in df_filtrado.columns:
                    top_clientes = df_filtrado.groupby('Cliente')['V. Líquido'].sum().nlargest(10)
                    st.dataframe(top_clientes.reset_index().rename(columns={'V. Líquido': 'Total Vendas'}), use_container_width=True)
            
            with col_top2:
                st.markdown("### 🎯 Top 10 Artigos")
                if 'Artigo' in df_filtrado.columns and 'V. Líquido' in df_filtrado.columns:
                    top_artigos = df_filtrado.groupby('Artigo')['V. Líquido'].sum().nlargest(10)
                    st.dataframe(top_artigos.reset_index().rename(columns={'V. Líquido': 'Total Vendas'}), use_container_width=True)

    with tab2:
        st.markdown("## 📊 Análise Comparativa: Cliente x Comercial")
        
        if len(df_filtrado) > 0:
            # Heatmap de Vendas por Cliente e Comercial
            st.markdown("### 🔥 Heatmap - Vendas por Cliente e Comercial")
            
            if all(col in df_filtrado.columns for col in ['Cliente', 'Comercial', 'V. Líquido']):
                # Agrupar por Cliente e Comercial
                pivot_data = df_filtrado.pivot_table(
                    values='V. Líquido', 
                    index='Cliente', 
                    columns='Comercial', 
                    aggfunc='sum',
                    fill_value=0
                )
                
                # Criar heatmap
                fig_heatmap = px.imshow(
                    pivot_data,
                    title="Heatmap de Vendas - Cliente vs Comercial",
                    color_continuous_scale='viridis',
                    aspect="auto"
                )
                fig_heatmap.update_layout(height=600)
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Tabela de dados do heatmap
                with st.expander("📋 Ver Dados do Heatmap"):
                    st.dataframe(pivot_data, use_container_width=True)
            
            # Análise de performance por comercial
            st.markdown("### 📈 Performance por Comercial")
            
            if all(col in df_filtrado.columns for col in ['Comercial', 'Cliente', 'V. Líquido']):
                performance_data = df_filtrado.groupby('Comercial').agg({
                    'V. Líquido': ['sum', 'mean', 'count'],
                    'Cliente': 'nunique'
                }).round(2)
                
                performance_data.columns = ['Total Vendas', 'Ticket Médio', 'Nº Vendas', 'Clientes Únicos']
                performance_data = performance_data.sort_values('Total Vendas', ascending=False)
                
                col_perf1, col_perf2 = st.columns(2)
                
                with col_perf1:
                    st.dataframe(performance_data, use_container_width=True)
                
                with col_perf2:
                    fig_perf = px.bar(
                        performance_data.reset_index(), 
                        x='Comercial', 
                        y='Total Vendas',
                        title="Comparação de Vendas por Comercial",
                        color='Total Vendas',
                        color_continuous_scale='plasma'
                    )
                    st.plotly_chart(fig_perf, use_container_width=True)

    with tab3:
        st.markdown("## 📋 Análise Detalhada por Artigo")
        
        if len(df_filtrado) > 0 and 'Artigo' in df_filtrado.columns:
            # Selecionar artigo para análise detalhada
            artigos_disponiveis = sorted(df_filtrado['Artigo'].unique())
            artigo_selecionado = st.selectbox("Selecione um Artigo para análise detalhada:", artigos_disponiveis)
            
            if artigo_selecionado:
                dados_artigo = df_filtrado[df_filtrado['Artigo'] == artigo_selecionado]
                
                col_art1, col_art2, col_art3 = st.columns(3)
                
                with col_art1:
                    total_artigo = dados_artigo['V. Líquido'].sum()
                    st.metric("💰 Total do Artigo", f"€{total_artigo:,.2f}")
                
                with col_art2:
                    qtd_artigo = dados_artigo['Qtd.'].sum() if 'Qtd.' in dados_artigo.columns else 0
                    st.metric("📦 Quantidade Vendida", f"{qtd_artigo:,.0f}")
                
                with col_art3:
                    clientes_artigo = dados_artigo['Cliente'].nunique()
                    st.metric("👥 Clientes que Compraram", clientes_artigo)
                
                # Top clientes para este artigo
                st.markdown(f"### 🏆 Top Clientes - {artigo_selecionado}")
                top_clientes_artigo = dados_artigo.groupby('Cliente')['V. Líquido'].sum().nlargest(10)
                
                col_clientes1, col_clientes2 = st.columns(2)
                
                with col_clientes1:
                    st.dataframe(
                        top_clientes_artigo.reset_index().rename(columns={'V. Líquido': 'Total Gasto'}),
                        use_container_width=True
                    )
                
                with col_clientes2:
                    fig_clientes_artigo = px.bar(
                        top_clientes_artigo.reset_index(), 
                        x='Cliente', 
                        y='V. Líquido',
                        title=f"Top Clientes - {artigo_selecionado}",
                        color='V. Líquido',
                        color_continuous_scale='thermal'
                    )
                    fig_clientes_artigo.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_clientes_artigo, use_container_width=True)
                
                # Performance por comercial para este artigo
                st.markdown(f"### 👨‍💼 Performance Comercial - {artigo_selecionado}")
                performance_artigo = dados_artigo.groupby('Comercial').agg({
                    'V. Líquido': ['sum', 'count'],
                    'Cliente': 'nunique'
                }).round(2)
                
                performance_artigo.columns = ['Total Vendas', 'Nº Vendas', 'Clientes Únicos']
                performance_artigo = performance_artigo.sort_values('Total Vendas', ascending=False)
                
                st.dataframe(performance_artigo, use_container_width=True)

    with tab4:
        st.markdown("## 📁 Exportação de Dados")
        
        if len(df_filtrado) > 0:
            # Criar arquivo Excel com múltiplas abas
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                # Dados filtrados
                df_filtrado.to_excel(writer, sheet_name='Dados_Filtrados', index=False)
                
                # Resumos
                if all(col in df_filtrado.columns for col in ['Comercial', 'V. Líquido']):
                    resumo_comercial = df_filtrado.groupby('Comercial').agg({
                        'V. Líquido': ['sum', 'mean', 'count'],
                        'Cliente': 'nunique',
                        'Qtd.': 'sum' if 'Qtd.' in df_filtrado.columns else None
                    }).round(2)
                    resumo_comercial.columns = ['Total Vendas', 'Ticket Médio', 'Nº Vendas', 'Clientes Únicos', 'Quantidade Total']
                    resumo_comercial.to_excel(writer, sheet_name='Resumo_Comercial')
                
                if all(col in df_filtrado.columns for col in ['Cliente', 'V. Líquido']):
                    resumo_cliente = df_filtrado.groupby('Cliente')['V. Líquido'].sum().nlargest(50)
                    resumo_cliente.to_excel(writer, sheet_name='Top_Clientes')
                
                if all(col in df_filtrado.columns for col in ['Artigo', 'V. Líquido']):
                    resumo_artigo = df_filtrado.groupby('Artigo')['V. Líquido'].sum().nlargest(50)
                    resumo_artigo.to_excel(writer, sheet_name='Top_Artigos')
            
            excel_buffer.seek(0)
            
            # Botão de download
            st.download_button(
                label="⬇️ BAIXAR RELATÓRIO COMPLETO (Excel)",
                data=excel_buffer.getvalue(),
                file_name=f"analise_vendas_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            # Estatísticas do relatório
            st.info(f"""
            **📊 Relatório contém:**
            - {len(df_filtrado)} registros de vendas
            - {df_filtrado['Cliente'].nunique()} clientes únicos
            - {df_filtrado['Comercial'].nunique()} comerciais
            - {df_filtrado['Artigo'].nunique()} artigos diferentes
            - Total de vendas: €{df_filtrado['V. Líquido'].sum():,.2f}
            """)

else:
    st.error("❌ Não foi possível carregar os dados do Excel.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "📊 Dashboard de Análise de Vendas - Cliente x Comercial • "
    f"Última execução: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    "</div>", 
    unsafe_allow_html=True
)
