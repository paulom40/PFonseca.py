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
import io

st.set_page_config(page_title="📊 Overdue Invoices Summary", layout="wide")
st.title("📌 Soma de Valores Pendentes")

github_url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/V0808.xlsx"

@st.cache_data
def load_data():
    try:
        response = requests.get(github_url)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), sheet_name="Sheet1", header=None)
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar ficheiro: {e}")
        return None

# 🔄 Atualizar dados
if st.button("🔄 Atualizar dados do Excel"):
    st.session_state.df = load_data()
    st.session_state.last_updated = datetime.now()
    st.success("✅ Dados atualizados com sucesso!")

# 🕒 Mostrar data/hora da última atualização
if "last_updated" in st.session_state:
    st.caption(f"🕒 Última atualização: {st.session_state.last_updated.strftime('%d/%m/%Y %H:%M:%S')}")

df = st.session_state.get("df", None)

if df is not None:
    # Renomear colunas relevantes
    df = df.rename(columns={
        1: "Entidade",
        7: "Data Doc.",
        8: "Dias",
        10: "Valor Pendente",
        11: "Comercial"
    })

    # Limpeza e preparação
    df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
    df['Valor Pendente'] = pd.to_numeric(df['Valor Pendente'], errors='coerce')
    df['Days_Overdue'] = (-df['Dias']).clip(lower=0)
    df['Comercial'] = df['Comercial'].astype(str).str.strip()
    df['Entidade'] = df['Entidade'].astype(str).str.strip()

    # Filtrar pendências
    overdue_df = df[(df['Dias'] <= 0) & (df['Valor Pendente'] > 0)].copy()

    # 🔎 Filtro lateral por Comercial
    st.sidebar.header("🔎 Filtro por Comercial")
    comerciais = sorted(overdue_df['Comercial'].dropna().unique())
    selected_comercial = st.sidebar.selectbox("👤 Selecionar Comercial", ["Todos"] + comerciais)

    # Aplicar filtro diretamente sobre overdue_df
    if selected_comercial == "Todos":
        df_filtrado = overdue_df.copy()
    else:
        df_filtrado = overdue_df[overdue_df['Comercial'] == selected_comercial]

    # Agrupamento por Comercial e Entidade
    summary = df_filtrado.groupby(['Comercial', 'Entidade'], as_index=False).agg({
        'Valor Pendente': 'sum',
        'Days_Overdue': 'max'
    })
    summary['Valor Pendente'] = summary['Valor Pendente'].round(2)
    summary = summary.rename(columns={'Days_Overdue': 'Max Days Overdue'})

    st.subheader("📋 Resumo por Comercial")
    st.dataframe(summary)

    sub_total = summary['Valor Pendente'].sum()
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
        summary.to_excel(writer, index=False, sheet_name='Resumo')
        writer.sheets['Resumo'].set_column('A:D', 25)
    excel_buffer.seek(0)

    st.download_button(
        label="⬇️ Download Excel",
        data=excel_buffer.getvalue(),
        file_name=f"Resumo_{selected_comercial.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 📧 Envio por Email
    st.subheader("📤 Enviar Resumo por Email")
    sender_email = st.text_input("✉️ Email Remetente", value="teu_email@example.com")
    sender_password = st.text_input("🔑 Password", type="password")
    receiver_email = st.text_input("📨 Email Destinatário", value="destinatario@example.com")
    smtp_server = st.text_input("🌐 SMTP Server", value="smtp.gmail.com")
    smtp_port = st.number_input("📡 SMTP Port", value=587)

    if st.button("📬 Enviar Email"):
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = f"📌 Resumo de Pendências - {selected_comercial}"

            body = f"""
Olá,

Segue em anexo o resumo de pendências para o comercial '{selected_comercial}'.

Total pendente: €{sub_total:,.2f}

Atenciosamente,
Dashboard Streamlit
"""
            msg.attach(MIMEText(body, 'plain'))

            csv_buffer = io.StringIO()
            summary.to_csv(csv_buffer, index=False)
            attachment = MIMEApplication(csv_buffer.getvalue(), _subtype="csv")
            attachment.add_header('Content-Disposition', 'attachment', filename=f'resumo_{selected_comercial.replace(" ", "_")}.csv')
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
    st.info("ℹ️ Clica no botão acima para carregar os dados.")
