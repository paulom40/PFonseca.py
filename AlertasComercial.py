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

st.set_page_config(page_title="📊 Overdue Invoices Summary", layout="wide")
st.title("📌 Soma de Valores Pendentes")

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

# 🔄 Atualizar dados
if st.button("🔄 Atualizar dados do Excel"):
    st.cache_data.clear()
    st.session_state.df = load_data()
    st.session_state.last_updated = datetime.now()
    st.success("✅ Dados atualizados com sucesso!")

# 🕒 Mostrar data/hora da última atualização
if "last_updated" in st.session_state:
    st.caption(f"🕒 Última atualização: {st.session_state.last_updated.strftime('%d/%m/%Y %H:%M:%S')}")

df = st.session_state.get("df", load_data())

if df is not None:
    st.write("📊 Colunas detectadas:", df.columns.tolist())

    # Verificar se a coluna 'Dias' existe
    if "Dias" not in df.columns:
        st.error("❌ A coluna 'Dias' não foi encontrada no ficheiro. Verifique o cabeçalho.")
        st.stop()

    # Limpeza e preparação
    df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
    df['Valor Pendente'] = pd.to_numeric(df['Valor Pendente'], errors='coerce')
    df['Days_Overdue'] = (-df['Dias']).clip(lower=0)
    df['Comercial'] = df['Comercial'].astype(str).str.replace(r'[\t\n\r ]+', ' ', regex=True).str.strip()
    df['Entidade'] = df['Entidade'].astype(str).str.strip()

    # Filtrar pendências
    overdue_df = df[(df['Dias'] <= 0) & (df['Valor Pendente'] > 0)].copy()
    overdue_df['Comercial'] = overdue_df['Comercial'].astype(str).str.replace(r'[\t\n\r ]+', ' ', regex=True).str.strip()

    # 🔎 Filtro por Comercial - CORRIGIDO
    st.sidebar.header("🔎 Filtro por Comercial")
    
    # Lista de comerciais únicos para referência
    comerciais = sorted(overdue_df['Comercial'].dropna().unique())
    
    # Adicionar opção "Todos" no início
    opcoes_comerciais = ["Todos"] + comerciais
    selected_comercial = st.sidebar.selectbox("Selecione o Comercial:", opcoes_comerciais)
    
    # Busca por texto alternativo
    search_term = st.sidebar.text_input("Ou digite o nome do Comercial (busca parcial):")
    
    # Aplicar filtro
    if selected_comercial == "Todos" and not search_term:
        # Mostrar todos
        df_filtrado = overdue_df.copy()
        filtro_aplicado = "Todos os comerciais"
        
    elif selected_comercial != "Todos":
        # Filtro por seleção do dropdown
        df_filtrado = overdue_df[overdue_df['Comercial'] == selected_comercial].copy()
        filtro_aplicado = f"Comercial: {selected_comercial}"
        
    elif search_term:
        # Filtro por busca de texto (parcial + fuzzy)
        search_upper = search_term.upper().strip()
        
        # Primeiro tenta busca parcial case-insensitive
        mask_partial = overdue_df['Comercial'].str.upper().str.contains(search_upper, na=False)
        df_partial = overdue_df[mask_partial].copy()
        
        if len(df_partial) > 0:
            # Se encontrou com busca parcial, usa esses resultados
            df_filtrado = df_partial
            comerciais_encontrados = df_filtrado['Comercial'].unique()
            filtro_aplicado = f"Busca parcial: '{search_term}' - Encontrados: {', '.join(comerciais_encontrados)}"
        else:
            # Se não encontrou, tenta fuzzy matching
            matches = difflib.get_close_matches(search_term, comerciais, n=3, cutoff=0.3)
            if matches:
                mask_fuzzy = overdue_df['Comercial'].isin(matches)
                df_filtrado = overdue_df[mask_fuzzy].copy()
                filtro_aplicado = f"Busca aproximada: '{search_term}' - Correspondências: {', '.join(matches)}"
            else:
                # Se não encontrou nada, mostra vazio
                df_filtrado = pd.DataFrame()
                filtro_aplicado = f"Busca: '{search_term}' - Nenhum resultado encontrado"
                st.sidebar.warning(f"Nenhum comercial encontrado para '{search_term}'")
    else:
        # Fallback
        df_filtrado = overdue_df.copy()
        filtro_aplicado = "Todos os comerciais"

    # Debug no sidebar
    st.sidebar.write(f"**Filtro aplicado:** {filtro_aplicado}")
    st.sidebar.write(f"**Linhas em overdue_df:** {len(overdue_df)}")
    st.sidebar.write(f"**Linhas após filtro:** {len(df_filtrado)}")
    
    if len(df_filtrado) > 0:
        st.sidebar.write(f"**Comerciais no filtro:** {df_filtrado['Comercial'].nunique()}")
        st.sidebar.write("**Amostra:**", df_filtrado['Comercial'].unique()[:3].tolist())

    # Agrupamento por Comercial e Entidade
    if len(df_filtrado) > 0:
        summary = df_filtrado.groupby(['Comercial', 'Entidade'], as_index=False).agg({
            'Valor Pendente': 'sum',
            'Days_Overdue': 'max'
        })
        summary['Valor Pendente'] = summary['Valor Pendente'].round(2)
        summary = summary.rename(columns={'Days_Overdue': 'Max Days Overdue'})
        
        # Ordenar por valor pendente (decrescente)
        summary = summary.sort_values('Valor Pendente', ascending=False)
    else:
        summary = pd.DataFrame()

    st.subheader("📋 Resumo por Comercial")
    
    if len(summary) > 0:
        st.dataframe(summary)
        
        sub_total = summary['Valor Pendente'].sum()
        st.metric("📌 Subtotal", f"€{sub_total:,.2f}")

        # Alertas
        if sub_total > 10000:
            st.error(f"🚨 Alerta: {filtro_aplicado} tem mais de €10.000 em pendências!")
        elif sub_total > 5000:
            st.warning(f"⚠️ {filtro_aplicado} ultrapassa €5.000 em pendências.")
        else:
            st.success(f"✅ {filtro_aplicado} está dentro do limite.")

        # 📁 Exportação Excel
        st.subheader("📁 Exportar Resumo em Excel")
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            summary.to_excel(writer, index=False, sheet_name='Resumo')
            writer.sheets['Resumo'].set_column('A:D', 25)
        excel_buffer.seek(0)

        # Nome do arquivo baseado no filtro
        if selected_comercial != "Todos":
            filename_base = selected_comercial.replace(' ', '_')
        elif search_term:
            filename_base = f"busca_{search_term.replace(' ', '_')}"
        else:
            filename_base = "todos"
            
        filename = f"Resumo_{filename_base}.xlsx"
        
        st.download_button(
            label="⬇️ Download Excel",
            data=excel_buffer.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Nenhum dado encontrado com os filtros aplicados.")
        sub_total = 0

    # 📧 Envio por Email (mantido igual)
    st.subheader("📤 Enviar Resumo por Email")
    if len(summary) > 0:
        sender_email = st.text_input("✉️ Email Remetente", value="teu_email@example.com")
        sender_password = st.text_input("🔑 Password", type="password")
        receiver_email = st.text_input("📨 Email Destinatário", value="destinatario@example.com")
        smtp_server = st.text_input("🌐 SMTP Server", value="smtp.gmail.com")
        smtp_port = st.number_input("📡 SMTP Port", value=587)

        if st.button("📬 Enviar Email"):
            try:
                email_excel_buffer = BytesIO()
                with pd.ExcelWriter(email_excel_buffer, engine='xlsxwriter') as writer:
                    summary.to_excel(writer, index=False, sheet_name='Resumo')
                    writer.sheets['Resumo'].set_column('A:D', 25)
                email_excel_buffer.seek(0)

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['Subject'] = f"📌 Resumo de Pendências - {filtro_aplicado[:30]}"

                body = f"""
Olá,

Segue em anexo o resumo de pendências para {filtro_aplicado}.

Total pendente: €{sub_total:,.2f}

Atenciosamente,
Dashboard Streamlit
"""
                msg.attach(MIMEText(body, 'plain'))

                attachment = MIMEApplication(email_excel_buffer.getvalue(), _subtype="xlsx")
                attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(attachment)

                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
                server.quit()

                st.success("✅ Email enviado com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao enviar email: {str(e)}")
    else:
        st.info("ℹ️ Adicione dados ao resumo para habilitar o envio por email.")

else:
    st.info("ℹ️ Clica no botão acima para carregar os dados.")
