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

# 🎯 Page config
st.set_page_config(page_title="📊 Overdue Invoices Summary", layout="wide")

# 🏷️ Title
st.title("📌 Sum of Pending Values for Overdue Invoices")

# 📁 GitHub raw URL for the Excel file
github_url = "https://raw.githubusercontent.com/paulom40/PFonseca.py/main/V0808.xlsx"

# 📥 Load the Excel file from GitHub
@st.cache_data
def load_data():
    try:
        response = requests.get(github_url)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), sheet_name="Sheet1")
        df.columns = [col.strip() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"❌ Error loading file from GitHub: {e}")
        return None

df = load_data()

# 📊 Excel styling function
def create_styled_excel(summary_df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        summary_df.to_excel(writer, sheet_name='Overdue Summary', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Overdue Summary']

        # 🎨 Formats
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#4F81BD', 'font_color': 'white',
            'border': 1, 'align': 'center'
        })
        currency_format = workbook.add_format({'num_format': '€#,##0.00', 'border': 1})
        days_format = workbook.add_format({'border': 1})
        entity_format = workbook.add_format({'border': 1})
        comercial_format = workbook.add_format({'border': 1, 'bg_color': '#DDEBF7'})

        # 🧾 Apply header format
        for col_num, value in enumerate(summary_df.columns):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 20)

        # 🧾 Apply cell formats
        for row_num, row_data in enumerate(summary_df.values, start=1):
            worksheet.write(row_num, 0, row_data[0], entity_format)
            worksheet.write(row_num, 1, row_data[1], comercial_format)
            worksheet.write(row_num, 2, row_data[2], currency_format)
            worksheet.write(row_num, 3, row_data[3], days_format)

    output.seek(0)
    return output

# ✅ Initialize early to avoid NameError
summary = pd.DataFrame()
total_overdue = 0
comerciales = []

# 📊 Data processing
if df is not None:
    st.subheader("🔍 Raw Data Preview")
    st.dataframe(df.head())

    df['Dias'] = pd.to_numeric(df['Dias'], errors='coerce')
    df['Valor Pendente'] = pd.to_numeric(df['Valor Pendente'], errors='coerce')
    df['Days_Overdue'] = (-df['Dias']).clip(lower=0)

    overdue_df = df[(df['Dias'] <= 0) & (df['Valor Pendente'] > 0)].copy()

    if not overdue_df.empty:
        summary = overdue_df.groupby(['Entidade', 'Comercial']).agg({
            'Valor Pendente': 'sum',
            'Days_Overdue': 'max'
        }).reset_index()
        summary['Valor Pendente'] = summary['Valor Pendente'].round(2)
        summary = summary.rename(columns={'Days_Overdue': 'Max Days Overdue'})
        total_overdue = summary['Valor Pendente'].sum()

        if 'Comercial' in summary.columns:
            comerciales = sorted(summary['Comercial'].dropna().unique())

        st.subheader("📊 Overall Summary")
        st.dataframe(summary)
        st.metric("💰 Total Overdue Amount", f"€{total_overdue:,.2f}")
    else:
        st.warning("⚠️ No overdue invoices found.")

    # 🎯 Sidebar filter
    st.sidebar.header("🔎 Filter Options")
    selected_comercial = st.sidebar.selectbox(
        "👤 Select Comercial",
        ["All"] + list(comerciales) if comerciales else ["All"]
    )

    # 📋 Resume Table
    st.subheader("📋 Resume Table by Comercial")
    if selected_comercial == "All":
        filtered_summary = summary[['Comercial', 'Entidade', 'Valor Pendente', 'Max Days Overdue']]
    else:
        filtered_summary = summary[summary['Comercial'] == selected_comercial][['Comercial', 'Entidade', 'Valor Pendente', 'Max Days Overdue']]

    st.dataframe(filtered_summary)
    sub_total = filtered_summary['Valor Pendente'].sum()
    st.metric("📌 Sub Total", f"€{sub_total:,.2f}")

    # 📥 Excel download
    st.subheader("📁 Download Styled Excel Summary")
    excel_data = create_styled_excel(summary)
    st.download_button(
        label="⬇️ Download Excel File",
        data=excel_data,
        file_name="Overdue_Invoices_Summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 📧 Email section
    st.subheader("📤 Send Summary via Email")
    sender_email = st.text_input("✉️ Sender Email", value="your_email@example.com")
    sender_password = st.text_input("🔑 Sender Password", type="password")
    receiver_email = st.text_input("📨 Receiver Email", value="recipient@example.com")
    smtp_server = st.text_input("🌐 SMTP Server", value="smtp.gmail.com")
    smtp_port = st.number_input("📡 SMTP Port", value=587)

    if st.button("📬 Send Emails Per Commercial"):
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

                st.success("✅ Email sent: No overdue invoices.")
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

                st.success(f"✅ Emails sent successfully for {len(commercial_groups)} commercials!")
        except Exception as e:
            st.error(f"❌ Error sending emails: {str(e)}")
else:
    st.info("ℹ️ Unable to load the Excel file. Please check the GitHub link.")
