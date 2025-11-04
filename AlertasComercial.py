import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from io import BytesIO
import xlsxwriter
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página com layout wide
st.set_page_config(
    page_title="Dashboard de Vendas - Análise Completa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.5rem;">📊 DASHBOARD DE VENDAS - ANÁLISE COMPLETA</h1>
    <p style="margin:0; opacity: 0.9; font-size: 1.1rem;">Análise Cliente x Comercial + Alertas de Inatividade</p>
</div>
""", unsafe_allow_html=True)

# URL do arquivo Excel
url = "https://github.com/paulom40/PFonseca.py/raw/main/Vendas_Globais.xlsx"

@st.cache_data
def load_data():
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Carregar o ficheiro Excel
        excel_file = BytesIO(response.content)
        
        # Ler o ficheiro mantendo a estrutura original
        df = pd.read_excel(excel_file, sheet_name="Sheet1", header=0)
        
        st.info(f"📊 Colunas originais carregadas: {list(df.columns)}")
        
        # VERIFICAÇÃO DAS COLUNAS - CORREÇÃO: Já temos a coluna "Artigo"
        st.info("🔍 Estrutura das colunas identificada:")
        for i, col in enumerate(df.columns):
            st.write(f"Coluna {i}: '{col}'")
        
        # CORREÇÃO CRÍTICA: Não precisamos renomear, a coluna "Artigo" já existe
        if 'Artigo' in df.columns:
            st.success("✅ COLUNA 'ARTIGO' JÁ EXISTE NO DATASET!")
            
            # Verificar o conteúdo real da coluna Artigo
            st.info("📦 Conteúdo da Coluna Artigo - Primeiros 15 valores:")
            artigos_sample = df['Artigo'].dropna().head(15).tolist()
            for i, artigo in enumerate(artigos_sample):
                st.write(f"  {i+1}. {artigo}")
        else:
            st.error("❌ Coluna 'Artigo' não encontrada!")
            st.info("📋 Colunas disponíveis:")
            for i, col in enumerate(df.columns):
                st.write(f"{i}: {col}")
            return None
        
        # Processar colunas
        df.columns = [col.strip() for col in df.columns]
        
        # Converter colunas numéricas
        if 'Qtd.' in df.columns:
            df['Qtd.'] = pd.to_numeric(df['Qtd.'], errors='coerce')
        if 'V. Líquido' in df.columns:
            df['V. Líquido'] = pd.to_numeric(df['V. Líquido'], errors='coerce')
        
        # Limpar dados de texto
        text_columns = ['Cliente', 'Comercial', 'Artigo', 'Categoria']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Processar datas
        if 'Mês' in df.columns and 'Ano' in df.columns:
            meses_map = {
                'Janeiro': '01', 'Fevereiro': '02', 'Março': '03', 'Abril': '04',
                'Maio': '05', 'Junho': '06', 'Julho': '07', 'Agosto': '08',
                'Setembro': '09', 'Outubro': '10', 'Novembro': '11', 'Dezembro': '12'
            }
            
            df['Mês_Num'] = df['Mês'].map(meses_map)
            df['Data'] = pd.to_datetime(
                df['Ano'].astype(str) + '-' + df['Mês_Num'] + '-01', 
                errors='coerce'
            )
            df = df.drop('Mês_Num', axis=1, errors='ignore')
        
        st.success(f"✅ Dados carregados com sucesso: {len(df)} registos")
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar ficheiro: {e}")
        return None

# Container principal para controles
with st.container():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔄 Gestão de Dados")
        if st.button("🔄 Atualizar Dados do Excel", use_container_width=True):
            st.cache_data.clear()
            st.session_state.df = load_data()
            st.session_state.last_updated = datetime.now()
            if st.session_state.df is not None:
                st.success("✅ Dados atualizados com sucesso!")

# Carregar dados
df = st.session_state.get("df", load_data())

if df is not None:
    # Sidebar com filtros
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
        
        # Filtro por Cliente
        if 'Cliente' in df.columns:
            clientes = sorted(df['Cliente'].dropna().unique())
            selected_cliente = st.multiselect(
                "Selecione o(s) Cliente(s):",
                clientes,
                default=clientes[:3] if len(clientes) > 3 else clientes
            )
        
        # FILTRO POR ARTIGO - CORREÇÃO: Usar a coluna Artigo correta
        st.markdown("### 📦 Filtro por Artigo")
        if 'Artigo' in df.columns:
            # Obter valores únicos da coluna Artigo
            artigos = sorted(df['Artigo'].dropna().unique())
            
            st.success(f"🎯 {len(artigos)} artigos únicos carregados da coluna 'Artigo'")
            
            # Mostrar alguns exemplos para confirmação
            with st.expander("🔍 Ver primeiros 20 artigos disponíveis"):
                for i, artigo in enumerate(artigos[:20]):
                    st.write(f"{i+1}. {artigo}")
            
            # Filtro multiselect
            selected_artigo = st.multiselect(
                "Selecione o(s) Artigo(s):",
                options=artigos,
                default=artigos[:5] if len(artigos) > 5 else artigos,
                help="Selecione os artigos que deseja analisar"
            )
            
            if selected_artigo:
                st.success(f"✅ {len(selected_artigo)} artigo(s) selecionado(s)")
        else:
            st.error("❌ Coluna 'Artigo' não encontrada!")
            selected_artigo = []
        
        # Filtro por Categoria
        if 'Categoria' in df.columns:
            categorias = sorted(df['Categoria'].dropna().unique())
            selected_categoria = st.multiselect(
                "Selecione a(s) Categoria(s):",
                categorias,
                default=categorias
            )
        
        # Estatísticas rápidas
        st.markdown("---")
        st.markdown("### 📈 Estatísticas Rápidas")
        
        if len(df) > 0:
            total_vendas = df['V. Líquido'].sum() if 'V. Líquido' in df.columns else 0
            total_artigos = df['Artigo'].nunique() if 'Artigo' in df.columns else 0
            total_clientes = df['Cliente'].nunique() if 'Cliente' in df.columns else 0
            
            st.metric("💰 Total Vendas", f"€{total_vendas:,.2f}")
            st.metric("📦 Total Artigos", total_artigos)
            st.metric("👥 Total Clientes", total_clientes)

    # Layout principal
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard Principal", "📋 Dados Detalhados", "🎯 Análise por Artigo"])

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
            st.success(f"✅ {len(df_filtrado)} registos encontrados")
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_vendas_filtrado = df_filtrado['V. Líquido'].sum()
                st.markdown(f"""
                <div class="metric-card-success">
                    <h3 style="margin:0; font-size: 0.9rem;">Total Vendas</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">€{total_vendas_filtrado:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                artigos_unicos_filtrado = df_filtrado['Artigo'].nunique()
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size: 0.9rem;">Artigos Únicos</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{artigos_unicos_filtrado}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                clientes_unicos_filtrado = df_filtrado['Cliente'].nunique()
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size: 0.9rem;">Clientes Únicos</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{clientes_unicos_filtrado}</p>
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
                st.markdown("### 📈 Top Artigos por Vendas")
                if 'Artigo' in df_filtrado.columns and 'V. Líquido' in df_filtrado.columns:
                    top_artigos = df_filtrado.groupby('Artigo')['V. Líquido'].sum().nlargest(10)
                    
                    fig = px.bar(
                        top_artigos, 
                        x=top_artigos.values,
                        y=top_artigos.index,
                        orientation='h',
                        title="Top 10 Artigos por Vendas",
                        color=top_artigos.values,
                        color_continuous_scale='viridis'
                    )
                    fig.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_chart2:
                st.markdown("### 📊 Vendas por Categoria")
                if 'Categoria' in df_filtrado.columns and 'V. Líquido' in df_filtrado.columns:
                    vendas_categoria = df_filtrado.groupby('Categoria')['V. Líquido'].sum()
                    
                    fig2 = px.pie(
                        vendas_categoria, 
                        values=vendas_categoria.values, 
                        names=vendas_categoria.index,
                        title="Distribuição de Vendas por Categoria"
                    )
                    st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown("### 📋 Dados Detalhados")
        
        # Mostrar dados filtrados
        st.dataframe(
            df_filtrado[['Artigo', 'Cliente', 'Comercial', 'Categoria', 'Qtd.', 'V. Líquido', 'Mês', 'Ano']],
            use_container_width=True
        )

    with tab3:
        st.markdown("### 🎯 Análise Detalhada por Artigo")
        
        if 'Artigo' in df.columns:
            # Estatísticas por artigo
            stats_artigos = df.groupby('Artigo').agg({
                'V. Líquido': ['sum', 'mean', 'count'],
                'Qtd.': 'sum',
                'Cliente': 'nunique',
                'Comercial': 'nunique'
            }).round(2)
            
            stats_artigos.columns = [
                'Total_Vendas', 'Ticket_Medio', 'Num_Vendas', 
                'Quantidade_Total', 'Clientes_Unicos', 'Comerciais_Unicos'
            ]
            stats_artigos = stats_artigos.sort_values('Total_Vendas', ascending=False)
            
            st.dataframe(stats_artigos, use_container_width=True)
            
            # Download da análise
            st.markdown("### 📁 Exportar Dados")
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                stats_artigos.to_excel(writer, sheet_name='Analise_Artigos', index=True)
            
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Download Análise de Artigos",
                data=excel_data,
                file_name=f"analise_artigos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )

else:
    st.error("❌ Não foi possível carregar os dados do Excel.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "📊 Dashboard de Análise de Vendas • "
    f"Última execução: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    "</div>", 
    unsafe_allow_html=True
)
