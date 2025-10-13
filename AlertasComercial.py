import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import BytesIO
import xlsxwriter
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import difflib

# Configuração da página com layout wide
st.set_page_config(
    page_title="📊 Dashboard de Pendências",
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
    
    .metric-card-danger {
        background: linear-gradient(135deg, #ff5858 0%, #f09819 100%);
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
    
    /* Download button específico */
    .download-btn {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%) !important;
    }
    
    /* Email button específico */
    .email-btn {
        background: linear-gradient(135deg, #ff5858 0%, #f09819 100%) !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Input fields styling */
    .stTextInput input, .stTextInput textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.5rem;
    }
    
    .stTextInput input:focus, .stTextInput textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Selectbox styling */
    .stSelectbox div div {
        border-radius: 10px;
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
    
    /* Alert boxes customizados */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Container principal */
    .main-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal com gradiente
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.5rem;">📊 DASHBOARD DE PENDÊNCIAS</h1>
    <p style="margin:0; opacity: 0.9; font-size: 1.1rem;">Gestão Inteligente de Valores em Atraso</p>
</div>
""", unsafe_allow_html=True)

# URL do arquivo Excel
url = "https://github.com/paulom40/PFonseca.py/raw/refs/heads/main/V0808.xlsx"

@st.cache_data
def load_data():
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), sheet_name="Sheet1", header=0)
        df.columns = [col.strip() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar ficheiro: {e}. Verifica o URL ou usa ficheiro local.")
        return None

# Container principal
with st.container():
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 🔄 Gestão de Dados")
        if st.button("🔄 Atualizar Dados do Excel", use_container_width=True):
            st.cache_data.clear()
            st.session_state.df = load_data()
            st.session_state.last_updated = datetime.now()
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
        
        st.markdown("### 📊 Filtro por Comercial")
        
        # Lista de comerciais únicos
        comerciais = sorted(df['Comercial'].dropna().astype(str).unique())
        opcoes_comerciais = ["Todos"] + comerciais
        
        selected_comercial = st.selectbox(
            "Selecione o Comercial:",
            opcoes_comerciais,
            index=0
        )
        
        st.markdown("---")
        st.markdown("### 🔍 Busca Avançada")
        search_term = st.text_input("Digite o nome do Comercial:")
        
        st.markdown("---")
        st.markdown("### 📈 Estatísticas Rápidas")
        
        if len(df) > 0:
            total_pendente = df['Valor Pendente'].sum() if 'Valor Pendente' in df.columns else 0
            total_registros = len(df)
            
            st.metric("📋 Total de Registros", f"{total_registros:,}")
            st.metric("💰 Valor Total", f"€{total_pendente:,.2f}")

    # Processamento dos dados
    st.markdown("### 📋 Processamento de Dados")
    
    # Verificar colunas necessárias
    if "Dias" not in df.columns:
        st.error("❌ A coluna 'Dias' não foi encontrada no ficheiro.")
        st.stop()

    # Limpeza e preparação
    df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
    df['Valor Pendente'] = pd.to_numeric(df['Valor Pendente'], errors='coerce')
    df['Days_Overdue'] = (-df['Dias']).clip(lower=0)
    df['Comercial'] = df['Comercial'].astype(str).str.replace(r'[\t\n\r ]+', ' ', regex=True).str.strip()
    df['Entidade'] = df['Entidade'].astype(str).str.strip()

    # Filtrar pendências
    overdue_df = df[(df['Dias'] <= 0) & (df['Valor Pendente'] > 0)].copy()

    # Aplicar filtros
    if selected_comercial == "Todos" and not search_term:
        df_filtrado = overdue_df.copy()
        filtro_aplicado = "Todos os comerciais"
    elif selected_comercial != "Todos":
        df_filtrado = overdue_df[overdue_df['Comercial'] == selected_comercial].copy()
        filtro_aplicado = f"Comercial: {selected_comercial}"
    elif search_term:
        search_upper = search_term.upper().strip()
        mask_partial = overdue_df['Comercial'].str.upper().str.contains(search_upper, na=False)
        df_filtrado = overdue_df[mask_partial].copy()
        filtro_aplicado = f"Busca: '{search_term}'"
    else:
        df_filtrado = overdue_df.copy()
        filtro_aplicado = "Todos os comerciais"

    # Layout principal com tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard Principal", "📁 Exportação", "📧 Envio por Email"])

    with tab1:
        st.markdown("### 📈 Resumo Analítico")
        
        if len(df_filtrado) > 0:
            # Agrupamento e cálculo
            summary = df_filtrado.groupby(['Comercial', 'Entidade'], as_index=False).agg({
                'Valor Pendente': 'sum',
                'Days_Overdue': 'max'
            })
            summary['Valor Pendente'] = summary['Valor Pendente'].round(2)
            summary = summary.rename(columns={'Days_Overdue': 'Max Days Overdue'})
            summary = summary.sort_values('Valor Pendente', ascending=False)

            # Métricas em cards
            col1, col2, col3, col4 = st.columns(4)
            
            sub_total = summary['Valor Pendente'].sum()
            num_entidades = summary['Entidade'].nunique()
            num_comerciais = summary['Comercial'].nunique()
            max_dias = summary['Max Days Overdue'].max()

            with col1:
                card_class = "metric-card-danger" if sub_total > 10000 else "metric-card-warning" if sub_total > 5000 else "metric-card-success"
                st.markdown(f"""
                <div class="{card_class}">
                    <h3 style="margin:0; font-size: 0.9rem;">Total Pendente</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">€{sub_total:,.2f}</p>
                    <p style="margin:0; font-size: 0.8rem;">{filtro_aplicado}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size: 0.9rem;">Entidades</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{num_entidades}</p>
                    <p style="margin:0; font-size: 0.8rem;">Clientes únicos</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size: 0.9rem;">Comerciais</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{num_comerciais}</p>
                    <p style="margin:0; font-size: 0.8rem;">Em análise</p>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size: 0.9rem;">Máx. Dias</h3>
                    <p style="margin:0; font-size: 1.5rem; font-weight: bold;">{int(max_dias)}</p>
                    <p style="margin:0; font-size: 0.8rem;">Em atraso</p>
                </div>
                """, unsafe_allow_html=True)

            # Alertas
            if sub_total > 10000:
                st.error(f"🚨 ALERTA CRÍTICO: {filtro_aplicado} tem €{sub_total:,.2f} em pendências!")
            elif sub_total > 5000:
                st.warning(f"⚠️ AVISO: {filtro_aplicado} ultrapassa €5.000 em pendências.")
            else:
                st.success(f"✅ SITUAÇÃO CONTROLADA: {filtro_aplicado} dentro dos limites.")

            # Tabela de dados
            st.markdown("### 📋 Detalhamento por Comercial e Entidade")
            st.dataframe(
                summary,
                use_container_width=True,
                height=400
            )

        else:
            st.warning("📭 Nenhum dado encontrado com os filtros aplicados.")

    with tab2:
        st.markdown("### 📁 Exportação de Dados")
        
        if len(df_filtrado) > 0:
            # Criar arquivo Excel
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                summary.to_excel(writer, index=False, sheet_name='Resumo')
                worksheet = writer.sheets['Resumo']
                worksheet.set_column('A:D', 25)
                
                # Formatação condicional
                format_currency = writer.book.add_format({'num_format': '#,##0.00€'})
                worksheet.set_column('C:C', 20, format_currency)
                
            excel_buffer.seek(0)

            # Nome do arquivo
            if selected_comercial != "Todos":
                filename_base = selected_comercial.replace(' ', '_')
            elif search_term:
                filename_base = f"busca_{search_term.replace(' ', '_')}"
            else:
                filename_base = "todos_comerciais"
            
            filename = f"Resumo_Pendencias_{filename_base}.xlsx"
            
            # Botão de download
            st.download_button(
                label="⬇️ BAIXAR RELATÓRIO EXCEL",
                data=excel_buffer.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="download_excel"
            )
            
            st.info(f"📊 Relatório contendo {len(summary)} registros de {summary['Comercial'].nunique()} comerciais.")
        else:
            st.warning("ℹ️ Nenhum dado disponível para exportação.")

    with tab3:
        st.markdown("### 📧 Envio de Relatório por Email")
        
        if len(df_filtrado) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔐 Configuração do Email")
                sender_email = st.text_input("✉️ Email Remetente", placeholder="seu_email@empresa.com")
                sender_password = st.text_input("🔑 Password", type="password", placeholder="Sua senha de app")
                receiver_email = st.text_input("📨 Email Destinatário", placeholder="destinatario@empresa.com")
            
            with col2:
                st.markdown("#### 🌐 Configuração SMTP")
                smtp_server = st.text_input("Servidor SMTP", value="smtp.gmail.com")
                smtp_port = st.number_input("Porta SMTP", value=587, min_value=1, max_value=65535)
                
                st.markdown("---")
                st.markdown("#### 📋 Pré-visualização")
                st.write(f"**Assunto:** Relatório de Pendências - {filtro_aplicado}")
                st.write(f"**Registros:** {len(summary)} entradas")
                st.write(f"**Total:** €{sub_total:,.2f}")

            if st.button("📬 ENVIAR RELATÓRIO POR EMAIL", use_container_width=True, key="send_email"):
                if not all([sender_email, sender_password, receiver_email]):
                    st.error("❌ Preencha todos os campos de email.")
                else:
                    try:
                        # Criar arquivo para anexo
                        email_excel_buffer = BytesIO()
                        with pd.ExcelWriter(email_excel_buffer, engine='xlsxwriter') as writer:
                            summary.to_excel(writer, index=False, sheet_name='Resumo')
                            writer.sheets['Resumo'].set_column('A:D', 25)
                        email_excel_buffer.seek(0)

                        # Criar mensagem
                        msg = MIMEMultipart()
                        msg['From'] = sender_email
                        msg['To'] = receiver_email
                        msg['Subject'] = f"📊 Relatório de Pendências - {filtro_aplicado}"

                        body = f"""
                        <html>
                            <body style="font-family: Arial, sans-serif;">
                                <h2 style="color: #667eea;">📊 Relatório de Valores Pendentes</h2>
                                <p>Segue em anexo o relatório de pendências para <strong>{filtro_aplicado}</strong>.</p>
                                
                                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 15px 0;">
                                    <h3 style="color: #333;">📈 Resumo Estatístico:</h3>
                                    <ul>
                                        <li><strong>Total Pendente:</strong> €{sub_total:,.2f}</li>
                                        <li><strong>Número de Comerciais:</strong> {num_comerciais}</li>
                                        <li><strong>Número de Entidades:</strong> {num_entidades}</li>
                                        <li><strong>Máximo de Dias em Atraso:</strong> {int(max_dias)} dias</li>
                                    </ul>
                                </div>
                                
                                <p>Atenciosamente,<br>
                                <strong>Dashboard de Gestão de Pendências</strong></p>
                            </body>
                        </html>
                        """
                        
                        msg.attach(MIMEText(body, 'html'))

                        # Anexar arquivo
                        attachment = MIMEApplication(email_excel_buffer.getvalue(), _subtype="xlsx")
                        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                        msg.attach(attachment)

                        # Enviar email
                        server = smtplib.SMTP(smtp_server, smtp_port)
                        server.starttls()
                        server.login(sender_email, sender_password)
                        server.sendmail(sender_email, receiver_email, msg.as_string())
                        server.quit()

                        st.success("✅ Email enviado com sucesso!")
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao enviar email: {str(e)}")
        else:
            st.warning("ℹ️ Nenhum dado disponível para envio por email.")

else:
    st.info("📝 Clique no botão 'Atualizar Dados do Excel' para carregar as informações.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "📊 Dashboard desenvolvido para gestão eficiente de pendências • "
    f"Última execução: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    "</div>", 
    unsafe_allow_html=True
)
