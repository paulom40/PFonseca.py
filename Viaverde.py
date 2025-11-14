import streamlit as st
import pandas as pd
import altair as alt
import base64
from io import BytesIO
from datetime import datetime
import json

# Configuração da página
st.set_page_config(
    page_title="Via Verde Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para aparência moderna
st.markdown("""
<style>
    /* Ocultar menu, header e footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Estilos modernos */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
        border-left: 4px solid #667eea;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    
    .metric-card.green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .metric-card.pink {
        background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);
    }
    
    .metric-card.orange {
        background: linear-gradient(135deg, #fdbb2d 0%, #22c1c3 100%);
    }
    
    .filter-section {
        background: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
    }
    
    .export-buttons {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
    }
    
    h1, h2, h3 {
        color: white !important;
        font-weight: 700 !important;
    }
    
    .stSelectbox > div > div, .stMultiselect > div > div {
        border-radius: 10px;
    }
    
    .export-button {
        display: inline-block;
        padding: 12px 24px;
        margin: 5px;
        border-radius: 10px;
        font-weight: 600;
        text-decoration: none;
        text-align: center;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        color: white !important;
        width: 90%;
    }
    
    .export-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        text-decoration: none;
        color: white !important;
    }
    
    .export-excel {
        background: linear-gradient(135deg, #217346 0%, #28a745 100%);
    }
    
    .export-csv {
        background: linear-gradient(135deg, #fd7e14 0%, #e44d26 100%);
    }
    
    .export-html {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
    }
</style>
""", unsafe_allow_html=True)

# Funções para exportação
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet com dados completos
        df.to_excel(writer, index=False, sheet_name='Dados_ViaVerde')
        
        # Sheet com resumo
        summary_data = {
            'Métrica': ['Total de Registos', 'Valor Total', 'Valor Médio', 'Valor Máximo', 'Valor Mínimo'],
            'Valor': [
                len(df),
                f"€{df['Value'].sum():,.2f}",
                f"€{df['Value'].mean():.2f}",
                f"€{df['Value'].max():.2f}",
                f"€{df['Value'].min():.2f}"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, index=False, sheet_name='Resumo')
        
        workbook = writer.book
        
        # Formatar sheet de dados
        worksheet_data = writer.sheets['Dados_ViaVerde']
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#667eea',
            'font_color': 'white',
            'border': 1
        })
        
        for col_num, value in enumerate(df.columns.values):
            worksheet_data.write(0, col_num, value, header_format)
            
        worksheet_data.autofilter(0, 0, 0, len(df.columns) - 1)
        
        # Formatar sheet de resumo
        worksheet_summary = writer.sheets['Resumo']
        for col_num, value in enumerate(summary_df.columns.values):
            worksheet_summary.write(0, col_num, value, header_format)
        
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link_excel(df, filename="dados_viaverde.xlsx"):
    excel_data = to_excel(df)
    b64 = base64.b64encode(excel_data).decode()
    return f'<a class="export-button export-excel" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📊 Excel (.xlsx)</a>'

def get_table_download_link_csv(df, filename="dados_viaverde.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a class="export-button export-csv" href="data:file/csv;base64,{b64}" download="{filename}">📝 CSV (.csv)</a>'

def create_complete_html_report(df, filtered_df, filters, charts_data, filename="relatorio_completo_viaverde.html"):
    """Cria um relatório HTML completo com toda a página"""
    
    # Preparar dados para os gráficos
    month_order = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    # Dados para gráfico de meses
    chart_df_month = filtered_df.groupby("Month")["Value"].sum().reset_index()
    all_months_df = pd.DataFrame({'Month': month_order})
    chart_df_month = all_months_df.merge(chart_df_month, on='Month', how='left').fillna(0)
    
    # Dados para gráfico de dias
    chart_df_day = filtered_df.groupby("Dia")["Value"].sum().reset_index().sort_values("Dia")
    
    # Criar HTML completo
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Relatório Completo - Via Verde Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .header {{
                text-align: center;
                color: white;
                padding: 40px 0;
                margin-bottom: 30px;
            }}
            
            .header h1 {{
                font-size: 3em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            
            .header p {{
                font-size: 1.3em;
                opacity: 0.9;
            }}
            
            .report-section {{
                background: white;
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            }}
            
            .filters-info {{
                background: rgba(255, 255, 255, 0.95);
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 25px;
                border-left: 4px solid #667eea;
            }}
            
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }}
            
            .metric-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            }}
            
            .metric-card.green {{
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            }}
            
            .metric-card.pink {{
                background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);
            }}
            
            .metric-card.orange {{
                background: linear-gradient(135deg, #fdbb2d 0%, #22c1c3 100%);
            }}
            
            .metric-card h3 {{
                font-size: 1.1em;
                margin-bottom: 10px;
                opacity: 0.9;
            }}
            
            .metric-card h2 {{
                font-size: 2em;
                margin: 10px 0;
            }}
            
            .metric-card p {{
                opacity: 0.8;
                font-size: 0.9em;
            }}
            
            .charts-container {{
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 30px;
                margin: 30px 0;
            }}
            
            .chart-card {{
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}
            
            .chart-placeholder {{
                background: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 10px;
                padding: 60px 20px;
                text-align: center;
                color: #6c757d;
                margin: 20px 0;
            }}
            
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}
            
            .data-table th {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
            }}
            
            .data-table td {{
                padding: 12px;
                border-bottom: 1px solid #dee2e6;
            }}
            
            .data-table tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            
            .data-table tr:hover {{
                background-color: #e3f2fd;
            }}
            
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                color: white;
                opacity: 0.8;
            }}
            
            .summary-stats {{
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 25px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #667eea;
            }}
            
            @media (max-width: 768px) {{
                .charts-container {{
                    grid-template-columns: 1fr;
                }}
                
                .metrics-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .header h1 {{
                    font-size: 2em;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Cabeçalho -->
            <div class="header">
                <h1>🚗 Via Verde Dashboard</h1>
                <p>Relatório Completo - Análise de Portagens</p>
                <p style="margin-top: 10px; font-size: 1em;">Gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M")}</p>
            </div>
            
            <!-- Informações dos Filtros -->
            <div class="filters-info">
                <h2>🔍 Filtros Aplicados</h2>
                <div style="margin-top: 15px;">
                    <p><strong>Matrícula:</strong> {filters['matricula']}</p>
                    <p><strong>Ano:</strong> {filters['ano']}</p>
                    <p><strong>Meses:</strong> {filters['meses']}</p>
                    <p><strong>Dias:</strong> {filters['dias']}</p>
                </div>
            </div>
            
            <!-- Métricas Principais -->
            <div class="report-section">
                <h2>📊 Métricas Principais</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>💰 Total Gasto</h3>
                        <h2>€{filtered_df['Value'].sum():,.2f}</h2>
                        <p>Valor acumulado</p>
                    </div>
                    <div class="metric-card green">
                        <h3>📊 Total de Registos</h3>
                        <h2>{len(filtered_df):,}</h2>
                        <p>Transações totais</p>
                    </div>
                    <div class="metric-card pink">
                        <h3>📈 Média por Registo</h3>
                        <h2>€{filtered_df['Value'].mean():.2f}</h2>
                        <p>Valor médio</p>
                    </div>
                    <div class="metric-card orange">
                        <h3>🎯 Valor Máximo</h3>
                        <h2>€{filtered_df['Value'].max():.2f}</h2>
                        <p>Maior transação</p>
                    </div>
                </div>
            </div>
            
            <!-- Gráficos -->
            <div class="report-section">
                <h2>📈 Visualizações</h2>
                
                <div class="charts-container">
                    <!-- Gráfico de Barras - Mensal -->
                    <div class="chart-card">
                        <h3>📅 Valor Total por Mês</h3>
                        <canvas id="monthlyChart" width="400" height="200"></canvas>
                    </div>
                    
                    <!-- Gráfico de Área - Diário -->
                    <div class="chart-card">
                        <h3>📈 Tendência por Dia</h3>
                        <canvas id="dailyChart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- Dados Detalhados -->
            <div class="report-section">
                <h2>📋 Dados Detalhados</h2>
                <p><strong>Total de registos exibidos:</strong> {len(filtered_df)}</p>
                {filtered_df[['Matricula', 'Date', 'Month', 'Dia', 'Value']].to_html(classes='data-table', index=False, border=0, escape=False)}
            </div>
            
            <!-- Resumo do Dataset -->
            <div class="report-section">
                <h2>📊 Informações do Dataset</h2>
                <div class="summary-stats">
                    <p><strong>Período Total:</strong> {df['Ano'].min()} - {df['Ano'].max()}</p>
                    <p><strong>Matrículas Únicas:</strong> {len(df['Matricula'].unique())}</p>
                    <p><strong>Total de Registos no Dataset:</strong> {len(df):,}</p>
                    <p><strong>Valor Total no Dataset:</strong> €{df['Value'].sum():,.2f}</p>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p>🚗 <strong>Via Verde Dashboard</strong> - Relatório gerado automaticamente</p>
                <p>© 2024 - Todos os direitos reservados</p>
            </div>
        </div>
        
        <script>
            // Dados para os gráficos
            const monthlyData = {{
                labels: {json.dumps(chart_df_month['Month'].tolist())},
                values: {json.dumps(chart_df_month['Value'].tolist())}
            }};
            
            const dailyData = {{
                labels: {json.dumps(chart_df_day['Dia'].astype(str).tolist())},
                values: {json.dumps(chart_df_day['Value'].tolist())}
            }};
            
            // Gráfico Mensal
            const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
            new Chart(monthlyCtx, {{
                type: 'bar',
                data: {{
                    labels: monthlyData.labels,
                    datasets: [{{
                        label: 'Valor (€)',
                        data: monthlyData.values,
                        backgroundColor: '#667eea',
                        borderColor: '#764ba2',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Distribuição Mensal de Gastos'
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return '€' + context.parsed.y.toFixed(2);
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Valor (€)'
                            }}
                        }}
                    }}
                }}
            }});
            
            // Gráfico Diário
            const dailyCtx = document.getElementById('dailyChart').getContext('2d');
            new Chart(dailyCtx, {{
                type: 'line',
                data: {{
                    labels: dailyData.labels,
                    datasets: [{{
                        label: 'Valor (€)',
                        data: dailyData.values,
                        backgroundColor: 'rgba(17, 153, 142, 0.2)',
                        borderColor: '#11998e',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Distribuição Diária de Gastos'
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return '€' + context.parsed.y.toFixed(2);
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Valor (€)'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: 'Dia do Mês'
                            }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    b64 = base64.b64encode(html_content.encode()).decode()
    return f'<a class="export-button export-html" href="data:text/html;base64,{b64}" download="{filename}">🌐 Relatório Completo HTML</a>'

def get_table_download_link_html(df, filtered_df, filters, filename="relatorio_completo_viaverde.html"):
    return create_complete_html_report(df, filtered_df, filters, {}, filename)

# 📂 Carregar Excel do GitHub
file_url = "https://github.com/paulom40/PFonseca.py/raw/main/ViaVerde_streamlit.xlsx"

# 🔷 Header moderno
st.markdown("""
<div style='text-align: center; padding: 30px 0;'>
    <h1 style='color: white; font-size: 3em; margin-bottom: 10px;'>🚗 Via Verde Dashboard</h1>
    <p style='color: white; font-size: 1.3em; opacity: 0.9;'>Análise Inteligente de Portagens</p>
</div>
""", unsafe_allow_html=True)

# 📊 Carregar e validar dados
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(file_url)
        df = df.drop(columns=['Mês'], errors='ignore')
        return df, True
    except Exception as e:
        st.error(f"❌ Erro ao carregar o arquivo: {e}")
        return None, False

df, success = load_data()

if not success:
    st.stop()

required_cols = ['Matricula', 'Date', 'Ano', 'Month', 'Dia', 'Value']
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"⚠️ Faltam colunas: {', '.join(missing_cols)}")
    st.stop()

# 🗓️ Normalizar nomes dos meses
month_mapping = {
    'janeiro': 'Janeiro', 'fevereiro': 'Fevereiro', 'março': 'Março', 'abril': 'Abril',
    'maio': 'Maio', 'junho': 'Junho', 'julho': 'Julho', 'agosto': 'Agosto',
    'setembro': 'Setembro', 'outubro': 'Outubro', 'novembro': 'Novembro', 'dezembro': 'Dezembro'
}
df['Month'] = df['Month'].str.lower().map(month_mapping).fillna(df['Month'])

# 🔍 Seção de Filtros
st.markdown('<div class="filter-section">', unsafe_allow_html=True)
st.markdown("### 🔍 Filtros Avançados")

col1, col2, col3, col4 = st.columns([2, 2, 3, 2])

with col1:
    matriculas = sorted(df['Matricula'].unique())
    selected_matricula = st.selectbox("**Matrícula**", ["Todas"] + matriculas)

with col2:
    anos = sorted(df['Ano'].unique())
    selected_ano = st.selectbox("**Ano**", ["Todos"] + anos)

with col3:
    months_available = sorted(df['Month'].unique(), key=lambda x: [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ].index(x))
    selected_months = st.multiselect("**Mês**", months_available, default=months_available)
    
with col4:
    dias = sorted(df['Dia'].unique())
    selected_dias = st.multiselect("**Dia**", ["Todos"] + dias, default=["Todos"])

st.markdown('</div>', unsafe_allow_html=True)

# Aplicar filtros
filtered_df = df.copy()

if selected_matricula != "Todas":
    filtered_df = filtered_df[filtered_df['Matricula'] == selected_matricula]

if selected_ano != "Todos":
    filtered_df = filtered_df[filtered_df['Ano'].astype(str) == str(selected_ano)]

if selected_months:
    filtered_df = filtered_df[filtered_df['Month'].isin(selected_months)]

if "Todos" not in selected_dias:
    filtered_df = filtered_df[filtered_df['Dia'].isin(selected_dias)]

# Preparar informações dos filtros para o relatório
filters_info = {
    'matricula': selected_matricula,
    'ano': selected_ano,
    'meses': ', '.join(selected_months) if selected_months else 'Todos',
    'dias': ', '.join(map(str, selected_dias)) if "Todos" not in selected_dias else 'Todos'
}

# 📤 Seção de Exportação
if not filtered_df.empty:
    st.markdown('<div class="export-buttons">', unsafe_allow_html=True)
    st.markdown("### 📤 Exportar Dados")
    st.markdown("Faça download dos dados filtrados nos seguintes formatos:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(get_table_download_link_excel(filtered_df), unsafe_allow_html=True)
    
    with col2:
        st.markdown(get_table_download_link_csv(filtered_df), unsafe_allow_html=True)
    
    with col3:
        st.markdown(get_table_download_link_html(df, filtered_df, filters_info), unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-top: 15px; font-size: 0.9em; color: #666;">
        <strong>Formatos disponíveis:</strong><br>
        • <strong>Excel:</strong> Ideal para análise em planilhas<br>
        • <strong>CSV:</strong> Formato universal para dados<br>
        • <strong>HTML:</strong> Relatório completo com gráficos interativos
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 📊 Métricas em tempo real
if not filtered_df.empty:
    total_value = filtered_df['Value'].sum()
    total_records = len(filtered_df)
    avg_value = filtered_df['Value'].mean()
    max_value = filtered_df['Value'].max()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: white; margin: 0; font-size: 1.1em;'>💰 Total Gasto</h3>
            <h2 style='color: white; margin: 10px 0; font-size: 2em;'>€{total_value:,.2f}</h2>
            <p style='color: rgba(255,255,255,0.8); margin: 0;'>Valor acumulado</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card green'>
            <h3 style='color: white; margin: 0; font-size: 1.1em;'>📊 Total de Registos</h3>
            <h2 style='color: white; margin: 10px 0; font-size: 2em;'>{total_records:,}</h2>
            <p style='color: rgba(255,255,255,0.8); margin: 0;'>Transações totais</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card pink'>
            <h3 style='color: white; margin: 0; font-size: 1.1em;'>📈 Média por Registo</h3>
            <h2 style='color: white; margin: 10px 0; font-size: 2em;'>€{avg_value:.2f}</h2>
            <p style='color: rgba(255,255,255,0.8); margin: 0;'>Valor médio</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card orange'>
            <h3 style='color: white; margin: 0; font-size: 1.1em;'>🎯 Valor Máximo</h3>
            <h2 style='color: white; margin: 10px 0; font-size: 2em;'>€{max_value:.2f}</h2>
            <p style='color: rgba(255,255,255,0.8); margin: 0;'>Maior transação</p>
        </div>
        """, unsafe_allow_html=True)

# 📈 Visualizações
if not filtered_df.empty:
    st.markdown("---")
    
    # Gráfico 1: Valor Total por Mês
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📅 Valor Total por Mês")
    
    month_order = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    
    chart_df_month = filtered_df.groupby("Month")["Value"].sum().reset_index()
    all_months_df = pd.DataFrame({'Month': month_order})
    chart_df_month = all_months_df.merge(chart_df_month, on='Month', how='left').fillna(0)
    
    bar_chart = alt.Chart(chart_df_month).mark_bar(color='#667eea').encode(
        x=alt.X('Month:O', title='Mês', sort=month_order, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Value:Q', title='Valor Total (€)'),
        tooltip=['Month', alt.Tooltip('Value:Q', title='Valor (€)', format='.2f')]
    ).properties(height=400)
    
    bar_labels = alt.Chart(chart_df_month[chart_df_month['Value'] > 0]).mark_text(
        align='center', baseline='bottom', fontWeight='bold', color='#2c3e50', dy=-8
    ).encode(
        x=alt.X('Month:O', sort=month_order), y='Value:Q', text=alt.Text('Value:Q', format='.2f')
    )
    
    st.altair_chart(bar_chart + bar_labels, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráfico 2 e Tabela
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📈 Tendência por Dia")
        
        chart_df_day = filtered_df.groupby("Dia")["Value"].sum().reset_index().sort_values("Dia")
        area_chart = alt.Chart(chart_df_day).mark_area(color='#11998e', opacity=0.7).encode(
            x=alt.X('Dia:O', title='Dia do Mês'), y=alt.Y('Value:Q', title='Valor Total (€)'),
            tooltip=['Dia', alt.Tooltip('Value:Q', title='Valor (€)', format='.2f')]
        ).properties(height=300)
        
        st.altair_chart(area_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📋 Dados Filtrados")
        display_df = filtered_df[['Matricula', 'Date', 'Month', 'Dia', 'Value']].copy()
        display_df['Value'] = display_df['Value'].map('€{:.2f}'.format)
        st.dataframe(display_df, use_container_width=True, height=350)
        st.markdown(f"**Total de registos:** {len(filtered_df)}")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning("""
    <div style='background: #fff3cd; color: #856404; padding: 20px; border-radius: 10px; border-left: 5px solid #ffc107; margin: 20px 0;'>
        <h4 style='margin: 0;'>⚠️ Nenhum dado encontrado</h4>
        <p style='margin: 10px 0 0 0;'>Tente ajustar os filtros para visualizar os dados.</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 30px; opacity: 0.8;'>
    <p style='margin: 0; font-size: 1.1em;'>🚗 <strong>Via Verde Dashboard</strong> - Análise de Portagens</p>
</div>
""", unsafe_allow_html=True)
