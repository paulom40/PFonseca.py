import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas - ResumoTR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar dados - CORRIGIDA para nomes de colunas
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('ResumoTR.xlsx')
        
        # IMPORTANTE: Corrigir nomes de colunas com espaços
        # Criar versões sem espaços para uso no código
        df = df.rename(columns={
            'V Líquido': 'V_Liquido',
            'PM': 'Preco_Medio'
        })
        
        # Se 'Nome' existe, renomear para consistência
        if 'Nome' in df.columns:
            df = df.rename(columns={'Nome': 'Entidade_Nome'})
        
        # Garantir que as colunas de data sejam datetime
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            df = df[df['Data'].notna()]
            
            # Extrair informações temporais
            df['Ano'] = df['Data'].dt.year
            df['Mes_Num'] = df['Data'].dt.month
            df['Mes_Nome'] = df['Data'].dt.strftime('%B')
            df['Dia'] = df['Data'].dt.day
        
        # Converter colunas numéricas
        numeric_cols = ['Quantidade', 'V_Liquido', 'Preco_Medio']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(0)
        
        # Verificar colunas obrigatórias
        if 'Comercial' not in df.columns:
            df['Comercial'] = 'Não Informado'
        
        return df
    
    except FileNotFoundError:
        st.error("❌ Arquivo 'ResumoTR.xlsx' não encontrado!")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return None

# Função para criar filtros multiselect
def create_filters(df):
    filtros = {}
    
    # Filtro de Ano
    if 'Ano' in df.columns:
        anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
        anos_selecionados = st.multiselect(
            "**📅 Ano**",
            options=anos_disponiveis,
            default=anos_disponiveis,
            key="filtro_ano"
        )
        filtros['anos'] = anos_selecionados if anos_selecionados else anos_disponiveis
    
    # Filtro de Artigo
    if 'Artigo' in df.columns:
        artigos_disponiveis = sorted(df['Artigo'].dropna().astype(str).unique())
        artigos_selecionados = st.multiselect(
            "**🛒 Artigo**",
            options=artigos_disponiveis,
            default=[],
            key="filtro_artigo"
        )
        filtros['artigos'] = artigos_selecionados
    
    return filtros

def main():
    st.title("📊 Dashboard de Vendas - ResumoTR")
    
    # Carregar dados
    df = load_data()
    if df is None:
        return
    
    # Sidebar com filtros
    with st.sidebar:
        st.header("⚙️ Filtros")
        filtros = create_filters(df)
    
    # Aplicar filtros
    df_filtrado = df.copy()
    if 'anos' in filtros:
        df_filtrado = df_filtrado[df_filtrado['Ano'].isin(filtros['anos'])]
    if 'artigos' in filtros and filtros['artigos']:
        df_filtrado = df_filtrado[df_filtrado['Artigo'].isin(filtros['artigos'])]
    
    # VERIFICAÇÃO DOS DADOS - ADICIONE ESTA SEÇÃO
    with st.expander("🔍 Verificação dos Dados"):
        st.write("Colunas disponíveis:", list(df.columns))
        st.write("Primeiras linhas:", df.head())
        st.write("Tipos de dados:", df.dtypes)
        if 'V_Liquido' in df.columns:
            st.write("Valores V_Liquido (primeiros 10):", df['V_Liquido'].head(10).tolist())
    
    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        total_vendas = df_filtrado['V_Liquido'].sum() if 'V_Liquido' in df_filtrado.columns else 0
        st.metric("💰 Total Vendas", f"€{total_vendas:,.2f}")
    
    with col2:
        total_qtd = df_filtrado['Quantidade'].sum() if 'Quantidade' in df_filtrado.columns else 0
        st.metric("📦 Quantidade", f"{total_qtd:,.0f}")
    
    with col3:
        num_entidades = df_filtrado['Entidade_Nome'].nunique() if 'Entidade_Nome' in df_filtrado.columns else 0
        st.metric("👥 Entidades", num_entidades)
    
    # GRÁFICO CORRIGIDO - EVOLUÇÃO DIÁRIA
    st.markdown("---")
    st.subheader("📈 Evolução Diária de Vendas")
    
    # Verificação antes de criar o gráfico
    if 'Data' in df_filtrado.columns and 'V_Liquido' in df_filtrado.columns and len(df_filtrado) > 0:
        try:
            # Preparar dados
            df_filtrado['Data_Dia'] = df_filtrado['Data'].dt.date
            
            # Verificar se temos dados após o agrupamento
            vendas_diarias = df_filtrado.groupby('Data_Dia')['V_Liquido'].sum().reset_index()
            
            if len(vendas_diarias) > 0:
                # Converter datas para string para evitar problemas com Plotly
                vendas_diarias['Data_Dia'] = vendas_diarias['Data_Dia'].astype(str)
                
                # Criar gráfico SIMPLIFICADO primeiro para testar
                fig = px.line(
                    vendas_diarias,
                    x='Data_Dia',
                    y='V_Liquido',
                    title='Vendas Diárias',
                    markers=True
                )
                
                # Atualizar layout de forma SEGURA
                fig.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Vendas Líquidas (€)",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Se funcionar, mostrar gráfico mais complexo
                st.subheader("📊 Gráfico Detalhado (Vendas + Quantidade)")
                
                # Preparar dados para gráfico com eixo secundário
                dados_diarios = df_filtrado.groupby('Data_Dia').agg({
                    'V_Liquido': 'sum',
                    'Quantidade': 'sum'
                }).reset_index()
                dados_diarios['Data_Dia'] = dados_diarios['Data_Dia'].astype(str)
                
                # Criar figura
                fig2 = go.Figure()
                
                # Adicionar linha de vendas
                fig2.add_trace(go.Scatter(
                    x=dados_diarios['Data_Dia'],
                    y=dados_diarios['V_Liquido'],
                    mode='lines+markers',
                    name='Vendas (€)',
                    line=dict(color='blue', width=2)
                ))
                
                # Adicionar barras de quantidade
                fig2.add_trace(go.Bar(
                    x=dados_diarios['Data_Dia'],
                    y=dados_diarios['Quantidade'],
                    name='Quantidade',
                    marker_color='lightblue',
                    opacity=0.6,
                    yaxis='y2'
                ))
                
                # Atualizar layout com tratamento de erro
                try:
                    fig2.update_layout(
                        title=dict(text='Vendas vs Quantidade Diária'),
                        xaxis=dict(title='Data'),
                        yaxis=dict(
                            title='Vendas (€)',
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
                        hovermode='x unified',
                        height=400
                    )
                except Exception as layout_error:
                    st.warning(f"Aviso no layout: {layout_error}")
                    # Fallback para layout simples
                    fig2.update_layout(
                        title='Vendas vs Quantidade Diária',
                        xaxis_title='Data',
                        yaxis_title='Vendas (€)',
                        height=400
                    )
                
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Sem dados para mostrar após o agrupamento diário.")
                
        except Exception as e:
            st.error(f"Erro ao criar gráfico: {str(e)}")
            # Mostrar dados para debug
            st.write("Dados usados para o gráfico:")
            if 'df_filtrado' in locals():
                st.write(df_filtrado[['Data', 'V_Liquido', 'Quantidade']].head())
    else:
        st.warning("Dados insuficientes para criar gráfico de evolução diária.")
    
    # Tabela de dados
    st.markdown("---")
    st.subheader("📋 Dados Detalhados")
    
    if len(df_filtrado) > 0:
        # Mostrar colunas relevantes
        colunas_mostrar = ['Data', 'Entidade_Nome', 'Artigo', 'Quantidade', 'V_Liquido', 'Comercial']
        colunas_disponiveis = [c for c in colunas_mostrar if c in df_filtrado.columns]
        
        df_display = df_filtrado[colunas_disponiveis].copy()
        if 'Data' in df_display.columns:
            df_display['Data'] = df_display['Data'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(df_display.head(50), use_container_width=True)
        
        # Botão de download
        csv = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name="dados_filtrados.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
