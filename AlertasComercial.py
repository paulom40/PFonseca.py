import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import io
from io import BytesIO
import xlsxwriter

st.set_page_config(page_title="📊 Overdue Invoices Summary", layout="wide")
st.title("📌 Soma de Valores Pendentes")

github_url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/V0808.xlsx"

@st.cache_data
def load_data():
    try:
        response = requests.get(github_url)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), sheet_name="Sheet1")
        df.columns = [col.strip() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar ficheiro: {e}")
        return None

# 🔄 Botão para atualizar dados
if st.button("🔄 Atualizar dados do Excel"):
    st.session_state.df = load_data()
    st.session_state.last_updated = datetime.now()
    st.success("✅ Dados atualizados com sucesso!")

# 🕒 Mostrar data/hora da última atualização
if "last_updated" in st.session_state:
    st.caption(f"🕒 Última atualização: {st.session_state.last_updated.strftime('%d/%m/%Y %H:%M:%S')}")

df = st.session_state.get("df", None)

if df is not None:
    st.subheader("🔍 Raw Data Preview")
    st.dataframe(df.head())

    # Limpeza e preparação
    df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
    df['Valor Pendente'] = pd.to_numeric(df['Valor Pendente'], errors='coerce')
    df['Days_Overdue'] = (-df['Dias']).clip(lower=0)
    df['Comercial'] = df.iloc[:, 11].astype(str).str.strip()  # Coluna L = índice 11
    df['Entidade'] = df['Entidade'].astype(str).str.strip()

    overdue_df = df[(df['Dias'] <= 0) & (df['Valor Pendente'] > 0)].copy()

    if not overdue_df.empty:
        summary = overdue_df.groupby(['Entidade', 'Comercial'], as_index=False).agg({
            'Valor Pendente': 'sum',
            'Days_Overdue': 'max'
        })
        summary['Valor Pendente'] = summary['Valor Pendente'].round(2)
        summary = summary.rename(columns={'Days_Overdue': 'Max Days Overdue'})

        st.subheader("📊 Resumo Geral")
        st.dataframe(summary)
        st.metric("💰 Total Pendente", f"€{summary['Valor Pendente'].sum():,.2f}")

        # 🔎 Filtro lateral por Comercial
        st.sidebar.header("🔎 Filtro por Comercial")
        comerciales = sorted(summary['Comercial'].dropna().unique())
        selected_comercial = st.sidebar.selectbox("👤 Selecionar Comercial", ["Todos"] + comerciales)

        if selected_comercial == "Todos":
            filtered_summary = summary[['Comercial', 'Entidade', 'Valor Pendente', 'Max Days Overdue']]
        else:
            filtered_summary = summary[summary['Comercial'] == selected_comercial][['Comercial', 'Entidade', 'Valor Pendente', 'Max Days Overdue']]

        st.subheader("📋 Resumo por Comercial")
        st.dataframe(filtered_summary)

        sub_total = filtered_summary['Valor Pendente'].sum()
        st.metric("📌 Subtotal", f"€{sub_total:,.2f}")

        if sub_total > 10000:
            st.error(f"🚨 Alerta: Comercial '{selected_comercial}' tem mais de €10.000 em pendências!")
        elif sub_total > 5000:
            st.warning(f"⚠️ Comercial '{selected_comercial}' ultrapassa €5.000 em pendências.")
        else:
            st.success(f"✅ Comercial '{selected_comercial}' está dentro do limite.")

        # 📁 Exportação Excel
        st.subheader("📁 Exportar Resumo em Excel")
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            filtered_summary.to_excel(writer, index=False, sheet_name='Resumo')
            writer.sheets['Resumo'].set_column('A:D', 25)
        excel_buffer.seek(0)

        st.download_button(
            label="⬇️ Download Excel",
            data=excel_buffer.getvalue(),
            file_name=f"Resumo_{selected_comercial.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # 📧 Enviar por Email
        st.subheader("📤 Enviar Resumo por Email")
        sender_email = st.text_input("✉️ Email Remetente", value="your_email@example.com")
        sender_password = st.text_input("🔑 Password", type="password")
        receiver_email = st.text_input("📨 Email Destinatário", value="recipient@example.com")
        smtp_server = st.text_input("🌐 SMTP Server", value="smtp.gmail.com")
        smtp_port = st.number_input("📡 SMTP Port", value=587)

        if st.button("📬 Enviar Emails por Comercial"):
            try:
                if summary.empty or len(comerciales) == 0:
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg['Subject'] = "📌 Overdue Invoices Summary - No Overdue Invoices"
                    body = "Dear Recipient,\n\nNo overdue invoices found at this time.\n\nBest regards,\nStreamlit App"
                    msg.attach(MIMEText(body, 'plain'))

                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, msg.as_string())
                    server.quit()

                    st.success("✅ Email enviado: Sem pendências.")
                else:
                    commercial_groups = summary.groupby('Comercial')
                    for comercial, group in commercial_groups:
                        sub_total = group['Valor Pendente'].sum()
                        msg = MIMEMultipart()
                        msg['From'] = sender_email
                        msg['To'] = receiver_email
                        msg['Subject'] = f"📌 Overdue Summary for {comercial} - €{sub_total:,.2f}"

                        body = f"""
Dear Recipient,

Please find the summary of overdue invoices for {comercial} below:

{group[['Entidade', 'Valor Pendente', 'Max Days Overdue']].to_string(index=False)}

Total for {comercial}: €{sub_total:,.2f}

Best regards,
Streamlit App
"""
                        msg.attach(MIMEText(body, 'plain'))

                        csv_buffer = io.StringIO()
                        group.to_csv(csv_buffer, index=False)
                        attachment = MIMEApplication(csv_buffer.getvalue(), _subtype="csv")
                        attachment.add_header('Content-Disposition', 'attachment', filename=f'overdue_summary_{comercial.replace(" ", "_")}.csv')
                        msg.attach(attachment)

                        server = smtplib.SMTP(smtp_server, smtp_port)
                        server.starttls()
                        server.login(sender_email, sender_password)
                        server.sendmail(sender_email, receiver_email, msg.as_string())
                        server.quit()

                    st.success(f"✅ Emails enviados com sucesso para {len(commercial_groups)} comerciais!")
            except Exception as e:
                st.error(f"❌ Erro ao enviar emails: {str(e)}")
else:
    st.info("ℹ️ Clica no botão acima para carregar os dados.")
